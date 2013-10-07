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
#sys.path.append('/home/pos/possum-software')
sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, \
    Categorie, Cuisson, Facture, Paiement, \
    PaiementType, Produit, ProduitVendu, Follow, Table, Zone, VAT, \
    Printer, VATOnBill, DailyStat, WeeklyStat, MonthlyStat, Config
from django.contrib.auth.models import User, Permission

# on efface toutes la base
VAT.objects.all().delete()
Printer.objects.all().delete()
VATOnBill.objects.all().delete()
Categorie.objects.all().delete()
Cuisson.objects.all().delete()
Sauce.objects.all().delete()
Accompagnement.objects.all().delete()
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
user = User(username="demo", 
        first_name="first name", 
        last_name="last name", 
        email="demo@possum-software.org")
user.set_password("demo")
user.save()
# on ajoute les droits d'admin
for i in xrange(1,10):
    user.user_permissions.add(Permission.objects.get(codename="p%d" % i))
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

# Tables
z = Zone(nom='Bar', surtaxe=False, prix_surtaxe='0.2')
z.save()
Table(nom="T--", zone=z).save()
z = Zone(nom='Rez de chaussee', surtaxe=False, prix_surtaxe='0.2')
z.save()
for i in xrange(1, 15):
    Table(nom="T%02d" % i, zone=z).save()
z = Zone(nom='Terrasse', surtaxe=True, prix_surtaxe='0.2')
z.save()
for i in xrange(15, 25):
    Table(nom="T%02d" % i, zone=z).save()

# TVA
vat_alcool = VAT(name="alcool")
vat_alcool.set_tax("19.6")
vat_alcool.save()
vat_onsite = VAT(name="sur place")
vat_onsite.set_tax("7")
vat_onsite.save()
vat_takeaway = VAT(name=u"à emporter")
vat_takeaway.set_tax("7")
vat_takeaway.save()

# on entre les nouveaux produits, les prix sont TTC
cat = Categorie(nom="Jus", 
        priorite=25,
        surtaxable=False,
        disable_surtaxe=False,
        made_in_kitchen=False,
        color="#44b3dc",
        vat_onsite=vat_onsite, 
        vat_takeaway=vat_takeaway)
cat.save()
Produit(nom="abricot", 
        nom_facture="jus abricot", 
        prix="2.80", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()
Produit(nom="pomme", 
        nom_facture="jus pomme", 
        prix="2.80", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()

cat = Categorie(nom="Bieres", 
        priorite=2,
        surtaxable=False,
        disable_surtaxe=False,
        made_in_kitchen=False,
        color="#ea97b5",
        vat_onsite=vat_alcool, 
        vat_takeaway=vat_alcool)
cat.save()
Produit(nom="biere 50cl", 
        nom_facture="biere", 
        prix="2.80", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()

cat = Categorie(nom="Entrees", 
        priorite=5,
        surtaxable=False,
        disable_surtaxe=False,
        made_in_kitchen=True,
        color="#ff9f00",
        vat_onsite=vat_onsite, 
        vat_takeaway=vat_takeaway)
cat.save()
entree = cat
Produit(nom="salade normande", 
        nom_facture="salade", 
        prix="3.40", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()
Produit(nom="buffet", 
        nom_facture="buffet", 
        prix="6.40", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()

cat = Categorie(nom="Plat", 
        priorite=10,
        surtaxable=False,
        disable_surtaxe=False,
        made_in_kitchen=True,
        color="#c9a100",
        vat_onsite=vat_onsite, 
        vat_takeaway=vat_takeaway)
cat.save()
plat = cat
Produit(nom="entrecote", 
        nom_facture="entrecote", 
        prix="8.40", 
        choix_cuisson=True,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()
Produit(nom=u"pavé de saumon", 
        nom_facture="pave de saumon", 
        prix="9.40", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat).save()
# pour les menu
cat = Categorie(nom="Menu", 
        priorite=22,
        surtaxable=False,
        disable_surtaxe=False,
        made_in_kitchen=False,
        color="#88f027",
        vat_onsite=vat_onsite, 
        vat_takeaway=vat_takeaway)
cat.save()
menu = Produit(nom=u"Entree/Plat", 
        nom_facture="menu express", 
        prix="13.40", 
        choix_cuisson=False,
        choix_accompagnement=False,
        choix_sauce=False,
        categorie=cat)
menu.save()
menu.categories_ok.add(entree)
menu.categories_ok.add(plat)
for nom in ["salade normande", "entrecote", u"pavé de saumon"]:
    try:
        produit = Produit.objects.get(nom=nom)
    except Produit.DoesNotExist:
        print "Le produit [%s] n'existe pas !" % nom
        sys.exit()
    menu.produits_ok.add(produit)
menu.save()

# mis a jour des TTC et TVA
for product in Produit.objects.all():
    product.update_vats()
