import json

from django.conf import settings
from elasticsearch import Elasticsearch

from core.constants import ElasticIndex


class ElasticService:
    def __init__(self, setting, data, partial=False, id=None, is_script=False):
        if not id:
            try:
                self.id = data["id"]
            except KeyError:
                raise AssertionError("No id found.")
        else:
            self.id = id
        if not partial and is_script:
            raise AssertionError("script is only allowed for partial updates")
        self.index = setting.index
        self.doc_type = setting.doc_type
        self.partial = partial
        if partial:
            self.body = {"doc": data}
            if is_script:
                self.body = {"script": data}
        else:
            self.body = data

    def __call__(self, **kwargs):
        retry_on_conflict = 0
        if kwargs.get('retry_on_conflict'):
            retry_on_conflict = kwargs.get('retry_on_conflict')
        es = Elasticsearch(settings.ES_HOST)
        if self.partial:
            es.update(index=self.index, doc_type=self.doc_type, id=self.id, body=self.body,
                      retry_on_conflict=retry_on_conflict)
        else:
            es.index(index=self.index, doc_type=self.doc_type, id=self.id, body=self.body, refresh='wait_for')


class BulkElasticService:
    def __init__(self, setting, data, ids: list):
        self.index = setting.index
        self.doc_type = setting.doc_type
        self.data = data
        assert len(ids), "Received empty list of ids."
        self.ids = ids

    def __call__(self):
        es = Elasticsearch(settings.ES_HOST)
        # Build bulk data
        bulk_data = []
        for id in self.ids:
            bulk_data.append(json.dumps({
                "update": {
                    "_index": self.index,
                    "_type": self.doc_type,
                    "_id": str(id)
                }
            }))
            bulk_data.append(json.dumps({"doc": self.data}))
        es.bulk(body="\n".join(bulk_data))


class ElasticDocIterator:
    """
    Iterator to fetch elasticsearch documents
    Example Usage:
        # Print all IDs of the applications created today
        for hit in ElasticDocIterator('Application', query={
            'query': {
                'bool': {
                    'filter': {
                        'range': {
                            'created': {'gte': 'now/d'}
                        }
                    }
                }
            }
        }):
            print(hit['_id'])

    """
    scroll_duration = '10m'

    def __init__(self, entity: ElasticIndex, query: dict = None):
        assert isinstance(entity, ElasticIndex), 'entity should be an object of ElasticIndex'
        self.es_index = entity.index
        self.es_doc_type = entity.doc_type
        self.es_client = Elasticsearch(settings.ES_HOST)
        self.query = query if query else self._match_all_query
        # Internal variables
        self._hits = []
        self._scroll_id = None

    @property
    def _match_all_query(self):
        return {
            'query': {'match_all': {}}
        }

    def __iter__(self):
        # First time scrolling, retrieve the next scroll id
        res = self.es_client.search(
            index=self.es_index,
            doc_type=self.es_doc_type,
            body=self.query,
            scroll=self.scroll_duration
        )
        self._scroll_id = res['_scroll_id']
        # Reversing the result as we are gonna pop the elements
        self._hits = list(reversed(res['hits']['hits']))
        return self

    def __next__(self):
        try:
            x = self._hits.pop()
        except IndexError:
            raise StopIteration
        # If the popped hit was the last element we need to fetch the next scroll
        if not len(self._hits):
            res = self.es_client.scroll(scroll_id=self._scroll_id, scroll=self.scroll_duration)
            self._scroll_id = res['_scroll_id']
            self._hits = res['hits']['hits']
        return x
