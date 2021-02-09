from typing import List, Dict


def get_participants_responses(participants, kind=None):
    res = []
    for part in participants:
        responses = part.get_responses(kind)
        for resp in responses:
            res.append(resp)
    return res


def merge_distributions(distributions: List[Dict[int, int]], expected_keys=range(-40, 50, 10)):
    totals = {}
    for ek in expected_keys:
        totals[ek] = 0
    for dist in distributions:
        for (key, value) in dist.items():
            if not totals.get(key):
                totals[key] = 0
            totals[key] += value
    return totals


def print_distribution(distribution: Dict[int, int]):
    keys = sorted(distribution.keys())
    pairs = [f"{key}:{distribution[key]}" for key in keys]
    max_pair_length = max(len(p) for p in pairs)
    print(" ".join(p.rjust(max_pair_length) for p in pairs))