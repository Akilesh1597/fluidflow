#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import asyncio

from coalesce.containers.future import FutureData
LOG = logging.getLogger(__name__)


class Task:
    profile = {}
    promise = {}

    def __init__(self, tracker, task_id, job_card, loop):
        self.loop = loop
        self.tracker = tracker
        self.job_card = job_card
        self.task_id = task_id
        self.name = '{}:{}'.format(__class__.__name__, self.task_id)
        self.promise_futures()
        self.update_status('scheduled')

    async def execute(self):
        pass

    async def revert(self):
        pass

    async def retry(self):
        pass

    def promise_futures(self):
        self.job_card.promise(self.promise, self)

    def update_status(self, state, ref=None, source=None,
                      data=None, attempt=None):
        self.tracker.update_status(state, ref=ref, source=source,
                                   data=data, attempt=attempt)

    def update_result(self, step, status, percentage, message):
        self.tracker.update_result(step, status, percentage, message)

    async def start(self):
        if not await self._run_execute():
            if not await self._run_retry():
                await self._run_revert()

    async def _run_execute(self):
        execute_args = await self.prepare('execute')
        LOG.debug('executing %s with args %s', self.name, str(execute_args))
        self.update_status('execute')
        try:
            message = await self.execute(*execute_args)
        except Exception as e:
            LOG.exception('execution failed: %s', self.name)
            self.update_result('execute', False, 100, str(e))
        else:
            LOG.info('execute successful: %s', self.name)
            self.update_result('execute', True, 100, message)
            return True

    async def _run_retry(self):
        async for attempt, retry_args in self.prepare_retry():
            LOG.debug('retrying %s with args %s', self.name, str(retry_args))
            self.update_status('retry', attempt=attempt)
            try:
                message = await self.retry(*retry_args)
            except Exception as e:
                LOG.exception('retry %s failed: %s', attempt, self.name)
                self.update_result('retry', False, 100, str(e))
            else:
                LOG.info('retry %s successful: %s', attempt, self.name)
                self.update_result('retry', True, 100, message)
                return True

    async def _run_revert(self):
        revert_args = await self.prepare('revert')
        LOG.debug('reverting %s with args %s', self.name, str(revert_args))
        self.update_status('revert')
        try:
            message = await self.revert(*revert_args)
        except Exception as e:
            LOG.exception('revert failed: %s', self.name)
            self.update_result('revert', False, 100, str(e))
        else:
            LOG.info('revert successful: %s', self.name)
            self.update_result('revert', True, 100, message)

    async def prepare(self, stage):
        self.update_status('prepare_{}'.format(stage))
        arg_refs = self._flatten_args(self.profile.get(stage, ()))
        return await self.extract_args(arg_refs)

    async def prepare_retry(self):
        attempt = 1
        for arg_refs in self._flatten_args(self.profile.get('retry', ())):
            self.update_status('prepare_retry{}'.format(attempt))
            yield attempt, await self.extract_args(arg_refs)
            attempt += 1

    async def extract_args(self, arg_refs):
        arg_futures = asyncio.gather(
            loop=self.loop, *tuple(self.fetch(arg_ref) for
                                   arg_ref in arg_refs))
        await arg_futures
        return arg_futures.result()

    async def fetch(self, arg_ref):
        data = self.job_card.find(*arg_ref)
        if isinstance(data, FutureData):
            self.update_status('awaiting', ref=arg_ref, source=data.source)
            arg = await data.fetch()
            self.update_status('received', ref=arg_ref, source=data.source,
                               data=arg)
            return arg
        return data

    def _flatten_args(self, args_list):
        result_arg_list = []
        skip = False
        for index, item in enumerate(args_list):
            if skip:
                skip = False
                continue
            try:
                next_arg = args_list[index+1]
            except:
                next_arg = None
            if next_arg and isinstance(next_arg, (tuple, list)):
                skip = True
                for nested_arg in self._flatten_args(next_arg):
                    result_arg_list.append((item,) + nested_arg)
            else:
                result_arg_list.append((item,))
        return tuple(result_arg_list)
