from os import listdir, path
from csv import DictReader

from models import Response, Block, Participant, ParticipantException
from study import Study

invalid_prolific_pids = [
    "5feb726715b59bbd3c904409",  # Wrote in to say semicolon was broken
    "5e328fc0a7365325cc819dae",  # Repeat runs > 10 of same choice
    "5febda8badaa09d0c281c8c4",  # Me
    "5f9195db475c94016b4a9750",  # Phoning it in...
    # "5f3d8b0bd9a75c164958578a",
    # "5bc623acd2bea100010c808e",
    # "5bc2e0ec4f3bfd00012e97b5",
]


def get_file_paths(parent_dir):
    children = [path.join(parent_dir, child) for child in listdir(parent_dir)]
    return [child for child in children if path.isfile(child) and child.endswith(".csv")]


def get_data_file_paths():
    data_dir = path.normpath(
        path.join(__file__, "..", "supernormal-echolocation-presentations", "data")
    )
    return get_file_paths(data_dir)


def get_participant_metadata_file_paths():
    metadata_dir = path.normpath(path.join(__file__, "..", "participant-metadata"))
    return get_file_paths(metadata_dir)


def load_participant_metadata():
    metadata_by_pid = {}
    for path in get_participant_metadata_file_paths():
        with open(path, "r") as file:
            reader = DictReader(file)
            for row in reader:
                pid = row["participant_id"]
                age = row["age"]
                sex = row["Sex"]
                metadata_by_pid[pid] = {"age": age, "sex": sex}
    return metadata_by_pid


def get_participant_for_file(path, metadata_by_pid):
    with open(path, "r") as data_file:
        reader = DictReader(data_file)
        blocks = []
        prolific_pid = None
        slowdown = None
        keyset = None
        compensation = None
        user_agent = None
        current_block_responses = []
        current_block_center = None
        compensation_descriptor = None
        version = None
        model_name = None
        for row in reader:
            prolific_pid = row.get("prolificPid")
            if prolific_pid in invalid_prolific_pids:
                raise ParticipantException(prolific_pid, "marked-invalid")
            if row.get("version") is None:
                raise ParticipantException(prolific_pid, "no-version")
            if row["trial_type"] == "keyset-select":
                keyset = row.get("chosenKeyset")
            if row["trial_type"] == "block-bookend" and len(current_block_responses) == 20:
                next_block = Block(
                    center_azimuth=current_block_center, responses=current_block_responses
                )
                blocks.append(next_block)
                current_block_responses = []
            if row["trial_type"] == "echo-presentation":
                compensation_str = row.get("compensation")
                if compensation_str == "NaN":
                    compensation = 0
                else:
                    compensation = int(compensation_str)
                choices = list(map(int, row.get("choices").split(",")))
                current_block_center = choices[2]
                slowdown = int(row.get("slowdown"))
                compensation_descriptor = row.get("compensationDescriptor")
                true_azimuth = row.get("azimuth")
                user_agent = row.get("userAgent")
                version = row.get("version")
                model_name = row.get("modelName")
                response_azimuth = row.get("responseAzimuth")
                response_delay = row.get("responseDelay")
                filename = row.get("filename")
                if true_azimuth and response_azimuth:
                    response = Response(
                        true_azimuth=int(true_azimuth),
                        response_azimuth=int(response_azimuth),
                        azimuth_choices=choices,
                        response_delay_ms=int(response_delay),
                        filename=filename,
                    )
                    current_block_responses.append(response)
        metadata = metadata_by_pid.get(prolific_pid)
        if (
            len(blocks) == 6
            and slowdown
            and compensation is not None
            and compensation_descriptor
            and version
            and prolific_pid
        ):
            return Participant(
                version=version,
                user_agent=user_agent,
                compensation=compensation,
                compensation_descriptor=compensation_descriptor,
                slowdown=slowdown,
                blocks=blocks,
                keyset=keyset,
                prolific_pid=prolific_pid,
                model_name=model_name,
                sex=metadata["sex"],
                age=(int(metadata["age"]) if metadata["age"] else None),
            )
    raise ParticipantException(prolific_pid, "missing-data")


_participants = []
_exceptions = []
_metadata = load_participant_metadata()
for file in get_data_file_paths():
    try:
        participant = get_participant_for_file(file, _metadata)
        _participants.append(participant)
    except ParticipantException as ex:
        _exceptions.append(ex)

echo_study = Study(_participants, _exceptions)
echo_study.print_summary()
