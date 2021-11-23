import random
from random import randint
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import csv


def random_surfer_rank():
    # use same code from default_rank to retrieve iterative page rank values to use
    # for modified page rank
    outlinks_sum = generate_outlinks_sum_dict()
    outlinks = generate_outgoing_url_dict()
    n = len(outlinks)
   # print("Number of links with outlinks:", n)
    # floating point precision means that data will be lost.
    page_rank = np.full((n, 1), 1 / n)
   # print(modified_page_rank)
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

    loops = 100
    for i in range(loops):
        page_rank = M @ page_rank

    outlink_keys = list(outlinks.keys())
    index_sorted = sorted(
        range(len(page_rank)), key=lambda x: page_rank[x], reverse=True
    )
    sorted_urls = [outlink_keys[x] for x in index_sorted]
   # print(sorted_urls[0:30])
    #print([page_rank[x][0] for x in index_sorted][0:30])
    #print("Total:", sum(page_rank[i][0] for i in range(len(page_rank))))

    #random surfer model
    surfer_lambda = 0.2
    r = randint(0,1)
    if r < surfer_lambda:
        print("Go to random page")
        random_page = random.choice(sorted_urls)
        print(random_page)
    if r >= surfer_lambda:
        print("Click link at random page")


  #use iterative page rank to calculate the modified page rank
    result_pt1 = np.dot((1-surfer_lambda), page_rank)
    modified_page_rank = ((surfer_lambda/n) + result_pt1)
    sum1 = 0
    for i in modified_page_rank:
        for j in i:
            sum1 += j
    print("Sum for random surfer model:", sum1)



def hits_rank():
    Node_link = np.array(
    [[1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0]])

    n = Node_link.shape[0]
    degree = np.sum(Node_link, axis=1, keepdims=1)

    Node_link = Node_link + (degree == 0)
    degree = np.sum(Node_link, axis=1, keepdims=1)

    WORDS = 100000
    list = [[col for col in range(n) if Node_link[row, col]] for row in range(n)]
    count = [0]*n
    state = 0

    for _ in range(WORDS):
        count[state] += 1
        if randint(1, 6) == 6:
            state = randint(0, 5)
    else:
        d = len(list[state])
        state = list[state][randint(0, d - 1)]
        print(list, [c / WORDS for c in count], sep="\n")

    Node_link = nx.DiGraph()
    Node_link.edges([('A', 'D'), ('B', 'C'), ('B', 'E'), ('C', 'A'),
                  ('D', 'C'), ('E', 'D'), ('E', 'B'), ('E', 'F'),
                  ('E', 'C'), ('F', 'C'), ('F', 'H'), ('G', 'A'),
                  ('G', 'C'), ('H', 'A')])
    plt.figure(figsize=(10, 10))
    nx.draw_networkx(Node_link, with_labels=True)

    hubs, authorities = nx.hits(Node_link, max_iter=50, normalized=True)
    print("Hub Points", hubs)
    print("Authority Points" , authorities)

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

    loops = 100
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
    hits_rank()
    random_surfer_rank()
