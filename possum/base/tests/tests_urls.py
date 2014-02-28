#!/usr/bin/python
# -*- coding: utf-8 -*-

# from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
#from django.utils.unittest.case import TestCase
from django.test import TestCase
from possum.base.models import Facture


# import mock
class Tests_urls(TestCase):
    fixtures = ['demo.json']

    def setUp(self):
        self.client = Client()
        self.latest_bill = Facture.objects.latest()

    def tearDown(self):
        self.logout()

    def test_home(self):
        ''' Test that the home urls work'''
        urls = [
            reverse('home'),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test__carte_categories(self):
        ''' Test that the home urls work. '''
        urls = [
            reverse('categories'),
# il doit y avoir une imprimante            reverse('categories_print'),
#            reverse('categories_send'),
            reverse('categories'),
            reverse('categories_add'),
#            reverse('categories_new'),
#            reverse('categories_view', args=('42',)),
#            reverse('categories_less_priority', args=('42',)),
#            reverse('categories_more_priority', args=('42',)),
#            reverse('categories_less_priority', args=('42',)),
#            reverse('categories_more_priority', args=('42',)),
#            reverse('categories_surtaxable', args=('42',)),
#            reverse('categories_name', args=('42',)),
#            reverse('categories_set_name', args=('42',)),
#            reverse('categories_color', args=('42',)),
#            reverse('categories_set_color', args=('42',)),
#            reverse('categories_vat_onsite', args=('42',)),
#            reverse('categories_set_vat_onsite', args=('42', '73')),
#            reverse('categories_vat_takeaway', args=('4')),
#            reverse('categories_set_vat_takeaway', args=('42', '73')),
#            reverse('categories_delete', args=('42',)),
#            reverse('categories_disable_surtaxe', args=('42',)),
#            reverse('categories_set_kitchen', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_carte(self):
        ''' Test that the carte urls work. '''
        urls = [
#            reverse('products_new', args=('2',)),
#            reverse('products_view', args=('4',)),
#            reverse('products_change', args=('4',)),
#            reverse('products_category', args=('2',)),
#            reverse('products_select_categories_ok', args=('2',)),
#            reverse('products_add_categories_ok', args=('4', '3')),
#            reverse('products_del_categories_ok', args=('4', '3')),
#            reverse('products_select_produits_ok', args=('4',)),
#            reverse('products_add_produits_ok', args=('4', '3')),
#            reverse('products_del_produits_ok', args=('4', '3')),
#            reverse('products_set_category', args=('4', '3')),
#            reverse('products_enable', args=('4',)),
#            reverse('products_cooking', args=('3',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_bill(self):
        ''' Test that the bill urls work. '''
        urls = [
            reverse('bill_home'),
            reverse('bill_new'),
            reverse('table_select', args=('4',)),
            reverse('table_set', args=('5', '2')),
            reverse('couverts_select', args=('42',)),
            reverse('couverts_set', args=('4', '7')),
            reverse('bill_categories', args=(self.latest_bill.id,)),
#            reverse('bill_categories', args=('2', '3')),
#            reverse('product_add', args=('4', '7')),
#            reverse('product_select', args=('4', '7')),
#            reverse('product_select_made_with', args=('42', '73')),
#            reverse('product_set_made_with', args=('42', '73', '51')),
#            reverse('subproduct_select', args=('42', '73', "51")),
            reverse('sold_view', args=('1', '13')),
#            reverse('sold_cooking', args=('42', '73', '51')),
#            reverse('sold_cooking', args=('42', '73', '51', '13')),
#            reverse('sold_cooking', args=('42', '73')),
#            reverse('sold_cooking', args=('42', '73', '51')),
#            reverse('sold_delete', args=('42', '73')),
#            reverse('subproduct_add', args=('42', '73', '51')),
#            reverse('bill_delete', args=('42',)),
#            reverse('bill_onsite', args=('42',)),
            reverse('prepare_payment', args=(self.latest_bill.id,)),
#            reverse('bill_payment', args=('42',)),
#            reverse('bill_payment_view', args=('42', '73')),
#            reverse('bill_payment_delete', args=('42', '73')),
#            reverse('bill_payment', args=('42', '73')),
#            reverse('bill_payment', args=('42', '73', '51', '7', '13')),
#            reverse('bill_payment_save', args=('42', '73', '51', '7', '13')),
#            reverse('bill_payment_set', args=('42', '73', '51', '7', '13')),
#            reverse('bill_payment_set', args=('42', '73', '51', '7', '13')),
#            reverse('bill_payment_set_left',
#                    args=('42', '73', '51', '7', '13', '1')),
#            reverse('bill_payment_set_right',
#                    args=('42', '73', '51', '7', '13', '1')),
#            reverse('bill_payment_count', args=('42', '73', '51', '7')),
#            reverse('bill_print', args=('42',)),
            reverse('bill_view', args=(self.latest_bill.id,)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)
        urls = [
                reverse('bill_send_kitchen', args=('5',)),
                ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 302)

    def test_jukebox(self):
        ''' Test that the jukebox urls work. '''
        urls = [
            reverse('jukebox'),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_kitchen(self):
        ''' Test that the kitchen urls work. '''
        urls = [
            reverse('kitchen'),
#            reverse('kitchen_for_bill', args=('4',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_manager(self):
        ''' Test that the manager urls work. '''
        urls = [
            reverse('manager'),
            reverse('credits'),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_archives(self):
        ''' Test that the archives urls work. '''
        urls = [
            reverse('archives'),
            reverse('archives_bill', args=('15',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_printer(self):
        ''' Test that the carte urls work. '''
        urls = [
            reverse('home'),
#            reverse('printer_add'),
#            reverse('printer_added', args=('42',)),
#            reverse('printer_view', args=('42',)),
#            reverse('printer_change_kitchen', args=('42',)),
#            reverse('printer_change_billing', args=('42',)),
#            reverse('printer_change_manager', args=('42',)),
#            reverse('printer_select_width', args=('42',)),
#            reverse('printer_test_print', args=('42',)),
#            reverse('printer_set_width', args=('42', '73',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_user(self):
        ''' Test that the user urls work. '''
        urls = [
            reverse('profile'),
            reverse('users'),
#            reverse('users_new'),
#            reverse('users_passwd', args=('2',)),
#            reverse('users_active', args=('1',)),
#            reverse('users_change', args=('1',)),
        ]
#        for perm in ["p1", "p2", "p3"]:
#            urls.append(reverse('users_change_perm', args=('2', perm,)))
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_authentication(self):
        ''' Test that the login/logout urls work. '''
        login = [reverse("login"), ]
        self.assert_http_status(login, 200)
        # We could want to redirect the user to the main page
        # if he/she is already logged
        # self.assert_http_status_after_login(login, 302)
        logout = [reverse("logout"), ]
        self.assert_http_status(logout, 302)
#        self.assert_http_status_after_login(logout, 200)

    def test_vats(self):
        ''' Test that the vats urls work. '''
        urls = [
            reverse('vat_new'),
            reverse('vats'),
            reverse('vats_view', args=('1',)),
            reverse('vats_change', args=('1',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_table(self):
        ''' Test that the table urls work'''
        urls = [
            reverse('tables'),
#            reverse('tables_zone_new'),
            reverse('tables_zone', args=('2',)),
#            reverse('tables_table_new', args=('42',)),
#            reverse('tables_table', args=('2', "2")),
#            reverse('tables_zone_delete', args=('2',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def assert_http_status(self, urls, status, msg='without logging in'):
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status,
             "For '{0}' {1}, the http response".format(url, msg)
             + ' status is {0} '.format(resp.status_code)
             + 'but it should be {0}'.format(status))

    def login(self):
        self.client.post('/users/login/',
                         {'username': 'demo', 'password': 'demo'})

    def logout(self):
        self.client.logout()

    def assert_http_status_after_login(self, urls, status):
        self.login()
        self.assert_http_status(urls, status, 'after a standard login')
        self.logout()
