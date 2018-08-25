# -*- coding: utf-8 -*-

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/coalesce/'))


from tests.containers_tests import future_test
#from tests.executables_tests import task_test


future_test.run_test()
#task_test.run_test()
