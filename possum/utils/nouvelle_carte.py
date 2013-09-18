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
sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone

# on efface tous les produits présents
Produit.objects.all().delete()
Categorie.objects.all().delete()

# TVA
vat_onsite = VAT(name="sur place")
vat_onsite.set_tax("19.6")
vat_onsite.save()
vat_takeaway = VAT(name=u"à emporter")
vat_takeaway.set_tax("7")
vat_takeaway.save()

# on entre les nouveaux produits, les prix sont TTC
cat = Categorie(nom="Entrees", vat_onsite=vat_onsite, vat_takeaway=vat_takeaway)
cat.save()
Produit(nom="salade", nom_facture="salade", prix="3.40", categorie=cat).save()
Produit(nom="salade2", nom_facture="salade2", prix="3.40", categorie=cat).save()

# mis a jour des TTC et TVA
for product in Produit.objects.all():
    p.update_vats()
