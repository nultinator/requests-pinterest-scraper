import os
import csv
import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import concurrent.futures
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def scrape_search_results(keyword, location, retries=3):
    formatted_keyword = keyword.replace(" ", "+")
    url = f"https://www.pinterest.com/search/pins/?q={formatted_keyword}&rs=typed"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        try:
            response = requests.get(url)
            logger.info(f"Recieved [{response.status_code}] from: {url}")
            if response.status_code != 200:
                raise Exception(f"Failed request, Status Code {response.status_code}")
                
                ## Extract Data

            soup = BeautifulSoup(response.text, "html.parser")            
            
            div_cards = soup.find_all("div")

            result_count = 0

            for div_card in div_cards:
                if div_card.get("data-grid-item"):

                    result_count += 1

                    title = div_card.text
                    a_element = div_card.find("a")
                    url = f"https://pinterest.com{a_element['href']}"
                    img = div_card.find("img")
                    img_url = img["src"]

                    search_data = {
                        "name": title,
                        "url": url,
                        "image": img_url
                    }

                    print(search_data)

            success = True
        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")





if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    LOCATION = "uk"

    logger.info(f"Crawl starting...")

    ## INPUT ---> List of keywords to scrape
    keyword_list = ["grilling"]
    aggregate_files = []

    ## Job Processes
    for keyword in keyword_list:
        scrape_search_results(keyword, LOCATION, retries=MAX_RETRIES)
        
    logger.info(f"Crawl complete.")
