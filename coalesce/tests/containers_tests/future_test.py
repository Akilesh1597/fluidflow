#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 21:07:58 2018

@author: akandavelu
"""
import asyncio

from containers.future import FutureMap


loop = asyncio.get_event_loop()
common_map = FutureMap(loop)
promises = {'network': {'id': None, 'name': None, 'vms': []}}
print('producer promising {}'.format(str(promises)))
common_map.promise(promises)
print('common map contents {}'.format(str(common_map)))


async def producer():
    await asyncio.sleep(1)
    print('producer filling id')
    common_map.fulfil({'network': {'id': 10}})
    await asyncio.sleep(3)
    print('producer filling name')
    common_map.fulfil({'network': {'name': 'test network'}})


async def consumer1():
    print('consumer1 got network id {}'.format(
        await common_map.fetch('network', 'id')))


async def consumer2():
    print('consumer2 got network name {}'.format(
        await common_map.fetch('network', 'name')))


def run_test():
    res = asyncio.gather(producer(), consumer1(), consumer2())
    loop.run_until_complete(res)
    print('final data {}'.format(common_map))


if __name__ == '__main__':
    run_test()
