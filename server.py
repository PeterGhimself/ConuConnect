#!/usr/bin/env python3

import json
from os import listdir
from os.path import isfile, join

from flask import Flask, request
from flask_cors import CORS

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

@app.route('/login', methods = ['POST'])
def login():
    netName = request.json.get('netName')
    password = request.json.get('password')

    print('netName: ' + str(netName),flush=True)
    print('password: ' + str(password),flush=True)

    return json.dumps({
        "ID": 27516495,
        "email": "davidhuculak5@gmail.com",
        "name": "David Hunkulak",
        "program": "Computer Science",
        "schedule": theSchedule
    })

@app.route('/rank-breaks')
def rankBreaks():
    callerStudentID = request.args.get('callerStudentID')
    selectedBreakStartTime = request.args.get('selectedBreakStartTime')
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
    #     "ID": 97516495,
    #     "email": "davidhuculak5@gmail.com",
    #     "name": "David Hunkulakz",
    #     "program": "Computer Science"
    # })
    # print(getAllStudentInfo())
    cors = CORS(app)
    app.run()
