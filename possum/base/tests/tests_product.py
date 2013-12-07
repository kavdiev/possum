#!/usr/bin/python
# -*- coding: utf-8 -*-

#from django.utils.unittest.case import TestCase
from django.test import TestCase

from possum.base.bill import Facture
from possum.base.category import Categorie
from possum.base.product import ProduitVendu, Produit


class Tests_Products(TestCase):
    fixtures = ['demo.json']

    def test_is_full(self):
        menu = ProduitVendu()
        menu.save()
        menu.produit = Produit.object.get(nom="biere 50cl")
        menu.save()
        self.assertTrue(menu.isFull())

        menu.produit = Produit.object.get(nom="Entree/Plat")
        self.assertFalse(menu.isFull())

        plat = ProduitVendu()
        plat.produit = Produit.object.get(nom="entrecote")
        plat.save()
        menu.produits.add(plat)
        self.assertFalse(menu.isFull())

        entree = ProduitVendu()
        entree.produit = Produit.object.get(nom="salade normande")
        entree.save()
        menu.produits.add(entree)
        self.assertTrue(menu.isFull())

    def test_free_category(self):
        menu = ProduitVendu()
        menu.save()
        menu.produit = Produit.object.get(nom="biere 50cl")
        menu.save()
        self.assertEqual(None, menu.getFreeCategorie())

        menu.produit = Produit.object.get(nom="Entree/Plat")
        cat_entrees = Categorie.objects.get(nom="Entrees")
        self.assertEqual(cat_entrees, menu.getFreeCategorie())

        entree = ProduitVendu()
        entree.produit = Produit.object.get(nom="salade normande")
        entree.save()
        menu.produits.add(entree)
        cat_plats = Categorie.objects.get(nom="Plat")
        self.assertEqual(cat_plats, menu.getFreeCategorie())

        plat = ProduitVendu()
        plat.produit = Produit.object.get(nom="entrecote")
        plat.save()
        menu.produits.add(plat)
        self.assertEqual(None, menu.getFreeCategorie())

        menu.produits.remove(entree)
        self.assertEqual(cat_entrees, menu.getFreeCategorie())

        menu.produits.add(entree)
        self.assertEqual(None, menu.getFreeCategorie())
