#!/bin/bash
JQUERY="jquery-2.0.3.min.js"
HIGHCHARTS="Highcharts-3.0.6.zip"
APPS="base stats"

function my_help {
    cat << 'EOF'

Usage: ./make [a command]

List of commands:
    create_json_demo   :  create JSON fixtures in possum/base/fixtures/demo.json
    doc                :  make the documentation in html
    deb_install_apache :  install apache on Debian/Ubuntu (*)
    deb_install_nginx  :  install nginx on Debian/Ubuntu (*)
    fastcoverage       :  make only the unit tests and display the coverage in your browser
    utests             :  make only the unit tests
    help               :  this help
    init_demo          :  erase database with data of demonstration
    init_mine          :  run possum/utils/init_mine.py in virtualenv
    load_demo          :  load database with data of demonstration
    model              :  generate doc/images/models-base.png
    models_changed     :  prepare files after modified models
    sh                 :  run ./manage.py shell_plus in virtualenv
    run                :  run ./manage.py runserver_plus in virtualenv
    tests              :  make tests and coverage
    update             :  install/update Possum environnement

Note: If you need to define a proxy, set $http_proxy.
Example: export http_proxy="http://proxy.possum-software.org:8080/"

Note2: (*) must be root to do it

EOF
    exit 1
}

function enter_virtualenv {
    if [ ! -d env ]
    then
        update
    fi
    source env/bin/activate 2>/dev/null
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
    for translation in en fr
    do
        pushd docs/$translation
        make html
        popd
    done
}

function create_json_demo {
    enter_virtualenv
    ./manage.py dumpdata --format=json --indent=4 --exclude=contenttypes --exclude=auth.Permission > possum/base/fixtures/demo.json
}

function tests {
    enter_virtualenv
    if [ ! -d reports ]
    then
        mkdir reports
    fi
    ./manage.py validate_templates --settings=possum.settings_tests
    if [ ! $? == 0 ]
    then
        exit $?
    fi
    csslint possum/base/static/possum --format=lint-xml > reports/csslint.report
    flake8 --exclude=migrations --max-complexity 12 possum > reports/flake8.report
    clonedigger --cpd-output -o reports/clonedigger.xml $(find possum -name "*.py" | fgrep -v '/migrations/' | fgrep -v '/tests/' | xargs echo )
    sloccount --duplicates --wide --details possum | fgrep -v .git | fgrep -v '/migrations/' | fgrep -v '/highcharts/' > reports/soccount.sc
    ./manage.py jenkins --settings=possum.settings_tests
    utests
    exit $?
}

function utests {
    enter_virtualenv
    ./manage.py test --settings=possum.settings_tests
    return $?
}

function fastcoverage {
    enter_virtualenv
    coverage run --source=possum manage.py test --settings=possum.settings_tests --verbosity=2 --traceback
    coverage html
    x-www-browser htmlcov/index.html
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
#    chmod 755 possum/static/
    if [ ! -d env ]
    then
        echo
        echo "Host must be connected to Internet for this step."
        echo "And you must have some packages installed:"
        echo "You must read documentation :)"
        echo
        # For the moment, we stay with python2.
        virtualenv --python=python2 env
    fi
    enter_virtualenv
    pip -q install --proxy=${http_proxy} --requirement requirements.txt --upgrade
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
    if [ ! -e possum.db ]
    then
        ./manage.py syncdb --noinput --migrate
    fi
    ./manage.py migrate
    possum/utils/update_categories_css.py
}

function deb_install_apache {
    sudo apt-get install apache2-mpm-worker libapache2-mod-wsgi
    a2dismod status cgid autoindex auth_basic cgi dir env
    a2dismod authn_file deflate setenvif reqtimeout negotiation
    a2dismod authz_groupfile authz_user authz_default
    a2enmod wsgi ssl
    echo
    echo "Config example for https in: possum/utils/apache2.conf"
    echo "To use one:"
    echo "  cp possum/utils/apache2.conf /etc/apache2/sites-available/possum.conf"
    echo "  a2dissite 000-default.conf"
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

function graph_models {
    enter_virtualenv
    for app in $APPS
    do
        ./manage.py graph_models --output=docs/images/models-${app}.png -g ${app}
        echo "[docs/images/models-${app}.png] updated"
    done
}

function clear_db {
    enter_virtualenv
    if [ -e possum.db ]
    then
        if [ ! -d backup ]
        then
            mkdir backup
        fi
        mv possum.db backup/possum.db.$(date +%Y%m%d%H%M)
    fi
    ./manage.py syncdb --noinput --migrate
#    ./manage.py flush --noinput
}

if [ ! $# -eq 1 ]
then
    my_help
fi

case "$1" in
create_json_demo)
    create_json_demo
    ;;
init_mine)
    enter_virtualenv
    clear_db
    possum/utils/init_mine.py
    ;;
init_demo)
    enter_virtualenv
    clear_db
    possum/utils/init_demo.py
    ;;
load_demo)
    enter_virtualenv
    clear_db
    ./manage.py syncdb --noinput --migrate
    ./manage.py loaddata demo
    ;;
deb_install_apache)
    deb_install_apache
    ;;
utests)
    utests
    ;;
fastcoverage)
    fastcoverage
    ;;
deb_install_nginx)
    deb_install_nginx
    ;;
doc)
    doc
    ;;
model)
    graph_models
    ;;
update)
    update
    ;;
models_changed)
    enter_virtualenv
    ./manage.py syncdb --noinput --migrate
    ./manage.py schemamigration base --auto
    ./manage.py schemamigration stats --auto
    ./manage.py migrate
    clear_db
    possum/utils/init_demo.py
    create_json_demo
    graph_models
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
