Glossary
========

.. glossary::

  **action**
    An action is one of the basic building blocks in Boost.Faber. It is
    performed to make an artefact, typically from one or more sources.

  **build**
    A build is a single execution of the build instructions associated
    with a project. It typically corresponds to a single invocation of
    the build tool, with a set of either explicitly or implicitly selected
    make artefacts, as well as a set of explicitly or implicitly defined
    build parameters.

  **feature**
    Features define typed variables that can be used to customize the
    build process.
    
  **module**
    A module provides the means to sub-structure build instructions into
    (somewhat) independent units. Each module uses a single conscript,
    and may reference other modules.
    
  **rule**
    A rule expresses how one or more artefacts can be made by virtue of an
    action.

   **implicit rule**
    An implicit rule is a rule template that expresses how one artefact *type*
    can be made from another artefact *type*. Implicit rules are defined by
    tools.

  **source**
    Something (typically a file) from which an artefact can be made by means
    of an action.

  **artefact**
    Something (typically a file) which can be made by means of an action.

  **tool**
    A tool provides one or more actions. Tools may be instantiated
    to customize their actions. Tools may be related using typical
    sub-/super-class relationships, allowing for actions to become
    polymorphic.
