Installation
============

This documentation is written for Debian, and should work with 
all distributions (Ubuntu, Gentoo, ...).

Here is the general pattern of different software bricks:

.. image:: ../images/overview_apache.png
    :scale: 50
    :alt: Overview

Possum
------

You have 2 options here, in all cases, it will be positioned in a directory.
Consider the **/opt** directory:

::

  cd /opt

Either use the last up to date version:

::

  sudo apt-get install git
  sudo git clone https://github.com/possum-software/possum.git possum-software

Either download the latest stable version of POSSUM here:
`GitHub <https://github.com/possum-software/possum/releases>`_

We will use the git version.

Prerequisites
-------------

Possum requires the installation of some packages.

For Debian/Ubuntu:

.. include:: ../common/install_deb.rst


Then for installation or updates, we will use **./make**:

::

  cd /opt/possum-software
  sudo ./make update

This will install and configure any virtual environment for Possum.

Now we need to initialize the data, why it is recommended to copy the script
**possum/utils/init_db.py**. For a more complete example, you can inspire 
**possum/utils/init_demo.py** file: 

::

  sudo cp possum/utils/init_db.py possum/utils/init_mine.py
  # adapt file possum/utils/init_mine.py
  sudo gedit possum/utils/init_mine.py
  # and run it:
  sudo ./make init_mine

Printing
----------

Possum can print to multiple printers. In order to use them, you need 
a server cups set on the server. You can verify that the printers are 
available with the command:

::

  lpstat -v

You can configure the print server via a web interface, usually at the
following address: `Cups <http://localhost:631>`_

On the other hand, ticket printing requires the creation and deletion 
of many files. I recommend you to use a tmpfs virtual file types for 
**tickets** directory. Default place is in **possum-software**
directory.

For example, if the absolute path to your **tickets** directory is
**/opt/possum-software/tickets/**, you must add the following line 
in your **/etc/fstab**:

::

  tmpfs /opt/possum-software/tickets/ tmpfs defaults,nodev,nosuid 0 0

This can be done with the following commands (as root):

::

  echo "tmpfs /opt/possum-software/tickets/ tmpfs defaults,nodev,nosuid 0 0" >> /etc/fstab
  mount /opt/possum-software/tickets/

Documentation
-------------

You can generate documentation in HTML with the following command:

::

  source env/bin/activate
  cd docs/en
  make html
  deactivate

It will be available here: **/opt/possum-software/docs/en/_build/html/**.
Otherwise it is also available on the official website: 
`Documentation <http://possum.readthedocs.org>`_.

Web server configuration
------------------------

We now need a web server. There are several possibilities,
it is based on the web server `Apache <http://httpd.apache.org/>`_.

In short, the module `mod_wsgi <http://code.google.com/p/modwsgi/>`_
used to run Possum.

Begin by installing the required packages:

.. include:: ../common/install_apache_deb.rst


It remains to do the configuration. For this, there are typical
configurations in the **possum/utils/** directory.

For example, a standard and secure configuration:

::

  cp possum/utils/apache2.conf /etc/apache2/sites-available/possum.conf

It will modify the **/etc/apache2/sites-available/possum.conf**
to suit your installation, then:

::

  sudo a2dissite 000-default.conf
  sudo a2ensite possum
  sudo service apache2 restart


The recommended configuration uses **https** to secure exchanges
between clients (android, ...) and server. To use this configuration
file, **/etc/hosts** should be configured correctly.

Example:

::

  # hostname
  possum

Here, the server is called **possum**.

::

  # Give the necessary rights to the web server directory
  chown -R www-data /opt/possum-software
  # Create SSL certificates
  make-ssl-cert generate-default-snakeoil --force-overwrite


Reports & Statistics
--------------------

To build various reports and display graphics a number of statistics 
should be calculated on the bills that resulted. These calculations 
can be costly in time, it is visible when you enter the party
**Manager/rapports**.

To overcome this problem, it is recommended to update this information
throughout the day using the GNU/Linux crontab.

To do this, it will adapt the **possum/utils/update_stats.sh** file 
you need to edit the following line indicating your installation
directory:

::

  pushd /opt/possum-software >/dev/null


Then just save the automatic execution of this command using the 
**crontab -e** (for more information: **man crontab**).

Here is an example:

::

  # At 11h20 every day
  20 11 * * * /opt/possum-software/possum/utils/update_stats.sh
  # After the lunch service at 14:30 every day
  30 14 * * * /opt/possum-software/possum/utils/update_stats.sh
  # Before the evening service at 18:30 every day
  30 18 * * * /opt/possum-software/possum/utils/update_stats.sh


Mail
----

It is better to have a mail server configured on the job. Indeed, 
POSSUM can sent messages if there are any attempts to access the 
administration panel or bugs.

::

  sudo apt-get install postfix bsd-mailx

  Typical configuration of the mail server: Website
  Name mail: possum (or whatever name you want) 

It is advisable to define an alias for the root user in 
**/etc/aliases**.  In this case, you have a line like:

::

  root: your_address@possum-software.org

This alias will allow you to receive alerts any operating system.
After changing this file, you must run the command:

::

  sudo newaliases

If everything is set up, you should receive an email with as a
**test** subject and the message sends the date using the following
command:

::

  date | mail -s test root

The installation is almost complete, you must now configure the 
automatic backup of the database. This part depends on the type of 
database you have chosen. The simplest being based sqlite, his backup 
is limited to copying a file.

To access POSSUM, simply launch a web browser.

Stopping the server
-------------------

To shutdown the server, you can configure **sudo** to allow the Apache 
server to start the server shutdown (provided that there have not 
calculating current statistics). With the **visudo** command,
you can add the following line:

::

  www-data ALL=(ALL) NOPASSWD: /sbin/shutdown

