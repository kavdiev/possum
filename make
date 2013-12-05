#!/bin/bash
JQUERY="jquery-2.0.3.min.js"
HIGHCHARTS="Highcharts-3.0.6.zip"

function my_help {
    cat << 'EOF'

Usage: ./make [a command]

List of commands:
    doc                :  make the documentation in html
    help               :  this help
    deb_install        :  install required packages on Debian/Ubuntu (*)
    deb_install_apache :  install apache on Debian/Ubuntu (*)
    deb_install_nginx  :  install nginx on Debian/Ubuntu (*)
    init_demo          :  erase database with data of demonstration
    init_mine          :  run possum/utils/init_mine.py in virtualenv 
    model              :  generate doc/images/models-base.png
    sh                 :  run ./manage.py shell_plus in virtualenv
    run                :  run ./manage.py runserver_plus in virtualenv
    tests              :  make tests and coverage
    fasttu             :  make only the unit tests
    update             :  install/update Possum environnement

Note: If you need to define a proxy, set $http_proxy.
Example: export http_proxy="http://proxy.possum-software.org:8080/"

Note2: (*) must be root to do it

EOF
    exit 1
}

function enter_virtualenv {
    if [ ! -d .virtualenv ]
    then
        update
    fi
    source .virtualenv/bin/activate 2>/dev/null
    if [ ! $? -eq 0 ]
    then
        echo
        echo "Virtualenv does not work !"
        echo
        exit 2
    fi
}

function doc {
    enter_virtualenv
    cd doc
    make html
    echo "Documentation is in: doc/_build/html/"
}

function install_tests {
    # prerequis: sloccount csslint
    enter_virtualenv
    pip install --proxy=${http_proxy} django-jenkins pep8 pyflakes clonedigger \
        flake8 flake8-todo coverage >/dev/null
}

function tests {
    install_tests
    enter_virtualenv
    csslint possum/base/static/ --format=lint-xml --exclude-list=possum/base/static/jquery.min.js,possum/base/static/highcharts > reports/csslint.report
    flake8 --exclude=migrations --max-complexity 12 possum > reports/flake8.report
    clonedigger --cpd-output -o reports/clonedigger.xml $(find possum -name "*.py" | fgrep -v '/migrations/' | fgrep -v '/tests/' | xargs echo )
    sloccount --duplicates --wide --details possum | fgrep -v .git | fgrep -v '/migrations/' | fgrep -v '/static/highcharts/' > reports/soccount.sc
    ./manage.py jenkins
    echo "> $?"
    return $?
#    ./manage.py test base 
}

function fasttu {
    install_tests
    enter_virtualenv
    python -Wall manage.py test base --settings=possum.settings_tests --verbosity=2 --traceback
}

function update_js {
    # update javascript part
    if [ ! -e possum/base/static/jquery.min.js ]
    then
        echo "Download and install JQuery..."
        wget http://code.jquery.com/${JQUERY} -O possum/base/static/jquery.min.js
    fi

    if [ ! -d possum/base/static/highcharts ]
    then
        mkdir -v possum/base/static/highcharts
    fi
    if [ ! -e possum/base/static/highcharts/${HIGHCHARTS} ]
    then
        echo "Download HighCharts..."
        wget http://code.highcharts.com/zips/${HIGHCHARTS} -O possum/base/static/highcharts/${HIGHCHARTS}
    fi
    if [ ! -e possum/base/static/highcharts/js/highcharts.js ]
    then
        echo "Unzip HighCharts..."
        pushd possum/base/static/highcharts/ >/dev/null
        unzip Highcharts-3.0.6.zip
        popd >/dev/null
    fi
    enter_virtualenv
    ./manage.py collectstatic --noinput --no-post-process
}

function update {
    echo
    echo "Host must be connected to Internet for this step."
    echo "And you must have some packages installed:"
    echo "Debian/Ubuntu> ./make deb_install"
    echo
    if [ ! -d .virtualenv ]
    then
        # For the moment, we stay with python2.
        virtualenv --prompt=="POSSUM" --python=python2 .virtualenv
    fi
    enter_virtualenv
    pip install --proxy=${http_proxy} --requirement requirements.txt
    update_js
    if [ ! -e possum/settings.py ]
    then
        # default conf is production
        cp possum/settings_production.py possum/settings.py
        ./manage.py syncdb --noinput --migrate
        possum/utils/init_db.py
        cat << 'EOF'
-------------------------------------------------------
To use Possum, copy and adapt possum/utils/init_db.py.

Example:
  cp possum/utils/init_db.py possum/utils/init_mine.py
  # adapt possum/utils/init_yours.py file
  # and execute it
  ./make init_mine
-------------------------------------------------------
EOF
    fi
    ./manage.py migrate base
}

function deb_install_apache {
    sudo apt-get install apache2-mpm-worker libapache2-mod-wsgi
    a2dismod status cgid autoindex auth_basic cgi dir env
    a2dismod authn_file deflate setenvif reqtimeout negotiation
    a2dismod authz_groupfile authz_user authz_default
    a2enmod wsgi ssl
    echo 
    echo "Config example for http in: possum/utils/apache2.conf"
    echo "Config example for https in: possum/utils/apache2-ssl.conf"
    echo "To use one:"
    echo "  cp possum/utils/apache2-ssl.conf /etc/apache2/sites-available/possum"
    echo "  a2dissite default"
    echo "  a2ensite possum"
    echo
}

function deb_install_nginx {
    sudo apt-get install nginx-light supervisor
    echo 
    echo "Config example for Supervisor: possum/utils/supervisor.conf"
    echo "  cp possum/utils/supervisor.conf /etc/supervisor/conf.d/possum.conf"
    echo "  /etc/init.d/supervisor restart"
    echo
    echo "Config example for NGinx: possum/utils/nginx-ssl.conf"
    echo "  cp possum/utils/nginx-ssl.conf /etc/nginx/sites-enabled/default"
    echo "  /etc/init.d/nginx restart"
    echo
}

function deb_install {
    sudo apt-get install graphviz-dev graphviz libcups2-dev memcached \
        python-virtualenv unzip \
        pkg-config python-dev cups-client cups
#    deb_install_apache
}

if [ ! $# -eq 1 ]
then
    my_help
fi

case "$1" in
init_mine)
    enter_virtualenv
    possum/utils/init_mine.py
    ;;
init_demo)
    enter_virtualenv
    possum/utils/init_demo.py
    ;;
deb_install)
    deb_install
    ;;
deb_install_apache)
    deb_install_apache
    ;;
fasttu)
    fasttu
    ;;
deb_install_nginx)
    deb_install_nginx
    ;;
doc)
    doc
    ;;
model)
    enter_virtualenv
    ./manage.py graph_models --output=doc/images/models-base.png -g base
    echo "[doc/images/models-base.png] updated"
    ;;
update)
    update
    ;;
tests)
# TODO: diff sur le settings.py et backup de securite
#    if [ ! -e possum/settings.py ]
#    then
#    cp possum/settings_tests.py possum/settings.py
#    fi
    update >/dev/null
    tests
    doc >/dev/null
    ;;
sh)
    enter_virtualenv
    ./manage.py shell_plus
    ;;
run)
    enter_virtualenv
    ./manage.py runserver
    ;;
*)
    my_help
    ;;
esac
