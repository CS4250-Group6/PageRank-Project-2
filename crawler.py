# Crawl pages and save relevant data here.
import requests
import time
import csv
from bs4 import BeautifulSoup
import urllib.robotparser as robotparser


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
        return None


def save_csv(url, links):
    """fun(url: String, links: Int) -> Void: save these two values in a csv file"""
    with open(f"linksOut.csv", "a") as file:
        writer = csv.writer(file)
        row = (url, links)
        writer.writerow(row)


def save_link_csv(url, links):
    with open(f"linksTo.csv", "a") as file:
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


def get_links(soup, baseUrl):
    """fun(page: String) -> list(urls: String): parse page for links"""
    links = set()

    for link in soup.findAll("a", href=True, download=None):
        newUrl = link.get("href")
        if newUrl is not None:
		if x[-4:] != '.png' and x[-4:] != '.jpg' and x[-5:] != '.jpeg' and parser.can_fetch("*", newUrl) and newUrl != "en.wikipedia.orgjavascript:print();":
		    if newUrl[0:7] == "http://" or newUrl[0:8] == "https://" or newUrl.startswith("//"):
			no_protocol_url = replace_http_protocol(url)
			if restrict_domain == no_protocol_url[0 : len(restrict_domain)]:
				links.add(no_protocol_url)
		    elif (
			not newUrl.startswith("#")
			and not newUrl.startswith("ftp://")
			and not newUrl.startswith("mailto:")
			and not newUrl == ""
		    ):
			if newUrl.find(baseUrl) == -1:
			    links.add(baseUrl + newUrl)
			elif restrict_domain == x[0 : len(restrict_domain)]:
			    links.add(newUrl)

 
    return links


visited = set()
crawl = ["en.wikipedia.org/wiki/Computer_science"]
restrict_domain = "en.wikipedia.org"
searchCount = 1000

try:
    robotsTxt = get_page("en.wikipedia.org/robots.txt")
except:
    print("ERR, COULDN'T READ ROBOTS.TXT URL!")
    exit(1)
    
parser = robotparser.RobotFileParser()
parser.set_url("http://www.wikipedia.org/robots.txt") # change for cpp crawling, needs to be this url for wikipedia
parser.read()

while len(crawl) != 0 and len(visited) < searchCount:

    url = crawl.pop(0)
    baseUrl = get_base_url(url)

    if url not in visited and parser.can_fetch("*", url):
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
