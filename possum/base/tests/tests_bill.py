#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    from collections import OrderedDict
except:
    #  Needed if you use a python older than 2.7
    from ordereddict import OrderedDict

from decimal import Decimal

from django.test import TestCase

from possum.base.models import Facture, PaiementType, Paiement, \
    ProduitVendu, Produit


class Tests_Bill(TestCase):
    fixtures = ['demo.json']

    def test_is_empty(self):
        facture = Facture()
        facture.save()
        self.assertTrue(facture.is_empty())
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        self.assertFalse(facture.is_empty())

    def test_add_product_prize(self):
        facture = Facture()
        facture.save()
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product_prize(plat)
        self.assertEqual(plat.prix, facture.total_ttc)
        self.assertEqual(plat.prix, facture.restant_a_payer)

    def test_add_product(self):
        facture = Facture()
        facture.save()
        self.assertTrue(facture.is_empty())

        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        self.assertTrue(plat in facture.produits.iterator())
        self.assertEqual(plat.prix, facture.total_ttc)
        self.assertEqual(plat.prix, facture.restant_a_payer)

    def test_del_product(self):
        facture = Facture()
        facture.save()
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        facture.del_product(plat)
        self.assertTrue(plat not in facture.produits.iterator())
        self.assertEqual(Decimal("0"), facture.total_ttc)
        self.assertEqual(Decimal("0"), facture.restant_a_payer)

    def test_regroup_produits(self):
        facture = Facture()
        facture.save()
        plat1 = ProduitVendu()
        plat1.produit = Produit.objects.get(nom="entrecote")
        plat2 = ProduitVendu()
        plat2.produit = Produit.objects.get(nom="entrecote")
        plat3 = ProduitVendu()
        plat3.produit = Produit.objects.get(nom="pave de saumon")
        entree = ProduitVendu()
        entree.produit = Produit.objects.get(nom="salade normande")
        menu = ProduitVendu()
        menu.produit = Produit.objects.get(nom="jus abricot")
        facture.add_product(plat1)
        facture.add_product(plat2)
        facture.add_product(plat3)
        facture.add_product(entree)
        facture.add_product(menu)
        resultat = OrderedDict([('salade normande', [(entree.id, entree)]),
                                ('entrecote', [(plat1.id, plat1),
                                               (plat2.id, plat2)]),
                                ('pave de saumon', [(plat3.id, plat3)]),
                                ('jus abricot', [(menu.id, menu)])])
        self.assertEqual(resultat, facture.regroup_produits())

    def test_is_valid_payment(self):
        facture = Facture()
        facture.save()
        self.assertFalse(facture.is_valid_payment(42))
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        self.assertTrue(facture.is_valid_payment(42))
        facture.restant_a_payer = Decimal("0")
        self.assertFalse(facture.is_valid_payment(42))

    def test_rendre_monnaie(self):
        paiement = Paiement.objects.all()[0]
        facture = Facture()
        facture.save()
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        facture.rendre_monnaie(paiement)
        self.assertEqual(Decimal("-82.80"), facture.paiements.all()[0].montant)

    def test_add_payment(self):
        facture = Facture()
        facture.save()
        plat = ProduitVendu()
        plat.produit = Produit.objects.get(nom="entrecote")
        facture.add_product(plat)
        facture.add_payment(PaiementType.objects.get(nom="CB"), "2")
        self.assertEqual(facture.restant_a_payer, Decimal(str(plat.prix - 2)))
        facture.add_payment(PaiementType.objects.get(nom="Espece"), "10")
        self.assertEqual(facture.restant_a_payer, Decimal(0))
        self.assertEqual(Decimal(str(plat.prix - 12)),
                         (facture.paiements.all()[2]).montant)
