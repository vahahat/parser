"""
This script is used to scrape Casio Russia website for G-Shock watches.

The script uses the following libraries:
- requests
- BeautifulSoup
- csv
- json
- os
- time
- datetime

The script follows the following steps:
1. Get all pages: The script uses the requests library to make a GET request to the Casio Russia website, and saves the response HTML to a file named "data/page_1.html". The script then uses BeautifulSoup to parse the HTML and extract the number of pages from the pagination element. The script then makes a GET request to each page and saves the response HTML to a file named "data/page_x.html", where x is the page number. The script also adds a 2-second sleep between requests to avoid overwhelming the server.
2. Collect data: The script loops through each page, extracts the product information from the product cards, and saves it to a list of dictionaries. The script also saves the data to a CSV file named "data_<current date>.csv" and a JSON file named "data_<current date>.json".

The script uses the following functions:
- get_all_pages: This function makes GET requests to all pages of the Casio Russia website, saves the response HTML to files, and returns the number of pages.
- collect_data: This function loops through each page, extracts the product information from the product cards, and saves it to a list of dictionaries. It also saves the data to a CSV file and a JSON file.
- main: This function calls the get_all_pages and collect_data functions.

Note: The script assumes that the user is running the script from the project root directory, and that the "data" directory exists.
"""

import csv
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_all_pages():
    """
    This function makes GET requests to all pages of the Casio Russia website, saves the response HTML to files, and returns the number of pages.
    """
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    r = requests.get(url="https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/", headers=headers)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/page_1.html", "w") as file:
        file.write(r.text)

    with open("data/page_1.html") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    pages_count = int(soup.find("div", class_="bx-pagination-container").find_all("a")[-2].text)

    for i in range(1, pages_count + 1):
        url = f"https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/?PAGEN_1={i}"

        r = requests.get(url=url, headers=headers)

        with open(f"data/page_{i}.html", "w") as file:
            file.write(r.text)

        time.sleep(2)

    return pages_count + 1


def collect_data(pages_count):
    """
    This function loops through each page, extracts the product information from the product cards, and saves it to a list of dictionaries. It also saves the data to a CSV file and a JSON file.
    """
    cur_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"data_{cur_date}.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Артикул",
                "Ссылка",
                "��ена"
            )
        )

    data = []
    for page in range(1, pages_count):
        with open(f"data/page_{page}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_cards = soup.find_all("a", class_="product-item__link")

        for item in items_cards:
            product_article = item.find("p", class_="product-item__articul").text.strip()
            product_price = item.find("p", class_="product-item__price").text.lstrip("руб. ")
            product_url = f'https://shop.casio.ru{item.get("href")}'

            # print(f"Article: {product_article} - Price: {product_price} - URL: {product_url}")

            data.append(
                {
                    "product_article": product_article,
                    "product_url": product_url,
                    "product_price": product_price
                }
            )

            with open(f"data_{cur_date}.csv", "a") as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        product_article,
                        product_url,
                        product_price
                    )
                )

        print(f"[INFO] Обработана страница {page}/5")

    with open(f"data_{cur_date}.json", "a") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    """
    This function calls the get_all_pages and collect_data functions.
    """
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)


if __name__ == '__main__':
    main()
