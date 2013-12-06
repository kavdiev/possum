#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.unittest.case import TestCase

from possum.base.bill import Facture
from possum.base.category import Categorie
from possum.base.product import ProduitVendu, Produit


class Tests_Products(TestCase):

    def test_is_full(self):
        vendu = ProduitVendu()
        vendu.save()
        self.assertTrue(vendu.isFull())
        cat1 = Categorie(nom="cat1")
        cat1.save()
        cat2 = Categorie(nom="cat2")
        cat2.save()
        vendu.categories_ok.add(cat1, cat2)
        self.assertFalse(vendu.isFull())
        vendu.produits = [1]
        self.assertFalse(vendu.isFull())
        vendu.produits = [1, 2]
        self.assertTrue(vendu.isFull())
        vendu.produits = [1, 2, 3]
        self.assertTrue(vendu.isFull())

    def test_free_category(self):
        f = Facture(id=3)
        cat1 = Categorie(id=1, nom="cat1")
        cat2 = Categorie(id=2, nom="cat2")
        produit1 = Produit(id=1, nom="p1", categorie=cat1)
        produit2 = Produit(id=2, nom="p2", categorie=cat2)
        vendu = ProduitVendu(id=1, produit=produit1, facture=f)
        self.assertEqual(0, vendu.getFreeCategorie())
        produit1.categories_ok.add(cat1, cat2)
        self.assertEqual(0, vendu.getFreeCategorie())
        sub = ProduitVendu(id=2, produit=produit1, facture=f)
        vendu.contient.add(sub)
        self.assertEqual(1, vendu.getFreeCategorie())
        sub = ProduitVendu(id=3, produit=produit2, facture=f)
        sub.produit.categorie = cat2
        vendu.contient.add(sub)
        self.assertEqual(0, vendu.getFreeCategorie())
