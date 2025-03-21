# Simmons University Finals Scheduler

Finals season is stressful enough, but getting late finals exam schedules only adds to the stress.

The Computer Science department at Simmons University started a challenge in 2023 to create an application that can produce a final exam schedule that meets the following requirements:

## Requirements

0. Each exam date is split into 4 slots
1. No students may have 2 exams during the same period
2. No student may have more than 2 exams in 1 day

**The Goal:** Fit the final exam schedule in the fewest number of days!

### Example input .csv file:

The input file should contain 3 required columns, `SID`, `CourseSection`, and `Time Slot` in any order. For each SID, all the courses that student takes must be listed.

| SID | CourseSection | Time Slot |
| :---: | :---: | :---: |
| 0001 | CS 101-01 | M/W/F 11:00 AM - 12:20 PM |
| 0001 | CS 102-01 | T/Th 12:30 PM - 1:50 PM |
| ... | ... | ... |

## Future Improvements

With more information about each each course, a more accurate and concise schedule could be created. Important information to consider would be:

- Professor schedules, so each professor could attend their classes' final exams
- Which courses will *not* have final exams
- In person vs. online courses, as online courses will have online finals
