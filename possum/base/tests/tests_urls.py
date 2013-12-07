#!/usr/bin/python
# -*- coding: utf-8 -*-

# from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
#from django.utils.unittest.case import TestCase
from django.test import TestCase


# import mock
class Tests_urls(TestCase):
    fixtures = ['demo.json']

    def setUp(self):
        self.client = Client()

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
            reverse('categories_send'),
            reverse('categories'),
            reverse('categories_add'),
            reverse('categories_new'),
            reverse('categories_view', args=('42',)),
            reverse('categories_less_priority', args=('42',)),
            reverse('categories_more_priority', args=('42',)),
            reverse('categories_less_priority', args=('42',)),
            reverse('categories_more_priority', args=('42',)),
            reverse('categories_surtaxable', args=('42',)),
            reverse('categories_name', args=('42',)),
            reverse('categories_set_name', args=('42',)),
            reverse('categories_color', args=('42',)),
            reverse('categories_set_color', args=('42',)),
            reverse('categories_vat_onsite', args=('42',)),
            reverse('categories_set_vat_onsite', args=('42', '73')),
            reverse('categories_vat_takeaway', args=('4')),
            reverse('categories_set_vat_takeaway', args=('42', '73')),
            reverse('categories_delete', args=('42',)),
            reverse('categories_disable_surtaxe', args=('42',)),
            reverse('categories_set_kitchen', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_carte(self):
        ''' Test that the carte urls work. '''
        urls = [
            reverse('products_new', args=('42',)),
            reverse('products_view', args=('42',)),
            reverse('products_change', args=('42',)),
            reverse('products_category', args=('42',)),
            reverse('products_select_categories_ok', args=('42',)),
            reverse('products_add_categories_ok', args=('42', '73')),
            reverse('products_del_categories_ok', args=('42', '73')),
            reverse('products_select_produits_ok', args=('42',)),
            reverse('products_add_produits_ok', args=('42', '73')),
            reverse('products_del_produits_ok', args=('42', '73')),
            reverse('products_set_category', args=('42', '73')),
            reverse('products_enable', args=('42',)),
            reverse('products_cooking', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_bill(self):
        ''' Test that the bill urls work. '''
        urls = [
            reverse('home_factures'),
            reverse('bill_new'),
            reverse('table_select', args=('42',)),
            reverse('table_set', args=('42', '73')),
            reverse('couverts_select', args=('42',)),
            reverse('couverts_set', args=('42', '73')),
            reverse('category_select', args=('42',)),
            reverse('category_select', args=('42', '73')),
            reverse('product_add', args=('42', '73')),
            reverse('product_select', args=('42', '73')),
            reverse('product_select_made_with', args=('42', '73')),
            reverse('product_set_made_with', args=('42', '73', '51')),
            reverse('subproduct_select', args=('42', '73', "51")),
            reverse('sold_view', args=('42', '73')),
            reverse('sold_cooking', args=('42', '73', '51')),
            reverse('sold_cooking', args=('42', '73', '51', '13')),
            reverse('sold_cooking', args=('42', '73')),
            reverse('sold_cooking', args=('42', '73', '51')),
            reverse('sold_delete', args=('42', '73')),
            reverse('subproduct_add', args=('42', '73', '51')),
            reverse('bill_delete', args=('42',)),
            reverse('bill_onsite', args=('42',)),
            reverse('bill_payment', args=('42',)),
            reverse('bill_payment_view', args=('42', '73')),
            reverse('bill_payment_delete', args=('42', '73')),
            reverse('bill_payment', args=('42', '73')),
            reverse('bill_payment', args=('42', '73', '51', '7', '13')),
            reverse('bill_payment_save', args=('42', '73', '51', '7', '13')),
            reverse('bill_payment_set', args=('42', '73', '51', '7', '13')),
            reverse('bill_payment_set', args=('42', '73', '51', '7', '13')),
            reverse('bill_payment_set_left',
                    args=('42', '73', '51', '7', '13', '1')),
            reverse('bill_payment_set_right',
                    args=('42', '73', '51', '7', '13', '1')),
            reverse('bill_payment_count', args=('42', '73', '51', '7')),
            reverse('bill_print', args=('42',)),
            reverse('bill_send_kitchen', args=('42',)),
            reverse('bill_view', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

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
            reverse('kitchen_for_bill', args=('4',)),
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
            reverse('printer_add'),
            reverse('printer_added', args=('42',)),
            reverse('printer_view', args=('42',)),
            reverse('printer_change_kitchen', args=('42',)),
            reverse('printer_change_billing', args=('42',)),
            reverse('printer_change_manager', args=('42',)),
            reverse('printer_select_width', args=('42',)),
            reverse('printer_test_print', args=('42',)),
            reverse('printer_set_width', args=('42', '73',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_user(self):
        ''' Test that the user urls work. '''
        urls = [
            reverse('profile'),
            reverse('users'),
            reverse('users_new'),
            reverse('users_passwd', args=('42',)),
            reverse('users_active', args=('42',)),
            reverse('users_change', args=('42',)),
        ]
        for perm in ["p1", "p2", "p3"]:
            urls.append(reverse('users_change_perm', args=('42', perm,)))
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
        self.assert_http_status_after_login(logout, 200)

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
            reverse('tables_zone_new'),
            reverse('tables_zone', args=('42',)),
            reverse('tables_table_new', args=('42',)),
            reverse('tables_table', args=('42', "42")),
            reverse('tables_zone_delete', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_reports(self):
        ''' Test that the reports urls work. '''
        urls = [
            reverse('rapports_home'),
            reverse('rapports_daily'),
            reverse('rapports_daily_vats_print', args=('2013', '10', '10')),
            reverse('rapports_daily_vats_send', args=('2013', '10', '10')),
            reverse('rapports_daily_print', args=('2013', '10', '10')),
            reverse('rapports_daily_send', args=('2013', '10', '10')),
            reverse('rapports_weekly'),
            reverse('rapports_weekly_vats_print', args=('4242', '13')),
            reverse('rapports_weekly_vats_send', args=('4242', '13')),
            reverse('rapports_weekly_print', args=('4242', '13')),
            reverse('rapports_weekly_send', args=('4242', '13')),
            reverse('rapports_monthly'),
            reverse('rapports_monthly_vats_print', args=('4242', '73')),
            reverse('rapports_monthly_vats_send', args=('4242', '73')),
            reverse('rapports_monthly_print', args=('4242', '73')),
            reverse('rapports_monthly_send', args=('4242', '73')),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_charts(self):
        ''' Test that the charts urls work. '''
        urls = [
            reverse('charts_year'),
            reverse('charts_year_with_argument', args=("2013",)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

#     @mock.patch('model.PagesSearch.filter_by', pages_search_filter_by)
#     def test_page_oid_exists(self):
#         ''' Test that the page urls work'''
#
#         urls = [reverse('page', args=('5ae1e22d-6ea0073ed6e', ))]
#         self.assert_http_status(urls, 302)
#         self.assert_http_status_after_login(urls, 200)

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
