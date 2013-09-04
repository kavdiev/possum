#!/bin/bash
cd /home/pos/possum-software
NBLINE=$(git pull 2>&1 | wc -l)
if [ $NBLINE -gt 1 ]
then
    # update doc on each update
    source /home/pos/bin/activate
    cd /home/pos/possum-software/doc
    make html
fi

