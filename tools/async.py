#!/usr/bin/env python3

"""
This script contains a proof-of-concept of how streams (and their consumers) could be added and removed dynamically.
It has three main components:

- The code outside of the classes represents the tool, like the :mod:`tools.consume` tool.
  It has two purposes: it instantiates everything, and it assigns tasks to the :class:`TaskManager`.
  In reality, the code will be slightly more complex since, like the :mod:`tools.consume` tool, the outer code will be split into two processes: `stream_process` and a `consume_process`.

- The :class:`TaskManager` represents a `SplitConsumer`.
  While running, it continuously monitors its assigned tasks.
  If it has a task it has not seen before, it sets it running.
  If any ongoing task is no longer assigned to it, the class instructs the task to stop and stores its output.
  Once it has no more tasks to perform, the :class:`TaskManager` returns each task's output.

- The :class:`Task` represents a `Consumer`.
  The :class:`Task` performs its job until the :class:`TaskManager` instructs it to stop, at which point it returns an output.

The following communication takes place:

- Between the outer code and the :class:`TaskManager`.
  The two share a list of tasks for the input (from the outer code to the :class:`TaskManager`) and a dictionary for the input (from the :class:`TaskManager` to the outer code).
  The latter already exists in the :mod:`consume` tool, while the former would have to be added separately.
  The final version would also have to add a queue of tweets to the communication.
- Between the :class:`TaskManager` and the :class:`Task`.
  The :class:`TaskManager` instructs the :class:`Task` to stop, and when it does, the :class:`TaskManager` gathers its output.
"""

import asyncio
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import signal
import time

loop = asyncio.get_event_loop()

class TaskManager():

    def __init__(self):
        """
        Initialize the tasks application.
        """

        self.running = False

    def run(self, tasks, outputs):
        """
        Run the tasks from the given shared list.

        :param tasks: A list of tasks shared by all processes.
        :type tasks: :class:`multiprocessing.managers.ListProxy`
        :param outputs: A list of outputs shared by all processes.
        :type outputs: :class:`multiprocessing.managers.DictProxy`
        """

        async def run_tasks():
            ongoing = { } # the ongoing tasks, storing the tuples of the asyncio tasks and the :class:`Task` class.
            while tasks:
                # start the new tasks
                for task in tasks:
                    if task.ID not in ongoing and task.ID not in outputs:
                        _task = asyncio.ensure_future(task.run())
                        ongoing[task.ID] = (_task, task)

                # gather the results from the stopped tasks
                for task_id, (asyncio_task, task) in ongoing.items():
                    if task_id not in outputs and not any( task_id == _task.ID for _task in tasks ):
                        task.stop()
                        outputs[task_id] = (await asyncio.gather(asyncio_task))[0]
                        print(f"Task { task_id } has stopped with counter { outputs[task_id] }")

                await asyncio.sleep(0.1)

            # gather the results from any remaining tasks
            for task_id, (asyncio_task, task) in ongoing.items():
                if task_id not in outputs and not any( task_id == _task.ID for _task in tasks ):
                    task.stop()
                    outputs[task_id] = (await asyncio.gather(asyncio_task))[0]
                    print(f"Task { task_id } has stopped with counter { outputs[task_id] }")

        def sigint_handler(signal, frame):
            """
            Stop all remaining tasks when the user presses CTRL+C.
            Clearing the remaining tasks also means that the `run_tasks` function will stop processing any tasks.
            For a demo, try pressing CTRL+C before the third task starts.
            """
            while len(tasks):
                tasks.pop()

        signal.signal(signal.SIGINT, sigint_handler)

        self.running = True
        loop.run_until_complete(run_tasks())

    def stop(self):
        """
        Instruct the task manager to stop running.
        """

        self.running = False

class Task():

    def __init__(self, ID):
        """
        Create a task.

        :param ID: The task ID.
                   Tasks need a unique ID because when they are loaded from the shared list into memory, their ID changes.
        :type ID: int
        """

        self.ID = ID
        self.running = False

    async def run(self):
        """
        Set the task running.

        :return: The ID of times the function printed something.
        :rtype: int
        """

        print(f"Task { self.ID } starting")
        self.running = True
        counter = 0 # how many full seconds have elapsed
        progress = 0 # how long the task has run for (seconds)

        while self.running:
            progress += 0.1
            if int(round(progress, 2)) > counter:
                print(f"Task { self.ID } running", flush=True)
                counter = int(round(progress, 2))
            await asyncio.sleep(0.1)

        print(f"Task { self.ID } stopping after { round(progress, 2) }s")
        return counter

    def stop(self):
        """
        Instruct the task to stop running.
        """

        self.running = False

# do nothing (here) when the user presses CTRL+C as the task manager will stop on its own
def sigint_handler(signal, frame):
    return
signal.signal(signal.SIGINT, sigint_handler)

# set up the shared inputs and outputs
resource_manager = Manager()
tasks, outputs = resource_manager.list(), resource_manager.dict()

# start the task manager
manager = TaskManager()
task_manager = Process(target=manager.run, args=(tasks, outputs))
task_manager.start()

# start the first task
tasks.append(Task(1))

# start a second task
time.sleep(2)
tasks.append(Task(2))

# stop the first task and start a third
time.sleep(3)
if len(tasks):
    tasks.pop(0)
tasks.append(Task(3))

task_manager.join()
print(outputs)