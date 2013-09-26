Installation
============

Cette documentation est écrite pour GNU/Linux, et devrait fonctionner avec toutes les distributions (Ubuntu, Gentoo, ...).

Vous devez avoir python et virtualenv installés sur votre système.

Création de l'utilisateur POS
-----------------------------

::

 sudo adduser pos

Dans notre exemple, nous allons installer Possum dans le répertoire ''/home/pos''. Vous
pouvez évidemment choisir un autre répertoire si vous le souhaitez.

Impression
----------

Possum peut imprimer sur plusieurs imprimantes. Afin de pouvoir les utiliser, il faut avoir
un serveur cups configurer sur le serveur. Vous pouvez vérifier que les imprimantes sont bien
disponibles avec la commande:

::

  lpstat -v

D'autre part, l'impression des tickets nécessite la création et la suppression de nombreux
fichiers. Je vous recommande donc d'utiliser un système de fichier virtuel type tmpfs pour
ce répertoire (variable ''PATH_TICKET'' du fichier ''settings.py'').

Possum
------

Vous avez ici 2 possibilités, soit télécharger la dernière version
stable de POSSUM ici: `GitHub <https://github.com/possum-software/possum/archives/master>`_

::

  tar xzf possum-software-possum-*.tar.gz

L'autre possibilité est de récupérer la version en développement:

::

  git clone https://github.com/possum-software/possum.git possum-software

Prérequis
^^^^^^^^^

Il faut dans un premier temps installer l'outil virtualenv pour python si ce n'est déjà fait. 
Voir `VirtualEnv <https://pypi.python.org/pypi/virtualenv>`_

:: 

  su - pos
  virtualenv --prompt=='possum ' --python=python2 /home/pos

On va maintenant préparer cet environnement. Pour pouvoir installer pycups, il faut les 
outils de compilation et la bibliothèque ''libcups2-dev''.


::

  apt-get install libcups2-dev
  
  source /home/pos/bin/activate 
  pip install -r requirements.txt


Note: il faudra utiliser ''deactivate'' pour sortir du virtualenv Possum une fois toute
la configuration terminée.


Configuration
^^^^^^^^^^^^^

Maintenant, nous devons configurer POSSUM.

::

  cd /home/pos/possum-software/possum
  cp settings.py-sample settings.py

Pour les développeurs, je vous conseille de prendre plutôt le
fichier ''settings.py-dev''.

La base de données configurée par défaut est Sqlite3. À vous d'adapter le fichier
de configuration a vos besoins. Il faudrat au minimum modifier la variable ''SECRET_KEY''.

Pour plus d'informations
reportez vous à la documentation de Django:
`Installation de Django <http://docs.django-fr.org/intro/install.html>`_

Création de la base pour l'application et mise à jour des schémas:

::

  cd /home/pos/possum-software
  ./manage.py syncdb --noinput --migrate

Il nous faut maintenant définir quelques objets de base en exécutant
le script: ''possum/utils/init_db.py''. Je vous conseille d'adapter
le contenu de ce fichier (notamment l'utilisateur par défaut).

::

  cd /home/pos/possum-software
  possum/utils/init_db.py

Il existe un fichier plus complet d'initialisation qui est utilisé pour le
`site de démonstration <http://demo.possum-software.org/>`_. Ce fichier est:
''possum/utils/init_demo.py''.

Avant d'aller plus loin, vous pouvez tester le bon fonctionnement de l'ensemble en utilisant
le serveur de développement:

::

  cd /home/pos/possum-software
  ./manage.py runserver_plus 0.0.0.0:8000

Vous devez pouvoir accèder à l'interface web. 

À ce stade, vous pouvez également générer la documentation au format HTML dans le 
répertoire ''/home/pos/possum-software/doc/_build/html/'':

::

  cd /home/pos/possum-software/doc
  make html


Installation d'Apache
---------------------

Nous devons tout d'abord installer le serveur web Apache et le module mod_wsgi.

CentOS
^^^^^^

::

  yum install mod_wsgi

Gentoo
^^^^^^

::

  emerge -av www-servers/apache www-apache/mod_wsgi

Ubuntu
^^^^^^

::

  sudo apt-get install apache2 libapache2-mod-wsgi
  sudo a2enmod wsgi

Il faut éditer le fichier de configuration du serveur web pour activer
POSSUM. Le fichier par défaut doit être /etc/apache2/sites-enabled/default.

Configuration d'Apache
----------------------

Nous allons maintenant configurer le serveur web.
Vous trouverez la documentation officiel de Django 
`ici <https://docs.djangoproject.com/en/1.5/howto/deployment/wsgi/modwsgi/>`_

Voici un exemple avec possum accessible à l'adresse: '/'

::

  Alias /robots.txt /home/pos/possum-software/possum/static/robots.txt
  Alias /favicon.ico /home/pos/possum-software/possum/static/favicon.ico
  Alias /media/ /home/pos/possum-software/possum/media/
  Alias /static/ /home/pos/possum-software/possum/static/

  <Directory /home/pos/possum-software/possum/static>
      Order deny,allow
      Allow from all
  </Directory>

  <Directory /home/pos/possum-software/possum/media>
      Order deny,allow
      Allow from all
  </Directory>

  WSGIScriptAlias / /home/pos/possum-software/possum/wsgi.py
  WSGIPythonPath /home/pos/possum-software:/home/pos/lib/python2.7/site-packages
  #WSGIDaemonProcess possum python-path=/home/pos/possum-software:/home/pos/lib/python2.7/site-packages
  #WSGIProcessGroup possum

  <Directory /home/pos/possum-software/possum>
      <Files wsgi.py>
          Order deny,allow
          Require all granted
      </Files>
  </Directory>


Ensuite il faut redémarrer le serveur web:

::

  service apache2 restart

Mail
----

Il est préférable d'avoir un serveur de mail configurer sur le poste. En
effet, POSSUM peut envoyé des messages s'il y a des tentatives d'accès
au panneau d'administration ou des bugs.

::

  sudo apt-get install postfix bsd-mailx

  Système satellite : Tous les messages sont envoyés vers une autre machine, nommée un smarthost.
  Nom de courrier : possum (ou le nom que vous voulez)
  Serveur relais SMTP (vide pour aucun) :
  Destinataire des courriels de « root » et de « postmaster » : votre_adresse_mail@example.org
  Autres destinations pour lesquelles le courrier sera accepté (champ vide autorisé) : possum, localhost.localdomain, localhost
  Faut-il forcer des mises à jour synchronisées de la file d'attente des courriels ? Non
  Réseaux internes : 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
  Taille maximale des boîtes aux lettres (en octets) : 0
  Caractère d'extension des adresses locales : +
  Protocoles internet à utiliser : tous

Si tout est bien configurer, vous devriez recevoir un mail avec comme
sujet ''test'' et dans le message la date d'envoie en utilisant la
commande suivante:

::

  date | mail -s test root




L'installation est presque terminée, vous devez maintenant configurer
la sauvegarde automatique de la base de données. Cette partie dépend du
type de base que vous avez choisi. La plus simple étant la base sqlite,
sa sauvegarde se limite à la copie d'un fichier.

Pour accéder à POSSUM, il suffit de lancer un navigateur web.



Configuration initiale
----------------------

Malheureusement, il n'y a pas encore d'interface web pour la modification
et la saisie des produits, cela doit être fait à la main pour le moment.

À partir de la version 0.5 une interface web de gestion sera en place et
la documentation sera faire à ce moment là.

Exemple de Matériels
--------------------

Pour finir, voici un exemple de matériels utilisés et qui fonctionne:

PC:

- carte Mini ITX VIA M6000G
- Asus EEE PC
- Shuttle SD11G5

Écran tactile:

- ELo Touch 1515L

À noter que le support de la part de EloTouch est plutôt
moyen. Je vous conseille ce site: `EloTouchScreen <https://help.ubuntu.com/community/EloTouchScreen>`_

Imprimante à ticket:

- Epson MT M88 iv
