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

import datetime
from decimal import Decimal
from django.db import models
import logging

from django.db.models import Max, Avg

from chartit import PivotDataPool, PivotChart
from possum.base.category import Categorie
from possum.base.payment import PaiementType
from possum.base.product import Produit
from possum.base.utils import nb_sorted
from possum.base.vat import VAT


logger = logging.getLogger(__name__)


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
            return "%.2f" % stats
        else:
            return "0.00"

    def get_max(self, key):
        stats = MonthlyStat.objects.filter(key=key).aggregate(
                        Max('value'))['value__max']
        if stats:
            return "%.2f" % stats
        else:
            return "0.00"

    def get_common(self, year, month):
        """Return les stats pour date sous forme de liste
        """
        result = []
        result.append("  -- %s/%s --" % (month, year))
        result.append("Fait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
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

    def get_data(self, data, year, month):
        """Recupere les donnees pour un mois
        """
        for key in ['nb_bills', 'total_ttc']:
            data[key] = MonthlyStat().get_value(key, year, month)
        data['vats'] = []
        for vat in VAT.objects.order_by('name').iterator():
            key = "%s_vat" % vat.id
            value = MonthlyStat().get_value(key, year, month)
            data['vats'].append("TVA % 6.2f%% : %.2f" % (vat.tax, value))
        # restaurant
        for key in ['guests_nb', 'guests_average', 'guests_total_ttc']:
            data[key] = MonthlyStat().get_value(key, year, month)
        # bar
        for key in ['bar_nb', 'bar_average', 'bar_total_ttc']:
            data[key] = MonthlyStat().get_value(key, year, month)
        # categories & products
        categories = []
        products = []
        for category in Categorie.objects.order_by('priorite', 'nom').iterator():
            category.nb = MonthlyStat().get_value("%s_category_nb" % category.id,
                                                  year, month)
            if category.nb > 0:
                categories.append(category)
                for product in Produit.objects.filter(categorie=category,
                                                      actif=True).iterator():
                    product.nb = MonthlyStat().get_value("%s_product_nb" % product.id,
                                                         year, month)
                    if product.nb > 0:
                        products.append(product)
        data['categories'] = sorted(categories, cmp=nb_sorted)
        data['products'] = sorted(products, cmp=nb_sorted)
        # payments
        data['payments'] = []
        for payment_type in PaiementType.objects.order_by("nom").iterator():
            data['payments'].append("%s : %.2f" % (
                    payment_type.nom,
                    MonthlyStat().get_value("%s_payment_value" % payment_type.id,
                                             year, month)))
        return data
