# Fonte: Archives of Nethys (Elasticsearch)

- Endpoint: https://elasticsearch.aonprd.com/aon/_search
- Query: {"term": {"category": "spell"}}
- Data do dump: 2026-07-26
- Total de docs: 2461 (legado + remaster juntos, ver dedupe no extrator)
- Paginado em 9 lotes de 300 (from/size) por limite de banda do endpoint,
  arquivos crus em _batches/batch_<from>.json (formato bruto do _search)
