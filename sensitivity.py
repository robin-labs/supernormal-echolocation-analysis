from typing import List, Tuple
from functools import reduce
from statistics import NormalDist
import numpy as np
from scipy.optimize import curve_fit

from models import Participant
from confusion import ConfusionMatrix
from util import mean_of_matrices

InterstimSensitivities = List[Tuple[int, float]]
inverse_cdf = np.vectorize(NormalDist().inv_cdf)


def get_individual_interstim_sensitivities_for_participants(
    participants: List[Participant],
    sector=None,
    epsilon=0.001,
):
    all_sensitivities = []
    for part in participants:
        confusion_matrix = ConfusionMatrix.of_indices(part.get_responses(sector=sector))
        participant_sensitivities = get_interstim_sensitivities_for_confusion_matrix(
            confusion_matrix,
            epsilon,
        )
        all_sensitivities += participant_sensitivities
    return all_sensitivities


def get_interstim_sensitivities_for_confusion_matrix(
    cm: ConfusionMatrix,
    epsilon=0.001,
) -> InterstimSensitivities:
    false_alarms = cm.true_values_sum_to_unity
    regularized_false_alarms = np.clip(false_alarms, epsilon, 1 - epsilon)
    num_responses = regularized_false_alarms.shape[0]
    hits = np.tile(regularized_false_alarms.diagonal(), (num_responses, 1))
    d_prime = inverse_cdf(hits) - inverse_cdf(regularized_false_alarms)
    distances = []
    for i in range(num_responses):
        for j in range(num_responses):
            interstim_distance = abs(j - i)
            if interstim_distance == 0:
                continue
            value = d_prime[i, j]
            distances.append((interstim_distance, value))
    return list(sorted(distances, key=lambda x: x[0]))


def get_log(x: float, a_param: float, b_param: float) -> float:
    return a_param + b_param * np.log(x)


def get_lin(x: float, m_param: float, b_param: float) -> float:
    return b_param + m_param * x


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


def lin_fit_sensitivities(sensitivites: InterstimSensitivities):
    x, y = zip(*sensitivites)
    popt, _ = curve_fit(get_lin, x, y)
    x_interpolated = get_linspace_for_sensitivities(sensitivites)
    y_interpolated = get_lin(x_interpolated, *popt)
    return x_interpolated, y_interpolated


def multilinear_fit_sensitivities(sensitivities: InterstimSensitivities):
    x = []
    y = []
    for distance in range(1, 5):
        mean = np.mean([s[1] for s in sensitivities if s[0] == distance])
        x.append(distance)
        y.append(mean)
    return x, y