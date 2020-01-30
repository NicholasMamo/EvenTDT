#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
from __future__ import (absolute_import, division, print_function)
#                        unicode_literals)

import threading
import time


def func1(flag):
    time.sleep(5)
    flag.append(None)
    print('Func1: Out of sleep and returning')


def func2(flag):
    while not flag:
        time.sleep(1)
        print('Func2: looping')

    print('Func2: Flag set, leaving')


f = list()
t1 = threading.Thread(target=func1, kwargs=dict(flag=f))

# t2 = threading.Thread(target=func2, kwargs=dict(flag=f))

t1.start()
# t2.start()
func2(f)

t1.join()
f.append(None)
