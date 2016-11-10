import pysolr

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


class _SolrPagingIter:
    """ Traditional search paging, most flexible but will
        gradually get slower on each request due to deep-paging

        See graph here:
        http://opensourceconnections.com/blog/2014/07/13/reindexing-collections-with-solrs-cursor-support/
        """
    def __init__(self, solr_conn, query, **options):
        self.current = 0
        self.query = query
        self.solr_conn = solr_conn
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
        if self.docs is not None:
            try:
                return self.docs.next()
            except StopIteration:
                self.docs = None
        if self.docs is None:
            if self.current * self.rows < self.max:
                self.current += 1
                response = self.solr_conn.search(self.query, rows=self.rows,
                                                 start=(self.current - 1) * self.rows,
                                                 **self.options)
                self.docs = iter(response.docs)
                return self.docs.next()
            else:
                raise StopIteration()

SolrDocs = _SolrCursorIter # recommended, see note for SolrCursorIter
SlowSolrDocs = _SolrPagingIter
