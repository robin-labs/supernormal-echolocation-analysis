from typing import List
from csv import DictReader
from dataclasses import dataclass

import pandas as pd
import pingouin as pg
from statsmodels.formula.api import ols


from confusion import ConfusionMatrix
from sensitivity import get_interstim_sensitivities_for_confusion_matrix, InterstimSensitivities


@dataclass
class RmCorrResult:
    slowdown: int
    compensation_descriptor: str
    count: int
    sector: str
    slope: float
    rmcorr: float
    pval: float
    slope_ci95_lower: float
    slope_median: float
    slope_ci95_upper: float
    rmcorr_ci95_lower: float
    rmcorr_median: float
    rmcorr_ci95_upper: float

    @property
    def compensation(self):
        if self.compensation_descriptor == "1":
            return 1
        elif self.compensation_descriptor == "half":
            return self.slowdown / 2
        elif self.compensation_descriptor == "full":
            return self.slowdown

    def matches(self, query):
        for key, value in query.items():
            if hasattr(self, key) and getattr(self, key) != value:
                return False
        return True


def load_rmcorr_results():
    results = []
    with open("./rmcorr_analysis.csv", "r") as file:
        reader = DictReader(file)
        for line in reader:
            results.append(
                RmCorrResult(
                    **{
                        key: value if key in ("compensation_descriptor", "sector") else float(value)
                        for key, value in line.items()
                    }
                )
            )
    return results


def _get_dataframe_for_sensitivities_by_participant(
    sensitivities_by_participant: List[List[InterstimSensitivities]],
):
    data = {"subject": [], "distance": [], "dprime": []}
    for idx, sensitivities in enumerate(sensitivities_by_participant):
        subject = str(idx)
        for (distance, dprime) in sensitivities:
            data["subject"].append(subject)
            data["distance"].append(distance)
            data["dprime"].append(dprime)
    return pd.DataFrame(data)


def get_rmcorr_for_sensitivities_by_participant(
    sensitivities_by_participant: List[List[InterstimSensitivities]],
):
    df = _get_dataframe_for_sensitivities_by_participant(sensitivities_by_participant)
    model = ols("dprime ~ C(subject) + distance", data=df).fit()
    rm_corr = pg.rm_corr(df, x="distance", y="dprime", subject="subject")
    return (
        model.params["distance"],
        rm_corr.at["rm_corr", "r"],
        rm_corr.at["rm_corr", "CI95%"],
        rm_corr.at["rm_corr", "pval"],
    )
