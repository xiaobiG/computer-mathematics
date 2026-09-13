"""Finite binary relations and their adjacency-matrix representations for teaching."""
from __future__ import annotations

import platform
import sys
from statistics import median
from time import perf_counter_ns


CONTRACT = "finite-relation-matrix/v1"
BOOLEAN_COMPOSITION_CONTRACT = "boolean-relation-composition/v1"
BITSET_BATCH_CONTRACT = "bitset-batch-relation-query/v1"
CACHE_INVALIDATION_CONTRACT = "relation-bitset-cache-invalidation/v1"
RUNTIME_MEASUREMENT_CONTRACT = "relation-batch-runtime-measurement/v1"


def _domain(value):
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value) or len(set(value)) != len(value):
        raise ValueError("domain must be a non-empty duplicate-free list of strings")
    return list(value)


def _pairs(value, domain):
    if not isinstance(value, list):
        raise ValueError("pairs must be a list")
    normalized = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2 or pair[0] not in domain or pair[1] not in domain:
            raise ValueError("each pair must contain two domain members")
        normalized.append(tuple(pair))
    if len(set(normalized)) != len(normalized):
        raise ValueError("pairs must not repeat")
    return normalized


def finite_relation_report(domain, pairs):
    """Report relation properties and its 0/1 matrix under the declared order."""
    members, edges = _domain(domain), _pairs(pairs, domain)
    edge_set = set(edges)
    matrix = [[1 if (left, right) in edge_set else 0 for right in members] for left in members]
    reflexive = all((member, member) in edge_set for member in members)
    symmetric = all((right, left) in edge_set for left, right in edge_set)
    transitive = all((left, final) in edge_set for left, middle in edge_set for middle2, final in edge_set if middle == middle2)
    return {"contract": CONTRACT, "domain": members, "pairs": [list(pair) for pair in edges], "adjacency_matrix": matrix, "properties": {"reflexive": reflexive, "symmetric": symmetric, "transitive": transitive, "equivalence_relation": reflexive and symmetric and transitive}, "matrix_order": members}


def finite_relation_certificate(domain, pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == finite_relation_report(domain, pairs)
    except ValueError:
        return False


def relation_reachability_report(domain, pairs):
    """Compute transitive closure by adding one allowed intermediate at a time."""
    members, edges = _domain(domain), _pairs(pairs, domain)
    reach = set(edges)
    layers = []
    for middle in members:
        before = set(reach)
        reach |= {(left, right) for left, pivot in before for pivot2, right in before if pivot == middle == pivot2}
        layers.append({"intermediate": middle, "new_pairs": [list(pair) for pair in sorted(reach - before)]})
    return {"contract": "relation-reachability/v1", "domain": members, "pairs": [list(pair) for pair in edges], "closure_pairs": [list(pair) for pair in sorted(reach)], "layers": layers, "closure_matrix": [[1 if (left, right) in reach else 0 for right in members] for left in members]}


def relation_reachability_certificate(domain, pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == relation_reachability_report(domain, pairs)
    except ValueError:
        return False


def boolean_relation_composition_report(domain, left_pairs, right_pairs):
    """Compare boolean-matrix composition with sparse adjacency-list traversal."""
    members = _domain(domain)
    left, right = _pairs(left_pairs, members), _pairs(right_pairs, members)
    left_set, right_set = set(left), set(right)
    dense_checks = 0
    composed = set()
    for source in members:
        for target in members:
            exists = False
            for middle in members:
                dense_checks += 1
                if (source, middle) in left_set and (middle, target) in right_set:
                    exists = True
                    break
            if exists:
                composed.add((source, target))
    outgoing = {member: [] for member in members}
    for middle, target in right:
        outgoing[middle].append(target)
    sparse_checks = 0
    sparse_composed = set()
    for source, middle in left:
        for target in outgoing[middle]:
            sparse_checks += 1
            sparse_composed.add((source, target))
    matrix = [[1 if (source, target) in composed else 0 for target in members] for source in members]
    return {
        "contract": BOOLEAN_COMPOSITION_CONTRACT,
        "domain": members,
        "left_pairs": [list(pair) for pair in left],
        "right_pairs": [list(pair) for pair in right],
        "composition_pairs": [list(pair) for pair in sorted(composed)],
        "boolean_product_matrix": matrix,
        "verification": {"dense_and_sparse_pairs_match": composed == sparse_composed},
        "work": {"dense_candidate_checks": dense_checks, "sparse_two_hop_scans": sparse_checks},
        "interpretation": "operation_counts_for_this_snapshot_not_a_general_performance_guarantee",
    }


def boolean_relation_composition_certificate(domain, left_pairs, right_pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == boolean_relation_composition_report(domain, left_pairs, right_pairs)
    except ValueError:
        return False


def bitset_batch_relation_query_report(domain, left_pairs, right_pairs, query_sources, word_bits):
    """Compare repeated sparse two-hop queries to cached Boolean bitset rows.

    The bitset path models fixed-width machine words even though Python stores
    the packed rows as arbitrary-size integers.  It exposes query batching and
    cache reuse, rather than claiming wall-clock performance for any runtime.
    """
    members = _domain(domain)
    left, right = _pairs(left_pairs, members), _pairs(right_pairs, members)
    if (not isinstance(query_sources, list) or not query_sources
            or any(not isinstance(source, str) or source not in members for source in query_sources)):
        raise ValueError("query_sources must be a non-empty list of domain members")
    if (not isinstance(word_bits, int) or isinstance(word_bits, bool) or not 1 <= word_bits <= 64):
        raise ValueError("word_bits must be an integer from 1 to 64")
    outgoing_left = {member: [] for member in members}
    outgoing_right = {member: [] for member in members}
    for source, middle in left:
        outgoing_left[source].append(middle)
    for middle, target in right:
        outgoing_right[middle].append(target)
    index = {member: position for position, member in enumerate(members)}
    right_row_bitsets = {}
    for middle in members:
        mask = 0
        for target in outgoing_right[middle]:
            mask |= 1 << index[target]
        right_row_bitsets[middle] = mask
    words_per_row = (len(members) + word_bits - 1) // word_bits
    cache = {}
    batch_outputs = []
    sparse_scans = 0
    modeled_word_ors = 0
    cache_hits = 0
    for source in query_sources:
        sparse_targets = set()
        for middle in outgoing_left[source]:
            for target in outgoing_right[middle]:
                sparse_scans += 1
                sparse_targets.add(target)
        if source in cache:
            cache_hits += 1
            mask = cache[source]
            cache_hit = True
        else:
            mask = 0
            for middle in outgoing_left[source]:
                mask |= right_row_bitsets[middle]
                modeled_word_ors += words_per_row
            cache[source] = mask
            cache_hit = False
        bitset_targets = [member for member in members if mask & (1 << index[member])]
        if sparse_targets != set(bitset_targets):
            raise AssertionError("sparse and bitset paths must agree")
        batch_outputs.append({
            "query_source": source,
            "reachable_targets": bitset_targets,
            "cache_hit": cache_hit,
        })
    return {
        "contract": BITSET_BATCH_CONTRACT,
        "domain": members,
        "left_pairs": [list(pair) for pair in left],
        "right_pairs": [list(pair) for pair in right],
        "query_sources": list(query_sources),
        "word_bits": word_bits,
        "right_row_bitsets": [right_row_bitsets[member] for member in members],
        "batch_outputs": batch_outputs,
        "verification": {"sparse_and_bitset_outputs_match": True},
        "work": {
            "query_count": len(query_sources),
            "unique_source_count": len(cache),
            "sparse_two_hop_scans": sparse_scans,
            "bitset_row_construction_bit_writes": len(right),
            "bitset_modeled_word_ors_after_construction": modeled_word_ors,
            "modeled_words_per_row": words_per_row,
            "bitset_cache_hits": cache_hits,
        },
        "interpretation": "fixed_word_operation_model_for_this_batch_not_wall_clock_or_dynamic_update_guarantee",
    }


def bitset_batch_relation_query_certificate(domain, left_pairs, right_pairs, query_sources, word_bits, report):
    """Rebuild packed rows, batch outputs and modeled work counters."""
    if not isinstance(report, dict):
        return False
    try:
        return report == bitset_batch_relation_query_report(
            domain, left_pairs, right_pairs, query_sources, word_bits,
        )
    except ValueError:
        return False


def _batch_query_inputs(domain, left_pairs, right_pairs, query_sources):
    members = _domain(domain)
    left, right = _pairs(left_pairs, members), _pairs(right_pairs, members)
    if (not isinstance(query_sources, list) or not query_sources
            or any(not isinstance(source, str) or source not in members for source in query_sources)):
        raise ValueError("query_sources must be a non-empty list of domain members")
    left_outgoing = {member: [] for member in members}
    right_outgoing = {member: [] for member in members}
    for source, middle in left:
        left_outgoing[source].append(middle)
    for middle, target in right:
        right_outgoing[middle].append(target)
    return members, left_outgoing, right_outgoing


def _sparse_two_hop_batch_outputs(members, left_outgoing, right_outgoing, query_sources):
    return [
        sorted({target for middle in left_outgoing[source] for target in right_outgoing[middle]})
        for source in query_sources
    ]


def _bitset_cached_batch_outputs(members, left_outgoing, right_outgoing, query_sources):
    positions = {member: index for index, member in enumerate(members)}
    rows = {
        middle: sum(1 << positions[target] for target in right_outgoing[middle])
        for middle in members
    }
    cache = {}
    outputs = []
    for source in query_sources:
        if source not in cache:
            mask = 0
            for middle in left_outgoing[source]:
                mask |= rows[middle]
            cache[source] = mask
        else:
            mask = cache[source]
        outputs.append([member for member in members if mask & (1 << positions[member])])
    return outputs


def relation_batch_runtime_measurement(domain, left_pairs, right_pairs, query_sources, repetitions=7, warmup_runs=1, clock_ns=None):
    """Measure two declared finite query kernels on this runtime only.

    The report deliberately records raw samples and environment metadata instead
    of declaring a winner.  `clock_ns` exists only so tests can inspect the
    timing contract; ordinary readers use Python's monotonic performance clock.
    """
    if (not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions < 3
            or not isinstance(warmup_runs, int) or isinstance(warmup_runs, bool) or warmup_runs < 0):
        raise ValueError("repetitions must be at least 3 and warmup_runs must be non-negative integers")
    if clock_ns is not None and not callable(clock_ns):
        raise ValueError("clock_ns must be callable when supplied")
    members, left_outgoing, right_outgoing = _batch_query_inputs(domain, left_pairs, right_pairs, query_sources)
    for _ in range(warmup_runs):
        _sparse_two_hop_batch_outputs(members, left_outgoing, right_outgoing, query_sources)
        _bitset_cached_batch_outputs(members, left_outgoing, right_outgoing, query_sources)
    clock = perf_counter_ns if clock_ns is None else clock_ns
    sparse_samples, bitset_samples = [], []
    expected_outputs = None
    for _ in range(repetitions):
        start = clock()
        sparse_outputs = _sparse_two_hop_batch_outputs(members, left_outgoing, right_outgoing, query_sources)
        end = clock()
        sparse_samples.append(end - start)
        start = clock()
        bitset_outputs = _bitset_cached_batch_outputs(members, left_outgoing, right_outgoing, query_sources)
        end = clock()
        bitset_samples.append(end - start)
        if sparse_outputs != bitset_outputs:
            raise AssertionError("sparse and bitset timing kernels must agree")
        expected_outputs = sparse_outputs
    if any(sample < 0 for sample in sparse_samples + bitset_samples):
        raise ValueError("clock_ns must not move backwards within a measurement")
    return {
        "contract": RUNTIME_MEASUREMENT_CONTRACT,
        "query_sources": list(query_sources),
        "repetitions": repetitions,
        "warmup_runs": warmup_runs,
        "clock": "time.perf_counter_ns" if clock_ns is None else "injected_test_clock",
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "outputs": expected_outputs,
        "verification": {"sparse_and_bitset_outputs_match_each_repetition": True},
        "sparse_two_hop_elapsed_ns": sparse_samples,
        "bitset_cached_elapsed_ns": bitset_samples,
        "sparse_two_hop_median_ns": median(sparse_samples),
        "bitset_cached_median_ns": median(bitset_samples),
        "interpretation": "local_runtime_measurement_not_cross_machine_throughput_or_concurrent_cache_guarantee",
        "automatic_action": "none",
    }


def relation_cache_invalidation_report(domain, left_pairs, right_before, right_after, query_sources, word_bits):
    """Show that a cached two-hop answer is tied to one declared relation version."""
    before = bitset_batch_relation_query_report(domain, left_pairs, right_before, query_sources, word_bits)
    after = bitset_batch_relation_query_report(domain, left_pairs, right_after, query_sources, word_bits)
    changed = before["batch_outputs"] != after["batch_outputs"]
    return {"contract": CACHE_INVALIDATION_CONTRACT, "versions": [0, 1],
            "before": before, "after": after,
            "old_cache_valid_for_version_1": not changed,
            "changed_query_indexes": [index for index, pair in enumerate(zip(before["batch_outputs"], after["batch_outputs"])) if pair[0]["reachable_targets"] != pair[1]["reachable_targets"]],
            "interpretation": "cache_entries_are_valid_only_for_the_declared_relation_version",
            "boundary": "finite_snapshot_contract_not_concurrent_cache_coherence_or_runtime_performance", "automatic_action": "none"}


def relation_cache_invalidation_certificate(domain, left_pairs, right_before, right_after, query_sources, word_bits, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == relation_cache_invalidation_report(domain, left_pairs, right_before, right_after, query_sources, word_bits)
    except ValueError:
        return False
