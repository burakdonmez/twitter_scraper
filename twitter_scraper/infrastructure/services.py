class RequestPaginator:
    def __init__(
        self,
        request_func,
        iter_objects_func,
        next_page_request_func,
        has_next_page_func,
        max_pages=None,
        max_items=None,
    ):
        self.request = request_func
        self.iter_objects = iter_objects_func
        self.next_page_request = next_page_request_func
        self.has_next_page = has_next_page_func
        self.max_pages = max_pages
        self.max_items = max_items

    def __call__(self, max_pages=None, max_items=None):
        self.max_pages = max_pages
        self.max_items = max_items

    def _reached_max_limits(self, page_count, item_count):
        reached_page_limit = self.max_pages is not None and self.max_pages <= page_count
        reached_item_limit = self.max_items is not None and self.max_items <= item_count
        return reached_page_limit or reached_item_limit

    def get_objects(self):
        response = self.request()
        iter_objs = self.iter_objects(response=response)
        page_count = 0
        item_count = 0

        while iter_objs:
            for obj in iter_objs:
                if self._reached_max_limits(page_count, item_count):
                    break

                yield obj
                item_count += 1

            if self._reached_max_limits(page_count, item_count):
                break

            if not self.has_next_page(response):
                break

            response = self.next_page_request(prev_response=response)
            iter_objs = self.iter_objects(response=response)
            page_count += 1
