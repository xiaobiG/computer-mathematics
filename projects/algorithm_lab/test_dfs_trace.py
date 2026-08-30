import unittest

from dataclasses import replace

from projects.algorithm_lab.dfs_trace import (
    dfs_trace,
    dfs_trace_certificate,
    directed_cycle_certificate,
    directed_cycle_report,
)


class DfsTraceTests(unittest.TestCase):
    def test_discovery_precedes_finish_and_times_are_unique(self):
        times, events = dfs_trace({"a": ["b", "c"], "b": ["d"], "c": [], "d": []}, "a")
        self.assertEqual(set(times), {"a", "b", "c", "d"})
        self.assertTrue(all(discovered < finished for discovered, finished in times.values()))
        self.assertEqual(len({event.time for event in events}), 2 * len(times))
        self.assertTrue(dfs_trace_certificate({"a": ["b", "c"], "b": ["d"], "c": [], "d": []}, "a", times, events))

    def test_trace_certificate_rejects_tampered_time_or_stack_snapshot(self):
        graph = {"a": ["b"], "b": []}
        times, events = dfs_trace(graph, "a")
        altered_times = dict(times)
        altered_times["b"] = (2, 99)
        self.assertFalse(dfs_trace_certificate(graph, "a", altered_times, events))
        tampered = list(events)
        tampered[0] = replace(tampered[0], stack_after_event=())
        self.assertFalse(dfs_trace_certificate(graph, "a", times, tampered))

    def test_cycle_does_not_repeat_vertex(self):
        times, events = dfs_trace({"a": ["b"], "b": ["c"], "c": ["a"]}, "a")
        self.assertEqual(len(times), 3)
        self.assertEqual(sum(event.phase == "discover" for event in events), 3)

    def test_rejects_missing_start_and_implicit_neighbor(self):
        with self.assertRaises(ValueError):
            dfs_trace({"a": []}, "missing")
        with self.assertRaises(ValueError):
            dfs_trace({"a": ["missing"]}, "a")

    def test_directed_cycle_report_returns_a_closed_gray_back_edge_witness(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a", "d"], "d": []}
        report = directed_cycle_report(graph, "a")
        self.assertTrue(report["has_cycle"])
        self.assertEqual(report["back_edge"], ("c", "a"))
        self.assertEqual(report["cycle"], ("a", "b", "c", "a"))
        self.assertTrue(directed_cycle_certificate(graph, "a", report))
        tampered = dict(report)
        tampered["cycle"] = ("a", "c", "a")
        self.assertFalse(directed_cycle_certificate(graph, "a", tampered))

    def test_directed_cycle_report_distinguishes_a_dag_from_a_cycle(self):
        graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
        report = directed_cycle_report(graph, "a")
        self.assertEqual(report["reachable"], ("a", "b", "d", "c"))
        self.assertFalse(report["has_cycle"])
        self.assertIsNone(report["back_edge"])
        self.assertIsNone(report["cycle"])


if __name__ == "__main__":
    unittest.main()
