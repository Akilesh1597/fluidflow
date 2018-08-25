#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 22:08:52 2018

@author: akandavelu
"""
from asyncio import Lock


class FutureData:
    def __init__(self, container, name, source=None):
        self.lock = Lock()
        self.container = container
        self.name = name
        self.source = source
        self.future = container.loop.create_future()

    async def fetch(self):
        async with self.lock:
            await self.future
            return self.container[self.name]

    def set_result(self, result):
        self.container[self.name] = result
        self.future.set_result(1)


class FutureContainer(object):
    def __init__(self, loop):
        super(FutureContainer, self).__init__()
        self.loop = loop

    def new_future(self, name, source=None):
        return FutureData(self, name, source)

    def fulfil(self, items):
        for item_name, item_value in self.iter_items(items):
            f_item = self[item_name]
            if f_item is None:
                self[item_name] = item_value
            elif isinstance(f_item, FutureData):
                f_item.set_result(item_value)
            elif isinstance(f_item, FutureContainer):
                f_item.fulfil(item_value)

    def promise(self, items, source=None):
        for item_name, item_value in self.iter_items(items):
            if item_value is None:
                self[item_name] = self.new_future(item_name, source)
            elif isinstance(item_value, list):
                self[item_name] = FutureList(self.loop)
                self[item_name].promise(item_value, source)
            elif isinstance(item_value, dict):
                self[item_name] = FutureMap(self.loop)
                self[item_name].promise(item_value, source)

    async def fetch(self, *item_path):
        item = await self.find(*item_path)
        if isinstance(item, FutureData):
            item = await item.fetch()
        return item

    async def find(self, *item_path):
        item_name = item_path[0]
        next_path = item_path[1:]
        item = self[item_name]
        if next_path:
            if isinstance(item, FutureContainer):
                return await item.find(*next_path)
            else:
                raise KeyError(str(next_path))
        return item


class FutureList(FutureContainer, list):
    def __init__(self, loop):
        FutureContainer.__init__(self, loop)
        list.__init__(self)

    def iter_items(self, items):
        yield from enumerate(items)


class FutureMap(FutureContainer, dict):
    def __init__(self, loop):
        FutureContainer.__init__(self, loop)
        dict.__init__(self)

    def iter_items(self, items):
        yield from items.items()
