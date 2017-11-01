/*
 * Copyright (c) 2017 Stefan Seefeld
 * All rights reserved.
 *
 * This file is part of Faber. It is made available under the
 * Boost Software License, Version 1.0.
 * (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)
 */

#include "graph.h"

void cleanup_depth(TARGET *t)
{
  TARGETS *c;
  t->depth = 0;
  for (c = t->depends; c; c = c->next)
    cleanup_depth(c->target);
}

static TARGET *find_cycle(TARGET *t)
{
  /*
   * Use the 'depth' member to store processing status,
   * as that is only used inside make0(), and the two never run at
   * the same time.
   * Return a target that's part of a cycle. Follow its dependencies and look for
   * those who have depth set to 1 to get all targets that are part of the cycle.
   * 0: init
   * 1: visited
   * 2: done
   */
  TARGETS *c;
  if (t->depth == 1)
    return t;
  else if (t->depth == 2)
    return 0;
  t->depth = 1;
  for (c = t->depends; c; c = c->next)
  {
    TARGET *f = find_cycle(c->target);
    if (f) return f;
  }
  t->depth = 2;
  return 0;
}

static void print_cycle_(TARGET *t, TARGET *root)
{
  TARGETS * c;
  int count = 0;
  printf("%s (%s)\n", object_str(t->name), object_str(t->boundname));
  for (c = t->depends; c; c = c->next)
    count++;
  for (c = t->depends; c; c = c->next)
    if (c->target->depth == 1)
    {
      if (c->target != root)
	print_cycle_(c->target, root);
      else
	printf("%s (%s)\n",
	       object_str(root->name),
	       object_str(root->boundname));
      return;
    }
}
static void print_cycle(TARGET *t) { print_cycle_(t, t);}

static TARGETS *add_unique(TARGETS *chain, LIST *target_names)
{
  LISTITER iter = list_begin(target_names);
  LISTITER const end = list_end(target_names);
  for (; iter != end; iter = list_next(iter))
  {
    TARGET *t = bindtarget(list_item(iter));
    TARGETS *i = chain;
    for (; i; i = i->next)
      if (i->target == t) break;
    if (!i)
      chain = targetentry(chain, t);
  }
  return chain;
}

int add_dependency(char const *t, LIST *const sources)
{
  OBJECT *name = object_new(t);
  TARGET *const target = bindtarget(name);
  TARGET * c;
  LISTITER i;
  LISTITER end;
  if (target->progress >= T_MAKE_BOUND)
    return -1;
  target->depends = add_unique(target->depends, sources);
  c = find_cycle(target);
  if (c)
  {
    print_cycle(c);
    return -2;
  }
  else
    cleanup_depth(target);

  /* Enter reverse links */
  end = list_end(sources);
  for (i = list_begin(sources); i != end; i = list_next(i))
  {
    TARGET * const s = bindtarget(list_item(i));
    LIST *targets = list_new(name);
    s->dependants = add_unique(s->dependants, targets);
  }
  if (target->progress >= T_MAKE_LAUNCHED)
    schedule_targets(sources, target);
  return 0;
}

void set_flags(LIST *const targets, int flags)
{
  LISTITER i;
  LISTITER const end = list_end(targets);
  for (i = list_begin(targets); i != end; i = list_next(i))
    bindtarget(list_item(i))->flags |= flags;
}

int update(LIST *const targets)
{
  return make(targets);
}
