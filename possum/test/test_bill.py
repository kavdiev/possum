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
import unittest

class Test_Facture(unittest.TestCase):

    def test_something_for_the_kitchen(self):
        """If one, set the first category to prepare in the
        kitchen. Example: Entree if there are Entree and Plat.
        """
        pass # TODO

    def test_get_first_todolist_for_kitchen(self):
        """Prepare la liste des produits a envoyer en cuisine
        """
        pass # TODO

    def test_send_in_the_kitchen(self):
        """We send the first category available to the kitchen.
        """
        pass # TODO

    def test_guest_couverts(self):
        """Essaye de deviner le nombre de couverts"""
        pass # TODO

    def test_set_couverts(self, nb):
        """Change le nombre de couvert"""
        pass # TODO

    def test_set_table(self, table):
        """Change la table de la facture
        On prend en compte le changement de tarification si changement
        de zone.

        On ne traite pas le cas ou les 2 tables sont surtaxées à des montants
        différents.
        """
        pass # TODO

    def test_nb_soldee_jour(self, date):
        """Nombre de facture soldee le jour 'date'"""
        pass # TODO

    def test_non_soldees(self):
        """Retourne la liste des factures non soldees"""
        pass # TODO

    def test_compute_total(self):
        pass # TODO

    def test_add_product_prize(self, product):
        """Ajoute le prix d'un ProduitVendu sur la facture."""
        pass # TODO

    def test_del_product_prize(self, product):
        pass # TODO

    def test_add_surtaxe(self):
        """Add surtaxe on all needed products
        """
        pass # TODO

    def test_remove_surtaxe(self):
        """Remove surtaxe on all needed products
        """
        pass # TODO

    def test_add_product(self, vendu):
        """Ajout d'un produit à la facture.
        Si c'est le premier produit alors on modifie la date de creation
        """
        pass # TODO

    def test_del_product(self, product):
        """On enleve un produit à la facture.

        Si le montant est négatif après le retrait d'un élèment,
        c'est qu'il reste certainement une remise, dans
        ce cas on enlève tous les produits.
        """
        pass # TODO

    def test_del_all_payments(self):
        """On supprime tous les paiements"""
        pass # TODO

    def test_del_payment(self, payment):
        """On supprime un paiement"""
        pass # TODO

    def test_get_users(self):
        """Donne la liste des noms d'utilisateurs"""
        pass # TODO

    def test_get_last_connected(self):
        pass # TODO

    def test_authenticate(self, username, password):
        pass # TODO

    def test_getTvaNormal(self):
        """
            calcul la TVA
            On arrondi seulement à 1 parce que les 2 décimals sont dans la partie entière du montant
            # la TVA est sur le HT !!
        """
        pass # TODO

    def test_getTvaAlcool(self):
        pass # TODO

    def test_get_resume(self):
        pass # TODO

    def test_get_montant(self):
        pass # TODO

    def test_add_payment(self, type_payment, montant, valeur_unitaire="1.0"):
        """
        type_payment est un TypePaiement
        montant et valeur_unitaire sont des chaines de caracteres
        qui seront converti en Decimal

        Si le montant est superieur au restant du alors on rembourse en
        espece.
        """
        pass # TODO

    def test_est_soldee(self):
        """La facture a été utilisée et soldée"""
        pass # TODO

    def test_est_un_repas(self):
        """Est ce que la facture contient un element qui est
        fabriqué en cuisine
        """
        pass # TODO

    def test_is_empty(self):
        """La facture est vierge"""
        pass # TODO

    def test_est_surtaxe(self):
        """
        Table is surtaxed et il n'y a pas de nourriture.
        """
        pass # TODO

    def test_get_bills_for(self, date):
        """Retourne la liste des factures soldees du jour 'date'
        date de type datetime
        """
        pass # TODO

    def test_print_ticket(self):
        pass # TODO

    def test_get_working_day(self):
        """Retourne la journee de travail officiel
            (qui fini a 5h du matin)
            date de type datetime.datetime.now()
        """
        pass # TODO
