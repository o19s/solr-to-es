import unittest
import pysolr
from os import environ


class SolrIntegrationTest(unittest.TestCase):

    def setUp(self):
        stateDecDefault = 'http://solr.quepid.com/solr/statedecoded'
        stateDecSolr = environ['STATE_DECODED_SOLR'] \
            if 'STATE_DECODED_SOLR' in environ \
            else stateDecDefault
        self.solr_conn = pysolr.Solr(stateDecSolr)
