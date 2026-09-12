import unittest

from projects.algorithm_lab.weighted_activity import (
    ActivitySelectionEvent,
    WeightedActivityEvent,
    activity_selection_certificate,
    activity_selection_trace,
    brute_force_best_value,
    brute_force_max_cardinality,
    compatible_schedule,
    diagnose_activity_task,
    unweighted_compatible_schedule,
    weighted_activity_selection,
    weighted_activity_trace,
    weighted_activity_trace_certificate,
)


class WeightedActivityTests(unittest.TestCase):
    def test_reader_task_contract_selects_greedy_from_a_cardinality_goal(self):
        task = {
            "interval_semantics": "half_open",
            "objective": "maximize_count",
            "acceptance_invariant": "compatible_schedule_and_maximum_cardinality",
            "activities": [
                {"start": 0, "finish": 2, "name": "review"},
                {"start": 2, "finish": 4, "name": "deploy"},
                {"start": 1, "finish": 3, "name": "meeting"},
            ],
        }
        diagnosis = diagnose_activity_task(task)
        self.assertEqual(diagnosis["recommended_method"], "earliest_finish_greedy")
        self.assertEqual(diagnosis["chosen_names"], ["review", "deploy"])
        self.assertEqual(diagnosis["oracle_value"], 2)
        self.assertIsNone(diagnosis["first_broken_greedy_premise"])

    def test_reader_task_contract_switches_to_dp_when_value_is_the_goal(self):
        task = {
            "interval_semantics": "half_open",
            "objective": "maximize_value",
            "acceptance_invariant": "compatible_schedule_and_maximum_total_value",
            "activities": [
                {"start": 0, "finish": 2, "value": 1, "name": "short"},
                {"start": 0, "finish": 4, "value": 100, "name": "valuable"},
                {"start": 4, "finish": 5, "value": 5, "name": "after"},
            ],
        }
        diagnosis = diagnose_activity_task(task)
        self.assertEqual(diagnosis["recommended_method"], "prefix_dag_dynamic_programming")
        self.assertEqual(diagnosis["chosen_names"], ["valuable", "after"])
        self.assertEqual(diagnosis["objective_value"], 105.0)
        self.assertEqual(diagnosis["earliest_finish_value"], 6.0)
        self.assertFalse(diagnosis["earliest_finish_is_optimal_on_this_input"])

    def test_reader_task_rejects_an_ambiguous_or_misaligned_contract(self):
        task = {
            "interval_semantics": "closed",
            "objective": "maximize_count",
            "acceptance_invariant": "compatible_schedule_and_maximum_total_value",
            "activities": [{"start": 0, "finish": 2, "name": "a"}],
        }
        with self.assertRaises(ValueError):
            diagnose_activity_task(task)

        task["interval_semantics"] = "half_open"
        with self.assertRaises(ValueError):
            diagnose_activity_task(task)
    def test_earliest_finish_trace_matches_a_cardinality_oracle(self):
        activities = [(0.0, 3.0, "A"), (1.0, 2.0, "B"), (2.0, 4.0, "C"), (3.0, 5.0, "D")]
        chosen, trace = activity_selection_trace(activities)
        self.assertEqual([activity[2] for activity in chosen], ["B", "C"])
        self.assertTrue(unweighted_compatible_schedule(chosen))
        self.assertEqual(len(chosen), brute_force_max_cardinality(activities))
        self.assertTrue(activity_selection_certificate(activities, chosen, trace))

        tampered = list(trace)
        event = tampered[0]
        tampered[0] = ActivitySelectionEvent(event.activity, not event.selected, event.current_end)
        self.assertFalse(activity_selection_certificate(activities, chosen, tampered))

    def test_dp_beats_the_earliest_finish_counterexample(self):
        activities = [(0.0, 2.0, 1.0, "short"), (0.0, 4.0, 100.0, "valuable")]
        value, chosen = weighted_activity_selection(activities)
        self.assertEqual(value, 100.0)
        self.assertEqual([activity[3] for activity in chosen], ["valuable"])

    def test_reconstruction_is_compatible_and_matches_brute_force_oracle(self):
        activities = [
            (0.0, 3.0, 5.0, "a"), (1.0, 4.0, 6.0, "b"), (3.0, 5.0, 5.0, "c"),
            (0.0, 6.0, 11.0, "d"), (5.0, 7.0, 4.0, "e"),
        ]
        value, chosen = weighted_activity_selection(activities)
        self.assertTrue(compatible_schedule(chosen))
        self.assertEqual(sum(activity[2] for activity in chosen), value)
        self.assertEqual(value, brute_force_best_value(activities))

    def test_trace_certificate_replays_each_prefix_dag_transition(self):
        activities = [
            (0.0, 2.0, 1.0, "short"), (0.0, 4.0, 100.0, "valuable"),
            (4.0, 5.0, 5.0, "after"),
        ]
        value, chosen, trace = weighted_activity_trace(activities)
        self.assertEqual(value, 105.0)
        self.assertTrue(weighted_activity_trace_certificate(activities, value, chosen, trace))

        tampered = list(trace)
        event = tampered[1]
        tampered[1] = WeightedActivityEvent(
            event.prefix_size, event.activity, event.compatible_prefix_size,
            event.skip_value, event.take_value, event.best_value + 1.0, event.chose_activity,
        )
        self.assertFalse(weighted_activity_trace_certificate(activities, value, chosen, tampered))

    def test_rejects_invalid_activities_and_large_brute_force_requests(self):
        with self.assertRaises(ValueError):
            weighted_activity_selection([(2.0, 1.0, 1.0, "bad")])
        with self.assertRaises(ValueError):
            weighted_activity_selection([(0.0, 1.0, -1.0, "bad")])
        with self.assertRaises(ValueError):
            brute_force_best_value([(float(index), float(index + 1), 1.0, str(index)) for index in range(19)])
        with self.assertRaises(ValueError):
            brute_force_max_cardinality([(float(index), float(index + 1), str(index)) for index in range(19)])
