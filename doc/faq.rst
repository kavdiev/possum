FAQ
===

Comment se connecter à distance à l'interface graphique
-------------------------------------------------------

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


Comment avoir un clavier virtuel
--------------------------------

Vous pouvez utiliser ''Onboard Virtual Keyboard'' sous Ubuntu:

::

  sudo apt-get install onboard

Vous pouvez le configurer avec un:

::

  onboard-settings


