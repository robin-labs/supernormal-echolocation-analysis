import itertools
from dataclasses import dataclass
from typing import List, Dict

from models import Participant, ParticipantException

import itertools


def dict_product(dict_of_vals_or_lists):
    values = [v if isinstance(v, list) else [v] for v in dict_of_vals_or_lists.values()]
    return list(dict(zip(dict_of_vals_or_lists, x)) for x in itertools.product(*values))

def create_query(**kwargs):
    query_args = {"version": "v1-up-stims", "model_name": "spherical", **kwargs}

    if query_args.get("compensation") and query_args.get("compensation_descriptor"):
        raise Exception("Cannot query on both compensation and compensation_descriptor")

    if query_args.get("version") is None:
        raise Exception("Refusing to run a query without an experiment version")

    def test(participant):
        for (key, value) in query_args.items():
            if getattr(participant, key) != value:
                return False
        return True

    return query_args, test


@dataclass
class Condition:
    participants: List[Participant]
    values: Dict[str, any]

    def query_participants(self, **kwargs):
        query_args, test = create_query(**kwargs)
        return Condition(
            participants=list(filter(test, self.participants)), values={**self.values, **query_args}
        )

    def get(self):
        return self.participants

    def get_participants_responses(self, kind=None):
        res = []
        for part in self.participants:
            responses = part.get_responses(kind)
            for resp in responses:
                res.append(resp)
        return res

    def count(self):
        return len(self.participants)

    def subsect(self, **kwargs):
        queries = dict_product(kwargs)
        return [self.query_participants(**query) for query in queries]

    def label(self, *keys):
        label_parts = []
        for entry in keys:
            if isinstance(entry, list):
                [key, label] = entry
            else:
                key = entry
                label = entry
            value = self.values.get(key)
            if key and value:
                label_parts.append(f"{label}={value}")
        return ", ".join(label_parts)


class Study(Condition):
    def __init__(self, participants: List[Participant], exceptions: List[ParticipantException]):
        super().__init__(participants=participants, values={})
        self.exceptions = exceptions

    def print_summary(self):
        print(f"✅ Loaded {len(self.participants)} entries")
        print(f"🚨 Rejected {len(self.exceptions)} entries")

    def spherical_vs_kemar(self, slowdown=20, compensation=20):
        return [
            self.query_participants(
                model_name="spherical", slowdown=slowdown, compensation=compensation
            ),
            self.query_participants(model_name="kemar", slowdown=slowdown),
        ]