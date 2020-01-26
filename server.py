#!/usr/bin/env python3

import json
from os import listdir
from os.path import isfile, join

from flask import Flask, request, abort
from flask_cors import CORS

import findOverlappingFreeTime
import scrapeschedule

app = Flask(__name__)

theSchedule =  [
    [
        {
            "course": "COMP 445",
            "startTime": "13:15",
            "endTime": "14:30"
        }
    ],
    [
        {
            "course": "COMP 425",
            "startTime": "15:30",
            "endTime": "17:30"
        },
        {
            "course": "COMP 425",
            "startTime": "17:45",
            "endTime": "20:15"
        }
    ],
    [
        {
            "course": "COMP 445",
            "startTime": "11:10",
            "endTime": "13:00"
        },
        {
            "course": "COMP 445",
            "startTime": "13:15",
            "endTime": "14:30"
        }
    ],
    [
        {
            "course": "ENCS 393",
            "startTime": "17:45",
            "endTime": "20:15"
        }
    ],
    []
]

def timeStringToHourFrac(timeString):
    [ hours, minutes ] = timeString.split(":")
    return int(hours) + (int(minutes) / 60)

def courseBlockToTuple(courseBlock):
    return (timeStringToHourFrac(courseBlock["startTime"]), timeStringToHourFrac(courseBlock["endTime"]))

def convertSchedule(schedule):
    return list(map(lambda dayOfWeek: list(map(lambda courseBlock: courseBlockToTuple(courseBlock), dayOfWeek)), schedule))

def ampmConverter(timeStr):
    timePortion = timeStr[:-2]
    [ hourStr, minStr ] = timePortion.split(":")

    if "AM" in timeStr.upper():
        return f"{hourStr}:{minStr}"
    elif "PM" in timeStr.upper():
        if(int(hourStr) < 12):
            return f"{int(hourStr) + 12}:{minStr}"
        else:
            return f"{hourStr}:{minStr}"


@app.route('/login', methods = ['POST'])
def login():
    netName = request.json.get('netName')
    password = request.json.get('password')

    print('netName: ' + str(netName),flush=True)
    # print('password: ' + str(password),flush=True)

    (user_info, weekdays) = scrapeschedule.scrape_user_data(netName, password)

#     {'netname': 'd_hucul', 'email': 'davidhuculak5@gmail.com', 'program': 'Bachelor of Computer Science', 'id': '27516495', 'name': 'David Huculak'}
# [['COMP 445,1:15PM - 2:30PM'], ['COMP 425,5:45PM - 8:15PM', 'COMP 425,3:30PM - 5:30PM'], ['COMP 445,1:15PM - 2:30PM', 'COMP 445,11:10AM - 1:00PM'], ['ENCS 393,5:45PM - 8:15PM'], []]


    # print(user_info)
    # print(weekdays)

    mySchedule = []
    for weekday in weekdays:
        newWeekday = []
        for courseBlock in weekday:
            [ courseCode, timeRangeStr ] = courseBlock.split(",")
            timeRangeStr = timeRangeStr.replace(" ", "")
            [ startTimeStr, endTimeStr ] = timeRangeStr.split("-")
            newWeekday.append({
                "course": courseCode,
                "startTime": ampmConverter(startTimeStr),
                "endTime": ampmConverter(endTimeStr)
            })
            newWeekday.sort(key=lambda x: timeStringToHourFrac(x["startTime"]), reverse=False)
        mySchedule.append(newWeekday)

    # print(json.dumps(mySchedule, indent=4, sort_keys=True))

    myStudentInfo = {
        "ID": user_info["id"],
        "email": user_info["email"],
        "name": user_info["name"],
        "program": user_info["program"],
        "schedule": mySchedule
    }

    saveStudentInfo(myStudentInfo)
    return json.dumps(myStudentInfo)

@app.route('/rank-breaks')
def rankBreaks():

    selectedBreak = request.args.get('selectedBreak')
    callerStudentID = request.args.get('callerStudentID')

    interval = tuple(map(lambda val: int(val), selectedBreak.split(":")))

    allStudentInfo = getAllStudentInfo();
    callerSchedule = None
    for studentInfo in allStudentInfo:
        if str(studentInfo["ID"]) == str(callerStudentID):
            callerSchedule = studentInfo["schedule"]

    print(callerSchedule)
    
    if callerSchedule is None:
        abort(500)

    otherStudentInfo = list(filter(lambda studentInfo: not (str(studentInfo["ID"]) == str(callerStudentID)), allStudentInfo))

    print(otherStudentInfo)

    results = []
    for studentInfo in otherStudentInfo:
        convertedSchedule = convertSchedule(studentInfo["schedule"])
        print(convertedSchedule)
        overlaps = findOverlappingFreeTime.findOverlappingFreeTime(interval, convertedSchedule)
        print(overlaps)
        if len(overlaps) > 0:
            results.append({ "studentInfo": studentInfo })

    return json.dumps(results)

    
    
    programFilter = request.args.get('programFilter')
    subjectFilter = request.args.get('subjectFilter')
    courseFilter = request.args.get('courseFilter')
    requireCommonCourses = request.args.get('filterByCommonCourses')
    requireSameCourseBeforeBreak = request.args.get('requireSameCourseBeforeBreak')
    requireSameCourseAfterBreak = request.args.get('requireSameCourseAfterBreak') 
    studentIDFilter = request.args.get('studentIDFilter')
    rankByProgramSimilarity = request.args.get('rankByProgramSimilarity')
    rankByBreakOverlap = request.args.get('rankByBreakOverlap')

    print('callerStudentID: ' + str(callerStudentID))
    print('selectedBreakStartTime: ' + str(selectedBreakStartTime))
    print('programFilter: ' + str(programFilter))
    print('subjectFilter: ' + str(subjectFilter))
    print('courseFilter: ' + str(courseFilter))
    print('requireCommonCourses: ' + str(requireCommonCourses))
    print('requireSameCourseBeforeBreak: ' + str(requireSameCourseBeforeBreak))
    print('requireSameCourseAfterBreak: ' + str(requireSameCourseAfterBreak))
    print('studentIDFilter: ' + str(studentIDFilter))
    print('rankByProgramSimilarity: ' + str(rankByProgramSimilarity))
    print('rankByBreakOverlap: ' + str(rankByBreakOverlap))

    return json.dumps([
        {
            "studentInfo": {
                "ID": 27516495,
                "email": "davidhuculak5@gmail.com",
                "name": "David Hunkulak",
                "program": "Computer Science",
                "schedule": theSchedule
            },
            "rankScores": {
                "programSimilarity": 4.5,
                "breakOverlap": 1.5
            }
        },
        {
            "studentInfo": {
                "ID": 27516495,
                "email": "davidhuculak5@gmail.com",
                "name": "David Hunkulak2",
                "program": "Computer Sciences",
                "schedule": theSchedule
            },
            "rankScores": {
                "programSimilarity": 3,
                "breakOverlap": 0.5
            }
        },
        {
            "studentInfo": {
                "ID": 27516495,
                "email": "davidhuculak5@gmail.com",
                "name": "David Hukalunk 3",
                "program": "Mathstertisticalation",
                "schedule": theSchedule
            },
            "rankScores": {
                "programSimilarity": 4.2,
                "breakOverlap": 1
            }
        }
    ])

def saveStudentInfo(studentInfo):
    with open('data/' + str(studentInfo["ID"]) + '.json', 'w') as f:
        f.write(json.dumps(studentInfo))

def getAllStudentInfo():
    allfiles = [f for f in listdir('data/') if isfile(join('data/', f))]
    fileContents = []
    for fileName in allfiles:
        with open('data/' + fileName) as f:
            fileContents.append(json.loads(f.read()))
    return fileContents

if __name__ == "__main__":
    # saveStudentInfo({
    #     "ID": 27516495,
    #     "email": "davidhuculak5@gmail.com",
    #     "name": "David Hunkulakz",
    #     "program": "Computer Science",
    #     "schedule": theSchedule
    # })
    # print(getAllStudentInfo())
    # allStudentInfo = getAllStudentInfo();
    # print(allStudentInfo)
    # schedule = convertSchedule(allStudentInfo[0]["schedule"])
    # print(schedule)
    # print(findOverlappingFreeTime.findOverlappingFreeTime((1, 17.5, 18), schedule))
    cors = CORS(app)
    app.run()
