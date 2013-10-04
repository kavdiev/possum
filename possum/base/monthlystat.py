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

from django.db import models
from django.db.models import Max, Avg, Min
from decimal import Decimal
import logging
import datetime

class MonthlyStat(models.Model):
    """Monthly statistics, full list of keys:
    # Common
    nb_bills      : number of invoices
    total_ttc        : total TTC
    ID_vat           : VAT part for vat ID
    
    # Products
    ID_product_nb    : how many product
    ID_product_value : total TTC for product ID
    ID_category_nb   : how many product sold in category ID
    ID_category_value: total TTC for category ID

    # Restaurant
    guests_nb        : how many people
    guests_average   : average TTC by guest
    guests_total_ttc : total TTC for guests

    # Bar
    bar_total_ttc    : total TTC for bar activity
    bar_nb           : how many invoices
    bar_average      : average TTC by invoice

    # Payments
    ID_payment_nb    : number of payment ID
    ID_payment_value : total for payment ID
    """
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    key = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ["year", "month"]

    def get_value(self, key, year, month):
        """Return value if exist and 0 else
        """
        try:
            stat = MonthlyStat.objects.get(key=key, year=year, month=month)
        except MonthlyStat.DoesNotExist:
            return Decimal("0")
        else:
            return stat.value

    def get_avg(self, key):
        stats = MonthlyStat.objects.filter(key=key).aggregate(
                        Avg('value'))['value__avg']
        if stats:
            return stats
        else:
            return Decimal("0")

    def get_max(self, key):
        stats = MonthlyStat.objects.filter(key=key).aggregate(
                        Max('value'))['value__max']
        if stats:
            return stats
        else:
            return Decimal("0")

    def add_bill(self, bill):
        date = bill.get_working_day()
        year = date.year
        month = date.month
        self.__add_bill_common(bill, year, month)
        self.__add_bill_products(bill, year, month)
        if bill.est_un_repas():
            self.__add_bill_guests(bill, year, month)
        else:
            self.__add_bill_bar(bill, year, month)
        self.__add_bill_payments(bill, year, month)
        return True

    def __add_bill_common(self, bill, year, month):
        nb_bills, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="nb_bills")
        nb_bills.value += 1
        nb_bills.save()
        total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="total_ttc")
        total_ttc.value += bill.total_ttc
        total_ttc.save()
        for vatonbill in bill.vats.iterator():
            key = "%s_vat" % vatonbill.vat_id
            stat, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)    
            stat.value += vatonbill.total
            stat.save()

    def __add_bill_products(self, bill, year, month):
        for product in bill.produits.iterator():
            key = "%s_product_nb" % product.produit_id
            product_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            product_nb.value += 1
            product_nb.save()
            key = "%s_product_value" % product.produit_id
            product_value, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            product_value.value += product.prix
            product_value.save()
            key = "%s_category_nb" % product.produit.categorie_id
            category_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            category_nb.value += 1
            category_nb.save()
            key = "%s_category_value" % product.produit.categorie_id
            category_value, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            category_value.value += product.prix
            category_value.save()
            # products in a menu
            for sub in product.contient.iterator():
                # il n'y a pas de prix pour les elements dans un menu
                key = "%s_product_nb" % sub.produit_id
                product_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
                product_nb.value += 1
                product_nb.save()
                key = "%s_category_nb" % sub.produit.categorie_id
                category_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
                category_nb.value += 1
                category_nb.save()

    def __add_bill_guests(self, bill, year, month):
        guests_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_nb")
        guests_nb.value += bill.couverts
        guests_nb.save()
        guests_total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_total_ttc")
        guests_total_ttc.value += bill.total_ttc
        guests_total_ttc.save()
        guests_average, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_average")
        if guests_nb.value:
            guests_average.value = guests_total_ttc.value / guests_nb.value
        else:
            guests_average.value = 0
        guests_average.save()

    def __add_bill_bar(self, bill, year, month):
        bar_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_nb")
        bar_nb.value += 1
        bar_nb.save()
        bar_total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_total_ttc")
        bar_total_ttc.value += bill.total_ttc
        bar_total_ttc.save()
        bar_average, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_average")
        if bar_nb.value:
            bar_average.value = bar_total_ttc.value / bar_nb.value
        else:
            bar_average.value = 0
        bar_average.save()

    def __add_bill_payments(self, bill, year, month):
        for payment in bill.paiements.iterator():
            key = "%s_payment_nb" % payment.type_id
            payment_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            payment_nb.value += 1
            payment_nb.save()
            key = "%s_payment_value" % payment.type_id
            payment_value, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            payment_value.value += payment.montant
            payment_value.save()

    def get_common(self, year, month):
        """Return les stats pour date sous forme de liste
        """
        result = []
        result.append("  -- %s/%s --" % (month, year))
        nb_bills = self.get_value("nb_bills", year, month)
        total_ttc = self.get_value("total_ttc", year, month)
        result.append("Total TTC (% 4d fact.): %11.2f" % (
                nb_bills, total_ttc))
        for vat in VAT.objects.iterator():
            tax = "TVA    % 6.2f%%:" % vat.tax
            key = "%s_vat" % vat.id
            result.append("%-20s %11.2f" % (
                    tax, MonthlyStat().get_value(key, year, month)))
        return result
