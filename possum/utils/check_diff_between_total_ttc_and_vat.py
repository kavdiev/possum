#!/usr/bin/env python
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
"""Check errors in bills by add all products and compare with montant
"""
from decimal import Decimal
import os
import sys

sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Facture
from possum.stats.models import Stat


for stat in Stat.objects.filter(interval="d", key="total_ttc"):
    total_ttc = stat.value
    vat_ttc = Decimal("0")
    for vat in Stat.objects.filter(year=stat.year, month=stat.month, day=stat.day, interval="d", key__contains="_vat"):
        vat_ttc += vat.value
    diff = total_ttc - vat_ttc
    if diff != Decimal("0"):
        date = "%d-%02d-%02d" % (stat.year, stat.month, stat.day)
        print "%s: %.2f" % (date, diff)
        for bill in Facture.objects.filter(date_creation__gte="%s 00:00" % date,
                                           date_creation__lt="%s 23:59" % date):
            vat = Decimal("0")
            tmp = ""
            for sold in bill.produits.iterator():
                tmp += "%s: %.2f\n" % (sold.produit.nom, sold.prix)
                vat += sold.prix
            diff = bill.total_ttc - vat
            if diff != Decimal("0"):
                print "[%s] not correct: %.2f" % (bill.id, diff)
                print "total: %.2f" % bill.total_ttc
                print tmp

