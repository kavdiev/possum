=============
Développement
=============

Le projet est ouvert à toutes contributions, le plus simple est de commmencer par forker
le projet sur `Github <https://github.com/possum-software/possum/>`_ et de consulter
la liste des tâches: `Issues <https://github.com/possum-software/possum/issues>`_.

Numéro de version
=================

Voici le cycle de développement adopté pour la sortie des versions:

.. image:: ../images/cycle_de_developpement.png
   :alt: Cycle de développement du projet

Voici un exemple pour la version 1.0:

* 1.0.alpha: début du développement, typiquement la version précédente
  vient de sortir. Il y a des ajouts de fonctionnalités.
* 1.0.beta: le développement de la version touche à sa fin, cependant
  des ajouts de fonctionnalités sont toujours possibles.
* 1.0.rc?: à partir des versions RC, les ajouts de fonctionnalités sont bloqués. Il y
  aura seulement des corrections de bugs.
* 1.0: les versions officiellements stables.
* 1.0.1: les corrections de bugs de la version stable.

Convention de codage
====================

La convention de codage utilisée pour le projet suit le 
`Style Guide for Python Code (PEP 8) <http://www.python.org/dev/peps/pep-0008/>`_.

Qualité
=======

La qualité générale de Possum est auditée grâce à Jenkins.
Les résultats sont consultables ici:  `Jenkins <https://www.possum-software.org/jenkins>`_.

Changement dans une classe
==========================

Après toute modification dans les modèles, il faudrat utiliser South pour les appliquer:

::

  ./manage.py schemamigration base --auto
  ./manage.py migrate base


On peut également se créer un jeu de données avec:

::

  ./manage.py dumpdata --indent=2 --format=json base > possum/base/fixtures/demo1.json


Base
====

Main class in this part is Facture_.

.. image:: ../images/models-base.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

Facture
-------

.. automodule:: possum.base.models.bill
   :members:

Stats
=====

.. image:: ../images/models-stats.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

.. automodule:: possum.stats.models
   :members:

