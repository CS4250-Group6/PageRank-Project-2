# Crawl pages and save relevant data here.
import sys
import requests
import time
import csv
from bs4 import BeautifulSoup
import urllib.robotparser as robotparser
import tldextract
import argparse
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np

def get_page(url):
    """fun(url: String) get_page -> String: get page"""
    try:
        site = requests.get("http://" + url)
    except:
        print("BAD HTTP URL REQUEST:", url)
        return None

    if site.status_code == 429:
        print("WARN: 429 Too Many Requests")
        time.sleep(3)
        return get_page(url)
    elif site.status_code < 300:
        return site.text
    else:
        print("err?")
        return None


def save_csv(url, links):
    """fun(url: String, links: Int) -> Void: save these two values in a csv file"""
    with open(f"{fileSuffix}linksOut.csv", "a") as file:
        writer = csv.writer(file)
        row = (url, links)
        writer.writerow(row)


def save_link_csv(url, links):
    with open(f"{fileSuffix}linksTo.csv", "a") as file:
        writer = csv.writer(file)
        r = (url, *links)
        writer.writerow(r)


def replace_http_protocol(url):
    new_url = url

    if url[0:7] == "http://":
        new_url = new_url[7:]
    elif url[0:8] == "https://":
        new_url = new_url[8:]
    elif url.startswith("//"):
        new_url = new_url[2:]

    return new_url


def get_base_url(url):
    base_url = replace_http_protocol(url)

    url_end = base_url.find("/")
    if url_end != -1:
        base_url = base_url[:url_end]
    return base_url
def get_url_subdirectory(url):
    subdi_url = replace_http_protocol(url)
    url_end = subdi_url.find("/")
    if url_end != -1:
        subdi_url = subdi_url[url_end:]
    return subdi_url
def verify_not_restricted(url_to_check: str) -> bool:
    check = tldextract.extract(url_to_check)
    against = tldextract.extract(restrict_domain)
    if restrict_domain == "www.cpp.edu":
        if check.domain == against.domain and check.suffix == against.suffix and verify_wiki_mainspace(url_to_check):
            return True
        else:
            return False
    else:
        if '.'.join(check) == '.'.join(against) and verify_wiki_mainspace(url_to_check):
            return True
        else:
            return False

def verify_wiki_mainspace(check_url: str) -> bool:
    if "wikipedia" in check_url:
        spl = check_url.split("/")
        if ":" in spl[-1]:
            return False
    return True


def get_links(soup, baseUrl):
    """fun(page: String) -> list(urls: String): parse page for links"""
    links = set()

    for link in soup.findAll("a", href=True, download=None):
        newUrl = link.get("href")
        if newUrl is not None:
            if newUrl[-4:] != '.png' and newUrl[-4:] != '.jpg' and newUrl[-5:] != '.jpeg' and newUrl not in hand_picked_problems:
                if newUrl[0:7] == "http://" or newUrl[0:8] == "https://" or newUrl.startswith("//"):
                    no_protocol_url = replace_http_protocol(newUrl)
                    if parser.can_fetch("*", "http://" + newUrl) and verify_not_restricted(no_protocol_url):
                        links.add(no_protocol_url)
                elif (
                not newUrl.startswith("#")
                and not newUrl.startswith("ftp://")
                and not newUrl.startswith("mailto:")
                and not newUrl == ""
                ):
                    if newUrl.find(baseUrl) == -1 and verify_not_restricted(baseUrl + newUrl) and parser.can_fetch("*", "http://" + baseUrl + newUrl):
                        links.add(baseUrl + newUrl)
                    elif parser.can_fetch("*", "http://" + newUrl) and verify_not_restricted(newUrl):
                        links.add(newUrl)
    return links


visited = set()
hand_picked_problems = set(["en.wikipedia.orgjavascript:print();"])
p = argparse.ArgumentParser(description="Crawl page")
p.add_argument("-n", default=1000)
p.add_argument("seed_url", default="www.cpp.edu", nargs="?")
p.add_argument("-r", default="www.cpp.edu")
p.add_argument("-o", default="")
args = p.parse_args(sys.argv[1:])

crawl = [args.seed_url]
restrict_domain = args.r
searchCount = int(args.n)
fileSuffix = args.o

print(f"Running crawler with: n={args.n}, seed={args.seed_url}, restrict={args.r}, file_suffix={args.o}.")

parser = robotparser.RobotFileParser()
parser.set_url(f"http://{restrict_domain}/robots.txt") # change for cpp crawling, needs to be this url for wikipedia
parser.read()

if parser.disallow_all: # type: ignore # pyright stuff, please ignore.
    print("ERR! NOT ALLOWED TO PARSE ANY!")
    exit(1)

while len(crawl) != 0 and len(visited) < searchCount:

    url = crawl.pop(0)
    baseUrl = get_base_url(url)

    if url not in visited and parser.can_fetch("*", "http://" + url):
        print(f"Crawling ({len(visited)}/{searchCount}): {url}")

        page = get_page(url)
        if page is not None:

            soup = BeautifulSoup(page, "html.parser")
            links = get_links(soup, baseUrl)

            save_csv(url, len(links))
            save_link_csv(url, links)

            crawl += list(links)
            time.sleep(0.5)

            visited.add(url)
objects = ('Us', 'Google')
y_pos = np.arange(len(objects))
performance = [time_took, 2.3 ]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('time in minutes')
plt.title('Time to Crawl 1000 Pages')

plt.show()
