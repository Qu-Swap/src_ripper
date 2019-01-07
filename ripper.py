import re
from bs4 import BeautifulSoup as soup
import scraper
import json

indexes = {0: "Short", 2: "Name", 6: "Link"}
numColumns = 11


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
        if "href" in html:
            return re.split("\"", html)[1].replace(" ", "%20").replace("&amp;", "&")
        else:
            return None


def get_subjects(filename):
    subjects = {}
    file = open(filename)

    for line in file:
        line = line.rstrip().split(',')
        subjects[line[0]] = line[1]

    return subjects


def get_courses(filename, subjects):
    courses = []
    page = soup(open(filename), "html.parser")

    # There's no identification for the course table so this is the only way
    table = page.findAll("table")[8]

    rows = table.findAll("tr")[3:]
    for row in rows:
        tds = row.findAll("td")
        if len(tds) == numColumns:
            course = {}
            for index in indexes:
                inner = tds[index].decode_contents().replace("\n", "")
                course[indexes[index]] = retrieve_info(inner, index)

            course["Subject"] = subjects[course["Short"].split()[0]]

            if check_duplicate(course, courses):
                courses.append(course)
        else:
            continue

    return courses


def get_books(courses):
    for i in range(len(courses)):
        course = courses[i]

        if course["Link"] is not None:
            course["Books"] = scraper.get_books(course["Link"])
        else:
            course["Books"] = None

        if i % 20 == 0:
            print(str(i) + "/" + str(len(courses)))


def write_json(filename, courses):
    with open(filename, "w") as write_file:
        json.dump(courses, write_file)


def main():
    courses = "Spring2019CourseGuide.html"
    subjects = "subjectPrefix.csv"

    subjects = get_subjects(subjects)
    courses = get_courses(courses, subjects)
    get_books(courses)

    for course in courses:
        print(course)

    write_json("courses.json", courses)


if __name__ == "__main__":
    main()
