::

    sudo apt-get install apache2-mpm-worker libapache2-mod-wsgi
    sudo a2dismod status cgid autoindex auth_basic cgi dir env
    sudo a2dismod authn_file deflate setenvif reqtimeout negotiation
    sudo a2dismod authz_groupfile authz_user authz_default
    sudo a2enmod wsgi ssl


