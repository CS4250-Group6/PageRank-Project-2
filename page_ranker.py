# import matplotlib.pyplot as plt
import numpy as np
import csv


def random_surfer_rank():
    pass


def teleporting_rank():
    pass


def default_rank():
    # incoming = generate_incoming_url_dict()
    outlinks_sum = generate_outlinks_sum_dict()
    outlinks = generate_outgoing_url_dict()
    n = len(outlinks)
    print("Number of links with outlinks:", n)
    # floating point precision means that data will be lost.

    page_rank = np.full((n, 1), 1 / n)

    #      url1, url2, url3
    # url1  x      x    x
    # url2
    # url3
    # Each nested array represents a row
    # So each row is the inlinks going to this row from this column.
    # AKA, the outlinks going from each column to this row.
    M = np.zeros((n, n))
    ii = -1
    for i in outlinks:  # column
        ii += 1
        jj = -1
        for j in outlinks:  # row
            jj += 1
            if j in outlinks[i]:
                M[jj][ii] = 1 / outlinks_sum[i]

    loops = 100000
    for i in range(loops):
        page_rank = M @ page_rank

    outlink_keys = list(outlinks.keys())
    index_sorted = sorted(
        range(len(page_rank)), key=lambda x: page_rank[x], reverse=True
    )
    sorted_urls = [outlink_keys[x] for x in index_sorted]
    print(sorted_urls[0:30])
    print([page_rank[x][0] for x in index_sorted][0:30])
    print("Total:", sum(page_rank[i][0] for i in range(len(page_rank))))


def generate_incoming_url_dict():
    res = {}
    with open(f"linksTo.csv", "r") as file:
        reader = csv.reader(file)
        for line in reader:
            for i in range(1, len(line)):
                if line[i] not in res:
                    res[line[i]] = set(line[0])
                else:
                    res[line[i]].add(line[0])

    return res


def generate_outgoing_url_dict():
    res = {}
    with open(f"linksTo.csv", "r") as file:
        reader = csv.reader(file)
        for line in reader:
            res[line[0]] = set([*line[1:]])

    return res


def generate_outlinks_sum_dict():
    res = {}
    with open(f"linksOut.csv", "r") as file:
        reader = csv.reader(file)
        for line in reader:
            res[line[0]] = int(line[1])

    return res


def default_rank_data_preprocessing():
    """
    Preprocessing done for the default PageRank algorithm.
    Removes recorded urls that haven't been scraped for their own links.
    Then updates the total outlinks for each url.

    Essentially removes all dangling pages.
    If this preprocessing wasn't done, then the summed PageRanks of all pages would eventually become 0.
    """
    outlinks_sum = generate_outlinks_sum_dict()
    temp = []
    with open(f"linksTo.csv", "r") as file:
        reader = csv.reader(file)
        for line in reader:
            filtered_line = list(filter(lambda x: x in outlinks_sum, line))
            temp.append(filtered_line)

    with open(f"linksTo.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(temp)

    with open(f"linksOut.csv", "w") as file:
        writer = csv.writer(file)
        for i in range(len(temp)):
            writer.writerow((temp[i][0], len(temp[i]) - 1))


if __name__ == "__main__":
    default_rank_data_preprocessing()
    default_rank()
