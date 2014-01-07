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
import random
import sys

sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from django.contrib.auth.models import User, Permission
from possum.base.models import Categorie, Cuisson, Option, \
    Facture, Paiement, PaiementType, Produit, ProduitVendu, Follow, Table, \
    Zone, VAT, Printer, VATOnBill, DailyStat, WeeklyStat, MonthlyStat, Config


# on efface toutes la base
VAT.objects.all().delete()
Printer.objects.all().delete()
VATOnBill.objects.all().delete()
Categorie.objects.all().delete()
Cuisson.objects.all().delete()
Option.objects.all().delete()
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

# ajout d'un utilisateur
user = User(username="demo", first_name="first name", last_name="last name",
            email="demo@possum-software.org")
user.set_password("demo")
user.save()
# on ajoute les droits d'admin
for i in xrange(1, 10):
    user.user_permissions.add(Permission.objects.get(codename="p%d" % i))
user.save()

# Cuisson
Cuisson(nom='bleu',
        nom_facture='B',
        color='#8CC6D7',
        priorite='10').save()
Cuisson(nom='saignant',
        nom_facture='S',
        color='#DB0B32',
        priorite='15').save()
Cuisson(nom=u'à point',
        nom_facture='AP',
        color='#C44C51',
        priorite='20').save()
Cuisson(nom='bien cuit',
        nom_facture='BC',
        color='#B78178',
        priorite='25').save()

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

# Montant de la surtaxe
Config(key="price_surcharge", value="0.20").save()

# Tables
z = Zone(nom='Bar', surtaxe=False)
z.save()
Table(nom="T--", zone=z).save()
z = Zone(nom='Rez de chaussee', surtaxe=False)
z.save()
for i in xrange(1, 15):
    Table(nom="T%02d" % i, zone=z).save()
z = Zone(nom='Terrasse', surtaxe=True)
z.save()
for i in xrange(15, 26):
    Table(nom="T%02d" % i, zone=z).save()

# TVA
vat_alcool = VAT(name="alcool")
vat_alcool.set_tax("19.6")
vat_alcool.save()
vat_onsite = VAT(name="sur place")
vat_onsite.set_tax("7")
vat_onsite.save()
vat_takeaway = VAT(name=u"à emporter")
vat_takeaway.set_tax("5")
vat_takeaway.save()

# on entre les nouveaux produits, les prix sont TTC
jus = Categorie(nom="Jus",
                priorite=25,
                surtaxable=False,
                disable_surtaxe=False,
                made_in_kitchen=False,
                color="#44b3dc",
                vat_onsite=vat_onsite,
                vat_takeaway=vat_takeaway)
jus.save()
abricot = Produit(nom="jus abricot",
                  prix="2.80",
                  choix_cuisson=False,
                  categorie=jus)
abricot.save()
pomme = Produit(nom="jus pomme",
                prix="2.80",
                choix_cuisson=False,
                categorie=jus)
pomme.save()

bieres = Categorie(nom="Bieres",
                   priorite=2,
                   surtaxable=False,
                   disable_surtaxe=False,
                   made_in_kitchen=False,
                   color="#ea97b5",
                   vat_onsite=vat_alcool,
                   vat_takeaway=vat_alcool)
bieres.save()
biere = Produit(nom="biere 50cl",
                prix="2.80",
                choix_cuisson=False,
                categorie=bieres)
biere.save()

entrees = Categorie(nom="Entrees",
                    priorite=5,
                    surtaxable=False,
                    disable_surtaxe=False,
                    made_in_kitchen=True,
                    color="#ff9f00",
                    vat_onsite=vat_onsite,
                    vat_takeaway=vat_takeaway)
entrees.save()
salade = Produit(nom="salade normande",
                 prix="3.40",
                 choix_cuisson=False,
                 categorie=entrees)
salade.save()
buffet = Produit(nom="buffet",
                 prix="6.40",
                 choix_cuisson=False,
                 categorie=entrees)
buffet.save()

plat = Categorie(nom="Plat",
                 priorite=10,
                 surtaxable=False,
                 disable_surtaxe=False,
                 made_in_kitchen=True,
                 color="#c9a100",
                 vat_onsite=vat_onsite,
                 vat_takeaway=vat_takeaway)
plat.save()
entrecote = Produit(nom="entrecote",
                    prix="8.40",
                    choix_cuisson=True,
                    categorie=plat)
entrecote.save()
pave = Produit(nom="pave de saumon",
               prix="9.40",
               choix_cuisson=False,
               categorie=plat)
pave.save()

# pour les menu
menu = Categorie(nom="Menu",
                 priorite=22,
                 surtaxable=False,
                 disable_surtaxe=False,
                 made_in_kitchen=False,
                 color="#88f027",
                 vat_onsite=vat_onsite,
                 vat_takeaway=vat_takeaway)
menu.save()
entree_plat = Produit(nom=u"Menu Entree/Plat",
                      prix="13.40",
                      choix_cuisson=False,
                      categorie=menu)
entree_plat.save()
entree_plat.categories_ok.add(entrees)
entree_plat.categories_ok.add(plat)
entree_plat.produits_ok.add(salade)
entree_plat.produits_ok.add(entrecote)
entree_plat.produits_ok.add(pave)
entree_plat.save()

# mis a jour des TTC et TVA
for product in Produit.objects.all():
    product.update_vats(keep_clone=False)

# on ajoute des données pour avoir des jolies graphiques de démonstrations
DailyStat(date="2013-10-01", key="total_ttc", value="234").save()
for month in xrange(1, 13):
    MonthlyStat(year=2013, month=month, key='total_ttc',
                value=100 * month).save()
    MonthlyStat(year=2013, month=month, key='bar_total_ttc',
                value=40 * month).save()
    MonthlyStat(year=2013, month=month, key='guests_total_ttc',
                value=60 * month).save()
    MonthlyStat(year=2013, month=month, key='nb_bills',
                value=random.randint(50, 500)).save()
    MonthlyStat(year=2013, month=month, key='guests_nb',
                value=random.randint(50, 500)).save()
    MonthlyStat(year=2013, month=month, key='guests_average',
                value=random.randint(50, 500)).save()
    MonthlyStat(year=2013, month=month, key='bar_nb',
                value=random.randint(50, 500)).save()
    MonthlyStat(year=2013, month=month, key='bar_average',
                value=random.randint(50, 500)).save()

# Création d'une dizaine de facture
for i in xrange(15):
    table = 'T%d' % random.randint(10, 25)
    f = Facture(table=Table.objects.get(nom=table),
                couverts=random.randint(1, 15))
    f.save()
    for produit in [salade, buffet, entrecote, pave, biere]:
        for j in xrange(3):
            p = ProduitVendu(produit=produit)
            p.save()
            f.add_product(p)
    nouveau_menu = ProduitVendu(produit=entree_plat)
    nouveau_menu.save()
    for produit in [salade, pave]:
        p = ProduitVendu(produit=produit)
        p.save()
        nouveau_menu.contient.add(p)
    nouveau_menu.save()
    if i % 2:
        f.send_in_the_kitchen()

# on sold une facture
type_cb = PaiementType.objects.get(nom='CB')
f.add_payment(type_cb, f.total_ttc)
