#!/bin/bash

counter=0
while :
do
    let "counter += 1"
    echo $counter
    sleep 0.1s
done

