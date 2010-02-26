#-*-coding:utf-8-*-

class Pagination(object):
    def __init__(self, totalItems, itemsPerPage, currentPage=1):
        floatPages = float(totalItems) / itemsPerPage
        intPages = totalItems / itemsPerPage
        if intPages == 0:
            pages = 1
        if floatPages > intPages:
            pages = pages + 1
        if currentPage < 1:
            currentPage = 1
        if currentPage > pages:
            currentPage = pages
        self.page = currentPage
        self.pages = pages
        self.items = totalItems
        self.limit = itemsPerPage

    def next_page(self):
        if self.page < self.pages:
            return self.page + 1
        else:
            return self.pages
    
    def prev_page(self):
        if self.page > 2:
            return self.page - 1

    def get_start(self):
        return (self.page - 1) * self.limit
