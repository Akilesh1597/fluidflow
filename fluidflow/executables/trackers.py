#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fluidflow.containers.future import FutureData
from fluidflow.exceptions import InvalidTaskState
from fluidflow.executables.task import Task


class StatusTracker(Task):
    _valid_states = ('scheduled', 'awaiting', 'execute', 'revert', 'retry')

    def __init__(self, job_card, task_id, loop):
        super(StatusTracker, self).__init__(self, task_id, loop)
        self.job_card = job_card
        self.past_states = []
        self.registered_tasks = []
        self.current_state = None

    def fulfill(self, data):
        self.tracker.fulfill(data)

    async def fetch(self, task, arg_ref):
        data = self.job_card.find(*arg_ref)
        if isinstance(data, FutureData):
            self.update_status(task, 'awaiting', ref=arg_ref,
                               source=data.source)
            arg = await data.fetch()
            self.update_status(task, task.state, ref=arg_ref,
                               source=data.source, data=arg)
            return arg
        return data

    def update_status(self, task, state, result=None, ref=None, source=None,
                      data=None, attempt=None, percentage=None, message=None):
        if state not in self._valid_states:
            raise InvalidTaskState('%s: %s', task.name, task.state)
        if state == 'scheduled':
            if task in self.registered_tasks:
                raise InvalidTaskState('%s: scheduling exiting task', task.name)
            self.registered_tasks.append(task)
            self.job_card.promise(task.promise)
        if self.current_state:
            self.past_states.append(self.current_state)
        self.current_state = state
