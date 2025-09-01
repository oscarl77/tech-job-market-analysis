import time
import random
import traceback

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
            all_job_details = self._scrape_job_details(page, job_urls)

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
            links = soup.select('a[data-testid="job-item-title"]')
            for link in links:
                job_url = link.get('href')
                job_urls.append(JOB_POST_BASE_URL + job_url)
            time.sleep(time_delay)
        return job_urls

    def _scrape_job_details(self, page, job_urls):
        """
        Visit each individual job post url and extract the detailed content.
        :param page: The active Playwright object.
        :param job_urls: List of individual job urls.
        :return: List of job details for each individual job post.
        """
        time_delay = random.uniform(4,8)
        all_job_details = []
        for url in job_urls:
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector('.job-ad-wrapper', timeout=10000)
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'lxml')
                job_title = self._extract_job_content(soup, '.job-ad-display-1sxnrxf')
                company_name = self._extract_job_content(soup, '.at-listing__list-icons_company-name.job-ad-display-h9xo01')
                location_raw = self._extract_job_content(soup, '.at-listing__list-icons_location.map-trigger.job-ad-display-h9xo01')
                employment_type = self._extract_job_content(soup, '.at-listing__list-icons_work-type.job-ad-display-h9xo01')
                date_posted_raw = self._extract_job_content(soup, '.at-listing__list-icons_date.job-ad-display-h9xo01')
                salary_raw = self._extract_job_content(soup, '.at-listing__list-icons_salary.job-ad-display-7usr2j')
                full_description = self._extract_job_content(soup, '.job-ad-display-nnx1yw')
                job_data_raw = {
                    'job_title': job_title,
                    'company_name': company_name,
                    'location': location_raw,
                    'employment_type': employment_type,
                    'date_posted_raw': date_posted_raw,
                    'salary_raw': salary_raw,
                    'full_description': full_description
                }
                all_job_details.append(job_data_raw)
                print(f"Successfully scraped: {job_title} at {company_name}")
            except Exception as e:
                print(f"Could not process page {url}")
                traceback.print_exc()
            time.sleep(time_delay)
        return all_job_details

    @staticmethod
    def _extract_job_content(soup, content_selector):
        element = soup.select_one(content_selector)
        content = element.get_text(strip=True) if element else 'N/A'
        return content

if __name__ == '__main__':
    scraper = JobScraper(BASE_URL, URL_TAIL)
    scraper.run(job_title=JOB_TITLE, pages_to_scrape=PAGES_TO_SCRAPE)