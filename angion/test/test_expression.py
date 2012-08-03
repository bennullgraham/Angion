import unittest
from angion.expression import Expression


class TestExpression(unittest.TestCase):
    def setUp(self):
        self.expression = Expression()

    def test_InitialisesWithOneTerm(self):
        terms = self.expression.terms
        self.assertEqual(len(terms), 1)

if __name__ == '__main__':
    unittest.main()
