from json import load
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb

with open('data.json') as f:
    json = load(f)

if 'members' not in json:
    print('Loaded json is not a valid leaderboard file.')
    exit()

members = json['members']

timestamps = []
for member_id, member_data in members.items():
    completion_data = member_data['completion_day_level']
    member_data = [member_id] + [(None, None)] * 25
    for day, day_data in completion_data.items():
        part1_ts, part2_ts = day_data['1']['get_star_ts'], day_data.get('2', None)
        if part2_ts is not None:
            part2_ts = part2_ts['get_star_ts']
        member_data[int(day)] = (part1_ts, part2_ts)
    timestamps.append(member_data)


def get_top_members(data: list[list], day: int) -> tuple[list[str], list[str]]:
    part1 = filter(lambda row: row[day][0], data)
    part2 = filter(lambda row: row[day][1], data)
    part1 = sorted(part1, key=lambda row: row[day][0])
    part2 = sorted(part2, key=lambda row: row[day][1])
    list1 = [row[0] for row in part1]
    list2 = [row[0] for row in part2]

    return (list1, list2)


ind_scores = {}
for row in timestamps:
    ind_scores[row[0]] = [0] * 25

for day in range(1, 26):
    part1, part2 = get_top_members(timestamps, day)
    for i, id in enumerate(part1):
        ind_scores[id][day - 1] += len(members) - i
    for i, id in enumerate(part2):
        ind_scores[id][day - 1] += len(members) - i


def accumulate(scores: list[int]):
    for i in range(1, len(scores)):
        scores[i] += scores[i - 1]


end = 25 # Hide unavailable days by setting this value to the amount of days unlocked
fig, ax = plt.subplots(layout="constrained")
styles = ['-', '--', '-.', ':']
for i, score_list in enumerate(ind_scores.values()):
    accumulate(score_list)
    ax.plot(range(1, 26), score_list, linestyle=styles[i % len(styles)], color=hsv_to_rgb(i * 77 / 360, 1, 0.9))
    ax.set_xbound(1, end)

ax.legend([data['name'] for _, data in members.items()], bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
plt.show()
