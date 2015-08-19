# Solr to Elasticsearch Migrator

This will migrate a Solr node to an Elasticsearch index.

## Requirements

  * Python 2.7+
    * elasticsearch
    * pysolr
    
## Usage

```
usage: solr-to-es [-h] [--solr-query SOLR_QUERY]
                  [--rows-per-page ROWS_PER_PAGE] [--es-timeout ES_TIMEOUT]
                  solr_url elasticsearch_url elasticsearch_index doc_type
```

The following example will page through all documents on the local Solr node, `node`, and submit them to the local Elasticsearch server in the index `es_index` with a document type of `solr_docs`.

```bash
solr-to-es.py localhost:8983/solr/node localhost:9200 es_index solr_docs
```

`solr_url` is the url to your Solr node.

`elasticsearch_url` is the url of your Elasticsearch server.

`elasticsearch_index` is the index you will submit the Solr documents to on Elasticsearch.

`doc_type` is the type of document Elasticsearch should assume you are importing.

`--solr-query` defaults to `*:*`

`--rows-per-page` defaults to `500`

`--es-timeout` defaults to `60`
