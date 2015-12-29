import json
import pprint
import urlparse

import networkx as nx

import click

from bbpr.bbpr.patterns import IGNORE


def reject_url(url):
    for pattern in IGNORE:
        if pattern.search(url) is not None:
            return True

    # reject path-less urls
    bits = urlparse.urlparse(url)
    if bits.path == '' or bits.path == '/':
        return True

    return False


@click.command()
@click.option('-i', 'input_files', type=click.File('rb'), multiple=True)
@click.option('-n', 'limit', type=click.INT, default=10)
@click.option('-w', '--internal-link-weight', 'internal_weight', default=0.5,
              type=click.FLOAT,
              help='Weight for same-hostname links')
def main(input_files, limit, internal_weight):
    graph = nx.DiGraph()

    for fh in input_files:
        raw_edges = json.load(fh)

        for raw_edge in raw_edges:
            # check once more against updated terms list
            if any(map(reject_url, (raw_edge['src_url'],
                                    raw_edge['dest_url'], ))):
                # click.echo('Rejecting -> {}'.format(raw_edge['dest_url']))
                continue

            # internal links should be scaled down
            if (urlparse.urlparse(raw_edge['src_url']).hostname == 
                urlparse.urlparse(raw_edge['dest_url']).hostname):
                weight = internal_weight
            else:
                weight = 1.0

            graph.add_edge(raw_edge['src_url'], raw_edge['dest_url'],
                           weight=weight)

    click.echo('Loaded graph: {}'.format(len(graph)))

    print('Calculating pagerank')
    pr = nx.pagerank_scipy(graph)

    top_nodes = sorted(pr.items(), key=lambda p: p[1], reverse=True)[:limit]
    pprint.pprint(top_nodes)


if __name__ == '__main__':
    main()
