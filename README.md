Angion
===================
![Example output](https://github.com/bennullgraham/Angion/raw/master/docs/img/fractal.png)

Running
-------------------
`python Angion.py`

Config
-------------------
Create `settings.cfg` in the Angion root directory. See angion/default.cfg for possible options.

Output
--------------------
Every second, Angion displays a list of fractals that have been solved. Angion also writes out some basic statistics to `./stat`. These can be graphed like:

    grep '^0' stat | awk '{print $2}' | gnuplot -persist <(echo "plot '<(cat -)' with lines")

The integer part of the argument to `grep` singles out an individual mutator thread.