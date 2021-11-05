# Crawl pages and save relevant data here.
import requests
import time
import csv
from langdetect import detect
from bs4 import BeautifulSoup


def can_scrape(url: str):
    """fun(url: String) can_scrape -> Bool: parse robots.txt check if the website is allowed to scrape"""

    if robotsTxt is not None:

        startAgentBlock = robotsTxt.find("User-agent: *")
        if startAgentBlock == -1:
            # If robots.txt exists and no wildcard user-agent exists, then we aren't allowed to crawl.
            return False

        endAgentBlock = robotsTxt.find("\n\n", startAgentBlock)
        if endAgentBlock == -1:
            # If no \n\n (2 return characters) and startAgentBlock exists, then assume that the block ends at the end of the document.
            endAgentBlock = len(robotsTxt)

        ourBlock = robotsTxt[startAgentBlock:endAgentBlock]
        split_by_line = ourBlock.split("\n")

        for each_line in split_by_line:
            if "#" not in each_line and ":" in each_line:
                # If Disallow: /something/ in url after root, then disallow.
                pre_colon = each_line.split(":")  # Allow or not.

                # Get everything after the base url.
                firstSlashI = url.find("/")
                pathPlusExtra = url[firstSlashI:]

                if pre_colon[1].strip() in pathPlusExtra:
                    if pre_colon[0] == "Allow":
                        return True
                    elif pre_colon[0] == "Disallow":
                        return False
    return True


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
            if newUrl[0:7] == "http://" or newUrl[0:8] == "https://":
                links.add(replace_http_protocol(url))
            elif newUrl.startswith("//"):
                links.add(newUrl[2:])
            elif (
                not newUrl.startswith("#")
                and not newUrl.startswith("ftp://")
                and not newUrl.startswith("mailto:")
                and not newUrl == ""
            ):
                if newUrl.find(baseUrl) == -1:
                    links.add(baseUrl + newUrl)
                else:
                    links.add(newUrl)

    links = set(
        filter(
            lambda x: can_scrape(x)
            and restrict_domain == x[0 : len(restrict_domain)]
            and x != "en.wikipedia.orgjavascript:print();", #TODO remove for cpp crawling.
            links,
        )
    )  # Filter out all links that we can't scrape or shouldn't be scraping.
    return links


visited = set()
crawl = ["en.wikipedia.org/wiki/Computer_science"]
restrict_domain = "en.wikipedia.org"
selectedLanguage = "en"
searchCount = 1000

try:
    robotsTxt = get_page("en.wikipedia.org/robots.txt")
except:
    print("ERR, COULDN'T READ ROBOTS.TXT URL!")
    exit(1)

while len(crawl) != 0 and len(visited) < searchCount:

    url = crawl.pop(0)
    baseUrl = get_base_url(url)

    if url not in visited and can_scrape(url) == True:
        print(f"Crawling ({len(visited)}/{searchCount}): {url}")

        page = get_page(url)
        if page is not None:

            soup = BeautifulSoup(page, "html.parser")
            if detect(soup.get_text()) == selectedLanguage:
                links = get_links(soup, baseUrl)

                save_csv(url, len(links))
                save_link_csv(url, links)

                crawl += list(links)
                time.sleep(0.5)

                visited.add(url)
