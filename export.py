from csv import DictWriter
from os import path

from loader import echo_study
from confusion import ConfusionMatrix
from sensitivity import get_interstim_sensitivities_for_confusion_matrix

filename = "data_export.csv"
file_path = path.normpath(path.join(__file__, "..", filename))

columns = [
    "participant_id",
    "slowdown",
    "compensation",
    "sector",
    "dist_positions",
    "dist_degrees",
    "d_prime",
]


with open(file_path, "w") as file:
    writer = DictWriter(file, columns)
    writer.writeheader()
    for participant in echo_study.query_participants().get():
        for sector in ("left", "center", "right"):
            responses = participant.get_responses(sector=sector)
            matrix = ConfusionMatrix.of_azimuths(responses)
            sensitivities = get_interstim_sensitivities_for_confusion_matrix(matrix)
            for (dist, d_prime) in sensitivities:
                writer.writerow(
                    {
                        "participant_id": participant.prolific_pid,
                        "slowdown": participant.slowdown,
                        "compensation": participant.compensation,
                        "sector": sector,
                        "dist_positions": dist,
                        "dist_degrees": 10 * dist,
                        "d_prime": d_prime,
                    }
                )
