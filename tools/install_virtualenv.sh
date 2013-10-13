#!/bin/bash
source .virtualenv/bin/activate
pip install --proxy=$1 --requirement requirements.txt
