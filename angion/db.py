from pymongo import Connection
import fractal

connection = Connection()
fractals = connection.angion.fractals


def inter(f):
    f = fractal.to_dict(f)
    return fractals.insert(f)


def unearth(id):
    f = fractals.find_one({"_id": id})
    return fractal.from_dict(f)
