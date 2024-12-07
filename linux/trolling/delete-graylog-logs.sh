#!/bin/bash

alias="graylog_deflector"
index="graylog_4"

# Delete the alias
curl -k -x DELETE "http://172.20.90.77:9200/${alias}"

# Set up the JSON data for alias change
json_data='
{
  "actions" : [
    { "remove" : { "index" : "*", "alias" : "'"${alias}"'" } },
    { "add" : { "index" : "'"${index}"'", "alias" : "'"${alias}"'" } }
  ]
}
'

# delete index
curl -k -X POST "http://172.20.90.77:9200/_aliases" -H 'Content-Type: application/json' -d "${json_data}"
curl -k -X DELETE http://172.20.90.77:9200/graylog_5