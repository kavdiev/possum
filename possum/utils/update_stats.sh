#!/bin/bash
pushd /opt/possum-software >/dev/null
source .virtualenv/bin/activate
possum/utils/update_stats.py
deactivate
popd >/dev/null
