import sys
from elasticsearch import Elasticsearch, exceptions
#
# source_query = ''
#
# for line in sys.stdin:
#     source_query = str(line).strip()
#     #with open("/var/test.txt", "w") as text_file:
#     #    text_file.write("Pipe Output was: {}".format(source_query))
#     break

source_query = str(sys.argv[1]).strip()

# update all documents matching the source and running state
query = {
     "script": {
        "inline": "ctx._source.spider_state='debug'",
        "lang": "painless"
     },
     "query": {
        "bool": {
          "must": [
            {
              "match" : {
                "spider_state": "running"
              }
            },
            {
              "match" : {
                "source": "{}".format(source_query)
              }
            }
          ]
        }
     }
}

#print(query)
# fix this host to whatever es is reachable at
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])
#es = Elasticsearch()
es.update_by_query(body=query, doc_type='', index='_all')
