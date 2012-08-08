from Queue import PriorityQueue, Empty
from heapq import heappush, heappop
from multiprocessing import Queue, Process, cpu_count
from fractal import Fractal
from solver import Solver
from mutator import Mutator
import time
import os


solveable = Queue()
mutateable = []
solver_processes = []


def worker_solve(solveable, mutateable):
    s = Solver()
    while True:
        try:
            f = solveable.get(block=False)
            s.solve(f)
            heappush(mutateable, (f.fitness, f))
        except Empty:
            time.sleep(0.1)


def worker_mutate(solveable, mutateable):
    m = Mutator()
    # while True:
    time.sleep(1)
    if len(mutateable) >= 4:
        fractals = [heappop(mutateable) for i in range(4)]
        m.mutate(fractals)

        for f in fractals:
            solveable.put(f)
    else:
        time.sleep(10)


def begin():
    # ensure solveable queue never empties
    for i in range(1):
        def feeder(solveable):
            while True:
                if solveable.qsize() < 10:
                    solveable.put(Fractal())
        p = Process(target=feeder, args=(solveable,))
        p.start()

    # solver processes
    for i in range(cpu_count()):
        p = Process(target=worker_solve, args=(solveable, mutateable))
        p.daemon = True
        p.start()
        solver_processes.append(p)
    print "Running {n} solver processes".format(n=len(solver_processes))

    # mutator processes
    # for i in range(1):
    #     p = Process(target=worker_mutate, args=(solveable, mutateable))
    #     p.daemon = True
    #     p.start()


begin()
while True:
    try:
        worker_mutate
        os.system('clear')
        os.system('date')
        print """
                                                  
                             `.                   
   `..    `.. `..     `..         `..    `.. `..  
 `..  `..  `..  `.. `..  `..`.. `..  `..  `..  `..
`..   `..  `..  `..`..   `..`..`..    `.. `..  `..
`..   `..  `..  `.. `..  `..`.. `..  `..  `..  `..
  `.. `...`...  `..     `.. `..   `..    `...  `..
                     `..                          
"""
        print "Solve queue length:  " + str(solveable.qsize())
        print "Mutate queue length: " + str(len(mutateable))
        time.sleep(1)
    except KeyboardInterrupt:
        os.system('clear')
        print "Terminated"
        break
    
# while True:
#     f = fractal.Fractal()
#     solveable.put(f)
#     solveable.put(f)
#     solveable.put(f)
#     # print "added:  " + f.__unicode__()
#     # print "apprx queue length: " + str(solveable.qsize())
#     time.sleep(0.2)
#     f = solveable.get()
#     print f.__unicode__()
#     break



# solveable = Queue()
# mutateable = PriorityQueue()

# for i in range(20):
#     f = fractal.create()
#     print f.__unicode__()
#     solveable.put(f)


# def solved(fractal):
#     mutateable.put(fractal)


# def mutated((fractals)):
#     for f in fractals:
#         solveable.put(f)


# def __solving_worker():
#     while True:
#         fractal = solveable.get(block=True)
#         solver.solve(fractal)
#         solved(fractal)
#         solveable.task_done()


# def __mutating_worker():
#     while True:
#         fractals = [mutateable.get(block=True) for i in range(4)]
#         mutator.mutate(fractals)
#         mutated(fractals)
#         for i in range(len(fractals)):
#             mutateable.task_done()

# print "{jobs} solve jobs".format(jobs=solveable.qsize())

# for i in range(cfg.getint('Solver', 'workers')):
#     print "Beginning solver %i" % i
#     worker = Process(target=__solving_worker)
#     # worker.setDaemon(True)
#     worker.start()

# for i in range(cfg.getint('Mutator', 'workers')):
#     print "Beginning mutator %i" % i
#     worker = Thread(target=__mutating_worker)
#     worker.setDaemon(True)
#     worker.start()


# time.sleep(10)
