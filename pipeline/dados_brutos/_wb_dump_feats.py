"""Dump dos feats do AoN (indice `aon`), particionado por nivel para paralelizar."""
import json, urllib.request, concurrent.futures, threading

URL = "https://elasticsearch.aonprd.com/aon/_search"
FIELDS = ["id", "name", "level", "rarity", "trait", "trait_raw", "source", "source_raw",
          "primary_source", "primary_source_raw", "text", "summary", "archetype",
          "archetype_raw", "remaster_id", "legacy_id", "url", "pfs", "type",
          "prerequisite", "release_date", "exclude_from_search"]


def q(body, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=240))
        except Exception:
            if i == tries - 1:
                raise


lock = threading.Lock()
out = []


def puxar(lvl):
    got = []
    frm = 0
    while True:
        b = {"track_total_hits": True, "size": 500, "from": frm, "_source": FIELDS,
             "query": {"bool": {"filter": [{"term": {"category": "feat"}},
                                           {"term": {"level": lvl}}]}},
             "sort": [{"id.keyword": "asc"}]}
        r = q(b)
        h = r["hits"]["hits"]
        tot = r["hits"]["total"]["value"]
        got += [x["_source"] for x in h]
        frm += len(h)
        if not h or frm >= tot:
            break
    with lock:
        out.extend(got)
        print("level", lvl, len(got), flush=True)
    return len(got)


with concurrent.futures.ThreadPoolExecutor(10) as ex:
    list(ex.map(puxar, range(0, 31)))
json.dump(out, open("aon_feats.json", "w"))
print("TOTAL", len(out))
