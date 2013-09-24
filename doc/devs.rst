=============
Développement
=============

Voici le cycle de développement adopté pour la sortie des versions:

.. image:: images/cycle_de_developpement.png
   :alt: Cycle de développement du projet

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

À nouveau les différentes classes avec leurs héritages.

.. inheritance-diagram:: possum.base.models
   :parts: 1

La classe centrale, et donc la plus importante, est la classe Facture_.

Après toute modification dans les modèles, il faudrat utiliser South pour les appliquer:

::

  ./manage.py schemamigration base --auto
  ./manage.py migrate base


On peut également se créer un jeu de données avec:

::

  ./manage.py dumpdata --indent=2 --format=json base > possum/base/fixtures/demo1.json

Facture
-------

.. inheritance-diagram:: possum.base.models.Facture
   :parts: 1

.. autoclass:: possum.base.models.Facture
   :members:


Qualité
=======

La qualité générale de Possum est mesurée par Pylint.
La définition de tous les codes est `ici <http://pylint-messages.wikidot.com/all-codes>`_.

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


