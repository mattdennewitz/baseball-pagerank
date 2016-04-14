# baseball-pagerank

Baseball research can be tricky to catalog. This is an experiment
in indexing links from the Sabermetric major league and surfacing
interesting or arguably important links from within research via PageRank.

This is a young project - expect rough edges.
Remember, too, that the goal is to surface interesting links,
not become Google.

## Spiders

- [x] The Hardball Times and THT-Live
- [x] Fangraphs, FG+, Community
    - Requires Fangraphs account with FG+ access
- [x] Baseball Prospectus (with paywall support)
    - Requires BP membership
- [ ] Beyond the Box Score
- [ ] Grantland baseball coverage (RIP)
- [x] 538 baseball coverage
- [ ] JABO (RIP)
- [ ] Tangotiger (incl. comments)
- [ ] Walk Like a Sabermetrician
- [ ] Phil Birnbaum's Sabermetric Research blog

... and more as they come up

Sites with easily accessible blog post indexes are given priority.

### Running spiders

```shell
$ scrapy crawl <spider name> -o /path/to/<site-name>.json
```

### Ranking

```shell
$ ./rank.py -i /path/to/<site-name>.json [-i ...]
```

See `./rank.py --help` for more options.

## Implementation

Data is collected by a suite of spiders, one per publisher.

### Link extraction

Each spider, designed for a single publisher, crawls a publisher's
article index pages. Each linked-to article is then crawled
and its links extracted. For each link found in an article,
a relationship of the following shape is emitted:

```json
{
  "src_url": "http://www.fangraphs.com/plus/is-there-an-adjustment-time-for-players-changing-leagues/",
  "dest_url": "http://www.hardballtimes.com/main/fantasy/article/the-statistical-impact-of-switching-leagues-for-hitters/",
  "pub_date": "2013-02-04",
  "publisher": "fg"
}
```

This simple digest describes the following:

- that `src_url` links to `dest_url`,
- that `src_url` was published on `pub_date`,
- that `fg` ("fangraphs") published the content at `src_url`

All of these emitted relationships eventually form a graph of links
between documents.

### Edge weighting

To start, all edges are naively weighted as `1.0`, except those
representing a link from a publisher to itself. In-house content links
are weighted to `0.5`, and this value is configurable at ranking runtime.

Ideally, new weights will be added as the project matures.

### URL pattern blacklist

A small regex-based URL pattern blacklist is used to reduce noise like
player card links, tweets, promotional Amazon links, FanDuel/DraftKings,
and known dead sites. New filters can be added in `bbpr.patterns.TERMS`.
