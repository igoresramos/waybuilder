import json,urllib.request,sys
URL="https://elasticsearch.aonprd.com/aon/_search"
def q(body):
    req=urllib.request.Request(URL,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req,timeout=120))
def dump(cat,out):
    hits=[];after=None;tot=0
    while True:
        b={"track_total_hits":True,"size":500,"query":{"term":{"category":cat}},"sort":[{"id.keyword":"asc"}]}
        if after: b["search_after"]=after
        r=q(b); h=r['hits']['hits']; tot=r['hits']['total']['value']
        if not h: break
        hits+=[x['_source'] for x in h]; after=h[-1]['sort']
        print(cat,len(hits),'/',tot,flush=True)
        if len(hits)>=tot: break
    json.dump(hits,open(out,'w'))
dump("archetype","aon_archetypes.json")
dump("feat","aon_feats.json")
