from solrTest import SolrIntegrationTest
from solr_to_es.solrSource import SolrDocs, InvalidPagingConfigError


class SolrIterateTest(SolrIntegrationTest):

    def test_basic_op(self):
        solrReq = SolrDocs(solr_conn=self.solr_conn, query="*:*", sort='id desc', rows=10)
        solrReq = iter(solrReq)
        nextDoc = next(solrReq)
        assert len(nextDoc['catch_line']) > 0
        nextDoc = next(solrReq)
        assert len(nextDoc['catch_line']) > 0

    def test_bad_sort(self):
        solrReq = SolrDocs(solr_conn=self.solr_conn, query="*:*", sort='score desc', rows=10)
        try:
            solrReq = iter(solrReq)
            next(solrReq)
            assert False
        except InvalidPagingConfigError as e:
            print(e.args)
        except Exception as e:
            print(e)
            raise e




