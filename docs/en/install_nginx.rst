Configuration du serveur Web NGinx
==================================

Voici le schéma général des différentes briques logiciels:

.. image:: ../images/overview_nginx.png
    :scale: 50
    :alt: Overview

Nous avons besoin maintenant d'un serveur web. Il y a plusieurs possibilités,
celle-ci est à priori la plus performante.

La solution à base de `NGinx <http://nginx.org/>`_, `Gunicorn <http://gunicorn.org/>`_ 
et `Supervisor <http://supervisord.org/>`_ semble à première
vue compliquée.

Commençons par installer les paquets nécessaires:

::

  ./make deb_install_nginx


Il reste la configuration à faire. Pour cela, il y a des configurations type dans 
le répertoire **possum/utils/**.

On configure maintenant **Supervisor** qui s'occupera de lancer **Possum**:

::

  cp possum/utils/supervisor.conf /etc/supervisor/conf.d/possum.conf
  /etc/init.d/supervisor restart

Pour **NGinx**:

::

  cp possum/utils/nginx-ssl.conf /etc/nginx/sites-enabled/default
  /etc/init.d/nginx restart


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

