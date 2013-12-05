#!/usr/bin/python
# -*- coding: utf-8 -*-

# from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.unittest.case import TestCase
# import mock


class Tests_urls(TestCase):

    @staticmethod
    def setUpClass():
        Tests_urls.client = Client()

    def tearDown(self):
        self.logout()

    def test_home(self):
        ''' Test that the home urls work'''
        urls = [reverse('home'),
                ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test__carte_categories(self):
        ''' Test that the home urls work'''
        urls = [
            reverse('categories'),
            reverse('categories_print'),
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
            reverse('categories_vat_takeaway', args=('42', '73')),
            reverse('categories_set_vat_takeaway', args=('42', '73')),
            reverse('categories_delete', args=('42', '73')),
            reverse('categories_disable_surtaxe', args=('42', '73')),
            reverse('categories_set_kitchen', args=('42', '73')),
                ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_table(self):
        ''' Test that the table urls work'''
        urls = [reverse('tables'),
                reverse('tables_zone_new'),
                reverse('tables_zone', args=('42',)),
                reverse('tables_table_new', args=('42',)),
                reverse('tables_table', args=('42', "42")),
                reverse('tables_zone_delete', args=('42',)),
                ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

#     @mock.patch('model.searchmanagement.PagesSearch.filter_by', pages_search_filter_by)
#     def test_page_oid_exists(self):
#         ''' Test that the page urls work'''
#
#         urls = [reverse('page', args=('5ae1e22d-f37d-43a4-90c1-d6ea0073ed6e', ))]
#         self.assert_http_status(urls, 302)
#         self.assert_http_status_after_login(urls, 200)

    def assert_http_status(self, urls, status, msg='without logging in'):
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status,
                             "For '{0}' {1}, the http response".format(url,
                                                                       msg)
                             + ' status is {0} '.format(resp.status_code)
                             + 'but it should be {0}'.format(status))

    @staticmethod
    def login():
        Tests_urls.client.post(reverse('login'), {
                               'username': "demo",
                               'password': "demo"})

    @staticmethod
    def logout():
        Tests_urls.client.post(reverse('logout'))

    def assert_http_status_after_login(self, urls, status):
        self.login()
        self.assert_http_status(urls, status, 'after a standard login')
        self.logout()
