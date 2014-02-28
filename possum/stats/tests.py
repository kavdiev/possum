# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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
from django.test import TestCase
from django.core.urlresolvers import reverse
from possum.stats.models import Stat
from possum.base.models import Facture
from django.test.client import Client
import datetime
from decimal import Decimal


class StatTests(TestCase):
    fixtures = ['demo.json']

    def setUp(self):
        """We create some bills and products to do tests
        """
        self.client = Client()

    def tearDown(self):
        self.logout()

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

    def test_login_for_urls(self):
        ''' Test that the reports urls work. '''
        urls = [
            reverse('stats_daily'),
            reverse('stats_weekly'),
            reverse('stats_monthly'),
            reverse('stats_charts'),
            reverse('stats_charts', args=('ttc',)),
            reverse('stats_charts', args=('bar',)),
            reverse('stats_charts', args=('guests',)),
            reverse('stats_charts', args=('vats',)),
            reverse('stats_charts', args=('payments',)),
            reverse('stats_charts', args=('categories',)),
            reverse('stats_charts', args=('42',)),
        ]
        self.assert_http_status(urls, 302)
        self.assert_http_status_after_login(urls, 200)

    def test_stats_monthly(self):
        """Test stats for a month
        """
        year = Facture.objects.all()[0].date_creation.year
        begin = "%d-03-31 23:59" % year
        end = "%d-05-01 00:00" % year
        bills = Facture.objects.filter(saved_in_stats=True,
                                       date_creation__gt=begin,
                                       date_creation__lt=end)
        objects = Stat.objects.filter(interval="m", year=year, month=4)
        # nb_bills
        stat_nb_bills = objects.filter(key="nb_bills")
        self.assertEqual(len(stat_nb_bills), 1)
        self.assertEqual(bills.count(), int(stat_nb_bills[0].value))
        # total_ttc, guests_total_ttc and bar_total_ttc
        total_ttc = Decimal("0")
        guests_total_ttc = Decimal("0")
        bar_total_ttc = Decimal("0")
        for bill in bills:
            total_ttc += bill.total_ttc
            if bill.est_un_repas():
                guests_total_ttc += bill.total_ttc
            else:
                bar_total_ttc += bill.total_ttc
        stat_total_ttc = objects.filter(key="total_ttc")
        self.assertEqual(len(stat_total_ttc), 1)
        stat_guests_total_ttc = objects.filter(key="guests_total_ttc")
        self.assertEqual(len(stat_guests_total_ttc), 1)
        stat_bar_total_ttc = objects.filter(key="bar_total_ttc")
        self.assertEqual(len(stat_bar_total_ttc), 1)
        self.assertEqual(total_ttc, stat_total_ttc[0].value)
        self.assertEqual(guests_total_ttc, stat_guests_total_ttc[0].value)
        self.assertEqual(bar_total_ttc, stat_bar_total_ttc[0].value)
        self.assertEqual(total_ttc, guests_total_ttc+bar_total_ttc)
        # VAT
        vat_ttc  = Decimal("0")
        for vat in objects.filter(key__contains="_vat"):
            vat_ttc += vat.value
        self.assertEqual(vat_ttc, total_ttc)

