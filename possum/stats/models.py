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

import datetime
from decimal import Decimal
from django.db import models
import logging
import os
from django.conf import settings
import itertools
from django.db.models import Max, Avg
from possum.base.models import Facture
from possum.base.models import Categorie
from possum.base.models import PaiementType
from possum.base.models import Produit
from possum.base.models import VAT


logger = logging.getLogger(__name__)
COMMON = ["total_ttc", "nb_bills", "guests_total_ttc", "guests_nb",
          "guests_average", "bar_total_ttc", "bar_nb", "bar_average"]


def nb_sorted(a, b):
    """ Tri sur les categories et les produits pour
    avoir les plus vendus en premier. """
    if b.nb < a.nb:
        return -1
    elif b.nb > a.nb:
        return 1
    else:
        return 0


def get_last_year(date):
    """Retourne le jour de l'année précédente
    afin de comparer les resultats des 2 journées
    date doit être au format datetime
    """
    try:
        return date - datetime.timedelta(days=364)
    except:
        return date


def get_data_on(bill, data):
    """Extract data on a bill to add it to the stats

    bill: Facture()
    data: {}
    """
    def add_value(key, value):
        if key in data.keys():
            data[key] += Decimal(value)
        else:
            data[key] = Decimal(value)
        logger.debug("%s = %.2f" % (key, data[key]))
    logger.debug("[B%s] extract stats" % bill.id)
    add_value("nb_bills", 1)
    add_value("total_ttc", bill.total_ttc)
    for sold in bill.produits.iterator():
        prix = sold.prix
        p_id = sold.produit.id
        add_value("%s_product_nb" % p_id, 1)
        add_value("%s_product_value" % p_id, prix)
        c_id = sold.produit.categorie_id
        add_value("%s_category_nb" % c_id, 1)
        add_value("%s_category_value" % c_id, prix)
        # VAT
        if bill.onsite:
            vat_id = sold.produit.categorie.vat_onsite_id
        else:
            vat_id = sold.produit.categorie.vat_takeaway_id
        add_value("%s_vat" % vat_id, prix)
        # products in a menu
        for sub in sold.contient.iterator():
            p_id = sub.produit.id
            add_value("%s_product_nb" % p_id, 1)
            c_id = sub.produit.categorie_id
            add_value("%s_category_nb" % c_id, 1)
    if bill.est_un_repas():
        # number of guests
        if bill.couverts == 0:
            # if not, we try to find a number
            bill.couverts = bill.guest_couverts()
            bill.save()
        add_value("guests_nb", bill.couverts)
        add_value("guests_total_ttc", bill.total_ttc)
    else:
        add_value("bar_nb", 1)
        add_value("bar_total_ttc", bill.total_ttc)
    for payment in bill.paiements.iterator():
        p_id = payment.type_id
        add_value("%s_payment_nb" % p_id, 1)
        add_value("%s_payment_value" % p_id, payment.montant)
    return data


def compute_avg_max(stats, stat_avg, stat_max):
    """Get and save maximum and average for all stats
    stats: Stat.objects.filter()
    stat_avg: Stat()
    stat_max: Stat()
    """
    avg = stats.aggregate(Avg('value'))['value__avg']
    if avg:
        stat_avg.value = avg
        stat_avg.save()
    best = stats.aggregate(Max('value'))['value__max']
    if best:
        stat_max.value = best
        stat_max.save()


def compute_all_time():
    """Update all time stats (average and max) for main keys
    """
    logger.debug("update all time stats")
    for key in COMMON:
        # for days
        stats = Stat.objects.filter(interval="d", key=key)
        avg, created = Stat.objects.get_or_create(interval="a",
                                                  key="avg_%s" % key)
        best, created = Stat.objects.get_or_create(interval="a",
                                                   key="max_%s" % key)
        compute_avg_max(stats, avg, best)
        # for months
        stats = Stat.objects.filter(interval="m", key=key)
        avg, created = Stat.objects.get_or_create(interval="b",
                                                  key="avg_%s" % key)
        best, created = Stat.objects.get_or_create(interval="b",
                                                   key="max_%s" % key)
        compute_avg_max(stats, avg, best)
        # for weeks
        stats = Stat.objects.filter(interval="w", key=key)
        avg, created = Stat.objects.get_or_create(interval="c",
                                                  key="avg_%s" % key)
        best, created = Stat.objects.get_or_create(interval="c",
                                                   key="max_%s" % key)
        compute_avg_max(stats, avg, best)


def record_day(year, month, week, day, data):
    """Record new values from data.
    Also update average, max.

    year: 2014
    month: 03
    week: 14
    day: 31
    data: {'key1': value1, 'key2': value2, ...}
    """
    logger.debug("[%d-%d-%d] update record" % (year, month, day))
    for key in data.keys():
        stat, created = Stat.objects.get_or_create(year=year,
                                                   month=month,
                                                   day=day,
                                                   key=key,
                                                   interval="d")
        stat.add_value(data[key])
        stat, created = Stat.objects.get_or_create(year=year,
                                                   month=month,
                                                   key=key,
                                                   interval="m")
        stat.add_value(data[key])
        stat, created = Stat.objects.get_or_create(year=year,
                                                   week=week,
                                                   key=key,
                                                   interval="w")
        stat.add_value(data[key])
        stat, created = Stat.objects.get_or_create(year=year,
                                                   key=key,
                                                   interval="y")
        stat.add_value(data[key])


def compute_avg(subkey, stats, avg):
    """Compute average
    subkey: "guests" or "bar"
    stats: Stat.objects.filter()
    avg: Stat()
    """
    try:
        total = stats.filter(key="%s_total_ttc" % subkey)[0]
        nb = stats.filter(key="%s_nb" % subkey)[0]
    except IndexError:
        logger.debug("no data for this date")
        # if no data here, no need to update month and week
        return False
    if nb.value:
        avg.value = total.value / nb.value
        avg.save()
    else:
        logger.debug("we don't divide by zero")
        return False
    return True


def update_avg(year, month, week, day):
    """Update average/max stats for day, week and month

    guests_average = guests_total_ttc.value / guests_nb.value
    bar_average = bar_total_ttc.value / bar_nb.value
    """
    logger.debug("update guests_average and bar_average")
    for key in ["guests", "bar"]:
        stats = Stat.objects.filter(year=year, month=month, day=day,
                                    interval="d")
        avg, created = Stat.objects.get_or_create(year=year, month=month,
                                                  day=day, interval="d",
                                                  key="%s_average" % key)
        if compute_avg(key, stats, avg):
            stats = Stat.objects.filter(year=year, month=month, interval="m")
            avg, created = Stat.objects.get_or_create(year=year, month=month,
                                                      key="%s_average" % key,
                                                      interval="m")
            compute_avg(key, stats, avg)
            stats = Stat.objects.filter(year=year, week=week, interval="w")
            avg, created = Stat.objects.get_or_create(year=year, week=week,
                                                      key="%s_average" % key,
                                                      interval="w")
            compute_avg(key, stats, avg)


def update_day(date):
    """Update stats with all bills availables on a day.

    date: String, "2014-03-31"
    """
    try:
        day_begin = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logger.warning("[%s] day invalid !" % date)
        return False
    day_end = day_begin + datetime.timedelta(days=1)
    bills = Facture.objects.filter(date_creation__gte=day_begin,
                                   date_creation__lt=day_end)\
                           .exclude(saved_in_stats=True)
    day = day_begin.day
    month = day_begin.month
    year = day_begin.year
    week = day_begin.isocalendar()[1]
    data = {}
    count = 0
    logger.debug("[%s] %d bills to update" % (date, bills.count()))
    for bill in bills:
        if bill.est_soldee():
            count += 1
            data = get_data_on(bill, data)
            bill.saved_in_stats = True
            bill.save()
    if data:
        record_day(year, month, week, day, data)
        update_avg(year, month, week, day)
    else:
        logger.debug("nothing to do")
    logging.info("updated record with %d bills" % count)
    return True


class Stat(models.Model):
    """Statistics, full list of keys:
    # Common
    nb_bills      : number of invoices
    total_ttc        : total TTC
    ID_vat           : total TTC for vat ID

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

    All time stats are use to record average/max
    """
    INTERVAL = (('a', 'All time day'),
                ('b', 'All time month'),
                ('c', 'All time week'),
                ('y', 'Year'),
                ('w', 'Week'),
                ('m', 'Month'),
                ('d', 'Day'))
    interval = models.CharField(max_length=1, choices=INTERVAL, default="d")
    year = models.PositiveIntegerField(default=0)
    month = models.PositiveIntegerField(default=0)
    day = models.PositiveIntegerField(default=0)
    week = models.PositiveIntegerField(default=0)
    key = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ['interval', 'year', 'month', 'day', 'key']

    def __unicode__(self):
        tmp = "[%s]" % self.interval
        if self.interval == 'y':
            tmp += "[%d]" % self.year
        elif self.interval == 'w':
            tmp += "[%d-w%d]" % (self.year, self.week)
        elif self.interval == 'm':
            tmp += "[%d-%d]" % (self.year, self.month)
        elif self.interval == 'd':
            tmp += "[%d-%d-%d]" % (self.year, self.month, self.day)
        return "%s %s" % (tmp, self.key)

    def update(self):
        """Update statistics with new bills
        """
        if os.path.isfile(settings.LOCK_STATS):
            logger.info("lock [%s] already here" % settings.LOCK_STATS)
            return False
        else:
            logger.debug("create lock for stats")
            fd = open(settings.LOCK_STATS, "w")
            fd.close()
            # we prepare list of days with bills to add
            bills = Facture.objects.filter(saved_in_stats=False)
            grouped = itertools.groupby(bills, lambda record:
                                        record.date_creation\
                                        .strftime("%Y-%m-%d"))
            for day, bills_this_day in grouped:
                update_day(day)
            if grouped:
                compute_all_time()
            logger.debug("release lock for stats")
            os.remove(settings.LOCK_STATS)
            return True

    def add_value(self, value):
        """Add a value to the stat
        """
        try:
            self.value += Decimal(value)
        except:
            logger.critical("can't convert [%s]" % value)
        self.save()

    def get_data_for_day(self, context):
        """Prepare stats for a day
        context must contains 'date' : Datetime()
        """
        if 'date' not in context:
            logger.warning("no date in context")
            return context
        date = context['date']
        all_time = Stat.objects.filter(interval="a")
        last = get_last_year(context['date'])
        objects = Stat.objects.filter(interval="d")
        last_year = objects.filter(year=last.year, month=last.month,
                                   day=last.day)
        current = objects.filter(year=date.year, month=date.month,
                                 day=date.day)
        return self.get_data(context, all_time, last_year, current)

    def get_data_for_week(self, context):
        """Prepare stats for a week
        context must contains 'year' and 'week' : Integer
        """
        if 'year' not in context:
            logger.warning("no year in context")
            return context
        if 'week' not in context:
            logger.warning("no week in context")
            return context
        week = context['week']
        year = context['year']
        all_time = Stat.objects.filter(interval="c")
        last = int(year) - 1
        objects = Stat.objects.filter(interval="w", week=week)
        last_year = objects.filter(year=last)
        current = objects.filter(year=year)
        return self.get_data(context, all_time, last_year, current)

    def get_data_for_month(self, context):
        """Prepare stats for a month
        context must contains 'year' and 'month' : Integer
        """
        if 'year' not in context:
            logger.warning("no year in context")
            return context
        if 'month' not in context:
            logger.warning("no month in context")
            return context
        month = context['month']
        year = context['year']
        all_time = Stat.objects.filter(interval="b")
        last = int(year) - 1
        objects = Stat.objects.filter(interval="m", month=month)
        last_year = objects.filter(year=last)
        current = objects.filter(year=year)
        return self.get_data(context, all_time, last_year, current)

    def get_data(self, context, all_time, last_year, current):
        """Get and construct data from Stat()

        context: {}
        all_time: [Stat(), ]
        last_year: [Stat(), ]
        current: [Stat(), ]

        return context with data
        """
        # all time stats
        for stat in all_time:
            context[stat.key] = "%.2f" % stat.value
        # last year stats
        for stat in last_year:
            context["last_%s" % stat.key] = "%.2f" % stat.value
        # current stats
        tmp = {}
        for stat in current:
            if stat.key in COMMON:
                context[stat.key] = "%.2f" % stat.value
                # if current better than average, we add a flag
                key = 'avg_%s' % stat.key
                if key in context.keys():
                    if float(stat.value) > float(context[key]):
                        logger.debug("[%s] better" % stat.key)
                        context["%s_better" % stat.key] = True
            else:
                # for VAT, Produit, Categorie and Payment
                switch = None
                pk = stat.key.split("_")[0]
                if "_product_nb" in stat.key:
                    switch = "products"
                    try:
                        elt = Produit.objects.get(pk=pk)
                    except Produit.DoesNotExist:
                        logger.critical("Produit(pk=%s) not here" % pk)
                        continue
                    elt.nb = stat.value
                elif "_category_nb" in stat.key:
                    switch = "categories"
                    try:
                        elt = Categorie.objects.get(pk=pk)
                    except Categorie.DoesNotExist:
                        logger.critical("Categorie(pk=%s) not here" % pk)
                        continue
                    elt.nb = stat.value
                elif "_vat" in stat.key:
                    switch = "vats"
                    try:
                        elt = VAT.objects.get(pk=pk)
                    except VAT.DoesNotExist:
                        logger.critical("VAT(pk=%s) not here" % pk)
                        continue
                    elt.nb = stat.value
                elif "_payment_value" in stat.key:
                    switch = "payments"
                    try:
                        elt = PaiementType.objects.get(pk=pk)
                    except PaiementType.DoesNotExist:
                        logger.critical("PaiementType(pk=%s) not here" % pk)
                        continue
                    elt.nb = stat.value
                if switch not in tmp.keys():
                    tmp[switch] = []
                tmp[switch].append(elt)
        # sort elements in tmp
        for switch in tmp.keys():
            context[switch] = sorted(tmp[switch], cmp=nb_sorted)
        logger.debug(context)
        return context
