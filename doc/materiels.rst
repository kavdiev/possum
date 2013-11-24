Matériels
=========

Il y a ici une liste de matériels afin de vous donnez une idée
des options possibles. Cette liste n'est pas exaustive, n'hésitez
pas à nous contacter pour la complèter.

Serveurs
--------

Les performances du serveur sont importantes pour Possum, cela aura un impact
direct sur la réactivité de la prise de commande.

De plus, si vous utilisez également ce serveur pour faire de la saisie, il
faudra également le prévoir au niveau des performances.

Afin de classer les différentes solutions, on utilise la base de
démonstration et la commande ''Apache Benchmark'' sur 3 essais consécutifs.
Évidemment, on désactive l'authentification le temps de faire le test.

::

  ab -t 30 -c 5 https://127.0.0.1/bills/ | grep 'Requests per second:'


======================= ========= ========== ========== ================
Matériel                essai 1   essai 2    essai 3    logiciels
======================= ========= ========== ========== ================
Raspberry 512Mo type B   1.35      1.88       1.83      raspbian / nginx
Mini-ITX VIA M6000G
Shuttle SD11G5          13.31     13.83      13.80      nginx
======================= ========= ========== ========== ================


Écrans tactiles
---------------

* ELo Touch 1515L

À noter que le support de la part de EloTouch est plutôt
moyen. Je vous conseille ce site: `EloTouchScreen
<https://help.ubuntu.com/community/EloTouchScreen>`_


Imprimantes à tickets
---------------------

* Epson MT M88 iv

