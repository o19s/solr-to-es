from solrTest import SolrIntegrationTest
from solr_to_es.__main__ import SolrRequestIter, InvalidPagingConfigError

class SolrIterateTest(SolrIntegrationTest):

    def test_basic_op(self):
        solrReq = SolrRequestIter(solr_conn=self.solr_conn, query="*:*", sort='id desc', rows=10)
        solrReq = iter(solrReq)
        nextDoc = solrReq.next()
        assert len(nextDoc['catch_line']) > 0
        nextDoc = solrReq.next()
        assert len(nextDoc['catch_line']) > 0

    def test_bad_sort(self):
        import pdb; pdb.set_trace()
        solrReq = SolrRequestIter(solr_conn=self.solr_conn, query="*:*", sort='score desc', rows=10)
        try:
            solrReq = iter(solrReq)
            next(solrReq)
            assert False
        except InvalidPagingConfigError as e:
            print e.message
        except Exception as e:
            print e
            raise e




