===========
Development
===========


The project is open to all contributions, the easiest way is to start by forking
the project on `Github <https://github.com/possum-software/possum/>`_ and consult
tasks list: `Issues <https://github.com/possum-software/possum/issues>`_.

Version number
==============

Here the development cycle adopted for the release version:

.. image:: ../images/cycle_de_developpement.png
   :alt: Development cycle

An example for version 1.0:

* 1.0.beta: development in progress
* 1.0.rc?: additions of features are blocked, only bug fixes
* 1.0: stable version
* 1.0.1: only bug fixes on stable version

Coding convention
=================

The coding convention used for the project following the
`Style Guide for Python Code (PEP 8) <http://www.python.org/dev/peps/pep-0008/>`_.

Compliance with agreements is verified by Jenkins,
the results are available here:
`Jenkins <https://www.possum-software.org/jenkins>`_.

Change in class
===============

After any change in the definitions of models, it will
update patterns with South and demo data. This command
will do it for us:

::

  ./make models_changed


Remenber to add new migration file on git.

Base
====

Main class in this part is Facture_.

.. image:: ../images/models-base.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

Categorie
---------
.. automodule:: possum.base.models.category
   :members:

Config
------
.. automodule:: possum.base.models.config
   :members:

Facture
-------
.. automodule:: possum.base.models.bill
   :members:

Follow
------
.. automodule:: possum.base.models.follow
   :members:

Generic
-------
.. automodule:: possum.base.models.generic
   :members:

Location
--------
.. automodule:: possum.base.models.location
   :members:

Options
-------
.. automodule:: possum.base.models.options
   :members:

Payment
--------
.. automodule:: possum.base.models.payment
   :members:

Printer
-------
.. automodule:: possum.base.models.printer
   :members:

Produit
-------
.. automodule:: possum.base.models.product
   :members:

ProduitVendu
------------
.. automodule:: possum.base.models.product_sold
   :members:

VAT
---
.. automodule:: possum.base.models.vat
   :members:

VATOnBill
---------
.. automodule:: possum.base.models.vatonbill
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

