Angion
===================
![Example output](https://github.com/bennullgraham/Angion/raw/master/readme/fractal.png)

Running
-------------------
Try `python fractal.py`

Stopping
-------------------
The multithreaded processing employed makes execution invulnerable to ^C, for reasons I haven't looked into. Try:

    ps ax | grep fractal.py | grep -v grep | awk '{print $1}' | while read PROC; do kill $PROC; done

Output
--------------------
In general, output only occurs when a generation improves on the current best.

 - A series of out.*n*.png files will be created in the working directory.
 - A description of the functions defining the current best solution is printed to stdout
 - Every 1000 generations, the generation number is also printed, regardless of improvement