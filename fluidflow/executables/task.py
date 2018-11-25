#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import asyncio

LOG = logging.getLogger(__name__)


class Task:
    profile = {}
    promise = {}

    def __init__(self, tracker, task_id, loop):
        self.loop = loop
        self.tracker = tracker
        self.task_id = task_id
        self.state = None
        self.name = '{}:{}'.format(__class__.__name__, self.task_id)
        self.update_status('scheduled')

    async def execute(self):
        pass

    async def revert(self):
        pass

    async def retry(self):
        pass

    def update_status(self, state=None, result=None, ref=None, source=None,
                      data=None, attempt=None, percentage=None, message=None):
        self.state = state or self.state
        self.tracker.update_status(self, state, result=result, ref=ref,
                                   source=source, data=data, attempt=attempt,
                                   percentage=percentage, message=message)

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
            LOG.exception('%s: execution failed', self.name)
            self.update_status('execute', result=False, percentage=100,
                               message=str(e))
        else:
            LOG.info('%s: execute successful', self.name)
            self.update_status('execute', result=True, percentage=100,
                               message=message)
            return True

    async def _run_retry(self):
        async for attempt, retry_args in self.prepare_retry():
            LOG.debug('retrying %s with args %s', self.name, str(retry_args))
            self.update_status('retry', attempt=attempt)
            try:
                message = await self.retry(*retry_args)
            except Exception as e:
                LOG.exception('retry %s failed: %s', attempt, self.name)
                self.update_status('retry', result=False, percentage=100,
                                   message=str(e))
            else:
                LOG.info('retry %s successful: %s', attempt, self.name)
                self.update_status('retry', result=True, percentage=100,
                                   message=message)
                return True

    async def _run_revert(self):
        revert_args = await self.prepare('revert')
        LOG.debug('reverting %s with args %s', self.name, str(revert_args))
        self.update_status('revert')
        try:
            message = await self.revert(*revert_args)
        except Exception as e:
            LOG.exception('revert failed: %s', self.name)
            self.update_status('revert', result=False, percentage=100,
                               message=str(e))
        else:
            LOG.info('revert successful: %s', self.name)
            self.update_status('revert',  result=True, percentage=100,
                               message=message)

    async def prepare(self, stage):
        arg_refs = self._flatten_args(self.profile.get(stage, ()))
        return await self.extract_args(arg_refs)

    async def prepare_retry(self):
        attempt = 1
        for arg_refs in self._flatten_args(self.profile.get('retry', ())):
            yield attempt, await self.extract_args(arg_refs)
            attempt += 1

    async def extract_args(self, arg_refs):
        arg_futures = asyncio.gather(
            *tuple(self.fetch(arg_ref) for arg_ref in arg_refs),
            loop=self.loop)
        await arg_futures
        return arg_futures.result()

    async def fetch(self, arg_ref):
        self.tracker.fetch(self, arg_ref)

    def _flatten_args(self, args_list):
        result_arg_list = []
        skip = False
        for index, item in enumerate(args_list):
            if skip:
                skip = False
                continue
            try:
                next_arg = args_list[index+1]
            except IndexError:
                next_arg = None
            if next_arg and isinstance(next_arg, (tuple, list)):
                skip = True
                for nested_arg in self._flatten_args(next_arg):
                    result_arg_list.append((item,) + nested_arg)
            else:
                result_arg_list.append((item,))
        return tuple(result_arg_list)
