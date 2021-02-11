from typing import List, Tuple
from statistics import NormalDist
import numpy as np

from models import Response


class ConfusionMatrix:
    def __init__(self, matrix: np.ndarray, labels=None):
        assert matrix.shape[0] == matrix.shape[1]
        if labels is None:
            labels = list(range(0, matrix.shape[0]))
        self._matrix = matrix
        self._labels = labels

    def _normalize(self, axis: int):
        return np.nan_to_num(self.totals / self.totals.sum(axis=axis, keepdims=1), 0)

    @property
    def false_alarms(self):
        return self._normalize(0)

    @property
    def size(self):
        return self._matrix.shape[0]

    @property
    def totals(self):
        return self._matrix

    @property
    def labels(self):
        return self._labels

    @staticmethod
    def from_true_reported_pairs(true_reported_pairs: List[Tuple[int, int]], provided_labels=None):
        if provided_labels:
            labels = provided_labels
        else:
            extracted_labels = set()
            for (true, reported) in true_reported_pairs:
                extracted_labels.add(true)
                extracted_labels.add(reported)
            labels = list(sorted(extracted_labels))
        size = len(labels)
        matrix = np.zeros((size, size))
        for (true, reported) in true_reported_pairs:
            true_index = labels.index(true)
            reported_index = labels.index(reported)
            matrix[true_index, reported_index] += 1
        return ConfusionMatrix(matrix, labels)

    @staticmethod
    def of_azimuths(responses: List[Response]):
        min_azimuth = float("inf")
        max_azimuth = float("-inf")
        for resp in responses:
            for az in (resp.true_azimuth, resp.response_azimuth):
                min_azimuth = min(min_azimuth, az)
                max_azimuth = max(max_azimuth, az)
        labels = list(range(min_azimuth, max_azimuth + 10, 10))
        return ConfusionMatrix.from_true_reported_pairs(
            [(r.true_azimuth, r.response_azimuth) for r in responses], labels
        )

    @staticmethod
    def of_indices(responses: List[Response]):
        return ConfusionMatrix.from_true_reported_pairs(
            [(r.true_index, r.response_index) for r in responses]
        )
