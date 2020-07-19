#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import asyncio
from enum import Enum, Flag, IntEnum
from os.path import dirname, lexists
from os import stat, makedirs, remove, rmdir
from collections import defaultdict
import logging

logger = logging.getLogger('scheduler')
summary_logger = logging.getLogger('summary')

flag = Flag('flag',
            'NONE '
            'TEMP NOCARE NOTFILE TOUCHED '
            'LEAVES NOUPDATE XX RMOLD '
            'INTERNAL PRECIOUS NOPROPAGATE', start=0)
binding = Enum('binding', 'UNBOUND MISSING PARENTS EXISTS')
fate = IntEnum('fate',
               'INIT MAKING STABLE NEWER SPOIL '
               'ISTMP BUILD TOUCHED REBUILD MISSING NEEDTMP '
               'OUTDATED UPDATE BROKEN CANTFIND CANTMAKE')
progress = IntEnum('progress',
                   'INIT LAUNCHED BOUND RUNNING DONE NOEXEC_DONE')


def _cyclic(artefact, root=None):
    if root == artefact:
        yield True
    root=root or artefact
    for p in artefact.prerequisites:
        yield from _cyclic(p, root)


def cyclic(artefact):
    return next(_cyclic(artefact), False)


class dependency_error(Exception): pass


class artefact(object):

    @classmethod
    def init(cls, files=[], keep_temps=False, force=False):
        """set up some global state."""
        cls.counter = defaultdict(int)
        cls.files = files
        cls.temp_files = set()
        cls.keep_temps = keep_temps
        cls.force = force

    @classmethod
    def finish(cls):
        """clean up."""
        # Remove temp files...
        if not cls.keep_temps:
            for i in cls.temp_files:
                if lexists(i):
                    remove(i)
        # ...and print a cumulative summary
        cls._format_count('...failed updating {} artefact{}...', 'failed')
        cls._format_count('...skipped {} artefact{}...', 'skipped')
        cls._format_count('...updated {} artefact{}...', 'updated')

        del cls.files

    @classmethod
    def clean(cls, level):
        """Remove generated files."""
        dirs = []
        # remove file artefacts...
        for f in cls.files:
            # We may encounter symbolic links during the cleanup
            # which no longer refer to existing files. To be able
            # to detect them we need to use `lexists`...
            if lexists(f):
                dirs.append(dirname(f))
                remove(f)
        if cls.files:
            cls.files.clear()
        # ...then clean up empty build directories
        dirs = sorted(set(dirs), reverse=True)
        root = '' if cls.files.root == '.' else cls.files.root
        for d in dirs:
            try:
                while d != root:
                    rmdir(d)
                    d = dirname(d)
            except OSError:  # directory wasn't empty, move on
                continue

    @classmethod
    def _format_count(cls, msg, what):
        number = cls.counter[what]
        if number:
            summary_logger.info(msg.format(number, 's' if number > 1 else ''))

    def __init__(self, frontend, prerequisites=[]):
        self.frontend = frontend
        self.boundname = None
        self.recipe = None
        self.prerequisites = set(prerequisites)
        self._lock = asyncio.Lock()
        self._pqueue = None
        self._dependants = set()
        self._rebuilds = set()    # targets that should be force-rebuilt whenever this one is
        self.flags = flag(self.frontend.attrs)
        self.reset()

    def reset(self):
        self.binding = binding.UNBOUND
        self._timestamp = 0
        self._fate = fate.INIT
        self.progress = progress.INIT
        self.status = None

    @property
    def isfile(self):
        return not self.flags & flag.NOTFILE

    @property
    def name(self):
        return self.frontend.name

    @property
    def timestamp(self):
        """Report the artefact's modification time (0 for non-file artefacts).
        For temporaries report the real timestamp only if the file exists.
        Otherwise return the most recent time among its prerequisites."""

        if self.binding == binding.EXISTS:
            return self._timestamp
        elif self.flags & flag.TEMP:  # report most recent prerequisite timestamps
            return max([p.timestamp for p in self.prerequisites], default=0)
        else:
            return 0

    @property
    def fate(self):
        """Return the artefact's fate. For temporaries report the least stable fate of its prerequisites."""
        return max([p.fate for p in self.prerequisites], default=fate.INIT) if self.flags & flag.TEMP else self._fate

    def add_prerequisite(self, p):
        """Add p to the artefact's set of prerequisites.
        This may fail for different reasons:
        * the prerequisite set is immutable once the artefact is bound.
        * the new prerequisite must not introduce a dependency cycle."""

        if self.progress >= progress.BOUND:
            raise dependency_error(f'can not add {p.frontend}: '
                                   f'{self.frontend.boundname} already bound')
        self.prerequisites.add(p)
        if cyclic(self):
            raise dependency_error(f'dependency cycle detected while adding '
                                   f'{self.frontend} -> {p.frontend}')
        if self._pqueue:
            self._pqueue.put_nowait(p)

    async def process(self, parent=None):
        """Process this artefact:
        * process all prerequisites
        * bind it
        * determine its fate
        * update it"""

        await self.launch(parent)
        # at this point all prereqs are bound, non-temps will even be updated.
        await self.bind(parent)
        # temps require parents to be bound first, to determine their fate
        if not self.flags & flag.TEMP or not parent:
            await self.compute_fate(parent)
            await self.update()

    async def launch(self, parent=None):
        """Update all prerequisites."""
        async with self._lock:
            if self.progress >= progress.LAUNCHED:
                return
            logger.info(f'progress -- {self.frontend} launching')
            # the prerequisite set may grow while we process it, so we use a queue.
            self._pqueue = asyncio.Queue()
            await asyncio.gather(*[self._pqueue.put(p) for p in self.prerequisites])
            while not self._pqueue.empty():
                p = await self._pqueue.get()
                await p.process(self)
            self._pqueue = None
            self.progress = progress.LAUNCHED
            logger.info(f'progress -- {self.frontend} launched')

    async def bind(self, parent=None):
        """Bind all artefact-specific variables, including the artefact's filename.
        Precondition: the prerequisite set is now immutable, and all prerequisites are bound."""

        async with self._lock:
            if self.progress >= progress.BOUND:
                return
            try:
                self.frontend.features.eval(update=False)
            except Exception as e:
                logger.critical(f'something went wrong binding {self.frontend}: {e}')
                raise
            self.boundname = self.frontend.boundname
            if not self.flags & flag.NOTFILE:
                d = dirname(self.boundname) or '.'
                if not lexists(d):
                    makedirs(d)
                self.binding = binding.EXISTS if lexists(self.boundname) else binding.MISSING
                self._timestamp = stat(self.boundname).st_mtime if self.binding == binding.EXISTS else 0

            # if temp file does not exist but parent does, use parent
            if (parent and
                self.flags & flag.TEMP and
                self.binding == binding.MISSING and
                parent.binding != binding.MISSING):
                self.binding = binding.PARENTS

            msg = f'bind -- {id(self)} {self.name}: {self.boundname} '
            msg += f'time={self._timestamp}' if self.binding == binding.EXISTS else f'{str(self.binding)}'
            logger.info(msg)
            self.progress = progress.BOUND
            logger.info(f'progress -- {self.frontend} bound')

    async def compute_fate(self, parent=None):

        async with self._lock:
            if self._fate != fate.INIT:
                return
            self._fate=fate.MAKING

            for p in self.prerequisites:
                await p.compute_fate(self)

            self._fate = fate.STABLE
            last = 0
            for p in self.prerequisites:
                if p.flags & flag.NOPROPAGATE:
                    continue
                last = max(last, p.timestamp)
                if self._fate < p.fate:
                    logger.info(f'fate -- change {self.boundname} from {str(self._fate)} to {str(p.fate)} by dependency')
                    self._fate = p.fate
            else:
                # if this a (non-existing) temporary without prerequisites, treat it MISSING
                if self.flags & flag.TEMP:
                    self._fate = fate.MISSING
            if self.flags & flag.NOUPDATE:
                logger.info(f'fate -- change {self.boundname} back to stable, NOUPDATE')
                self._fate = fate.STABLE
            # If can not find or make child, can not make target.
            elif self._fate >= fate.BROKEN:
                self._fate = fate.CANTMAKE
            # If children changed, make target.
            elif self._fate >= fate.SPOIL:
                self._fate = fate.UPDATE
            # If target missing, make it.
            elif self.binding == binding.MISSING:
                self._fate = fate.MISSING
            # If children newer, make target.
            elif self.binding == binding.EXISTS and last > self.timestamp:
                self._fate = fate.OUTDATED
            # If temp's children newer than parent, make temp.
            elif self.binding == binding.PARENTS and last > parent.timestamp:
                self._fate = fate.NEEDTMP
            # If deliberately touched, make it.
            elif self.flags & flag.TOUCHED:
                self._fate = fate.TOUCHED
            # If force flag is set, make it.
            elif artefact.force:
                self._fate = fate.TOUCHED
            # If up-to-date temp file present, use it.
            # If target newer than non-notfile parent, mark target newer.
            # Otherwise, stable!

            if self._fate == fate.MISSING and not self.recipe and not self.prerequisites:
                if self.flags & flag.NOCARE:
                    self._fate = fate.STABLE
                else:
                    self._fate = fate.CANTFIND
            logger.info(f'fate -- {self.boundname}: {str(self._fate)}')

    async def update(self):

        async with self._lock:
            if self.progress == progress.DONE:
                return

            if self._fate != fate.STABLE:
                # Update temporary prerequisites
                await asyncio.gather(*[p.update() for p in self.prerequisites if p.flags & flag.TEMP and p._fate != fate.STABLE])

            failed = None
            if self._fate != fate.STABLE:
                failed = next(iter([p for p in self.prerequisites
                                    if p.fate != fate.STABLE and not p.status and not p.flags & flag.NOCARE]), None)

            # if a prerequisite failed, fail.
            if failed:
                self.status = False
            elif self._fate in (fate.STABLE, fate.NEWER):
                self.status = True
            elif self._fate >= fate.CANTFIND:
                self.status = False
            elif self._fate == fate.ISTMP:
                summary_logger(f'...using {self.boundname}...')
                self.status = True
            elif self._fate >= fate.TOUCHED:
                if self.recipe:
                    self.progress = progress.RUNNING
                    logger.info(f'progress -- {self.frontend} running')
                    logger.info(f'update -- {self.boundname}')
                    self.status = await self.recipe()
                    if self.flags & flag.TEMP:
                        artefact.temp_files.add(self.boundname)
                    elif not self.flags & flag.NOTFILE:
                        artefact.files.append(self.boundname)
                    logger.info(f'update -- {self.boundname} done (status={self.status})')
                    artefact.counter['updated' if self.status else 'failed'] += 1
                else:
                    # TODO: how should we handle alias artefacts ? What if prereqs fail ? Etc.
                    self.status = True
            self.progress = progress.DONE
            logger.info(f'progress -- {self.frontend} done')
            self._report(failed)

    def _report(self, failed):

        if failed:
            msg = f'...skipped {self.boundname} for lack of {failed.boundname}...'
            if self.frontend.logfile:
                self.frontend.logfile.write(msg + '\n')
            else:
                summary_logger.info(msg)
        self.frontend.__status__(self.status)
