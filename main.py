from json import load
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from colorsys import hsv_to_rgb
from math import ceil

with open('data.json') as f:
    json = load(f)

if 'members' not in json:
    print('Loaded json is not a valid leaderboard file.')
    exit()

members = json['members']

members_timestamps = []
for member_id, member_data in members.items():
    completion_data = member_data['completion_day_level']
    member_data = [member_id] + [(None, None)] * 25
    for day, day_data in completion_data.items():
        part1_ts, part2_ts = day_data['1']['get_star_ts'], day_data.get('2', None)
        if part2_ts is not None:
            part2_ts = part2_ts['get_star_ts']
        member_data[int(day)] = (part1_ts, part2_ts)
    members_timestamps.append(member_data)


def get_top_members(members_data: list[list], day: int) -> tuple[list[tuple[str, int]], list[str]]:
    part1 = filter(lambda member_data: member_data[day][0], members_data)
    part2 = filter(lambda member_data: member_data[day][1], members_data)
    part1 = sorted(part1, key=lambda row: row[day][0])
    part2 = sorted(part2, key=lambda row: row[day][1])
    list1 = [(row[0], row[day][0]) for row in part1]
    list2 = [(row[0], row[day][1]) for row in part2]

    return (list1, list2)


ind_scores = {}
for row in members_timestamps:
    ind_scores[row[0]] = []

for day in range(1, 26):
    part1, part2 = get_top_members(members_timestamps, day)
    for i, pair in enumerate(part1):
        id, timestamp = pair
        ind_scores[id].append((len(members) - i, timestamp))
    for i, pair in enumerate(part2):
        id, timestamp = pair
        ind_scores[id].append((len(members) - i, timestamp))

for id in ind_scores:
    ind_scores[id] = sorted(ind_scores[id], key=lambda pair: pair[1])


def accumulate_points(pts_ts_pairs: list[tuple[int, int]]):
    for i in range(1, len(pts_ts_pairs)):
        prev_points, _ = pts_ts_pairs[i - 1]
        extra_points, current_timestamp = pts_ts_pairs[i]
        pts_ts_pairs[i] = (prev_points + extra_points, current_timestamp)


def get_beginning_of_dec():
    today = dt.datetime.today()
    year = today.year if today.month == 12 else today.year - 1
    return dt.datetime(year, 12, 1, 0, 0, 0, 0)


def add_intermediate_timestamps(pts_ts_pairs: list[tuple[int, int]]):
    pts_ts_pairs.insert(0, (0, int(get_beginning_of_dec().timestamp())))
    i = 1
    while i < len(pts_ts_pairs):
        previous_points, _ = pts_ts_pairs[i - 1]
        _, timestamp = pts_ts_pairs[i]
        pts_ts_pairs.insert(i, (previous_points, timestamp - 1))
        i += 2


fig, ax = plt.subplots(layout="constrained")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=90)
styles = ['-', '--', '-.', ':']
hue_interval = 360 / ceil(len(ind_scores) / len(styles))

for i, pts_ts_pairs in enumerate(ind_scores.values()):
    if not pts_ts_pairs:
        continue

    accumulate_points(pts_ts_pairs)
    add_intermediate_timestamps(pts_ts_pairs)
    total_points, timestamps = zip(*pts_ts_pairs)
    timestamps = list(map(dt.datetime.fromtimestamp, timestamps))
    style = styles[i % len(styles)]
    hue = i // len(styles) * hue_interval / 360
    ax.plot(
        timestamps, total_points,
        linestyle=style,
        color=hsv_to_rgb(hue, 1, 1)
    )

ax.legend([data['name'] for _, data in members.items()], bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
plt.show()
