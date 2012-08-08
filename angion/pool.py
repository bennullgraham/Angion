from Queue import PriorityQueue, Empty
# from heapq import heappush, heappop
from multiprocessing import Queue, Process, cpu_count
from threading import Thread, Lock
from fractal import Fractal
from solver import Solver
from mutator import Mutator
import time
import os

l = Queue()
solveable = Queue()
mutateable = Queue()
solver_processes = []

lock = Lock()


def worker_solve(solveable, mutateable, log):
    s = Solver()
    while True:
        try:
            f = solveable.get(block=False)
            s.solve(f)
            log.put("Solver: solved   %s" % f.__unicode__())
            mutateable.put(f)
        except Empty:
            time.sleep(0.1)


def worker_mutate(solveable, mutateable, log):
    m = Mutator()
    while True:
        fractals = []
        for n in range(8):
            fractals.append(mutateable.get(block=True))
        fractals = m.mutate(fractals)
        log.put("Mutator best: %s" % fractals[0].fitness)
        for f in fractals:
            solveable.put(f)
        # log.put("Mutator: mutated %s fractals" % len(fractals))


def begin(*args):
    # ensure solveable queue never empties
    for i in range(1):
        def feeder(solveable):
            while True:
                if solveable.qsize() < 10:
                    solveable.put(Fractal())
                time.sleep(0.1)
        p = Process(target=feeder, args=(solveable,))
        p.start()

    # solver processes
    for i in range(cpu_count()):
        p = Process(target=worker_solve, args=(solveable, mutateable, l))
        p.daemon = True
        p.start()
        solver_processes.append(p)
    l.put("Running %s solver processes" % len(solver_processes))

    # mutator threads
    for i in range(2):
        p = Process(target=worker_mutate, args=(solveable, mutateable, l))
        p.daemon = True
        p.start()

    # output process
    for i in range(1):
        def output(log):
            while True:
                os.system('clear')
                os.system('date')
                print "\033[34m"
                print """
         _                   _             _               _          _            _
        / /\                /\ \     _    /\ \            /\ \       /\ \         /\ \     _
       / /  \              /  \ \   /\_\ /  \ \           \ \ \     /  \ \       /  \ \   /\_\\
      / / /\ \            / /\ \ \_/ / // /\ \_\          /\ \_\   / /\ \ \     / /\ \ \_/ / /
     / / /\ \ \          / / /\ \___/ // / /\/_/         / /\/_/  / / /\ \ \   / / /\ \___/ /
    / / /  \ \ \        / / /  \/____// / / ______      / / /    / / /  \ \_\ / / /  \/____/
   / / /___/ /\ \      / / /    / / // / / /\_____\    / / /    / / /   / / // / /    / / /
  / / /_____/ /\ \    / / /    / / // / /  \/____ /   / / /    / / /   / / // / /    / / /
 / /_________/\ \ \  / / /    / / // / /_____/ / /___/ / /__  / / /___/ / // / /    / / /
/ / /_       __\ \_\/ / /    / / // / /______\/ //\__\/_/___\/ / /____\/ // / /    / / /
\_\___\     /____/_/\/_/     \/_/ \/___________/ \/_________/\/_________/ \/_/     \/_/
                                                                                              
"""
                print "\033[0m"
                print "Solve queue length:  %s" % str(solveable.qsize())
                print "Mutate queue length: %s" % str(mutateable.qsize())
                print "------------------------------------------------------------------"
                logs = ()
                try:
                    while True:
                        logs += (log.get(block=False), )
                except Empty:
                    pass
                more = len(logs) - 20
                for line in logs[:20]:
                    print line
                if more > 0:
                    print "\n(%s more lines)\n" % more
                print "------------------------------------------------------------------"
                time.sleep(0.5)
        p = Process(target=output, args=(l,))
        p.daemon = True
        p.start()
