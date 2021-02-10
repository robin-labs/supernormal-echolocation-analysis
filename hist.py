import matplotlib.pyplot as plt

from load import get_data_file_paths, get_participant_for_file
from util import print_distribution, merge_distributions

data_files = get_data_file_paths()
participants = list(
    filter(
        lambda x: x is not None
        and x.version == "v1-up-stims"
        and x.slowdown == 20
        and x.compensation == 1,
        [get_participant_for_file(file) for file in data_files],
    )
)

blocks = [block for part in participants for block in part.blocks]


def blocks_by_center_azimuth(center):
    return [block for block in blocks if block.center_azimuth == center]


left_blocks = blocks_by_center_azimuth(-60)
right_blocks = blocks_by_center_azimuth(60)
front_blocks = blocks_by_center_azimuth(0)

for part in participants:
    print_distribution(part.error_distribution)

print("\nTOTAL:")
total_distribution = merge_distributions(part.error_distribution for part in right_blocks)
print_distribution(total_distribution)
plt.bar(total_distribution.keys(), total_distribution.values())

print("\n======\n")

for (label, blocks) in [("left", left_blocks), ("right", right_blocks), ("front", front_blocks)]:
    errs = [b.average_error for b in blocks]
    fracs = [b.fraction_correct_responses for b in blocks]
    print(f"{label} avg error:", round(sum(errs) / len(errs), 2))
    print(f"{label} percent correct:", round(sum(fracs) / len(fracs), 2))

plt.show()
