import elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection
#import opensearchpy
#from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
import time
import os
from multiprocessing import Process
from datetime import datetime

ES_USER = os.getenv('ES_USER')
ES_PASS =  os.getenv('ES_PASS')
ES_SERVER = os.getenv('ES_SERVER')
start_index = int(os.getenv('START'))
end_index = int(os.getenv('END'))
batch_size = int(os.getenv('BATCH'))

# Function to reindex an index
def reindex_index(es, source_index, target_index):
    body = {
        "source": {
            "index": source_index
        },
        "dest": {
            "index": target_index
        }
    }
    es.reindex(body=body, wait_for_completion=True, request_timeout=1000000000)

# Function to create and modify index settings
def create_index_settings(es, index_name, primary_shards, replica_shards):
    body = {
        "settings": {
            "number_of_shards": primary_shards,
            "number_of_replicas": replica_shards
        }
    }
    es.indices.create(index=index_name, body=body, request_timeout=1000000000)

def full_reindex(index):
    count = es.count(index=index, request_timeout=100)['count']
    print(f"Document count func in index {batch_indices}: {count}")
    
    temp_index = f"temp_{index}"
    print("Temp_index: ", temp_index)
    # Update settings for the temporary index
    create_index_settings(es, temp_index, primary_shards=4, replica_shards=0)

    # Reindex to temporary index
    reindex_index(es, index, temp_index)

    # Delete original index
    es.indices.delete(index=index, request_timeout=1000000000)
    # Update settings for the temporary index
    create_index_settings(es, index, primary_shards=4, replica_shards=0)
    # Reindex back to original index
    reindex_index(es, temp_index, index)

    # Delete the temporary index
    es.indices.delete(index=temp_index, request_timeout=1000000000)

    print(f"Reindexed {index} to {temp_index} and back to {index} with new settings.")
    count = es.count(index=index, request_timeout=100)['count']

    print(f"Document count in index {index}: {count}")



# Elasticsearch connection
es = Elasticsearch(hosts=[{'host': ES_SERVER, 'port': 443}],
                   http_auth=(ES_USER, ES_PASS),
                   use_ssl= 'true',
                   connection_class=RequestsHttpConnection,
                   verify_certs=False)


print("Reindexing starting.")

time_seconds_beg = int(time.time())

for i in range(start_index, end_index + 1, batch_size):
    batch_indices = [f"graylog_{j}" for j in range(i, min(i + batch_size, end_index + 1))]
    print("Batch indices: ", batch_indices) 


    for index in batch_indices:
        globals()[index] = Process(target=full_reindex, args=(index,))
        globals()[index].start()
        print("Print process: ", globals()[index])
        #time.sleep(60)
        #full_reindex(index)

    for i in range(0, len(batch_indices), 1):
        print("iterem", i)
        print(batch_indices[i])
        globals()[batch_indices[i]].join()

    print("----------------------------------------------")
    print("New batch")
    print("----------------------------------------------")

    

print("Reindexing completed.")

time_seconds_fin = int(time.time())
total_time = time_seconds_fin - time_seconds_beg
print("Total time in seconds:", total_time)