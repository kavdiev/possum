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


.. include:: ../common/hardware_benchmark.rst

Écrans tactiles
---------------

.. include:: ../common/hardware_screens.rst

À noter que le support de la part de EloTouch est plutôt
moyen. Je vous conseille ce site: `EloTouchScreen
<https://help.ubuntu.com/community/EloTouchScreen>`_


Imprimantes à tickets
---------------------

.. include:: ../common/hardware_printers.rst
