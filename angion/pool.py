from Queue import PriorityQueue, Empty
# from heapq import heappush, heappop
from multiprocessing import Queue, Process, cpu_count
from threading import Thread, Lock
from fractal import Fractal
from solver import Solver
from mutator import Mutator
import time
import os

log = Queue()
solveable = Queue()
mutateable = Queue()
stat = Queue()
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


def worker_mutate(i, solveable, mutateable, stat):
    m = Mutator()
    while True:
        fractals = []
        for n in range(8):
            fractals.append(mutateable.get(block=True))
        fractals = m.mutate(fractals)
        stat.put("%s %f" % (i, fractals[0].fitness * 1000000))
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
        p = Process(target=worker_solve, args=(solveable, mutateable, log))
        p.daemon = True
        p.start()
        solver_processes.append(p)
    log.put("Running %s solver processes" % len(solver_processes))

    # mutator threads
    for i in range(2):
        p = Process(target=worker_mutate, args=(i, solveable, mutateable, stat))
        p.daemon = True
        p.start()

    # stat logger process
    for i in range(1):
        print 'grange'

        def statwrite(stat):
            with open('stat', 'w') as f:
                while True:
                    stats = ()
                    try:
                        while True:
                            stats += (stat.get(block=False), )
                    except Empty:
                        pass
                    for s in stats:
                        f.write(str(s) + '\n')
                    f.flush()
        p = Process(target=statwrite, args=(stat,))
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
        p = Process(target=output, args=(log,))
        p.daemon = True
        p.start()
