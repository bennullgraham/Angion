import unittest
from angion.db import inter, unearth
from angion.fractal import Fractal


class TestDb(unittest.TestCase):
    def test_Store(self):
        f = Fractal()
        f.fitness = 1234
        f.length_function.terms[0].innerMultiplier = 3.45

        _id = inter(f)
        f_retr = unearth(_id)
        print f.length_function.terms
        print f_retr.length_function.terms
        f_retr.length_function.terms.sort(key=lambda t: t.innerMultiplier != 3.45)
        self.assertEqual(f.fitness, f_retr.fitness)
        self.assertEqual(
            f.length_function.terms[0].innerMultiplier,
            f_retr.length_function.terms[0].innerMultiplier
        )
