# Solr to Elasticsearch Migrator

This will migrate a Solr node to an Elasticsearch index.

## Requirements

  * Python 3+
    * elasticsearch
    * pysolr

## Usage

```
usage: solr-to-es [-h] [--solr-query SOLR_QUERY] [--solr-fields COMMA_SEP_FIELDS]
                  [--rows-per-page ROWS_PER_PAGE] [--es-timeout ES_TIMEOUT]
                  solr_url elasticsearch_url elasticsearch_index doc_type
```

The following example will page through all documents on the local Solr, and submit them to the local Elasticsearch server in the index `es_index` with a document type of `solr_docs`.

```bash
solr-to-es http://localhost:8983/solr/<<collection_name>> http://localhost:9200 <<collection_name>> solr_docs
```

`solr_url` is the full url to your Solr,

`elasticsearch_url` is the url of your Elasticsearch server.

`elasticsearch_index` is the index you will submit the Solr documents to on Elasticsearch.

`doc_type` is the type of document Elasticsearch should assume you are importing.

`--solr-query` defaults to `*:*`

`--solr-fields` defaults to ` ` (i.e. all fields)

`--rows-per-page` defaults to `500`

`--es-timeout` defaults to `60`

`--es-user` for authentication in Elasticsearch

`--es-password` for authentication in Elasticsearch

`--es-max-retries` maximum number of times a document will be retried when 429 is received, set to 0 for no retries on 429

`--es-initial-backoff` number of seconds we should wait before the first retry. Any subsequent retries will be powers of initial_backoff * 2**retry_number

## Install

Run `python setup.py install` to install the script.

### Demo

Here is an example of grabbing the over 114 thousand journal articles from Plos.org API about *animals*.

```
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch

solr-to-es --solr-query animal http://api.plos.org/search localhost:9200 es_plos solr_docs

curl http://localhost:9200/_cat/indices?v

```
_Note: that you will get an 403 Forbidden error from the script, and that is because the solr.quepid.com doesn't allow deep paging, however you will have documents in your ES cluster_.
