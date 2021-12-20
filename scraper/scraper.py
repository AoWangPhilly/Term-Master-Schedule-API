"""
Term Master Schedule Scraper
----------------------------
The module scrapes Drexel's TMS from Fall Quarter 20-21 to Summer Quarter 21-22
in a little over a minute. It'll grab all subjects from each available school,
taking the subject_code, course_number, instruction type and method, section,
crn, course title, days / time, and instructor saving it all to a PostgreSQL db.
"""

import concurrent.futures
import time
from typing import List, Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.database import engine
from cleaner import clean_subjects

BASE_URL = "https://termmasterschedule.drexel.edu/"


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
    """Get subject's link in specific school"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    subject_anchors = soup.find("table", class_="collegePanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in subject_anchors]


def get_courses(term: int, coll_code: str, url: str) -> None:
    """Reads in the subject's table and cleans it up"""
    df = pd.read_html(url, attrs={"id": "sortableTable"})[0]
    df = clean_subjects(df)
    df["term"] = term
    df["coll_code"] = coll_code
    df.to_sql("quarters", engine, if_exists="append", index=False)


def get_course_details_urls(url: str) -> List[str]:
    """Takes all CRN links used to find details about the specific course"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    a_tags = soup.find("table", id="sortableTable").findAll("a")
    hrefs = [f"{BASE_URL}{a['href']}" for a in a_tags]
    return hrefs


def get_course_details(url: str) -> dict[str, Any]:
    """Grab crn, credits, max_enroll, enroll, course description, and prereqs of a course"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    crn = int(soup.find("td", text=r"CRN").findNext("td").text)
    credits = float(soup.find("td", text="Credits").findNext("td").text.strip())
    max_enroll = int(soup.find("td", text="Max Enroll").findNext("td").text)
    enroll = soup.find("td", text="Enroll").findNext("td").text.strip()
    if enroll == "CLOSED":
        enroll = max_enroll
    else:
        enroll = int(enroll)

    course_desc = soup.find("div", class_="courseDesc").text.strip()

    prereqs = soup.find("b", text="Pre-Requisites:").findParent().findAll("span")
    prereqs = ' '.join([prereq.text.strip() for prereq in prereqs])

    details = {"crn": crn,
               "credits": credits,
               "max_enroll": max_enroll,
               "enroll": enroll,
               "course_desc": course_desc,
               "prereqs": prereqs}
    return details


def get_all_course_details(url: str) -> pd.DataFrame:
    """Gets the course details of a subject page and create a dataframe"""
    urls = get_course_details_urls(url)
    output_df = pd.DataFrame(columns=["crn", "credits", "max_enroll", "enroll", "course_desc", "prereqs"])

    for url in urls:
        output_df = output_df.append(get_course_details(url), ignore_index=True)
    return output_df


def save_subjects(school_url: str) -> None:
    """Using threads to grab subjects in school concurrently to speed up scraping"""
    coll_code = school_url[school_url.find("collCode") + len("collCode") + 1:]
    term = int(school_url[school_url.find("collegesSubjects") + len("collegesSubjects") + 1: school_url.find(";")])
    urls = get_subjects_links(school_url)
    args = ((term, coll_code, url) for url in urls)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda p: get_courses(*p), args)


def save_subjects_per_term(url) -> None:
    """Get all subjects in all 8 terms"""
    quarters = get_quarter_term_links(url=url)
    for quarter in quarters:
        schools = get_school_links(url=quarter)
        for school in schools:
            save_subjects(school_url=school)


def main():
    t0 = time.time()
    save_subjects_per_term(BASE_URL)
    t1 = time.time()
    print(f"{t1 - t0} seconds to scrape.")


if __name__ == "__main__":
    main()
