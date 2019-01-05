import re

indexes = {0: "Short", 2: "Name", 6: "Books"}


def check_duplicate(course, courses):
    for c in courses:
        if course["Name"] == c["Name"]:
            return False

    return True


def retrieve_info(html, index):
    if index == 0:
        return html
    elif index == 2:
        return re.split("[<>]", html)[2]
    elif index == 6:
        if "HREF" in html:
            return re.split("\"", html)[1].replace(" ", "%20")
        else:
            return


def get_subjects(filename):
    subjects = {}
    file = open(filename)

    for line in file:
        line = line.rstrip().split(',')
        subjects[line[0]] = line[1]

    return subjects


def get_courses(filename, subjects):
    courses = []
    page = open(filename, "rb")

    flag = False
    index = 0
    course = {}
    for line in page:
        line = line.decode("utf-8", "ignore").rstrip()

        # Stupid breakpoints because the formatting of the course guide sucks
        if line == "<TD class='x2'>":
            flag = True
        elif flag and "</TD>" in line:
            if index in indexes:
                course[indexes[index]] = retrieve_info(line[:-5], index)

            index += 1
        elif flag and "</TR>" in line:
            flag = False
            index = 0

            if check_duplicate(course, courses):
                course["Subject"] = subjects[course["Short"].split(' ')[0]]
                courses.append(course)
            course = {}
        elif "<b>Cultural Perspectives" in line:
            break

    return courses


def main():
    courses = "Spring2019CourseGuide.html"
    subjects = "subjectPrefix.csv"

    subjects = get_subjects(subjects)
    courses = get_courses(courses, subjects)

    print(subjects)
    for course in courses:
        print(course)


if __name__ == "__main__":
    main()
