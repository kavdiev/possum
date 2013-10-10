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

class Test_Views(unittest.TestCase):

    # Création des répertoires obligatoires
    def test_create_default_directory(self):
        pass  # TODO
    
    def test_get_last_year(self, date):
        """Retourne le jour de l'année précédente
        afin de comparer les resultats des 2 journées
        date doit être au format datetime
        """
        pass  # TODO
    
    def test_get_user(self, request):
        pass  # TODO
    
    def test_permission_required(self, perm, **kwargs):
        """This decorator redirect the user to '/'
        if he hasn't the permission.
        """
        pass  # TODO
    

    def test_home(self, request):
        pass  # TODO
    

    def test_kitchen(self, request):
        pass  # TODO
    

    def test_kitchen_for_bill(self, request, bill_id):
        pass  # TODO
    

    def test_carte(self, request):
        """This is not used.
        """
        pass  # TODO
    

    def test_categories_send(self, request):
        pass  # TODO
    

    def test_categories_print(self, request):
        pass  # TODO
    

    def test_categories(self, request):
        pass  # TODO
    

    def test_categories_delete(self, request, cat_id):
        pass  # TODO
    

    def test_categories_view(self, request, cat_id):
        pass  # TODO
    

    def test_categories_add(self, request):
        pass  # TODO
    

    def test_categories_new(self, request):
        pass  # TODO
    

    def test_categories_name(self, request, cat_id):
        pass  # TODO
    

    def test_categories_color(self, request, cat_id):
        pass  # TODO
    

    def test_categories_less_priority(self, request, cat_id, nb=1):
        pass  # TODO
    

    def test_categories_more_priority(self, request, cat_id, nb=1):
        pass  # TODO
    

    def test_categories_surtaxable(self, request, cat_id):
        pass  # TODO
    

    def test_categories_vat_takeaway(self, request, cat_id):
        pass  # TODO
    

    def test_categories_set_vat_takeaway(self, request, cat_id, vat_id):
        pass  # TODO
    

    def test_categories_set_vat_onsite(self, request, cat_id, vat_id):
        pass  # TODO
    

    def test_categories_vat_onsite(self, request, cat_id):
        pass  # TODO
    

    def test_products_view(self, request, product_id):
        pass  # TODO
    

    def test_products_new(self, request, cat_id):
        pass  # TODO
    

    def test_categories_set_color(self, request, cat_id):
        pass  # TODO
    

    def test_products_set_category(self, request, product_id, cat_id):
        pass  # TODO
    

    def test_products_category(self, request, product_id):
        pass  # TODO
    

    def test_products_del_produits_ok(self, request, product_id, sub_id):
        pass  # TODO
    

    def test_products_select_produits_ok(self, request, product_id):
        pass  # TODO
    

    def test_products_add_produits_ok(self, request, product_id, sub_id):
        pass  # TODO
    

    def test_products_del_categories_ok(self, request, product_id, cat_id):
        pass  # TODO
    

    def test_products_add_categories_ok(self, request, product_id, cat_id):
        pass  # TODO
    

    def test_products_select_categories_ok(self, request, product_id):
        pass  # TODO
    

    def test_products_cooking(self, request, product_id):
        pass  # TODO
    

    def test_products_enable(self, request, product_id):
        pass  # TODO
    

    def test_products_change(self, request, product_id):
        pass  # TODO
    

    def test_categories_set_name(self, request, cat_id):
        pass  # TODO
    

    def test_categories_set_kitchen(self, request, cat_id):
        pass  # TODO
    

    def test_categories_disable_surtaxe(self, request, cat_id):
        pass  # TODO
    

    def test_tables_zone_delete(self, request, zone_id):
        pass  # TODO
    

    def test_tables_table_new(self, request, zone_id):
        pass  # TODO
    

    def test_tables_zone_new(self, request):
        pass  # TODO
    

    def test_tables_table(self, request, zone_id, table_id):
        pass  # TODO
    

    def test_tables_zone(self, request, zone_id):
        pass  # TODO
    

    def test_tables(self, request):
        pass  # TODO
    
    def test_vats(self, request):
        pass  # TODO
    

    def test_vats_view(self, request, vat_id):
        pass  # TODO
    

    def test_vats_change(self, request, vat_id):
        pass  # TODO
    

    def test_vat_new(self, request):
        pass  # TODO
    

    def test_credits(self, request):
        pass  # TODO
    

    def test_rapports_daily(self, request):
        """
        Affiche le rapport pour une journée
        """
        pass  # TODO
    

    def test_rapports_weekly(self, request):
        """
        Affiche le rapport pour une semaine
        """
        pass  # TODO
    

    def test_rapports_monthly(self, request):
        """
        Affiche le rapport pour un mois
        """
        pass  # TODO
    
    def test_rapports_send(self, request, subject, data):
        pass  # TODO
        
    

    def test_rapports_daily_send(self, request, year, month, day):
        pass  # TODO
    

    def test_rapports_weekly_send(self, request, year, week):
        pass  # TODO
    

    def test_rapports_monthly_send(self, request, year, month):
        pass  # TODO
    
    def test_rapports_print(self, request, subject, data):
        pass  # TODO
    

    def test_rapports_daily_print(self, request, year, month, day):
        pass  # TODO
    

    def test_rapports_weekly_print(self, request, year, week):
        pass  # TODO
    

    def test_rapports_monthly_print(self, request, year, month):
        pass  # TODO
    
    def test_rapports_vats_send(self, request, subject, data):
        pass  # TODO
    

    def test_rapports_daily_vats_send(self, request, year, month, day):
        pass  # TODO
    

    def test_rapports_weekly_vats_send(self, request, year, week):
        pass  # TODO
    

    def test_rapports_monthly_vats_send(self, request, year, month):
        pass  # TODO
    
    def test_rapports_vats_print(self, request, data):
        pass  # TODO
    

    def test_rapports_daily_vats_print(self, request, year, month, day):
        pass  # TODO
    

    def test_rapports_weekly_vats_print(self, request, year, week):
        pass  # TODO
    

    def test_rapports_monthly_vats_print(self, request, year, month):
        pass  # TODO
    

    def test_manager(self, request):
        pass  # TODO
    

    def test_printers(self, request):
        pass  # TODO
    

    def test_printer_add(self, request):
        pass  # TODO
    

    def test_printer_added(self, request, name):
        """Save new printer"""
        pass  # TODO
    

    def test_printer_view(self, request, printer_id):
        pass  # TODO
    

    def test_printer_select_width(self, request, printer_id):
        pass  # TODO
    

    def test_printer_set_width(self, request, printer_id, number):
        pass  # TODO
    

    def test_printer_test_print(self, request, printer_id):
        pass  # TODO
    

    def test_printer_change_kitchen(self, request, printer_id):
        pass  # TODO
    

    def test_printer_change_billing(self, request, printer_id):
        pass  # TODO
    

    def test_printer_change_manager(self, request, printer_id):
        pass  # TODO
    

    def test_profile(self, request):
        pass  # TODO
    

    def test_users(self, request):
        pass  # TODO
    

    def test_users_new(self, request):
        pass  # TODO
    

    def test_users_change(self, request, user_id):
        pass  # TODO
    

    def test_users_active(self, request, user_id):
        pass  # TODO
    

    def test_users_passwd(self, request, user_id):
        """Set a new random password for a user.
        """
        pass  # TODO
    

    def test_users_change_perm(self, request, user_id, codename):
        pass  # TODO
    

    def test_bill_new(self, request):
        """Create a new bill"""
        pass  # TODO
    

    def test_bill_send_kitchen(self, request, bill_id):
        """Send in the kitchen"""
        pass  # TODO
    

    def test_bill_print(self, request, bill_id):
        """Print the bill"""
        pass  # TODO
    

    def test_table_select(self, request, bill_id):
        """Select/modify table of a bill"""
        pass  # TODO
    

    def test_table_set(self, request, bill_id, table_id):
        """Select/modify table of a bill"""
        pass  # TODO
    

    def test_category_select(self, request, bill_id, category_id=None):
        """Select a category to add a new product on a bill."""
        pass  # TODO
    

    def test_product_select_made_with(self, request, bill_id, product_id):
        pass  # TODO
    

    def test_product_set_made_with(self, request, bill_id, product_id, category_id):
        pass  # TODO
    

    def test_product_select(self, request, bill_id, category_id):
        """Select a product to add on a bill."""
        pass  # TODO
    

    def test_subproduct_select(self, request, bill_id, sold_id, category_id):
        """Select a subproduct to a product."""
        pass  # TODO
    

    def test_sold_view(self, request, bill_id, sold_id):
        pass  # TODO
    

    def test_sold_delete(self, request, bill_id, sold_id):
         pass  # TODO
    

    def test_subproduct_add(self, request, bill_id, sold_id, product_id):
        """Add a product to a bill. If this product contains others products,
        we have to add them too."""
        pass  # TODO
    

    def test_product_add(self, request, bill_id, product_id):
        """Add a product to a bill. If this product contains others products,
        we have to add them too."""
        pass  # TODO
    

    def test_sold_cooking(self, request, bill_id, sold_id, cooking_id= -1, menu_id= -1):
        pass  # TODO
    

    def test_couverts_select(self, request, bill_id):
        """List of couverts for a bill"""
        pass  # TODO
    

    def test_couverts_set(self, request, bill_id, number):
        """Set couverts of a bill"""
        pass  # TODO
    

    def test_factures(self, request):
        pass  # TODO
    

    def test_bill_payment_set_right(self, request, bill_id, type_id, left, right, number, count):
        pass  # TODO
    

    def test_bill_payment_set_left(self, request, bill_id, type_id, left, right, number, count):
        pass  # TODO
    

    def test_bill_payment_delete(self, request, bill_id, payment_id):
        pass  # TODO
    

    def test_bill_payment_view(self, request, bill_id, payment_id):
        pass  # TODO
    

    def test_bill_payment_save(self, request, bill_id, type_id, left, right, count):
        """Enregistre le paiement
        """
        pass  # TODO
    

    def test_bill_payment_set(self, request, bill_id, type_id, left, right, count, part="left"):
        """if part == "left" alors on fait la partie gauche du nombre
        sinon on fait la partie droite
        """
        pass  # TODO
    

    def test_bill_payment_count(self, request, bill_id, type_id, left, right):
        pass  # TODO
    

    def test_bill_payment(self, request, bill_id, type_id= -1, count= -1, left=0, right=0):
        pass  # TODO
    

    def test_bill_view(self, request, bill_id):
        pass  # TODO
    

    def test_bill_delete(self, request, bill_id):
        pass  # TODO
    

    def test_bill_onsite(self, request, bill_id):
        pass  # TODO
    

    def test_archives(self, request):
        pass  # TODO
    

    def test_archives_bill(self, request, bill_id):
        pass  # TODO
    

    def test_jukebox(self, request):
        pass  # TODO
    
