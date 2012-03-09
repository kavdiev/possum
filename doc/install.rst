Installation
============

Cette documentation est écrite pour une distribution GNU/Linux Ubuntu 11.04.

Utilisateur
-----------

Tout d'abord, nous allons créer un utilisateur ''pos'' qui aura comme ''home'' : /home/pos:

::

  sudo adduser pos

Django
------

Installation de Django:

::

  sudo apt-get install python-django python-werkzeug

Il est conseillé de prendre au minimum une version 1.3.


Possum
------

Vous avez ici 2 possibilités, soit télécharger la dernière version
stable de POSSUM ici: `GitHub <https://github.com/possum-software/possum/archives/master>`_

::

  su - pos
  cd
  tar xzf possum-software-possum-*.tar.gz
  ln -sf /home/pos/possum-software-possum-??????? possum-software

L'autre possibilité est de récupérer la version en développement. Attention,
il est déconseillé de se servir de cette version dans un environnement
de production:

::

  sudo apt-get install git
  su - pos
  cd
  git clone git://github.com/possum-software/possum.git possum-software

Maintenant, nous devons configurer POSSUM.

::

  cd
  cd possum-software/possum
  cp settings.py-sample settings.py

La base de données configurée par défaut est Sqlite, pour plus d'informations
reportez vous à la documentation de Django:
`Installation de Django <http://docs.django-fr.org/intro/install.html>`_

Création de la base pour l'application:

::

  cd
  cd possum-software/possum
  ./manage.py syncdb

  You just installed Django's auth system, which means you don't have any superusers defined.
  Would you like to create one now? (yes/no): yes
  Username (Leave blank to use 'pos'): my_login
  E-mail address: my.login@example.org
  Password:
  Password (again):
  Superuser created successfully.


Il faut ensuite donner les droits minimums à cet utilisateur:

::

  cd
  cd possum-software/possum
  ./manage.py shell_plus
  u = User.objects.get(pk=1)
  u.user_permissions.add(Permission.objects.get(codename="p1"))
  u.save()
  quit()

Apache
------

Nous allons maintenant configurer le serveur web:

::

  sudo apt-get install apache2 libapache2-mod-python
  sudo a2enmod python

Il faut éditer le fichier de configuration du serveur web pour activer
POSSUM. Le fichier par défaut doit être /etc/apache2/sites-enabled/default.

Voici un exemple avec possum accessible à l'adresse: '/'

::

  <Location "/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE possum.settings
        PythonAutoReload On
        PythonOption django.root /
        PythonDebug Off
        PythonPath "['/home/pos/possum-software/'] + sys.path"
  </Location>
  Alias /static/ /home/pos/possum-software/possum/static/
  <Location "/static/">
        SetHandler None
  </Location>

Voici un autre exemple avec possum accessible à l'adresse: '/possum'

::

  <Location "/possum/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE possum.settings
        PythonAutoReload On
        PythonOption django.root /possum/
        PythonDebug Off
        PythonPath "['/home/pos/possum-software/'] + sys.path"
  </Location>
  Alias /possum/static/ /home/pos/possum-software/possum/static/
  <Location "/possum/static/">
        SetHandler None
  </Location>

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
