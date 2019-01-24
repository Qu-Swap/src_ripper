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
        tokens = html.split()
        return tokens[0] + " " + tokens[1]
    elif index == 2:
        # Returns the course name along with the name of the element holding the description
        return re.split("[<>]", html)[2], re.split("[\"]", html)[1]
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


def get_courses(link, subjects):
    courses = []
    page = soup(scraper.simple_get(link), "html.parser")

    # There's no identification for the course table so this is the only way
    table = page.findAll("table")[8]

    rows = table.findAll("tr")[3:]
    count = 0
    for row in rows:
        tds = row.findAll("td")
        if len(tds) == numColumns:
            course = {}
            for index in indexes:
                inner = tds[index].decode_contents().replace("\n", "")

                if index == 2:
                    info = retrieve_info(inner, index)
                    course[indexes[index]] = info[0]

                    # Pretty inefficient to not check a duplicate here, as finding the name takes a while
                    # Doesn't matter for now as the SRC course guide is pretty small and I have free time
                    head = page.find("a", {"name": info[1][1:]})

                    if head is not None:
                        # Also somewhat inefficient code, but I'm not going to change it because it would
                        # take too much effort to find something to pander towards our horseshit course guide
                        current = head.find_next("table").find_next("td").find_next("td")
                        desc = ""

                        while current.find("table") is None:
                            desc += current.text.strip("\n") + "  "
                            current = current.find_next("td")

                        course["Description"] = re.sub(" [ ]+", "  ", desc)
                    else:
                        course["Description"] = "Not available"

                else:
                    course[indexes[index]] = retrieve_info(inner, index)

            course["Subject"] = subjects[course["Short"].split()[0]]

            if check_duplicate(course, courses):
                courses.append(course)
        else:
            count += 1
            continue

        count += 1
        if count % 20 == 0:
            print("Catalog: " + str(round(100*count/len(rows))) + "%")

    return courses


def get_books(courses):
    for i in range(len(courses)):
        course = courses[i]

        if course["Link"] is not None:
            course["Books"] = scraper.get_books(course["Link"])
        else:
            course["Books"] = None

        if i % 20 == 0:
            print("Books: " + str(i) + "/" + str(len(courses)))


def write_json(filename, courses):
    with open(filename, "w") as write_file:
        json.dump(courses, write_file)


def main():
    courselink = "http://wilbur.simons-rock.edu/cg/Spring2019CourseGuide.php"
    subjects = "data/subjectPrefix.csv"

    subjects = get_subjects(subjects)
    courses = get_courses(courselink, subjects)

    get_books(courses)

    for course in courses:
        print(course)

    write_json("coursesUpdated.json", courses)


if __name__ == "__main__":
    main()
