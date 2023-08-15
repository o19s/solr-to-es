from __future__ import print_function
import argparse
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from solr_to_es.solrSource import SlowSolrDocs
import pysolr
import requests


DEFAULT_ES_MAX_RETRIES = 15
DEFAULT_ES_INITIAL_BACKOFF = 3


class SolrEsWrapperIter:
    def __init__(self, solr_itr, es_index, es_type, id_field=None):
        self.index = es_index
        self.type = es_type
        self.id_field = id_field
        self.solr_itr = iter(solr_itr)

    def __iter__(self):
        return self

    def __next__(self):
        doc = next(self.solr_itr)
        new_doc = dict()
        new_doc['_index'] = self.index
        new_doc['_type'] = self.type
        new_doc['_source'] = doc
        if self.id_field:
            new_doc['_id'] = doc[self.id_field]
        return new_doc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('solr_url',
                        type=str)

    parser.add_argument('--solr-query',
                        type=str,
                        default='*:*')

    parser.add_argument('--solr-filter',
                        type=str,
                        default='')

    parser.add_argument('--solr-fields',
                        type=str,
                        default='')

    parser.add_argument('--id-field',
                        type=str,
                        default=None)

    parser.add_argument('elasticsearch_url',
                        type=str)

    parser.add_argument('elasticsearch_index',
                        type=str)

    parser.add_argument('doc_type',
                        type=str)

    parser.add_argument('--rows-per-page',
                        type=int,
                        default=500)

    parser.add_argument('--es-timeout',
                        type=int,
                        default=60)

    parser.add_argument('--es-user',
                        type=str,
                        default='')

    parser.add_argument('--es-password',
                        type=str,
                        default='')

    parser.add_argument('--es-max-retries',
                        type=int,
                        default=DEFAULT_ES_MAX_RETRIES,
                        help='maximum number of times a document will be retried when 429 is received, set to 0 for no retries on 429. default {}'.format(DEFAULT_ES_MAX_RETRIES))

    parser.add_argument('--es-initial-backoff',
                        type=int,
                        default=DEFAULT_ES_INITIAL_BACKOFF,
                        help='number of seconds we should wait before the first retry. Any subsequent retries will be powers of initial_backoff * 2**retry_number. default {}'.format(DEFAULT_ES_INITIAL_BACKOFF))

    return vars(parser.parse_args())


def main():
    try:
        args = parse_args()
        if args['es_user']:
            es_conn = Elasticsearch(hosts=args['elasticsearch_url'], timeout=args['es_timeout'], http_auth=(args['es_user'], args['es_password']))
        else:
            es_conn = Elasticsearch(hosts=args['elasticsearch_url'], timeout=args['es_timeout'])

        # append /select to the solr URL if needed
        test_solr_query = dict(q="*", wt="json")
        response = requests.get(args['solr_url'], params=test_solr_query)
        if response.status_code != 200 or "responseHeader" not in response.json():
            args['solr_url'] = "/".join(args['solr_url'], "select")

        solr_fields = args['solr_fields'].split() if args['solr_fields'] else ''
        solr_filter = args['solr_filter'] if args['solr_filter'] else ''
        solr_itr = SlowSolrDocs(args['solr_url'], args['solr_query'], rows=args['rows_per_page'], fl=solr_fields,
                                fq=solr_filter)
        es_actions = SolrEsWrapperIter(solr_itr, args['elasticsearch_index'], args['doc_type'], args['id_field'])
        for ok, item in elasticsearch.helpers.streaming_bulk(es_conn, es_actions, max_retries=args['es_max_retries'], initial_backoff=args['es_initial_backoff']):
            if not ok:
                errors.append(item)

    except KeyboardInterrupt:
        print('Interrupted')


if __name__ == "__main__":
    main()
