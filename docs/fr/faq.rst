FAQ
===

Vous avez trouvé un bug ?
-------------------------

Lorsque vous avez trouvé un bug, vous pouvez vérifier en tout premier si ce bug est déjà connu.
Pour cela, il suffit de consulter la page suivante: 
`GitHub <https://github.com/possum-software/possum/issues>`_.

Si votre bug est inconnu, alors nous vous serons reconnaissant de décrire ce bug
et si possible les conditions pour le recréer à la même adresse que ci-dessus.

Comment se connecter à distance à l'interface graphique ?
---------------------------------------------------------

Pour cela, nous allons utiliser ''x11vnc'' sur le serveur:

::

  sudo apt-get install x11vnc


Pour que cette technique fonctionne, vous devez avoir un accès en SSH à
votre serveur. 

Sur notre poste, nous aurons besoin de ''gvncviewer'':

::

  sudo apt-get install gvncviewer

Toujours sur notre poste, nous allons maintenant relier l'interface graphique
distante à notre poste. Dans cet exemple, l'utilisateur utilisant l'interface
graphique est l'utilisateur ''pos'':

::

  ssh -t -L 5900:localhost:5900 pos@ADRESSE_DE_VOTRE_SERVEUR 'x11vnc -localhost -display :0'

Ensuite, nous allons utiliser cette connexion pour avoir l'affichage:

::

  gvncviewer localhost:0

Comment avoir un navigateur web en plein écran pour seulement utiliser Possum ?
-------------------------------------------------------------------------------

Le plus simple est d'utiliser ''Firefox'' en mode kiosque, c'est à dire: en plein écran avec
tous les raccourcis et autres menus désactivés. Il suffira de lancer automatiquement
au lancement de votre gestionnaire de fenêtre (par exemple: ''Fluxbox'').

Pour activer le mode kiosque, je vous conseille l'extension ''R-kiosk''.


Comment avoir un clavier virtuel ?
----------------------------------

Je vous conseille de directement utiliser une extension disponible pour ''Firefox'': FxKeyboard
