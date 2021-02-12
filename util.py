from typing import List, Dict


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


def flag_block(block):
    running_resp_count = 0
    running_resp = None
    max_running_resp_count = 0
    for resp in block.responses:
        azimuth = resp.response_azimuth
        if running_resp is None:
            running_resp = azimuth
        if running_resp == azimuth:
            running_resp_count += 1
        else:
            max_running_resp_count = max(max_running_resp_count, running_resp_count)
            running_resp_count = 1
        running_resp = azimuth
    max_running_resp_count = max(running_resp_count, max_running_resp_count)
    return max_running_resp_count > 7


def resolve_compensation_value(slowdown, compensation_descriptor):
    if compensation_descriptor == "full":
        return slowdown
    elif compensation_descriptor == "half":
        return slowdown // 2
    return int(compensation_descriptor)