import concurrent.futures
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.database import engine
from cleaner import clean_subjects

BASE_URL = "https://termmasterschedule.drexel.edu/"
SCHOOL_URL = f"{BASE_URL}webtms_du/collegesSubjects/202115?collCode=CI"
MAX_THREADS = 30


def get_quarter_term_links(url: str) -> list[str]:
    """Get links for quarter term courses on the front page"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    term_panel_anchors = soup.find("table", class_="termPanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in term_panel_anchors]


def get_school_links(url: str) -> list[str]:
    """Get the available school links on the side for each quarter term"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    school_panel = soup.find("div", id="sideLeft").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in school_panel]


def get_subjects_links(url: str) -> list[str]:
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    subject_anchors = soup.find("table", class_="collegePanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in subject_anchors]


def get_courses(coll_code: str, url: str) -> None:
    df = pd.read_html(url, attrs={"id": "sortableTable"})[0]
    df = clean_subjects(df)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    term_name = soup.find(text=re.compile(r"^Schedule for.*"))
    term_name = term_name[term_name.find("(") + 1: term_name.find(")")]
    df["term"] = int(term_name)
    # df["id"] = df["crn"] + df["term"]
    df["coll_code"] = coll_code
    df.to_sql("quarters", engine, if_exists="append", index=False)
    # return df


def save_subjects(school_url: str) -> None:
    coll_code = school_url[school_url.find("collCode") + 9:]
    urls = get_subjects_links(school_url)
    threads = min(30, len(urls))
    args = ((coll_code, url) for url in urls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(lambda p: get_courses(*p), args)


def save_subjects_per_school(term_url: str) -> None:
    schools = get_school_links(term_url)
    for school in schools:
        save_subjects(school_url=school)


def save_subjects_per_term() -> None:
    quarters = get_quarter_term_links(BASE_URL)
    for quarter in quarters:
        save_subjects_per_school(term_url=quarter)


def main():
    t0 = time.time()
    save_subjects_per_term()
    t1 = time.time()
    print(f"{t1 - t0} seconds to scrape.")

    # quarters = get_quarter_term_links(BASE_URL)
    # fall = quarters[0]
    #
    # schools_in_fall = get_school_links(fall)
    # ci = schools_in_fall[5]
    # subjects_in_ci = get_subjects_links(ci)
    # print(get_courses(subjects_in_ci[0]))


if __name__ == "__main__":
    main()
