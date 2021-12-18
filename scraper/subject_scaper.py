import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

BASE_URL = "https://termmasterschedule.drexel.edu/"
SCHOOL_URL = f"{BASE_URL}webtms_du/collegesSubjects/202115?collCode=CI"
MAX_THREADS = 30


def get_subjects_links(url: str) -> tuple[list[str], RequestsCookieJar]:
    page = requests.get(url)
    cookies = page.cookies

    soup = BeautifulSoup(page.content, "html.parser")
    subject_anchors = soup.find("table", class_="collegePanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in subject_anchors], cookies


def get_courses(url: str, cookies: RequestsCookieJar) -> pd.DataFrame:
    header = ["Subject Code", "Course Number", "Instr. Type", "Instr. Method", "Section", "CRN", "Course Title",
              "Days/Time", "Instructor"]
    df = pd.read_html(url, attrs={"id": "sortableTable"})[0]
    print(url)
    print(df.columns)
    # df.to_csv(path_or_buf=url[url.find("courseList") + 11: url.find(";")] + ".csv", index=False)
    return df


def get_quarter_term_links(url: str) -> list[str]:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    term_panel_anchors = soup.find("table", class_="termPanel").findAll("a")
    return [f"{BASE_URL}{a['href']}" for a in term_panel_anchors]


def main():
    print(get_quarter_term_links(BASE_URL))
    # subject_urls, cookie = get_subjects_links(SCHOOL_URL)
    # subject_links = [f"{BASE_URL}{link}" for link in subject_urls]
    # pd.set_option('max_columns', None)
    # print(get_courses(subject_links[0], cookies=cookie))
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
