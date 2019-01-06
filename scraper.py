import re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as soup


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print("Error during requests to {0} : {1}".format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def get_html(url):
    raw = simple_get(url)

    return soup(raw, "html.parser")


def get_books(url):
    books = []
    html = get_html(url)

    booklist = html.findAll("div", class_="container csTPad21")

    for book in booklist:
        newbook = {}

        infotable = book.find("table", class_="cmTableBkInfo")
        if infotable is None:
            alt = re.split("[<>]", str(book.find("h3", class_="name")))[2]

            if alt == "No Text Required For This Course":
                return None
            return alt

        rows = infotable.findAll("tr");

        for row in rows:
            elements = row.findAll("td")
            if len(elements) != 2:
                continue

            key = re.split('[<>]', str(elements[0]))[2][:-2]
            val = re.split('[<>]', str(elements[1]).replace("<span style=\"display: none;\">bogus</span>", ""))[2]

            newbook[key] = val

        name = book.find("h2", class_="p0m0 h3")
        newbook["Name"] = re.split("[<>]", str(name))[2]

        if "Required" in str(book):
            newbook["Requirement"] = "Required"
        # I haven't found a single listed book as not required
        else:
            newbook["Requirement"] = "Optional"

        books.append(newbook)

    return books
