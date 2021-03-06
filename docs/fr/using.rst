Utilisation
===========

En bref, le menu en haut avec les icones permettent un accès rapide 
vers les différentes parties qui sont dans l'ordre:

#. page d'accueil donnant accès à toutes les parties
#. accès rapide à la partie en cours (Factures, Cuisine ou Manager)
#. les produits en cours de préparation en cuisine
#. la partie dédiée au gérant

Gestion des utilisateurs
------------------------

Les gérants peuvent gérer les utilisateurs dans la partie dédiée aux managers.

Le point important est de ne pas donner le droit de manager à tout le monde, surtout au
compte utilisé pour la gestion des commandes. Au besoin, il est préférable de créer un utilisateur
dédié (par exemple: pos). En effet, le droit manager permet d'accéder notamment à tous les 
résultats, les rapports et à la partie archives des factures.

Fonctionnement des tickets envoyés en cuisine
---------------------------------------------

Les prérequis afin d'utiliser les tickets envoyés en cuisine sont:

* une imprimante configurée pour la cuisine (partie manager > imprimantes)
* des catégories marquées comme étant à préparer en cuisine (partie carte > catégories)

Pour illustrer le fonctionnement, nous allons prendre un exemple.

Nous avons 4 catégories avec des produits:

* Boissons (pas préparer en cuisine): bière, eau,
* Entrées (préparer en cuisine): salade
* Plats (préparer en cuisine): entrecôte
* Desserts (préparer en cuisine): banana split

Notre commande contient:

* 1 bière
* 1 eau
* 1 salade
* 2 entrecôtes
* 1 banana split

L'envoi en cuisine se fait au niveau de la gestion des commandes
en cours. 

Le premier ticket contiendra la liste complète des préparations:

::

  [12:30] Table T42 (2 couv.)
  >>> envoye Entrees

  ***> Entrees
  salade

  ***> Plats
  entrecote
  entrecote

  ***> Desserts
  banana split


Les tickets suivants contiennent seulement le nom de la catégorie
ainsi que les produits à préparer.

Le second ticket:

::

  [12:45] Table T42 (2 couv.)
  >>> envoye Plats

  entrecote
  entrecote


Et le dernier ticket:

::

  [13:15] Table T42 (2 couv.)
  >>> envoye Desserts

  banana split


