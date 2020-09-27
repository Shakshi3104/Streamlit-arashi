import urllib
from bs4 import BeautifulSoup
import csv


def find_sales(url, filename):
    print("Scraping... {}".format(url))
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

    soup = BeautifulSoup(urllib.request.urlopen(
        urllib.request.Request(url=url, headers=header)
    ), "html.parser")

    print("Find sales data")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")
    
    print("Write CSV file as {}".format(filename))
    with open(filename, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in rows:
            csv_row = []
            for cell in row.findAll(['td', 'th']):
                text = cell.get_text()
                text = text.replace("／", " / ").replace("~", "〜")
                csv_row.append(text)
            print(csv_row)
            writer.writerow(csv_row)


if __name__ == "__main__":
    find_sales("https://w.atwiki.jp/orideta/pages/70.html", "../ARASHI List/Single sales.csv")
    find_sales("https://w.atwiki.jp/orideta/pages/182.html", "../ARASHI List/Album sales.csv")