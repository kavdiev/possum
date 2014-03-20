FAQ
===

You have found a bug ?
----------------------

When you find a bug, you can check first if the bug is already known.
To do this, simply visit the following page:
`GitHub <https://github.com/possum-software/possum/issues>`_.

If your bug is unknown, then we will be grateful to you describe this bug
and if possible to recreate the conditions at the same address as above.

How to remotely connect to the GUI ?
------------------------------------


To do this, we will use ''x11vnc'' on the server:

::

  sudo apt-get install x11vnc

For this technique to work, you must have an SSH access to your server

Our position, we need ''gvncviewer'':

::

  sudo apt-get install gvncviewer

Always on our PC, we now connect the GUI
our remote office. In this example, the user interface using the
graphic is the user ''pos'':

::

  ssh -t -L 5900:localhost:5900 pos@SERVER_ADDRESS 'x11vnc -localhost -display :0'

Then we will use this connection for display:

::

  gvncviewer localhost:0

How to have a web browser in full screen only use Possum ?
----------------------------------------------------------

The easiest way is to use ''Firefox'' kiosk mode, ie: full screen with
all the shortcuts and other menus disabled. Suffice it to start automatically
launch your window manager (eg ''Fluxbox'').

To activate the kiosk mode, I recommend the extension ''R-kiosk''.

How to get a virtual keyboard ?
-------------------------------

We advise you to directly use an extension available for ''Firefox'': FxKeyboard
