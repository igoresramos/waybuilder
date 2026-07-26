import json,urllib.request
URL="https://elasticsearch.aonprd.com/aon/_search"
FIELDS=["id","name","level","rarity","trait","trait_raw","source","source_raw","primary_source",
        "primary_source_raw","text","summary","archetype","archetype_raw","remaster_id","legacy_id",
        "url","pfs","type","actions","prerequisite","prerequisite_raw","release_date","school","tradition",
        "spell_type","frequency","trigger","requirement","exclude_from_search","is_standard_ancestry_feat"]
def q(body):
    req=urllib.request.Request(URL,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req,timeout=180))
def dump(cat,out):
    hits=[];after=None;tot=0
    while True:
        b={"track_total_hits":True,"size":400,"_source":FIELDS,
           "query":{"term":{"category":cat}},"sort":[{"id.keyword":"asc"}]}
        if after: b["search_after"]=after
        r=q(b); h=r['hits']['hits']; tot=r['hits']['total']['value']
        if not h: break
        hits+=[x['_source'] for x in h]; after=h[-1]['sort']
        print(cat,len(hits),'/',tot,flush=True)
        if len(hits)>=tot: break
    json.dump(hits,open(out,'w'))
dump("archetype","aon_archetypes.json")
dump("feat","aon_feats.json")
print("DONE")
