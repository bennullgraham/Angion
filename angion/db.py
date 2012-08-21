from pymongo import Connection
from angion.fractal import Fractal

connection = Connection()
fractals = connection.angion.fractals


def inter(fractal):
    fractals.insert(fractal.as_dict())


def unearth(id):
    return fractals.find_one({"_id": id})
