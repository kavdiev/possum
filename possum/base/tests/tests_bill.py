#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    def test_add_product(self):
        self.assertTrue(self.facture.is_empty())
        self.facture.add_product(self.plat)
        self.facture.update()
        self.assertTrue(self.plat in self.facture.produits.iterator())
        self.assertEqual(self.plat.produit.prix, self.facture.total_ttc)
        self.assertEqual(self.plat.produit.prix, self.facture.restant_a_payer)

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
        payment = Paiement()
        payment.type = PaiementType()
        payment.montant = Decimal("900")
        self.facture.add_product(self.plat)
        self.facture.update()
        self.facture.rendre_monnaie(payment)
        left = self.facture.total_ttc - Decimal("900")
        self.assertEqual(left, self.facture.paiements.all()[0].montant)

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
        self.facture.print_ticket_kitchen()
        self.facture.est_un_repas()
        self.facture.print_ticket()
