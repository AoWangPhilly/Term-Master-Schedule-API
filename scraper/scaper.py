from pprint import pprint

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

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


def get_subjects_links(url: str) -> tuple[list[str], RequestsCookieJar]:
    page = requests.get(url)
    cookies = page.cookies

    soup = BeautifulSoup(page.content, "html.parser")
    subject_anchors = soup.find("table", class_="collegePanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in subject_anchors], cookies


def get_courses(url: str, cookies: str) -> pd.DataFrame:
    df = pd.read_html(url, attrs={"id": "sortableTable"})[0]
    df = clean_subjects(df)
    # df.to_csv(path_or_buf=url[url.find("courseList") + 11: url.find(";")] + ".csv", index=False)
    return df


# ;jsessionid=3CCF59D7618B76817516A1B6A1B56141

def main():
    quarters = get_quarter_term_links(BASE_URL)
    pprint(get_school_links(quarters[1]))
    # subject_urls, cookie = get_subjects_links(SCHOOL_URL)
    # print(get_courses(subject_urls[1], cookies=cookie))
    # print(cookie.values())
    # t0 = time.time()
    # # for link in subject_urls:
    # #     get_courses(f"{BASE_URL}{link}", cookie)
    # threads = min(30, len(subject_urls))
    # with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    #     executor.map(get_courses, subject_urls, repeat(cookie))
    # t1 = time.time()
    # print(f"{t1 - t0} seconds to scrape.")


if __name__ == "__main__":
    main()
