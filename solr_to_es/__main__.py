from __future__ import print_function
import argparse
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import pysolr

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


class InvalidPagingConfigError(RuntimeError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(message)


class SolrRequestIter:
    def __init__(self, solr_conn, query, sort, **options):
        self.query = query
        self.solr_conn = solr_conn
        self.lastCursorMark = ''
        self.cursorMark = '*'
        self.sort = sort

        try:
            self.rows = options['rows']
            del options['rows']
        except KeyError:
            self.rows = 0
        self.options = options
        self.max = None
        self.docs = None

    def __iter__(self):
        response = self.solr_conn.search(self.query, rows=0, **self.options)
        self.max = response.hits
        return self

    def next(self):
        try:
            if self.docs is not None:
                try:
                    return self.docs.next()
                except StopIteration:
                    self.docs = None
            if self.docs is None:

                if self.lastCursorMark != self.cursorMark:
                    response = self.solr_conn.search(self.query, rows=self.rows,
                                                     cursorMark=self.cursorMark,
                                                     sort=self.sort,
                                                     **self.options)
                    self.docs = iter(response.docs)
                    self.lastCursorMark = self.cursorMark
                    self.cursorMark = response.nextCursorMark
                    return self.docs.next()
                else:
                    raise StopIteration()
        except pysolr.SolrError as e:
            if "Cursor" in e.message:
                raise InvalidPagingConfigError(e.message)
            raise e



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('solr_url',
                        type=str)

    parser.add_argument('--solr-query',
                        type=str,
                        default='*:*')

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
        solr_conn = pysolr.Solr(args['solr_url'])
        solr_itr = SolrRequestIter(solr_conn, args['solr_query'], rows=args['rows_per_page'])
        es_actions = SolrEsWrapperIter(solr_itr, args['elasticsearch_index'], args['doc_type'])
        elasticsearch.helpers.bulk(es_conn, es_actions)
    except KeyboardInterrupt:
        print('Interrupted')


if __name__ == "__main__":
    main()
