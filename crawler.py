# Crawl pages and save relevant data here.
import requests
import time
import csv
import os
from langdetect import detect
from bs4 import BeautifulSoup


def can_scrape(robots: str, url: str):
    try:
        open_page = get_page(robots)
    except:
        return False

    if open_page is not None:

        startAgentBlock = open_page.find("User-agent: *")
        if startAgentBlock == -1:
            # If robots.txt exists and no wildcard user-agent exists, then we aren't allowed to crawl.
            return False

        endAgentBlock = open_page.find("\n\n", startAgentBlock)
        if endAgentBlock == -1:
            # If no \n\n (2 return characters) and startAgentBlock exists, then assume that the block ends at the end of the document.
            endAgentBlock = len(open_page)

        ourBlock = open_page[startAgentBlock:endAgentBlock]
        split_by_line = ourBlock.split("\n")

        for each_line in split_by_line:
            if "#" not in each_line and ":" in each_line:
                # If Disallow: /something/ in url after root, then disallow.
                pre_colon = each_line.split(":")  # Allow or not.

                # Get everything after the base url.
                firstSlashI = url.find("/")
                pathPlusExtra = url[firstSlashI:]
                # print("path:", pathPlusExtra)
                if pre_colon[1].strip() in pathPlusExtra:
                    # print(pre_colon[1].strip())
                    if pre_colon[0] == "Allow":
                        print("EXPLICITLY ALLOWED")
                        return True
                    elif pre_colon[0] == "Disallow":
                        print("DISALLOWED", pre_colon[1].strip(), url)
                        return False
    return True


# The url will be a robots.txt url this time so you need to do nothing more than what's written

# Use Andrew Daos get_page method with the url to get the page
# if none return true, else...

# Parse the robots.txt page and see if we can scrape it
# return true or false


def get_page(url):
    site = requests.get("http://" + url)
    if site.status_code == 429:
        print("WARN: 429 Too Many Requests")
        time.sleep(3)
        return get_page(url)
    elif site.status_code < 300:
        return site.text
    else:
        return None


def save_page(page, file_name):
    # Saving and extracting into file, probably
    langPath = os.path.join("repository", selectedLanguage)
    fullPathName = os.path.join(langPath, file_name)
    with open(fullPathName, "w") as f:
        f.write(page)
        f.close()


def save_csv(url, links):
    with open(f"linksOut.csv", "a") as file:
        writer = csv.writer(file)
        row = url, links
        writer.writerow(row)

def save_link_csv(url, links: list[str]):
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
    links = set()

    for link in soup.findAll("a", href=True, download=None):
        newUrl = link.get("href")
        if newUrl is not None:
            if newUrl[0:7] == "http://" or newUrl[0:8] == "https://":
                links.add(replace_http_protocol(url))
            elif (
                newUrl.startswith("//")
            ):
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

    return links


visited = set()
crawl = ["en.wikipedia.org/wiki/Computer_science"]
selectedLanguage = "en"
searchCount = 1000

while len(crawl) != 0 and len(visited) < searchCount:

    url = crawl.pop(0)
    baseUrl = get_base_url(url)

    # fun(url: String) can_scrape -> Bool: parse robots.txt check if the website is allowed to scrape (more details above)
    # Tasked to: Shurbur
    if url not in visited and can_scrape(baseUrl + "/robots.txt", url) == True:
        print(f"Crawling ({len(visited)}/{searchCount}): {url}")

        # fun(url: String) get_page -> String: get page
        # Tasked to: Andrew Dao
        page = get_page(url)
        if page is not None:

            soup = BeautifulSoup(page, "html.parser")
            if detect(soup.get_text()) == selectedLanguage:
                # fun(page: String, file_name: String) -> Void: save page
                # Tasked to: Andrew Dao
                # save_page(page, "page{}.html".format(len(visited) + 1))

                # fun(page: String) -> list(urls: String): parse page for links
                # Tasked to: Jonathan
                links = get_links(soup, baseUrl)

                # fun(url: String, links: Int) -> Void: save these two values in a csv file (more details above)
                save_csv(url, len(links))
                save_link_csv(url, links)

                crawl += list(links)
                time.sleep(0.5)

                visited.add(url)
