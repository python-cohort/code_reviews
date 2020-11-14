import requests
from bs4 import BeautifulSoup  # html parser
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

base_url = "https://www.reed.co.uk"


class HTML:
    def __init__(self, url):
        self.doc = BeautifulSoup(requests.get(url).text, "lxml")


class SitePagination:
    def __init__(self):
        pass

    @staticmethod
    def get_number_of_pages(url: str):
        result_per_page = 25
        html_doc = HTML(url).doc
        results_count = int(html_doc.find("span", class_="count").text.strip())
        print("Total number of match found: ", results_count)
        count = results_count // result_per_page
        return count if results_count % result_per_page == 0 else count + 1


class Urls:
    def __init__(
            self, keyword: str, salary: int, how_many_days_back: int, is_contract_only: bool
    ):
        self.keyword = keyword
        self.salary = salary
        self.how_many_days_back = how_many_days_back
        self.is_contract_only = is_contract_only
        with ThreadPoolExecutor() as e:
            self.urls = e.submit(self.extract_job_urls).result()

    @property
    def base_url(self):
        return (
            f"https://www.reed.co.uk/jobs/{self.normalised_keyword}-jobs?"
            f"&salaryfrom={self.salary}&contract={self.is_contract_only}&datecreatedoffset={self.how_many_days_back}"
        )

    def extract_job_urls(self):
        page_count = SitePagination.get_number_of_pages(self.base_url)
        all_job_urls = []
        for page_no in range(1, page_count + 1):
            url = (
                f"https://www.reed.co.uk/jobs/{self.normalised_keyword}-jobs?pageno={page_no}"
                f"&salaryfrom={self.salary}&contract={self.is_contract_only}&datecreatedoffset={self.normalised_date_posted}"
            )
            print(url)
            html_doc = HTML(url).doc
            job_urls = [
                base_url + item.a["href"]
                for item in html_doc.find_all("h3", class_="title")
            ]
            all_job_urls += job_urls

        print(all_job_urls, len(all_job_urls))
        return all_job_urls

    @property
    def normalised_keyword(self):
        return (
            "-".join(self.keyword.split(" ")) if " " in self.keyword else self.keyword
        )

    @property
    def normalised_date_posted(self):
        date_posted = {1: "Today", 2: "LastThreeDays", 3: "LastThreeDays"}
        return date_posted[self.how_many_days_back]


class ReedJobsScraper:
    def __init__(
            self, keyword: str, salary: int, how_many_days_back: int, is_contract_only: bool
    ):
        self.keyword = keyword
        self.urls = Urls(
            self.keyword, salary, how_many_days_back, is_contract_only
        ).urls
        self.df: pd.DataFrame = pd.DataFrame()
        # self.get_meta_data()
        # for url in self.urls:
        #     if self.is_valid_match(url):
        #         result = self.get_meta_data(url)
        #         self.df = self.df.append(result, ignore_index=True)
        # print(self.df.drop_duplicates())

        with ThreadPoolExecutor() as e:
            futures = [
                e.submit(self.get_meta_data, url)
                for url in self.urls
                if self.is_valid_match(url)
            ]
            print(len(futures))
            for future in futures:
                result = future.result()
                self.df = self.df.append(result, ignore_index=True)
        print(self.df.drop_duplicates())
        self.df.drop_duplicates().to_excel("reed_jobs.xlsx", index=False)

    def is_valid_match(self, url):
        html_doc = HTML(url).doc
        job_description = self.get_job_description(html_doc)
        return self.keyword.lower() in job_description.lower()

    def get_meta_data(self, url):
        data = {}
        html_doc = HTML(url).doc
        data["title"] = self.get_title(html_doc)
        data["advertiser"] = self.get_advertiser(html_doc)
        data["salary"] = self.get_salary(html_doc)
        data["location"] = self.get_location(html_doc)
        data["job_type"] = self.get_job_type(html_doc)
        data["post_date"] = self.get_post_date(html_doc)
        data["url"] = url
        return data

    @staticmethod
    def get_title(html_doc):
        return html_doc.find("h1").text

    @staticmethod
    def get_meta(html_doc, tag, class_: dict):
        return (
            html_doc.find(tag, class_).text
            if html_doc.find(tag, class_) is not None
            else "N/A"
        )

    def get_advertiser(self, html_doc):
        return self.get_meta(html_doc, "span", {"itemprop": "name"})

    def get_salary(self, html_doc):
        return self.get_meta(html_doc, "span", {"data-qa": "salaryLbl"})

    def get_location(self, html_doc):
        return self.get_meta(html_doc, "span", {"itemprop": "addressLocality"})

    def get_job_type(self, html_doc):
        return self.get_meta(html_doc, "span", {"itemprop": "employmentType"})

    def get_job_description(self, html_doc):
        return self.get_meta(html_doc, "span", {"itemprop": "description"})

    @staticmethod
    def get_post_date(html_doc):
        return (
            html_doc.find("span", {"itemprop": "hiringOrganization"})
                .text.split("\n")[1]
                .strip()
                .split("Posted")[1]
                .split("by")[0]
                .strip()
        )


ReedJobsScraper(
    keyword="python", salary=85000, how_many_days_back=2, is_contract_only=True
)

# search_for = ["python", "api", "aws"]
# print(7109376 * 7109376)


