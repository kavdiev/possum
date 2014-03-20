=============
Développement
=============

Le projet est ouvert à toutes contributions, le plus simple est de commmencer par forker
le projet sur `Github <https://github.com/possum-software/possum/>`_ et de consulter
la liste des tâches: `Issues <https://github.com/possum-software/possum/issues>`_.

Numéro de version
=================

Voici le cycle de développement adopté pour la sortie des versions:

.. image:: images/cycle_de_developpement.png
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

Modèles
=======

Voici le schèma général des différentes classes utilisées.

.. image:: images/models-base.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

.. image:: images/models-stats.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

La classe centrale, et donc la plus importante, est la classe Facture_.

Après toute modification dans les modèles, il faudrat utiliser South pour les appliquer:

::

  ./manage.py schemamigration base --auto
  ./manage.py migrate base


On peut également se créer un jeu de données avec:

::

  ./manage.py dumpdata --indent=2 --format=json base > possum/base/fixtures/demo1.json


Classes
=======

.. include:: classes.rst


Qualité
=======

La qualité générale de Possum est auditée grâce à Jenkins.
Les résultats sont consultables ici:  `Jenkins <https://www.possum-software.org/jenkins>`_.


Les bugs
========

Nouveau bug
-----------

Lorsque vous avez trouvé un bug, vous pouvez vérifier en tout premier si ce bug est déjà connu. 
Pour cela, il suffit de consulter la page suivante: `GitHub <https://github.com/possum-software/possum/issues>`_.

Si votre bug est inconnu, alors nous vous serons reconnaissant de décrire ce bug et si possible les conditions
pour le recréer à la même adresse que ci-dessus.

Correction d'un bug
-------------------

Cette section concerne surtout les développeurs.

Si vous avez corriger un bug qui est référencé dans le gestionnaire de bug, alors vous pouvez le fermer
automatiquement avec l'opération de commit en utilisant son numéro d'identifiant. Par exemple pour fermer
le bug numéro 42, il vous suffira d'ajouter dans le commentaire du commit: ''Closes #42''.

Si votre commit est en relation avec un bug mais ne le ferme pas, alors il suffit d'indiquer le numéro
du bug dans le commentaire du commit. Par exemple: ''Prépare la correction de #42.''.


