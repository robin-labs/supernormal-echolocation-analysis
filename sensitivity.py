from typing import List, Tuple
from statistics import NormalDist
import numpy as np
from scipy.optimize import curve_fit

from confusion import ConfusionMatrix

InterstimSensitivities = List[Tuple[int, float]]
inverse_cdf = np.vectorize(NormalDist().inv_cdf)


def get_interstim_sensitivities(matrix: ConfusionMatrix, epsilon=0.001) -> InterstimSensitivities:
    false_alarms = np.clip(matrix.false_alarms, epsilon, 1 - epsilon)
    hits = np.tile(false_alarms.diagonal(), (matrix.size, 1))
    d_prime = inverse_cdf(hits) - inverse_cdf(false_alarms)
    distances = []
    for i in range(matrix.size):
        for j in range(matrix.size):
            interstim_distance = abs(j - i)
            if interstim_distance == 0:
                continue
            value = d_prime[i, j]
            distances.append((interstim_distance, value))
    return list(sorted(distances, key=lambda x: x[0]))


def get_log(x: float, a_param: float, b_param: float) -> float:
    return a_param + b_param * np.log(x)


def get_linspace_for_sensitivities(sensitivites: InterstimSensitivities, delta=0.1):
    distances = [s[0] for s in sensitivites]
    min_distance = np.min(distances)
    max_distance = np.max(distances)
    return np.linspace(min_distance, max_distance, 1 + round((max_distance - min_distance) / delta))


def log_fit_sensitivities(sensitivites: InterstimSensitivities):
    x, y = zip(*sensitivites)
    popt, _ = curve_fit(get_log, x, y)
    x_interpolated = get_linspace_for_sensitivities(sensitivites)
    y_interpolated = get_log(x_interpolated, *popt)
    return x_interpolated, y_interpolated