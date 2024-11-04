import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

button_class_name = "Button-module__button_wd4He Button-module__button_theme_secondary_KSxrX Button-module__button_wide_true_zb7V3"

# parser for t-pulse main page news
class PulseMainNewsParser:
    def __init__(self, path_to_save="data/main_news"):
        self.path_to_save = path_to_save
        self.cols_names = ["title", "source_url", "date", "text", "refs"]

    def load_page(self, driver, iterations=150):
        for i in range(iterations):
            time.sleep(np.random.randint(1, 5))
            try:
                element = driver.find_element(By.CSS_SELECTOR, f"button[class='{button_class_name}']")
            except NoSuchElementException:
                return
            element.click()
            time.sleep(np.random.randint(2, 8))

    def main_page_refs(self, page_code):
        page_tree = BeautifulSoup(page_code, "html.parser") 
        news_refs = []
        post_class = "ResearchCatalogNews__container_mnkTT"
        news_elements = page_tree.find_all("div", {"data-qa-file": "ResearchCatalogNews", "class": post_class})
        for news_post in news_elements:
            href = news_post.a.get("href")
            news_refs.append(f"https://www.tbank.ru{href}")
        return news_refs
    
    def get_news_features(self, page_url):
        driver = webdriver.Chrome()
        driver.get(page_url)
        time.sleep(np.random.randint(2, 8))
        news_page = driver.page_source
        driver.close()
        time.sleep(np.random.randint(3, 6))
        news_tree = BeautifulSoup(news_page, "html.parser")
        if news_tree.find("h1", "pulse-postpage__b-+eQ4b") is not None:
            news_title = news_tree.find("h1", "pulse-postpage__b-+eQ4b").get_text()
        else:
            return [None for _ in range(5)]
        news_text = ""
        text_tree = news_tree.find("div", {"class": "pulse-postpage__h-+eQ4b"}).find_all(['p', 'h1', 'li'])
        for tag in text_tree:
            news_text += tag.get_text() + "\n"
        news_date = news_tree.find("div", "pulse-postpage__ciQY5O").get_text()
        hrefs_elements = news_tree.find("div", {"class": "pulse-postpage__h-+eQ4b"}).find_all(['a'])
        news_refs = [href_element.get("href") for href_element in hrefs_elements]
        return [news_title, page_url, news_date, news_text, news_refs]

    def parse_main_page(self, batch_size=256):
        driver = webdriver.Chrome()
        driver.get("https://www.tbank.ru/invest/research/all/")
        time.sleep(np.random.randint(3, 9))
        self.load_page(driver)
        main_page = driver.page_source
        time.sleep(np.random.randint(2, 5))
        driver.close()
        news_refs = self.main_page_refs(main_page)
        print("refs count: ", len(news_refs))
        news_dl = DataLoader(news_refs, batch_size=batch_size)
        for i, news_batch in enumerate(news_dl):
            data = []
            for news_ref in tqdm(news_batch, desc="progress: "):
                data.append(self.get_news_features(news_ref))
            df = pd.DataFrame(data, columns=self.cols_names)
            df.to_parquet(f"{self.path_to_save}/data_{i}.parquet")

# parser for t-pulse companies news
class PulseCompanyNewsParser:
    def __init__(self, path_to_save="data/company_news"):
        self.path_to_save = path_to_save
        self.cols_names = ["title", "source_url", "date", "text", "refs", "news_class", "company_name"]

    def get_news_features(self, page_url):
        driver = webdriver.Chrome()
        driver.get(page_url)
        time.sleep(np.random.randint(2, 8))
        news_page = driver.page_source
        driver.close()
        news_tree = BeautifulSoup(news_page, "html.parser")
        if news_tree.find("h1", "pulse-postpage__b-+eQ4b") is not None:
            news_title = news_tree.find("h1", "pulse-postpage__b-+eQ4b").get_text()
        else:
            return [None for _ in range(5)]
        news_text = ""
        text_tree = news_tree.find("div", {"class": "pulse-postpage__h-+eQ4b"}).find_all(['p', 'h1', 'li'])
        for tag in text_tree:
            news_text += tag.get_text() + "\n"
        news_date = news_tree.find("div", "pulse-postpage__ciQY5O").get_text()
        hrefs_elements = news_tree.find("div", {"class": "pulse-postpage__h-+eQ4b"}).find_all(['a'])
        if len(hrefs_elements):
            news_refs = [href_element.get("href") for href_element in hrefs_elements]
        else:
            news_refs = None
        return [news_title, page_url, news_date, news_text, news_refs]
    
    def load_page(self, driver, iterations=70):
        for i in range(iterations):
            time.sleep(np.random.randint(2, 5))
            driver.execute_script("window.scrollBy(0, 1200);")

    def company_refs(self, company_page):
        news_refs = []
        company_tree = BeautifulSoup(company_page, "html.parser")
        hrefs_elements = company_tree.find_all("div", {"data-qa-file": "PulseNewsByTicker"})
        sector_class = "SecurityHeader__panel_itBzT SecurityHeader__desktop_dL7RD"
        news_class = company_tree.find("div", {"class": sector_class, "data-qa-file": "SecurityHeader"}).get_text()[6:]
        for href_element in hrefs_elements:
            href = href_element.find("a", {"data-qa-file":"PulsePost", "data-qa-type":"uikit/link"}).get("href")
            news_refs.append(f"https://www.tbank.ru{href}")
        return news_refs, news_class

    def parse_company(self, company_url, batch_size=256):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(company_url)
        time.sleep(np.random.randint(3, 9))
        self.load_page(driver)
        main_page = driver.page_source
        time.sleep(np.random.randint(2, 5))
        driver.close()
        news_refs, news_class = self.company_refs(main_page)
        start_index = company_url.find("stocks/")
        end_index = company_url.find("/news")
        company_name = company_url[start_index+7:end_index]
        print(f"{company_name} refs count: {len(news_refs)}")
        news_dl = DataLoader(news_refs, batch_size=batch_size)
        for i, news_batch in enumerate(news_dl):
            data = []
            for news_ref in tqdm(news_batch, desc="progress: "):
                data.append(self.get_news_features(news_ref) + [news_class, company_name])
            df = pd.DataFrame(data, columns=self.cols_names)
            df.to_parquet(f"{self.path_to_save}/data_{company_name}_{i}.parquet")

    def parse_companies(self, company_urls, batch_size=256):
        for url in company_urls:
            self.parse_company(url, batch_size=batch_size)

class FomagParser:
    def __init__(self, path_to_save="data/fomag_news"):
        self.path_to_save = path_to_save
        self.cols_names = ["title", "source_url", "date", "text", "refs", "news_class", "company_name"]

    def parse_page(self, page_url):
        driver = webdriver.Chrome()
        driver.get(page_url)
        time.sleep(np.random.randint(2, 8))
        news_page = driver.page_source
        driver.close()
        news_tree = BeautifulSoup(news_page, "html.parser")
        arcticle_tree = news_tree.find("div", {"class": "article-frame"})
        if arcticle_tree is None:
            return [None for _ in range(7)]
        news_date = arcticle_tree.find("span", {"class": "info-date"}).get_text()
        news_title = arcticle_tree.find("h1").get_text()
        news_text = ""
        text_tree = arcticle_tree.find_all(['p', 'h2', 'blockquote'])
        for tag in text_tree:
            news_text += tag.get_text() + "\n"
        return [news_title, page_url, news_date, news_text, [], None, None]
    
    def parse_batch(self, urls, batch_size=64):
        news_dl = DataLoader(urls, batch_size=batch_size)
        for i, news_batch in enumerate(news_dl):
            data = []
            for news_ref in tqdm(news_batch, desc="progress: "):
                try:
                    page_feats = self.parse_page(news_ref)
                except TimeoutException as ex:
                    page_feats = [None for _ in range(7)]
                data.append(page_feats)
            df = pd.DataFrame(data, columns=self.cols_names)
            df.to_parquet(f"{self.path_to_save}/data_{i + 4}.parquet")
        