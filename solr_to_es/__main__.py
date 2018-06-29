from __future__ import print_function
import argparse
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import pysolr
from solrSource import SlowSolrDocs

class SolrEsWrapperIter:
    def __init__(self, solr_itr, es_index, es_type):
        self.index = es_index
        self.type = es_type
        self.solr_itr = iter(solr_itr)

    def __iter__(self):
        return self

    def next(self):
        doc = self.solr_itr.next()
        new_doc = dict()
        new_doc['_index'] = self.index
        new_doc['_type'] = self.type
        new_doc['_source'] = doc
        return new_doc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('solr_url',
                        type=str)

    parser.add_argument('--solr-query',
                        type=str,
                        default='*:*')

    parser.add_argument('--solr-fields',
                        type=str,
                        default='')

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

    return vars(parser.parse_args())


def main():
    try:
        args = parse_args()
        es_conn = Elasticsearch(hosts=args['elasticsearch_url'], timeout=args['es_timeout'])

        # Split the solr_url into the root and the request handler
        solr_conn = pysolr.Solr(args['solr_url'].rsplit('/', 1)[0], search_handler=args['solr_url'].rsplit('/', 1)[-1])
        solr_fields = args['solr_fields'].split() if args['solr_fields'] else ''
        solr_itr = SlowSolrDocs(solr_conn, args['solr_query'], rows=args['rows_per_page'], fl=solr_fields)
        es_actions = SolrEsWrapperIter(solr_itr, args['elasticsearch_index'], args['doc_type'])
        elasticsearch.helpers.bulk(es_conn, es_actions)
    except KeyboardInterrupt:
        print('Interrupted')


if __name__ == "__main__":
    main()
