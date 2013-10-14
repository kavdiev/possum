#!/bin/bash
# For the moment, we stay with python2.
# Must be execute like this: tools/create_virtualenv.sh
if [ -d .virtualenv ]
then
    echo ".virtualenv already exist"
else
    virtualenv --python=python2 .virtualenv
fi
echo "Launch your virtualenv with : 'source .virtualenv/bin/activate'"

