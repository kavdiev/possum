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

from decimal import Decimal
from django.db import models
from django.db.models import Max, Avg
from monthly_stat import MonthlyStat
from possum.base.bill import Facture
from possum.base.category import Categorie
from possum.base.payment import PaiementType
from possum.base.product import Produit
from possum.base.utils import nb_sorted
from possum.base.vat import VAT
from weekly_stat import WeeklyStat
import datetime
import logging

logger = logging.getLogger(__name__)

def add_value(values, key, value):
    if key in values:
        values[key] += value
    else:
        values[key] = value
    return values

class DailyStat(models.Model):
    """Daily statistics, full list of keys:
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
    date = models.DateField()
    key = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        get_latest_by = 'date'

    def get_value(self, key, date):
        """Return value if exist and 0 else
        """
        try:
            stat = DailyStat.objects.get(date=date, key=key)
        except DailyStat.DoesNotExist:
            return Decimal("0")
        else:
            return stat.value

    def get_avg(self, key):
        stats = DailyStat.objects.filter(key=key).aggregate(
                        Avg('value'))['value__avg']
        if stats:
            return "%.2f" % stats
        else:
            return "0.00"

    def get_max(self, key):
        stats = DailyStat.objects.filter(key=key).aggregate(
                        Max('value'))['value__max']
        if stats:
            return "%.2f" % stats
        else:
            return "0.00"

    def add_bill(self, bill):
        """if necessary, add this bill
        """
        logger.debug(" ")
        if bill.saved_in_stats:
            logger.warning("Bill [%s] is already in stats" % bill.id)
            return False
        else:
            if bill.est_soldee():
                date = bill.get_working_day()
                week = date.strftime("%U")
                month = date.month
                year = date.year
                self.__add_bill_common(bill, date, year, month, week)
                self.__add_bill_products(bill, date, year, month, week)
                if bill.est_un_repas():
                    self.__add_bill_guests(bill, date, year, month, week)
                else:
                    self.__add_bill_bar(bill, date, year, month, week)
                self.__add_bill_payments(bill, date, year, month, week)
                bill.saved_in_stats = True
                bill.save()
                return True
            else:
                logger.warning("Bill [%s] is not ended" % bill.id)
                return False

    def __add_bill_common(self, bill, date, year, month, week):
        logger.debug(" ")
        nb_bills, created = DailyStat.objects.get_or_create(date=date, key="nb_bills")
        nb_bills.value += 1
        nb_bills.save()
        nb_bills, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="nb_bills")
        nb_bills.value += 1
        nb_bills.save()
        nb_bills, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="nb_bills")
        nb_bills.value += 1
        nb_bills.save()
        total_ttc, created = DailyStat.objects.get_or_create(date=date, key="total_ttc")
        total_ttc.value += bill.total_ttc
        total_ttc.save()
        total_ttc, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="total_ttc")
        total_ttc.value += bill.total_ttc
        total_ttc.save()
        total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="total_ttc")
        total_ttc.value += bill.total_ttc
        total_ttc.save()
        for vatonbill in bill.vats.iterator():
            if vatonbill.total:
                key = "%s_vat" % vatonbill.vat_id
                stat, created = DailyStat.objects.get_or_create(date=date, key=key)    
                stat.value += vatonbill.total
                stat.save()
                stat, created = WeeklyStat.objects.get_or_create(year=year, week=week, key=key)
                stat.value += vatonbill.total
                stat.save()
                stat, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
                stat.value += vatonbill.total
                stat.save()

    def __add_bill_products(self, bill, date, year, month, week):
        """On fonctionne en deux passages:
        - en 1er on construit values avec toutes les stats
        - en 2eme on enregistre les résultats

        Cela nous permet de regrouper les stats de plusieurs catégories
        """
        logger.debug(" ")
        values = {}
        # on construit les valeurs
        for product in bill.produits.iterator():
            key = "%s_product_nb" % product.produit_id
            add_value(values, key, 1)
            key = "%s_product_value" % product.produit_id
            add_value(values, key, product.prix)
            key = "%s_category_nb" % product.produit.categorie_id
            add_value(values, key, 1)
            key = "%s_category_value" % product.produit.categorie_id
            add_value(values, key, product.prix)
            # products in a menu
            for sub in product.contient.iterator():
                # il n'y a pas de prix pour les elements dans un menu
                key = "%s_product_nb" % sub.produit_id
                add_value(values, key, 1)
                key = "%s_category_nb" % sub.produit.categorie_id
                add_value(values, key, 1)
        # on enregistre les stats
        for key in values.keys():
            stat, created = DailyStat.objects.get_or_create(date=date, key=key)
            stat.value += values[key]
            stat.save()
            stat, created = WeeklyStat.objects.get_or_create(year=year, week=week, key=key)
            stat.value += values[key]
            stat.save()
            stat, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            stat.value += values[key]
            stat.save()

    def __add_bill_guests(self, bill, date, year, month, week):
        logger.debug(" ")
        guests_nb, created = DailyStat.objects.get_or_create(date=date, key="guests_nb")
        if bill.couverts == 0:
            # if not, we try to find a number
            bill.couverts = bill.guest_couverts()
            bill.save()
        guests_nb.value += bill.couverts
        guests_nb.save()
        guests_nb, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="guests_nb")
        guests_nb.value += bill.couverts
        guests_nb.save()
        guests_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_nb")
        guests_nb.value += bill.couverts
        guests_nb.save()
        guests_total_ttc, created = DailyStat.objects.get_or_create(date=date, key="guests_total_ttc")
        guests_total_ttc.value += bill.total_ttc
        guests_total_ttc.save()
        guests_total_ttc, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="guests_total_ttc")
        guests_total_ttc.value += bill.total_ttc
        guests_total_ttc.save()
        guests_total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_total_ttc")
        guests_total_ttc.value += bill.total_ttc
        guests_total_ttc.save()
        guests_average, created = DailyStat.objects.get_or_create(date=date, key="guests_average")
        if guests_nb.value:
            guests_average.value = guests_total_ttc.value / guests_nb.value
        else:
            guests_average.value = 0
        guests_average.save()
        guests_average, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="guests_average")
        if guests_nb.value:
            guests_average.value = guests_total_ttc.value / guests_nb.value
        else:
            guests_average.value = 0
        guests_average.save()
        guests_average, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="guests_average")
        if guests_nb.value:
            guests_average.value = guests_total_ttc.value / guests_nb.value
        else:
            guests_average.value = 0
        guests_average.save()

    def __add_bill_bar(self, bill, date, year, month, week):
        logger.debug(" ")
        bar_nb, created = DailyStat.objects.get_or_create(date=date, key="bar_nb")
        bar_nb.value += 1
        bar_nb.save()
        bar_nb, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="bar_nb")
        bar_nb.value += 1
        bar_nb.save()
        bar_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_nb")
        bar_nb.value += 1
        bar_nb.save()
        bar_total_ttc, created = DailyStat.objects.get_or_create(date=date, key="bar_total_ttc")
        bar_total_ttc.value += bill.total_ttc
        bar_total_ttc.save()
        bar_total_ttc, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="bar_total_ttc")
        bar_total_ttc.value += bill.total_ttc
        bar_total_ttc.save()
        bar_total_ttc, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_total_ttc")
        bar_total_ttc.value += bill.total_ttc
        bar_total_ttc.save()
        bar_average, created = DailyStat.objects.get_or_create(date=date, key="bar_average")
        if bar_nb.value:
            bar_average.value = bar_total_ttc.value / bar_nb.value
        else:
            bar_average.value = 0
        bar_average.save()
        bar_average, created = WeeklyStat.objects.get_or_create(year=year, week=week, key="bar_average")
        if bar_nb.value:
            bar_average.value = bar_total_ttc.value / bar_nb.value
        else:
            bar_average.value = 0
        bar_average.save()
        bar_average, created = MonthlyStat.objects.get_or_create(year=year, month=month, key="bar_average")
        if bar_nb.value:
            bar_average.value = bar_total_ttc.value / bar_nb.value
        else:
            bar_average.value = 0
        bar_average.save()

    def __add_bill_payments(self, bill, date, year, month, week):
        logger.debug(" ")
        for payment in bill.paiements.iterator():
            key = "%s_payment_nb" % payment.type_id
            payment_nb, created = DailyStat.objects.get_or_create(date=date, key=key)
            payment_nb.value += 1
            payment_nb.save()
            payment_nb, created = WeeklyStat.objects.get_or_create(year=year, week=week, key=key)
            payment_nb.value += 1
            payment_nb.save()
            payment_nb, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            payment_nb.value += 1
            payment_nb.save()
            key = "%s_payment_value" % payment.type_id
            payment_value, created = DailyStat.objects.get_or_create(date=date, key=key)
            payment_value.value += payment.montant
            payment_value.save()
            payment_value, created = WeeklyStat.objects.get_or_create(year=year, week=week, key=key)
            payment_value.value += payment.montant
            payment_value.save()
            payment_value, created = MonthlyStat.objects.get_or_create(year=year, month=month, key=key)
            payment_value.value += payment.montant
            payment_value.save()

    def get_common(self, date):
        """Return les stats pour date sous forme de liste
        """
        logger.debug(" ")
        result = []
        result.append("  -- %s --" % date)
        result.append("Fait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        nb_bills = self.get_value("nb_bills", date)
        total_ttc = self.get_value("total_ttc", date)
        result.append("Total TTC (% 4d fact.): %11.2f" % (
                nb_bills, total_ttc))
        for vat in VAT.objects.iterator():
            tax = "TVA    % 6.2f%%:" % vat.tax
            key = "%s_vat" % vat.id
            result.append("%-20s %11.2f" % (
                    tax, DailyStat().get_value(key, date)))
        return result

    def update(self):
        """Update statistics with new bills
        """
        logger.debug(" ")
        for bill in Facture.objects.filter(saved_in_stats=False).iterator():
            DailyStat().add_bill(bill)

    def get_data(self, data, date):
        """Recupere les donnees pour une date, retourne data
            data = {}
        """
        logger.debug(" ")
        for key in ['nb_bills', 'total_ttc']:
            data[key] = DailyStat().get_value(key, date)
        data['vats'] = []
        for vat in VAT.objects.order_by('name').iterator():
            key = "%s_vat" % vat.id
            value = DailyStat().get_value(key, date)
            data['vats'].append("TVA % 6.2f%% : %.2f" % (vat.tax, value))
        # restaurant
        for key in ['guests_nb', 'guests_average', 'guests_total_ttc']:
            data[key] = DailyStat().get_value(key, date)
        # bar
        for key in ['bar_nb', 'bar_average', 'bar_total_ttc']:
            data[key] = DailyStat().get_value(key, date)
        # categories & products
        categories = []
        products = []
        for category in Categorie.objects.order_by('priorite', 'nom').iterator():
            category.nb = DailyStat().get_value("%s_category_nb" % category.id, date)
            if category.nb > 0:
                categories.append(category)
                for product in Produit.objects.filter(categorie=category, actif=True).iterator():
                    product.nb = DailyStat().get_value("%s_product_nb" % product.id, date)
                    if product.nb > 0:
                        products.append(product)
        data['categories'] = sorted(categories, cmp=nb_sorted)
        data['products'] = sorted(products, cmp=nb_sorted)
        # payments
        data['payments'] = []
        for payment_type in PaiementType.objects.order_by("nom").iterator():
            data['payments'].append("%s : %.2f" % (
                    payment_type.nom,
                    DailyStat().get_value("%s_payment_value" % payment_type.id, date)))
        return data

