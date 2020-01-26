import json
from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)

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
        "program": "Computer Science"
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
                "program": "Computer Science"
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
                "program": "Computer Sciences"
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
                "program": "Mathstertisticalation"
            },
            "rankScores": {
                "programSimilarity": 4.2,
                "breakOverlap": 1
            }
        }
    ])

if __name__ == "__main__":
    cors = CORS(app)
    app.run()

#     - Support filtering by the following criteria:
#     - Specific program(s) e.g. computer science, software eng   
#     - Specific subject(s) e.g. COMP, ENCS, MATH
#     - Specific course(s) e.g. COMP 248, ENGR 233
#     - Shares common course(s)
#     - Same course immediately before/after break
#     - Specific person(s)
#   - Support ranking by the following criteria:
#     - Program similarity composite score (common courses / same program)
#     - Break overlap percentage
#     - Specific person(s) / friends