import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from src.config import *

class JobScraper:
    """
    This class is responsible for scraping job posting websites.

    Parameters
    ----------
    base_url : str
        User supplied base url of the website to be scraped.
    """

    def __init__(self, base_url, url_tail=None):
        self.base_url = base_url
        self.url_tail = url_tail
        self.headers = {'User-Agent': 'My Job Scraper Project'}

    def run(self, job_title, pages_to_scrape=1):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page_urls = self._generate_page_urls(job_title, pages_to_scrape)
            job_urls = self._get_job_urls(page, page_urls)

    def _generate_page_urls(self, job_title, pages_to_scrape):
        """
        Generate a list of search result page urls.
        :param job_title: Job title to search.
        :param pages_to_scrape: Number of pages to scrape.
        :return: List of page urls.
        """
        formatted_job_title = job_title.replace(' ', '-').lower()
        url_template = self.base_url + formatted_job_title + self.url_tail
        page_urls = []
        for i in range(1, pages_to_scrape+1):
            page_url = url_template.format(page_number=i)
            page_urls.append(page_url)
        return page_urls

    def _get_job_urls(self, page, page_urls):
        """
        Visit each search page and extract individual job post urls.
        :param page: The active Playwright object.
        :param page_urls: List of page urls.
        :return: List of individual job post urls.
        """
        time_delay = random.uniform(2,4)
        search_page_visited = False
        job_urls = []
        for url in page_urls:
            page.goto(url, timeout=60000)
            if not search_page_visited:
                cookie_button = page.get_by_role("button", name="Just Necessary")
                cookie_button.wait_for(timeout=5000)
                cookie_button.click()
                search_page_visited = True
            page.wait_for_selector(ARTICLE_CLASS, timeout=10000)
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'lxml')
            links = soup.select(f'{ARTICLE_CLASS} a[href]')
            for link in links:
                job_url = link.get('href')
                job_urls.append(job_url)
            time.sleep(time_delay)
        return job_urls

    def _scrape_job_details(self, page, job_urls):
        """
        Visit each individual job post url and extract the detailed content.
        :param page: The active Playwright object.
        :param job_urls: List of individual job urls.
        :return:
        """
        time_delay = random.uniform(4,8)
        all_job_details = []
        for url in job_urls:
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector(ARTICLE_CLASS, timeout=10000)
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'lxml')
                # TODO
                time.sleep(time_delay)
            except Exception as e:
                # TODO
                pass


if __name__ == '__main__':
    scraper = JobScraper(BASE_URL, URL_TAIL)
    scraper.run(job_title=JOB_TITLE, pages_to_scrape=PAGES_TO_SCRAPE)



