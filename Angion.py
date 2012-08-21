if __name__ == '__main__':
    from angion import pool
    import time

    try:
        #terminal.wrapper(pool.begin)
        pool.begin()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Terminated"
