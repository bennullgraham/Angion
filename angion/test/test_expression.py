import unittest
from sys import float_info
from angion.config import cfg
from angion.expression import Expression


class TestExpression(unittest.TestCase):
    def setUp(self):
        self.expression = Expression()

    def test_InitialisesWithOneTerm(self):
        terms = self.expression.terms
        self.assertEqual(len(terms), 1)

    def test_MutationCanCreateTerm(self):
        cfg.set('Function', 'term_creation_chance', '1.0')
        cfg.set('Function', 'term_deletion_chance', '0.0')
        pre_count = len(self.expression.terms)
        self.expression.mutate()
        post_count = len(self.expression.terms)
        self.assertEqual(pre_count, post_count - 1)

    def test_MutationCanDeleteTerm(self):
        cfg.set('Function', 'term_creation_chance', '0.0')
        cfg.set('Function', 'term_deletion_chance', '1.0')
        self.expression._add_term()
        pre_count = len(self.expression.terms)
        self.expression.mutate()
        post_count = len(self.expression.terms)
        self.assertEqual(pre_count, post_count + 1)

    def test_ExpressionSummation(self):
        class DoublingTerm(object):
            def f(self, x):
                return 2 * x

        terms = 3
        x = 1
        self.expression.terms = [DoublingTerm() for n in range(3)]
        expected = terms * x * 2
        self.assertEqual(expected, self.expression.f(x))

    def test_ExpressionInfinityBounds(self):
        class PositiveInfinityTerm(object):
            def f(self, x):
                return float('inf')

        class NegativeInfinityTerm(object):
            def f(self, x):
                return -float('inf')

        x = 1
        self.expression.terms = [PositiveInfinityTerm()]
        expected = float_info.max
        self.assertEqual(expected, self.expression.f(x))

        self.expression.terms = [NegativeInfinityTerm()]
        expected = -float_info.max
        self.assertEqual(expected, self.expression.f(x))
