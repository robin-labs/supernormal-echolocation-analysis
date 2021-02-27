from typing import List
import itertools
import numpy as np
from scipy.stats import linregress

from confusion import ConfusionMatrix
from sensitivity import get_interstim_sensitivities_for_confusion_matrix, InterstimSensitivities

rng = np.random.default_rng(8675309)


def _get_slope_for_sensitivites(sensitivites: List[InterstimSensitivities]):
    x, y = zip(*sensitivites)
    linreg = linregress(x, y)
    return linreg.slope, linreg.rvalue ** 2


def bootstrap_dprime_slope(matrices: List[ConfusionMatrix], population_size=12, iterations=10000):
    sensitivities = [get_interstim_sensitivities_for_confusion_matrix(cm) for cm in matrices]
    slopes = []
    r2s = []
    for i in range(iterations):
        population_sensitivities = rng.choice(sensitivities, population_size)
        flattened_population_sensitivities = itertools.chain(*population_sensitivities)
        slope, r2 = _get_slope_for_sensitivites(flattened_population_sensitivities)
        slopes.append(slope)
        r2s.append(r2)
    return list(sorted(slopes)), list(sorted(r2s))
