#-*-coding:utf-8-*-

class Pagination(object):
    def __init__(self, totalItems, itemsPerPage, currentPage=1):
        floatPages = float(totalItems) / itemsPerPage
        intPages = totalItems / itemsPerPage
        pages = intPages
        page = currentPage
        if intPages == 0:
            pages = 1
        if floatPages > intPages:
            pages = intPages + 1
        if currentPage < 1:
            page = 1
        if currentPage > pages:
            page = pages
        self.page = currentPage
        self.pages = pages
        self.items = totalItems
        self.limit = itemsPerPage

    def _next_page(self):
        if self.page < self.pages:
            return self.page + 1
        else:
            return self.pages
    
    def _prev_page(self):
        if self.page > 2:
            return self.page - 1

    def _get_start(self):
        if self.page >= 1:
            return (self.page - 1) * self.limit
        else:
            return 0

    def __getattr__(self, attr):
        if attr == 'nextPage':
            return self._next_page()
        elif attr == 'prevPage':
            return self._prev_page()
        elif attr == 'start':
            return self._get_start()
