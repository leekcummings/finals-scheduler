# ---------------------------------------------------------------------------- #
#                 Simmons University Finals Schedule Generator                 #
#                                 Lee Cummings                                 #
# ---------------------------------------------------------------------------- #

import numpy as np
import pandas as pd

from excelExport import exportExcel

def cleanDF(df, courses):
    df = df.dropna()
    # Labs match the below pattern with a Course code, 3 numbers, and an L
    pattern = r'\w+ \d+L-.*'
    df = df[~df['CourseSection'].str.contains(pattern)]
    df = df[~df['CourseSection'].str.contains('SIM')]
    df = df[~df['CourseSection'].str.contains('CR')]
    # Remove classes that don't need final exams
    filter = [key for key, _ in courses.items() if courses[key]]
    df['CourseName'] = df['CourseSection'].str.extract(r'(\w* \d{3})')
    df = df[df['CourseName'].isin(filter)]
    
    return df

def createTimeslotGroups(df):
    df = df.drop('SID', axis=1).drop_duplicates().groupby(['Time Slot'], as_index=False)
    times = {}
    # Dictionary of timeslot per course
    for time, frame in df:
        for index, course in frame.iterrows():
            # KEY: Course ID
            # VALUE: Timeslot
            times[course['CourseSection']] = time[0]
    return times

def createStudentGroups(df, pop):
    courses = {}
    # Dictionary of students per course
    for course in pop:
        # Get a df of all students in a class
        students = df.loc[df['CourseSection'] == course]['SID']
        # KEY: Course ID
        # VALUE: Set of student
        courses[course] = set(students.to_numpy().flatten())
    return courses

def checkStudentConflicts(students, tests, i, max):
    for s in students:
        # If student has more than 2 tests in a day
        if s in tests[i // max] and tests[i // max][s] == 2:
            # Conflict found
            return True 
    # No conflicts
    return False 

def checkCourseTiming(times, schedule, c, i):
    currentTime = times[c]
    # For every course already in timeslot
    for otherCourse in schedule[i]:
        previousTime = times[otherCourse]
        # If times aren't the same
        if currentTime != previousTime:
            return True
    # All the same time
    return False

def checkRepeatedStudents(students, schedule, c, i):
    # Keep track of all student sets and number of students
    scheduledStudents = []
    totalStudents = 0
    # Students from unscheduled class
    scheduledStudents.append(students[c])
    totalStudents += len(students[c])

    for otherCourse in schedule[i]:
        # Students from previously scheduled classes
        scheduledStudents.append(students[otherCourse])
        totalStudents += len(students[otherCourse])
    
    # If the union of all student sets has repeats, 
    # it will be smaller than the total number of students
    if len(set.union(*scheduledStudents)) < totalStudents:
        # Repeats found
        return True
    # No repeats found
    return False

def updateStudentTests(students, tests, i, max):
    for s in students:
        tests[i // max][s] = tests[i // max].get(s, 0) + 1
    return tests

def generationStart(path, courses, maxTests, maxDays):
    # Import CSV of SID and Courses
    df = cleanDF(pd.read_csv(path), courses)
    courseTimes = createTimeslotGroups(df)

    # Array of most popular courses (most students)
    popularCourses = (df.groupby(['CourseSection'], sort=False)
                      .agg(NumStudents=('SID', 'count'))
                      .sort_values('NumStudents', ascending=False)
                      .index.to_numpy())
    courseStudent = createStudentGroups(df, popularCourses)

    # An array of exams, each index represents 1 timeslot
    schedule = []
    # To keep track of how many exams students have per day
    studentTests = {}

    for course in popularCourses:
        # The starting index for the schedule
        # Starting at 0 to ensure students get the earliest possible slot
        index = 0
        added = False
        students = courseStudent[course]

        while not added:
            # If the current day doesn't exist in studentTests
            if index // maxTests not in studentTests:
                studentTests[index // maxTests] = {}

            ### CASE 0: INDEX DOES NOT EXIST
            if index + 1 > len(schedule):
                studentConflict = checkStudentConflicts(students, studentTests, index, maxTests)
                if not studentConflict:
                    # Append course in list, as it is first item in index
                    schedule.append([course])
                    studentTests = updateStudentTests(students, studentTests, index, maxTests)
                    added = True
                else:
                    # Append a new empty list, to skip over index
                    schedule.append([])
            
            ### CASE 1: INDEX IS EMPTY
            elif len(schedule[index]) == 0:
                studentConflict = checkStudentConflicts(students, studentTests, index, maxTests)
                if not studentConflict:
                    # Append course in list, as it is first item in index
                    schedule[index].append(course)
                    studentTests = updateStudentTests(students, studentTests, index, maxTests)
                    added = True

            ### CASE 2: INDEX NOT EMPTY
            # If there are items in current index
            elif len(schedule[index]) > 0:
                differentTime = checkCourseTiming(courseTimes, schedule, course, index)
                studentConflict = checkStudentConflicts(students, studentTests, index, maxTests)
                # If all times are same or no conflicts, add to schedule
                ### CASE 2A: CLASS TIMES ARE THE SAME
                if not differentTime and not studentConflict:
                    # Add to schedule
                    schedule[index].append(course)
                    studentTests = updateStudentTests(students, studentTests, index, maxTests)
                    added = True
                ### CASE 2B: NO REPEATED STUDENTS DURING TIMESLOT
                else:
                    repeatStudents = checkRepeatedStudents(courseStudent, schedule, course, index)
                    # If no repeat students or conflicts, add to schedule
                    if not repeatStudents and not studentConflict:
                        schedule[index].append(course)
                        studentTests = updateStudentTests(students, studentTests, index, maxTests)
                        added = True

            ### CASE 2: NO ACCEPTABLE SLOTS FOUND
            # Add one to index if no slot found
            index += 1

    # Swap 1st and 3rd time slots
    # for i in range(len(schedule)):
    #     if i % 4 == 2:
    #         multiple = i // 4
    #         schedule[multiple + 2], schedule[multiple] = schedule[multiple], schedule[multiple + 2]

    ### PRINT THE RESULTS
    for index in range(len(schedule)):
        day = index // maxTests
        time = index % maxTests
        print(f'\n\nDAY {day + 1}: SLOT {time + 1}:')
        print(*sorted(schedule[index]))
    print(f'Number of slots used: {len(schedule)}')

    exportExcel(schedule, 4, "final_schedule.xlsx", False, 10)