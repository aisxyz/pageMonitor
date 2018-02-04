#!/bin/bash
events='delete,modify,create,attrib,move,delete_self,move_self,unmount'
inotifywait -mrq --format '%w%f %e' -e ${events} $1 | while read file event
do
	echo "$event $file"
done