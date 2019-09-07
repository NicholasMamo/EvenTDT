#!/bin/bash

for file in `ls -v rouge/out/$1/$2/$3*`; do
	cat $file
	echo ""
done
