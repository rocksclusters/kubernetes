#!/bin/bash
if [ "x$DATASTORE_TYPE" == "x" ]; then
	export DATASTORE_TYPE=kubernetes 
fi
