import time
# import terminal
import pool

try:
    #terminal.wrapper(pool.begin)
    pool.begin()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print "Terminated"
