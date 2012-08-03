import sqlite3 as db
import cPickle as pickle
from angion.fractal import Fractal

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


def inter(fractal):
    with c:
        cur = c.cursor()
        query = """INSERT INTO fractals
            (length_function, radiance_function, orientation_function, termination_function, inverse_fitness)
            VALUES
            (:length_function, :radiance_function, :orientation_function, :termination_function, :inverse_fitness);"""

        cur.execute(query, {
            'length_function': pickle.dumps(fractal.length_function),
            'radiance_function': pickle.dumps(fractal.radiance_function),
            'orientation_function': pickle.dumps(fractal.orientation_function),
            'termination_function': pickle.dumps(fractal.termination_function),
            'inverse_fitness': (1 / (fractal.fitness + 1))
        })

        c.commit()

        cur.execute("SELECT COUNT(id) FROM fractals")
        c.commit()


def unearth(id):
    f = Fractal()
    with c:
        cur = c.cursor()
        cur.execute("SELECT * FROM fractals WHERE id=:id", {'id': id})
        c.commit()
        row = cur.fetchone()
        f.length_function = pickle.loads(row[1].encode('utf-8'))
        f.radiance_function = pickle.loads(row[2].encode('utf-8'))
        f.orientation_function = pickle.loads(row[3].encode('utf-8'))
        f.termination_function = pickle.loads(row[4].encode('utf-8'))
        f.inverse_fitness = (1 / row[5]) - 1

        return f
