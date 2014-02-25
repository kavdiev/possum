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
import datetime


sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'


from django.contrib.auth.models import User, Permission
from possum.base.models import Categorie, Cuisson, Option, \
    Facture, Paiement, PaiementType, Produit, ProduitVendu, Follow, Table, \
    Zone, VAT, Printer, VATOnBill, Config
from possum.stats.models import Stat


# ajout des utilisateurs
for username in ['demo', 'demo1', 'demo2']:
    if User.objects.filter(username=username).count() == 0:
        user = User(username=username, first_name=username,
                    email="%s@possum-software.org" % username)
        user.set_password(username)
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


# Default PaymentType to select by default on the payment page
id_type_paiement = PaiementType.objects.get(nom="Espece").id
Config(key="default_type_payment", value=id_type_paiement).save()


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
vat_alcool.set_tax("20")
vat_alcool.save()
vat_onsite = VAT(name="sur place")
vat_onsite.set_tax("10")
vat_onsite.save()
vat_takeaway = VAT(name=u"à emporter")
vat_takeaway.set_tax("7")
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


def create_bill(finish=True):
    """Create a bill
    """
    table = 'T%d' % random.randint(10, 25)
    bill = Facture(table=Table.objects.get(nom=table),
                   couverts=random.randint(1, 15))
    bill.save()
    for produit in [salade, buffet, entrecote, pave, biere]:
        for i in xrange(3):
            sold = ProduitVendu(produit=produit)
            sold.save()
            bill.add_product(sold)
    nouveau_menu = ProduitVendu(produit=entree_plat)
    nouveau_menu.save()
    for produit in [salade, pave]:
        sold = ProduitVendu(produit=produit)
        sold.save()
        nouveau_menu.contient.add(sold)
    nouveau_menu.save()
    bill.update()
    if finish:
        type_cb = PaiementType.objects.get(nom='CB')
        bill.add_payment(type_cb, bill.total_ttc)
    return bill


# on ajoute des données pour avoir des jolies graphiques de démonstrations
now = datetime.datetime.now()
interval = "m"
for month in xrange(1, 13):
    for i in xrange(20):
        day = random.randint(1, 28)
        bill = create_bill()
        bill.date_creation = datetime.datetime(now.year, month, day)
        bill.save()

# Création d'une dizaine de facture
for i in xrange(15):
    bill = create_bill(finish=False)
    if i % 2:
        bill.update_kitchen()
        bill.send_in_the_kitchen()

Stat().update()
