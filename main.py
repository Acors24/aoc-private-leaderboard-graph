from json import load
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from datetime import date
from datetime import datetime
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

all_timestamps = set()
for id in ind_scores:
    ind_scores[id] = sorted(ind_scores[id], key=lambda pair: pair[1])
    all_timestamps |= set(map(lambda pair: pair[1], ind_scores[id]))

all_timestamps = sorted(list(all_timestamps))


def accumulate(pts_ts_pairs: list[tuple[int, int]]):
    for i in range(1, len(pts_ts_pairs)):
        prev_points, _ = pts_ts_pairs[i - 1]
        extra_points, current_timestamp = pts_ts_pairs[i]
        pts_ts_pairs[i] = (prev_points + extra_points, current_timestamp)


today = date.today()
if today.month == 12 and today.day < 25:
    last_day = today.day
else:
    last_day = 25


def fill_missing(pts_ts_pairs: list[tuple[int, int]]):
    year = today.year if today.month == 12 else today.year - 1
    beginning_of_december = datetime(year, 12, 1, 0, 0, 0, 0)
    current_points = 0
    point_index = -len(pts_ts_pairs)
    pts_ts_pairs.insert(0, (current_points, int(beginning_of_december.timestamp())))
    for ts in all_timestamps:
        if ts in map(lambda pair: pair[1], pts_ts_pairs):
            current_points = pts_ts_pairs[point_index][0]
            point_index += 1
        else:
            pts_ts_pairs.insert(len(pts_ts_pairs) + point_index, (current_points, ts))


def timestamp_to_readable(ts: int) -> str:
    return datetime.fromtimestamp(ts).isoformat()


fig, ax = plt.subplots(layout="constrained")
styles = ['-', '--', '-.', ':']
hue_interval = 360 / ceil(len(ind_scores) / len(styles))
for i, pts_ts_pairs in enumerate(ind_scores.values()):
    accumulate(pts_ts_pairs)
    fill_missing(pts_ts_pairs)
    try:
        total_points, timestamps = zip(*pts_ts_pairs)
    except ValueError as e:
        print(e, i, pts_ts_pairs)
        continue
    timestamps = list(map(timestamp_to_readable, timestamps))
    style = styles[i % len(styles)]
    hue = i // len(styles) * hue_interval / 360
    ax.plot(
        timestamps, total_points,
        linestyle=style,
        color=hsv_to_rgb(hue, 1, 1)
    )

ax.legend([data['name'] for _, data in members.items()], bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
plt.xticks(rotation=90)
plt.show()
