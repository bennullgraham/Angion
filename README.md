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
In general, output only occurs when a generation improves on the current best.

 - A series of out.*n*.png files will be created in the output directory. These are raster renderings of the fractals.
 - A series of out.*n*.json files will be created in the output directory. These are hierarchical JSON trees representing each point in the fractal.
 - A description of the functions defining the current best solution is printed to stdout
 - Every 1000 generations, the generation number is also printed, regardless of improvement

Output from previous runs currently isn't cleaned up, so you may want to invoke the program like: `rm output/out*{png,json} && python Angion.py`
