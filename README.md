# Reindex ES
This script reindex the current indexes to a remporary index and back to the original name, since Graylog requires the name to be the same. We need to use it in order to upgrade Opensearch instance.

#Run it
Run it like
```
ES_SERVER=opensearch-graylog.ktest.embl.de PYTHONWARNINGS="ignore:Unverified HTTPS request" START=333 END=340 BATCH=3 ES_USER=admin ES_PASS=xxxxxxxxxxxxxxxxxxxx python3.6 reindex.py
```
The credentials should be in passbolt.

For prod
```
ES_SERVER=eck-graylog.ops-kone.embl.de
```
