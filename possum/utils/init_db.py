#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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
import os
import sys

sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from django.contrib.auth.models import User, Permission
from possum.base.models import Categorie, Cuisson, \
    Facture, Paiement, PaiementType, Produit, ProduitVendu, Follow, Table, Zone, VAT, \
    Printer, VATOnBill, DailyStat, WeeklyStat, MonthlyStat, Config

# on efface toutes la base
VAT.objects.all().delete()
Printer.objects.all().delete()
VATOnBill.objects.all().delete()
Categorie.objects.all().delete()
Cuisson.objects.all().delete()
Produit.objects.all().delete()
DailyStat.objects.all().delete()
WeeklyStat.objects.all().delete()
MonthlyStat.objects.all().delete()
Follow.objects.all().delete()
Facture.objects.all().delete()
Zone.objects.all().delete()
Table.objects.all().delete()
User.objects.all().delete()
PaiementType.objects.all().delete()
Paiement.objects.all().delete()
Config.objects.all().delete()

# ajout du manager
user = User(username="demo",
        first_name="first name",
        last_name="last name",
        email="demo@possum-software.org")
user.set_password("demo")
user.save()
# on ajoute les droits d'admin
for i in xrange(1, 10):
    user.user_permissions.add(Permission.objects.get(codename="p%d" % i))
user.save()

# ajout d'un utilisateur pour la saisie des commandes
# ajout du manager
user = User(username="pos",
        first_name="",
        last_name="",
        email="")
user.set_password("pos")
user.save()
# on ajoute les droits d'admin
user.user_permissions.add(Permission.objects.get(codename="p3"))
user.save()

# Cuisson
Cuisson(nom='bleu', nom_facture='B', color='#8CC6D7', priorite='10').save()
Cuisson(nom='saignant', nom_facture='S', color='#DB0B32', priorite='15').save()
Cuisson(nom=u'à point', nom_facture='AP', color='#C44C51', priorite='20').save()
Cuisson(nom='bien cuit', nom_facture='BC', color='#B78178', priorite='25').save()

# Type de paiements
PaiementType(nom='AMEX', fixed_value=False).save()
PaiementType(nom='ANCV', fixed_value=True).save()
PaiementType(nom='CB', fixed_value=False).save()
PaiementType(nom='Cheque', fixed_value=False).save()
PaiementType(nom='Espece', fixed_value=False).save()
PaiementType(nom='Tic. Resto.', fixed_value=True).save()

# Type de paiements par défaut pour les remboursements lorsque
# le paiement dépasse le montant de la facture
id_type_paiement = PaiementType.objects.get(nom="Espece").id
Config(key="payment_for_refunds", value=id_type_paiement).save()

# Default PaymentType to select by default on the payment page
id_type_paiement = PaiementType.objects.get(nom="Espece").id
Config(key="default_type_payment", value=id_type_paiement).save()

# Le montant de surtaxe
Config(key="price_surcharge", value="0.20").save()
