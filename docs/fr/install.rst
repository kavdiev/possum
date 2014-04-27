Installation
============

Cette documentation est écrite pour Debian, et devrait fonctionner avec toutes les distributions (Ubuntu, Gentoo, ...).

Voici le schéma général des différentes briques logiciels:

.. image:: ../images/overview_apache.png
    :scale: 50
    :alt: Overview

Possum
------

Vous avez ici 2 possibilités, dans tous les cas, il faudra se positionner dans un répertoire.
Prenons le répertoire **/opt**:

::

  cd /opt

Soit on utilise la dernière version à jour:

::

  git clone https://github.com/possum-software/possum.git possum-software

Soit on télécharge la dernière version
stable de POSSUM ici: `GitHub <https://github.com/possum-software/possum/releases>`_

::

  tar xzf possum-software-possum-*.tar.gz

Nous allons prendre la première option.

Prérequis
---------

Possum nécessite l'installation de quelques paquets.

Pour un système Debian/Ubuntu:

.. include:: ../common/install_deb.rst


Ensuite pour l'installation ou les mises à jours, nous allons encore utiliser la
commande **./make**:

::

  ./make update

Cette opération va installer et configurer tout l'environnement virtuel nécessaire
à Possum.

Il nous reste maintenant à initialiser les données, pour cela il est recommandé
de copier le fichier d'initialisation **possum/utils/init_db.py**. Pour un exemple
plus complet, vous pouvez vous inspirer du fichier **possum/utils/init_demo.py**:

::

  cp possum/utils/init_db.py possum/utils/init_mine.py
  # adapt file possum/utils/init_mine.py and run it:
  ./make init_mine

Impression
----------

Possum peut imprimer sur plusieurs imprimantes. Afin de pouvoir les utiliser, il faut avoir
un serveur cups configurer sur le serveur. Vous pouvez vérifier que les imprimantes sont bien
disponibles avec la commande:

::

  lpstat -v

Vous pouvez configurer le serveur d'impression via une interface web, en général à l'adresse
suivante: `Cups <http://localhost:631>`_

D'autre part, l'impression des tickets nécessite la création et la suppression de nombreux
fichiers. Je vous recommande donc d'utiliser un système de fichier virtuel type tmpfs pour
le répertoire **tickets** qui se trouve par défaut dans le répertoire **possum-software**.

Par exemple, si le chemin absolu vers votre répertoire **tickets** est 
**/opt/possum-software/tickets/**, il faudra ajouter la ligne suivante dans votre 
fichier **/etc/fstab**:

::

  tmpfs /opt/possum-software/tickets/ tmpfs defaults,nodev,nosuid 0 0


Cela peut être fait avec les commandes suivantes (en étant root):

::

  echo "tmpfs /opt/possum-software/tickets/ tmpfs defaults,nodev,nosuid 0 0" >> /etc/fstab
  mount /opt/possum-software/tickets/

Documentation
-------------

Vous pouvez générer la documentation en html avec la commande suivante:

::

  source env/bin/activate
  cd docs/fr
  make html
  deactivate

Elle sera disponible ici: **/opt/possum-software/docs/fr/_build/html/**.

Sinon elle est également disponible sur le site officiel:
`Documentation <http://possum.readthedocs.org>`_.

Configuration du serveur Web
----------------------------

Nous avons besoin maintenant d'un serveur web. Il y a plusieurs possibilités,
celle-ci se base sur le serveur web `Apache <http://httpd.apache.org/>`_.

En bref, le module `mod_wsgi <http://code.google.com/p/modwsgi/>`_ servira
à exécuter Possum.

Commençons par installer les paquets nécessaires:

.. include:: ../common/install_apache_deb.rst

Il reste la configuration à faire. Pour cela, il y a des configurations type dans 
le répertoire **possum/utils/**.

Par exemple, pour une configuration standard et sécurisée:

::

  sudo cp possum/utils/apache2.conf /etc/apache2/sites-available/possum.conf

Il faudra modifier le fichier **/etc/apache2/sites-available/possum.conf**
pour l'adapter à votre installation, puis:

::

  sudo a2dissite 000-default.conf
  sudo a2ensite possum
  sudo service apache2 restart


La configuration conseillée utilise du **https** afin
de sécuriser les échanges entre les clients et le serveur. Pour utiliser 
cette configuration, le 
fichier **/etc/hosts** doit être correctement configuré. 

Exemple:

::

  # hostname
  possum

Ici, le serveur s'appelle **possum**.

::

  # on donne les droits nécessaires au serveur web sur le répertoire
  # possum-software
  chown -R www-data /opt/possum-software
  # création des certificats SSL
  make-ssl-cert generate-default-snakeoil --force-overwrite


Rapports & statistiques
-----------------------

Afin de construire les différents rapports et d'afficher les graphiques
un certain nombre de statistiques doivent être calculés sur les factures
qui sont soldées. Ces calculs peuvent être couteux en temps, cela est
visible lorsque l'on accède à la partie **Manager/rapports**.

Pour palier à ce problème, il est recommandé de mettre à jour ces informations
tout au long de la journée en utilisant la crontab GNU/Linux.

Pour cela, il faudra adapter le fichier **possum/utils/update_stats.sh** dans 
lequel vous devrez modifier la ligne suivante en indiquant votre répertoire
d'installation:

::

  pushd /opt/possum-software >/dev/null


Ensuite, il suffit d'enregistrer l'exécution automatique de cette commande
à l'aide de la commande **crontab -e** (pour plus d'informations: **man crontab**).

Voici un exemple:

::

  # à 11h20 tous les jours
  20 11 * * * /opt/possum-software/possum/utils/update_stats.sh
  # après le service du midi, à 14h30 tous les jours
  30 14 * * * /opt/possum-software/possum/utils/update_stats.sh
  # avant le service du soir, à 18h30 tous les jours
  30 18 * * * /opt/possum-software/possum/utils/update_stats.sh


Mail
----

Il est préférable d'avoir un serveur de mail configurer sur le poste. En
effet, POSSUM peut envoyé des messages s'il y a des tentatives d'accès
au panneau d'administration ou des bugs.

::

  sudo apt-get install postfix bsd-mailx

  Configuration type du serveur de messagerie: Site Internet
  Nom de courrier : possum (ou le nom que vous voulez)

Il est conseillé de définir un alias pour l'utilisateur root dans le fichier 
**/etc/aliases**. Dans ce cas, vous aurez une ligne du type:

::

  root: votre_adresse@possum-software.org

Cet alias vous permettra de recevoir les éventuelles alertes du système d'exploitation.
Après chaque modification de ce fichier, il faut lancer la commande:

::

  sudo newaliases

Si tout est bien configurer, vous devriez recevoir un mail avec comme
sujet **test** et dans le message la date d'envoie en utilisant la
commande suivante:

::

  date | mail -s test root


L'installation est presque terminée, vous devez maintenant configurer
la sauvegarde automatique de la base de données. Cette partie dépend du
type de base que vous avez choisi. La plus simple étant la base sqlite,
sa sauvegarde se limite à la copie d'un fichier.

Pour accéder à POSSUM, il suffit de lancer un navigateur web.

Arrêt du serveur
----------------

Afin d'arrêter proprement le serveur, on peut configurer une commande **sudo**
qui permettra au serveur Apache de lancer l'arrêt du serveur (à condition qu'il
n'y ai pas de calcul des statistiques en cours). Avec la commande **visudo**,
vous pouvez ajouter la ligne suivante:

::

  www-data ALL=(ALL) NOPASSWD: /sbin/shutdown

