#!/bin/bash
#
# awx_import <password> <filename>
#

TOWER_HOST=http://127.0.0.1:31768
TOWER_USERNAME=admin
TOWER_PASSWORD=$1
json=$(awx -k --conf.host $TOWER_HOST  --conf.username $TOWER_USERNAME --conf.password $TOWER_PASSWORD login)
#token=$(echo "$json" | sed 's/{.*"token":"\([^"]*\)".*}/\1/g')
token=$(echo "$json" | jq ".token"|tr -d '"')
echo $token
awx import -k --conf.host $TOWER_HOST --conf.token $token -f json < $2
