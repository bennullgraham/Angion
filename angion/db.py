import sqlite3 as db
import cPickle as pickle
from config import cfg

c = db.connect("angion.db")

def create():
    with c:
        cur = c.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS fractals(
            id INTEGER PRIMARY KEY, 
            length_function TEXT,
            radiance_function TEXT,
            orientation_function TEXT,
            termination_function TEXT,
            inverse_fitness INTEGER,
            created INTEGER,
            modified INTEGER
        );""")

        cur.execute("""CREATE TRIGGER IF NOT EXISTS insert_fractal_created AFTER INSERT ON fractals
            BEGIN
                UPDATE fractals SET created = DATETIME('NOW'), modified = DATETIME('NOW')
                WHERE id = new.id;
            END;""")

        cur.execute("""CREATE TRIGGER IF NOT EXISTS insert_fractal_modified AFTER UPDATE ON fractals
            BEGIN
                UPDATE fractals SET modified = DATETIME('NOW')
                WHERE id = old.id;
            END;""")

        c.commit()

def store(fractal):
    # functions = {
    #     'length': fractal.length_function,
    #     'radiance': fractal.radiance_function,
    #     'orientation': fractal.orientation_function,
    #     'termination': fractal.termination_function
    # }

    # # turn four functions times their two inner/outer multipliers 
    # # into an 8x dict for db storage
    # field_map = dict([(f + '_' + position, getattr(functions[f], position+'Multiplier')) for f in functions.keys() for position in ('inner', 'outer')])
    # with c:
    #     cur = c.cursor()
    #     c.execute("INSERT INTO fractals " +
    #         "(" + field_map.keys().join(', ') + ", inverse_fitness)" +
    #         " VALUES (" + 
    #             [':'+k for k in field_map.keys()].join(', ')+", :inverse_fitness);",
    #         field_map)

    #with c:
        cur = c.cursor()
        query = """INSERT INTO fractals
            (length_function, radiance_function, orientation_function, termination_function, inverse_fitness)
            VALUES
            (:length_function, :radiance_function, :orientation_function, :termination_function, :inverse_fitness);"""

        c.execute(query, {
            'length_function': pickle.dumps(fractal.length_function),
            'radiance_function': pickle.dumps(fractal.radiance_function),
            'orientation_function': pickle.dumps(fractal.orientation_function),
            'termination_function': pickle.dumps(fractal.termination_function),
            'inverse_fitness': (1 / (fractal.fitness + 1))
        })

        c.commit()

        cur.execute("SELECT COUNT(id) FROM fractals")
        c.commit()
        row = cur.fetchone()
        print row

