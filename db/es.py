from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index = 'upload_service_index'

def insert_file_metadata(data, index_=index):
  es.index(index_, doc_type='docs', body=data)
    