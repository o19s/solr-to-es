import requests

class InvalidPagingConfigError(RuntimeError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(message)


class _SolrCursorIter:
    """ Cursor-based iteration, most performant. Requires a sort on id somewhere
        in required "sort" argument.

        This is recommended approach for iterating docs in a Solr collection
        """
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

    def __next__(self):
        try:
            if self.docs is not None:
                try:
                    return next(self.docs)
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
                    return next(self.docs)
                else:
                    raise StopIteration()
        except pysolr.SolrError as e:
            if "Cursor" in e.args[0]:
                raise InvalidPagingConfigError(e.args)
            raise e


class _SolrPagingIter:
    """ Traditional search paging, most flexible but will
        gradually get slower on each request due to deep-paging

        See graph here:
        http://opensourceconnections.com/blog/2014/07/13/reindexing-collections-with-solrs-cursor-support/
        """
    def __init__(self, solr_url,query, **options):
        self.current = 0
        self.query = query
        self.solr_url = solr_url
        
        try:
            self.rows = options['rows']
            del options['rows']
        except KeyError:
            self.rows = 0
        
        try:
            self.fl = options['fl']
            del options['fl']
        except KeyError:
            self.fl = None

        self.options = options
        self.max = None
        self.docs = None

    def __iter__(self):
        r = requests.get(self.solr_url+'?q=' + self.query + '&wt=json&rows=0')
        response = r.json()
        self.max = response['response']['numFound']
        print("Found %s docs" % self.max)
        return self        

    def __next__(self):
        if self.docs is not None:
            try:
                return next(self.docs)
            except StopIteration:
                self.docs = None
        if self.docs is None:
            if self.current * self.rows < self.max:
                self.current += 1
                url = self.solr_url+ '?q=' + self.query + '&wt=json&rows=' + str(self.rows) + "&start=" + str(((self.current - 1) * self.rows))
                if self.fl:
                    url = url + "&fl=" + (','.join(self.fl))                
                r = requests.get(url)
                response = r.json()
                self.docs = iter(response['response']['docs'])
                return next(self.docs)
            else:
                raise StopIteration()


SolrDocs = _SolrCursorIter  # recommended, see note for SolrCursorIter
SlowSolrDocs = _SolrPagingIter
