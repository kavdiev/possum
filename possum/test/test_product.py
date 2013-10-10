# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published 
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

import unittest

class Test_Produit(unittest.TestCase):

    def test___cmp__(self, other):
        if self.categorie == other.categorie:
            return cmp(self.nom, other.nom)
        else:
            return cmp(self.categorie, other.categorie)

    class Meta:
        ordering = ['categorie', 'nom']
#        ordering = ['-actif', 'nom']

    def test___unicode__(self):
#        return u"[%s] %s (%.2f€)" % (self.categorie.nom, self.nom, self.prix)
        return u"%s" % self.nom

    def test_est_un_menu(self):
        if self.categories_ok.count():
            return True
        else:
            return False

    def test_get_prize(self):
        return "%.2f" % self.prix

    def test_set_prize(self, prize):
        """With new prize, we have to create a new product to keep statistics
        and historics.
        """
        pass  # TODO

    def test_set_category(self, category):
        self.categorie = category
        self.update_vats()

    def test_update_vats(self):
        """Update vat_onsite and vat_takeaway with prix in TTC
        """
        pass  # TODO

    def test_get_prize_takeaway(self):
        pass  # TODO

    def test_get_prize_onsite(self):
        pass  # TODO

    def test_get_list_with_all_products(self):
        pass  # TODO

class Test_ProduitVendu(unittest.TestCase):

    def test___unicode__(self):
        pass  # TODO

    def test_isFull(self):
        """
        True si tous les élèments sous présents (les sous produits pour les formules)
        et False sinon.

        >>> vendu = ProduitVendu()
        >>> vendu.save()
        >>> vendu.isFull()
        True
        >>> cat1 = Categorie(nom="cat1")
        >>> cat1.save()
        >>> cat2 = Categorie(nom="cat2")
        >>> cat2.save()
        >>> vendu.categories_ok.add(cat1, cat2)
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1 ]
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1, 2 ]
        >>> vendu.isFull()
        True
        >>> vendu.produits = [ 1, 2, 3 ]
        >>> vendu.isFull()
        True
        """
        pass  # TODO

    def test___cmp__(self, other):
        pass  # TODO

    def test_est_un_menu(self):
        pass  # TODO

    def test_get_menu_products(self):
        pass  # TODO

    def test_get_menu_resume(self):
        """Return a short string with product in menu
        """
        pass  # TODO

    def test_getFreeCategorie(self):
        """Retourne la premiere categorie dans la liste categories_ok
        qui n'a pas de produit dans la partir 'contient'. Sinon retourne
        None

        >>> f = Facture(id=3)
        >>> cat1 = Categorie(id=1, nom="cat1")
        >>> cat2 = Categorie(id=2, nom="cat2")
        >>> produit1 = Produit(id=1, nom="p1", categorie=cat1)
        >>> produit2 = Produit(id=2, nom="p2", categorie=cat2)
        >>> vendu = ProduitVendu(id=1, produit=produit1, facture=f)
        >>> vendu.getFreeCategorie()
        0
        >>> produit1.categories_ok.add(cat1, cat2)
        >>> vendu.getFreeCategorie()
        0
        >>> sub = ProduitVendu(id=2, produit=produit1, facture=f)
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        1
        >>> sub = ProduitVendu(id=3, produit=produit2, facture=f)
        >>> sub.produit.categorie = cat2
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        0
        """
        pass  # TODO

