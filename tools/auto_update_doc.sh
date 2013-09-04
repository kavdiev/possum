#!/bin/bash
cd /home/pos/possum-software
git pull >/dev/null 2>&1
if [ $? -gt 0 ]
then
    # update doc on each update
    source /home/pos/bin/activate
    cd /home/pos/possum-software/doc
    make html
fi

