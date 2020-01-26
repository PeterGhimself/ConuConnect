def findAllOverlappingFreeTime(interval, schedules):
    return [
        nothingPlannedAtIntervalInSchedule(interval, schedule)
        for schedule in schedules
    ]

def findOverlappingFreeTime(interval, schedule,
                                       front_buffer=0, back_buffer=0,
                                       min_overlap=0.25):
    day, starttime, endtime = interval

    day_schedule = schedule[day]

    earliest_start = min(starttime for (starttime,_) in day_schedule)
    latest_end = max(endtime for (_,endtime) in day_schedule)

    all_possible_breaks = \
        [(earliest_start-front_buffer,earliest_start)] + \
        [(e1,s2) for (s1,e1),(s2,e2) in zip(schedule[day], schedule[day][1:])] + \
        [(latest_end,latest_end+back_buffer)]

    result = []
    for (s,e) in all_possible_breaks:
        if e-s < min_overlap:
            continue
        overlap = max_overlap((s,e), (starttime, endtime))
        if overlap is not None:
            result.append(overlap)
    return result

# assume s1 lexicographically <= s2
def max_overlap(interval1, interval2):
    s1, e1 = interval1
    s2, e2 = interval2
    earliest_end = min(e1,e2)
    latest_start = max(s1,s2)

    if earliest_end - latest_start > 0:
        return (latest_start, earliest_end)

schedule = [
    [(9,12),(15,18)],
    [(8,10),(12,14),(14,15)],
    [(9,11),(11,13),(13.5,14.5)],
    [(8.5,9.5),(9.5,10.5),(1,2.5)],
    [(6,8),(10,12),(16,17),(17,18)]
]

print("schedule: [")
for day in schedule:
    print(f"  {day}")
print("]")
interval = 4, 7, 18
day, starttime, endtime = interval
print()
print(f"find availabilities on day: {day}, between {starttime} and {endtime}")
print(f"result: {findOverlappingFreeTime(interval, schedule)}")
