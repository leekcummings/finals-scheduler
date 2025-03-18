# ---------------------------------------------------------------------------- #
#                 Simmons University Finals Schedule Generator                 #
#                                 Lee Cummings                                 #
# ---------------------------------------------------------------------------- #

def cleanDF(df):
    # Remove blank rows
    df = df.dropna()
    # Labs match the below pattern with a Course code, 3 numbers, and an L
    pattern = r"\w* \d{3}L-.*"
    df = df[~df["CourseSection"].str.contains(pattern)]
    df = df[~df["CourseSection"].str.contains("SIM 101")]
    # Remove sections from course names
    # df['CourseSection'] = df['CourseSection'].str.replace(r'-.*', '', regex=True)
    return df

import numpy as np
import pandas as pd
import regex as re

if __name__ == "__main__":
    # Import CSV of SID and Courses
    df = pd.read_csv('StudentClassDataFullSet.csv')
    ### DATAFRAME CLEANING
    df = cleanDF(df)

    ### ADD COURSE INFO TO DICTIONARIES AND ARRAY
    groupedDF = df.drop('SID', axis=1).drop_duplicates().groupby(["Time Slot"], as_index=False)
    
    # Dictionary of timeslot per course
    courseTimes = {}
    for time, frame in groupedDF:
        for index, course in frame.iterrows():
            # KEY: Course ID
            # VALUE: Timeslot
            courseTimes[course["CourseSection"]] = time[0]
    
    # Array of most popular courses (most students)
    popularCourses = df.groupby(["CourseSection"], sort=False).agg(NumStudents=("SID", "count")).sort_values("NumStudents", ascending=False).index.to_numpy()

    # Dictionary of students per course
    courseStudent = {}
    for course in popularCourses:
        # Get a df of all students in a class
        students = df.loc[df['CourseSection'] == course]["SID"]
        # KEY: Course ID
        # VALUE: Set of student
        courseStudent[course] = set(students.to_numpy().flatten())

    schedule = []
    studentTests = {}
    # For every course, ordered by popularity
    for course in popularCourses:
        if course == "NURS 417-AC":
            pass
        print(course)
        index = 0
        added = False
        students = courseStudent[course]
        while not added:
            studentConflict = False
            if index > 4:
                pass
            if index // 4 not in studentTests:
                studentTests[index // 4] = {}
            # if index is empty
            if index + 1 > len(schedule):
                for student in students:
                    if student in studentTests[index // 4] and studentTests[index // 4][student] == 2:
                        studentConflict = True
                if not studentConflict:
                    # add to schedule
                    schedule.append([course])
                    added = True
                    for student in students:
                        studentTests[index // 4][student] = studentTests[index // 4].get(student, 0) + 1
            elif len(schedule[index]) > 0:
                differentTime = False
                currentTime = courseTimes[course]
                # For every course already in slot
                for course1 in schedule[index]:
                    previousTime = courseTimes[course1]
                    if currentTime != previousTime:
                        differentTime = True
                # If all times are the same, add to slot
                if not differentTime:
                    for student in students:
                        if student in studentTests[index // 4] and studentTests[index // 4][student] == 2:
                            studentConflict = True
                    if not studentConflict:
                        # add to schedule
                        schedule[index].append(course)
                        added = True
                        for student in students:
                            studentTests[index // 4][student] = studentTests[index // 4].get(student, 0) + 1
                if not added:
                    repeatStudents = False
                    currentStudents = courseStudent[course]
                    for course1 in schedule[index]:
                        previousStudents = courseStudent[course1]
                        if len(set.intersection(currentStudents, previousStudents)) > 0:
                            repeatStudents = True
                    # If there's no repeat students, add to schedule
                    if not repeatStudents:
                        for student in students:
                            if student in studentTests[index // 4] and studentTests[index // 4][student] == 2:
                                studentConflict = True
                        if not studentConflict:
                            # add to schedule
                            schedule[index].append(course)
                            added = True
                            for student in students:
                                studentTests[index // 4][student] = studentTests[index // 4].get(student, 0) + 1
            index += 1

    for group in schedule:
        print(*group)
    print(len(schedule))