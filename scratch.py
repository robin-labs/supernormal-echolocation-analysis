import numpy as np
import matplotlib.pyplot as plt

from confusion import ConfusionMatrix
from sensitivity import get_interstim_sensitivities, log_fit_sensitivities


def parse_str_example_data(str_data):
    return np.array(
        [[int(n_str) for n_str in row.split("\t")] for row in str_data.strip().splitlines()]
    )


cm_1 = ConfusionMatrix(
    parse_str_example_data(
        """
        39	4	1	0	0
        135	107	26	3	0
        24	87	146	108	15
        1	2	27	81	98
        0	0	0	8	87
        """
    )
)

cm_2 = ConfusionMatrix(
    parse_str_example_data(
        """
        7	4	0	0	0
        50	32	13	3	0
        37	58	70	55	8
        1	2	12	36	43
        0	0	1	5	45
        """
    )
)

cm_3 = ConfusionMatrix(
    parse_str_example_data(
        """
        19	9	2	2	0
        81	50	20	3	0
        4	45	77	71	17
        0	0	5	25	52
        0	0	0	0	34
        """
    )
)


labels = ["baseline", "stimulation", "poststim"]
colors = ["tab:orange", "tab:blue", "tab:green"]
markers = ["o", "*", "x"]
for idx, cm in enumerate((cm_1, cm_2, cm_3)):
    color = colors[idx]
    marker = markers[idx]
    label = labels[idx]
    s = get_interstim_sensitivities(cm)
    x, y = log_fit_sensitivities(s)
    plt.plot(x, y, color=color, label=f"{label} (log)")
    plt.plot(*zip(*s), color=color, marker=marker, linestyle="None", label=label)
plt.legend(loc="lower right")
plt.show()