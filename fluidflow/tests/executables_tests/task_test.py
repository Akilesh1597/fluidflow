#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 22:07:55 2018

@author: akandavelu
"""
from fluidflow.executables.task import Task


class PrintNetworkName(Task):
    profile = {'execute': ('network', ('id', 'name')),
               'revert': {},
               'retry': {}}

    def execute(self, network_id, network_name):
        print('running task on id: {}, name: {}'.format(network_id, network_name))





def run_test():
    pass