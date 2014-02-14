#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from collections import OrderedDict
except:
    #  Needed if you use a python older than 2.7
    from ordereddict import OrderedDict

from decimal import Decimal
from django.test import TestCase
from possum.base.models import Facture, PaiementType, Paiement, ProduitVendu, \
    Produit


class Tests_Bill(TestCase):
    fixtures = ['demo.json']

    def setUp(self):
        TestCase.setUp(self)
        self.facture = Facture()
        self.facture.save()
        self.plat = ProduitVendu()
        self.plat.produit = Produit.objects.get(nom="entrecote")
    
    def test_is_empty(self):
        self.assertTrue(self.facture.is_empty())
        self.facture.add_product(self.plat)
        self.assertFalse(self.facture.is_empty())

    def test_add_product_prize(self):
        self.facture.add_product_prize(self.plat)
        self.assertEqual(self.plat.prix, self.facture.total_ttc)
        self.assertEqual(self.plat.prix, self.facture.restant_a_payer)

    def test_add_product(self):
        self.assertTrue(self.facture.is_empty())
        self.facture.add_product(self.plat)
        self.facture.update()
        self.assertTrue(self.plat in self.facture.produits.iterator())
        self.assertEqual(self.plat.produit.prix, self.facture.total_ttc)
        self.assertEqual(self.plat.produit.prix, self.facture.restant_a_payer)

    def test_del_product(self):
        self.facture.add_product(self.plat)
        self.facture.update()
        self.facture.del_product(self.plat)
        self.facture.update()
        self.assertTrue(self.plat not in self.facture.produits.iterator())
        self.assertEqual(Decimal("0"), self.facture.total_ttc)
        self.assertEqual(Decimal("0"), self.facture.restant_a_payer)

    def test_regroup_produits(self):
        plat2 = ProduitVendu()
        plat2.produit = Produit.objects.get(nom="entrecote")
        plat3 = ProduitVendu()
        plat3.produit = Produit.objects.get(nom="pave de saumon")
        entree = ProduitVendu()
        entree.produit = Produit.objects.get(nom="salade normande")
        menu = ProduitVendu()
        menu.produit = Produit.objects.get(nom="jus abricot")
        self.facture.add_product(self.plat)
        self.facture.add_product(plat2)
        self.facture.add_product(plat3)
        self.facture.add_product(entree)
        self.facture.add_product(menu)
        resultat = OrderedDict([('salade normande', [(entree.id, entree)]),
                                ('entrecote', [(self.plat.id, self.plat), \
                                               (plat2.id, plat2)]),
                                ('pave de saumon', [(plat3.id, plat3)]),
                                ('jus abricot', [(menu.id, menu)])])
        self.assertEqual(resultat, self.facture.regroup_produits())

    def test_del_payment(self):
        payment = Paiement()
        montant = 42
        valeur_unitaire = 73
        paymentType = PaiementType()
        payment.montant = 73
        payment.type = paymentType
        payment.valeur_unitaire = Decimal(valeur_unitaire)
        payment.montant = Decimal(montant)
        self.facture.add_payment(paymentType, montant, valeur_unitaire)
        self.facture.del_payment(payment)

    def test_is_valid_payment(self):
        self.assertFalse(self.facture.is_valid_payment(42))
        self.facture.add_product(self.plat)
        self.facture.update()
        self.assertTrue(self.facture.is_valid_payment(42))
        self.facture.restant_a_payer = Decimal("0")
        self.assertFalse(self.facture.is_valid_payment(42))

    def test_rendre_monnaie(self):
        paiement = Paiement.objects.all()[0]
        self.facture.add_product(self.plat)
        self.facture.update()
        self.facture.rendre_monnaie(paiement)
        self.assertEqual(Decimal("-82.80"), self.facture.paiements.all()[0].montant)

    def test_add_payment(self):
        self.facture.add_product(self.plat)
        self.facture.update()
        self.facture.add_payment(PaiementType.objects.get(nom="CB"), "2")
        restant_a_payer = Decimal(str(self.plat.produit.prix - 2))
        self.assertEqual(self.facture.restant_a_payer, restant_a_payer)
        self.facture.add_payment(PaiementType.objects.get(nom="Espece"), "10")
        self.assertEqual(self.facture.restant_a_payer, Decimal(0))
        montant = Decimal(str(self.plat.produit.prix - 12))
        self.assertEqual(montant, (self.facture.paiements.all()[2]).montant)
        # TODO This is done just to execute more code
        # An assertion should be verified
        self.facture.send_in_the_kitchen()
        self.facture.est_un_repas()
        self.facture.get_working_day()
        self.facture.print_ticket()
