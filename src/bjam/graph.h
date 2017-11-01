/*
 * Copyright (c) 2017 Stefan Seefeld
 * All rights reserved.
 *
 * This file is part of Faber. It is made available under the
 * Boost Software License, Version 1.0.
 * (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)
 */
#ifndef graph_h_
#define graph_h_

#include "lists.h"
#include "rules.h"

/* reset the depth member of t and its prerequisites to 0 */
void cleanup_depth(TARGET *t);
/* declare dependencies. Return:
 *  * 0 on success
 *  * -1 if the target's update is already in progress
 *  * -2 if the new dependency introduces a cycle
 */
int add_dependency(char const *target, LIST *const sources);
/* set the target's flags */
void set_flags(LIST *const targets, int flags);
/* update the given targets */
int update(LIST *const targets);

#endif
