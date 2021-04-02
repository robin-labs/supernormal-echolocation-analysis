from typing import List, Tuple
import itertools

import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
from scipy.stats import linregress


from confusion import ConfusionMatrix
from sensitivity import get_interstim_sensitivities_for_confusion_matrix, InterstimSensitivities
from rmcorr import get_rmcorr_for_sensitivities_by_participant

rng = np.random.default_rng(8675309)


def _get_slope_for_sensitivites_by_participant(
    sensitivities_by_participant: List[List[InterstimSensitivities]],
):
    flattened_sensitivities = itertools.chain(*sensitivities_by_participant)
    x, y = zip(*flattened_sensitivities)
    linreg = linregress(x, y)
    return linreg.slope, linreg.intercept


def _get_rmcorr_slope_for_sensitivities_by_participant(
    sensitivities_by_participant: List[List[InterstimSensitivities]],
):
    slope, *_ = get_rmcorr_for_sensitivities_by_participant(sensitivities_by_participant)
    return slope


def bootstrap_dprime_slope(
    matrices: List[ConfusionMatrix],
    sample_size=12,
    iterations=10000,
    use_rmcorr=False,
):
    get_slope = (
        _get_rmcorr_slope_for_sensitivities_by_participant
        if use_rmcorr
        else _get_slope_for_sensitivites_by_participant
    )
    sensitivities = [get_interstim_sensitivities_for_confusion_matrix(cm) for cm in matrices]
    overall_slope, overall_intercept = get_slope(sensitivities)
    slopes = []
    r2s = []
    for i in range(iterations):
        psuedosample_sensitivities = rng.choice(sensitivities, sample_size)
        slope, _ = get_slope(psuedosample_sensitivities)
        slopes.append(slope)
    return (overall_slope, overall_intercept), list(sorted(slopes))


def percentiles(values):
    lower = np.percentile(values, 0.025)
    median = np.median(values)
    upper = np.percentile(values, 100 - 0.025)
    return (lower, median, upper)


def bootstrap_dprime_rmcorr_ci95(matrices: List[ConfusionMatrix], sample_size=12, iterations=10000):
    sensitivities = [get_interstim_sensitivities_for_confusion_matrix(cm) for cm in matrices]
    slopes = []
    rm_corrs = []
    for i in range(iterations):
        psuedosample_sensitivities = rng.choice(sensitivities, sample_size)
        slope, rm_corr, *_ = get_rmcorr_for_sensitivities_by_participant(psuedosample_sensitivities)
        slopes.append(slope)
        rm_corrs.append(rm_corr)
    return percentiles(slopes), percentiles(rm_corrs)
