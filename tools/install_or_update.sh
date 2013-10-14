#!/bin/bash
#
# Host must be connected to Internet.
#
# This script will install and update environnement for Possum.
# One parameter could be proxy.
#
JQUERY="jquery-2.0.3.min.js"
HIGHCHARTS="Highcharts-3.0.6.zip"

if [ "$0" != "tools/install_or_update.sh" ]
then
    echo "Must be execute as: tools/install_or_update.sh !"
    exit 1
fi
if [ ! -d .virtualenv ]
then
    # For the moment, we stay with python2.
    virtualenv --python=python2 .virtualenv
fi
source .virtualenv/bin/activate
pip install --proxy=$1 --requirement requirements.txt

if [ ! -e possum/static/jquery.min.js ]
then
    echo "Download and install JQuery..."
    wget http://code.jquery.com/${JQUERY} -O possum/static/jquery.min.js
fi

if [ ! -d possum/static/highcharts ]
then
    mkdir -v possum/static/highcharts
fi
if [ ! -e possum/static/highcharts/${HIGHCHARTS} ]
then
    echo "Download HighCharts..."
    wget http://code.highcharts.com/zips/${HIGHCHARTS} -O possum/static/highcharts/
fi
if [ ! -e possum/static/highcharts/js/highcharts.js ]
then
    echo "Unzip HighCharts..."
    pushd possum/static/highcharts/ >/dev/null
    unzip Highcharts-3.0.6.zip
    popd >/dev/null
fi

# MAJ Database
# TODO: init & install ? 
# ./manage.py syncdb --noinput --migrate
# possum/utils/init_db.py
./manage.py migrate base
