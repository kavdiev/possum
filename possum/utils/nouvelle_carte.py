#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    POSSUM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with POSSUM.  If not, see <http://www.gnu.org/licenses/>.
#
import sys, os
sys.path.append('/home/pos/possum-software')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, \
    Categorie, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone, VAT
from django.contrib.auth.models import User

# on efface toutes la base
VAT.objects.all().delete()
Printer.objects.all().delete()
VATOnBill.objects.all().delete()
LogType.objects.all().delete()
Log.objects.all().delete()
Categorie.objects.all().delete()
Cuisson.objects.all().delete()
Sauce.objects.all().delete()
Accompagnement.objects.all().delete()
Produit.objects.all().delete()
StatsJourCategorie.objects.all().delete()
StatsJourGeneral.objects.all().delete()
StatsJourPaiement.objects.all().delete()
StatsJourProduit.objects.all().delete()
Suivi.objects.all().delete()
Facture.objects.all().delete()
Zone.objects.all().delete()
Table.objects.all().delete()
User.objects.all()delete()
PaiementType.objects.all()delete()
Paiement.objects.all()delete()

# ajout d'un utilisateur
user = User(username="toto", 
        first_name="first name", 
        last_name="last name", 
        email="toto@example.net").save()
user.set_password(passwd)
user.save()
# on ajoute les droits d'admin
user.user_permissions.add(Permission.objects.get(codename="p1"))
user.save()

# TVA
vat_alcool = VAT(name="alcool")
vat_alcool.set_tax("19.6")
alcool.save()
vat_onsite = VAT(name="sur place")
vat_onsite.set_tax("7")
vat_onsite.save()
vat_takeaway = VAT(name=u"à emporter")
vat_takeaway.set_tax("7")
vat_takeaway.save()

# on entre les nouveaux produits, les prix sont TTC
cat = Categorie(nom="Entrees", 
        priorite=5,
        surtaxable=False,
        disable_surtaxe=False,
        couleur="#ff9f00",
        vat_onsite=vat_onsite, 
        vat_takeaway=vat_takeaway)
cat.save()
Produit(nom="salade", 
        nom_facture="salade", 
        prix="3.40", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()
# pour les menu
...

# mis a jour des TTC et TVA
for product in Produit.objects.all():
    product.update_vats()
