import concurrent.futures
import re
from typing import Optional, List, Tuple

import requests
import sqlalchemy as db
from bs4 import BeautifulSoup

from app.database import engine


def get_url(subject_code: str, course_number: str) -> str:
    return f"http://catalog.drexel.edu/search/?P={subject_code}%20{course_number}"


class CourseCatalog:
    def __init__(self, subject_code: str, course_number: str):
        self.subject_code = subject_code
        self.course_number = course_number
        self.course = f"{self.subject_code} {self.course_number}"
        self.url = get_url(subject_code, course_number)
        self.page = requests.get(self.url)
        self.content = BeautifulSoup(self.page.content, "html.parser")

    def find_credit(self) -> List[float]:
        results = self.content.find("div", class_="searchresult search-courseresult")
        header = results.next_element.text
        credit = list(map(float, re.findall(r"\d+\.\d+", header)))

        return credit

    def find_course_description(self) -> str:
        course_desc = self.content.find("p", class_="courseblockdesc").text.strip()
        return course_desc

    def find_preqs(self) -> Optional[str]:
        prereq_block = self.content.find("b", text="Prerequisites:")
        if not prereq_block:
            return None
        preq = prereq_block.next_sibling.strip()
        return preq


def get_course_info(subject_code: str, course_number: str):
    course_catalog = CourseCatalog(subject_code=subject_code, course_number=course_number)
    return course_catalog.find_credit(), course_catalog.find_course_description(), course_catalog.find_preqs()


def get_unique_courses() -> List[Tuple[str, str]]:
    connection = engine.connect()
    metadata = db.MetaData()
    quarters = db.Table("quarters", metadata, autoload=True, autoload_with=engine)
    query = db.select([quarters.columns.subject_code, quarters.columns.course_number]).distinct()
    return connection.execute(query).fetchall()


def insert_course_data_to_db(subject_code: str, course_number: str):
    credit, course_desc, prereq = get_course_info(subject_code, course_number)
    connection = engine.connect()
    metadata = db.MetaData()
    courses = db.Table("courses", metadata, autoload=True, autoload_with=engine)
    query = db.insert(courses).values(subject_code=subject_code, course_number=course_number, credit=credit,
                                      course_desc=course_desc, prereq=prereq)
    connection.execute(query)


def get_all_course_info() -> None:
    courses = get_unique_courses()
    threads = min(30, len(courses))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(lambda p: insert_course_data_to_db(*p), courses)


if __name__ == "__main__":
    get_all_course_info()
