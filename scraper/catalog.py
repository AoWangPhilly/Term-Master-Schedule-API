import re
from typing import Optional, List

import requests
from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    course_catalog = CourseCatalog("HNRS", "T480")
    print(course_catalog.find_course_description())
    print(course_catalog.find_preqs())
    print(course_catalog.find_credit())
