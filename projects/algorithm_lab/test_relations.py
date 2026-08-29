import unittest

from projects.algorithm_lab.relations import equivalence_classes, relation_report


class RelationTests(unittest.TestCase):
    def test_parity_relation_is_an_equivalence_and_partitions_the_set(self):
        items = {1, 2, 3, 4, 5, 6}
        parity = {(left, right) for left in items for right in items if left % 2 == right % 2}
        report = relation_report(items, parity)
        self.assertTrue(report["equivalence"])
        self.assertFalse(report["partial_order"])
        self.assertEqual({frozenset(group) for group in equivalence_classes(items, parity)},
                         {frozenset({1, 3, 5}), frozenset({2, 4, 6})})

    def test_less_equal_is_a_partial_order_not_an_equivalence(self):
        items = {1, 2, 3}
        less_equal = {(left, right) for left in items for right in items if left <= right}
        report = relation_report(items, less_equal)
        self.assertTrue(report["partial_order"])
        self.assertFalse(report["symmetric"])
        self.assertFalse(report["equivalence"])

    def test_rejects_outside_items_and_non_equivalence_partitioning(self):
        with self.assertRaises(ValueError):
            relation_report({1}, {(1, 2)})
        with self.assertRaises(ValueError):
            equivalence_classes({1, 2}, {(1, 1), (2, 2), (1, 2)})


if __name__ == "__main__":
    unittest.main()
