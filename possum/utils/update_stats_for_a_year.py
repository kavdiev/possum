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
"""Re-compute stats for a year
"""
from decimal import Decimal
import os
import sys
import datetime

sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Facture
from possum.stats.models import Stat


year = int(input("Quelle année mettre à jour (ex: 2013) ? "))


before = datetime.datetime.now()
print "[%s] delete stats before update" % datetime.datetime.now().strftime("%H:%M")
Stat.objects.filter(year=year).delete()

print "[%s] change status for bills" % datetime.datetime.now().strftime("%H:%M")
bills = Facture.objects.filter(date_creation__gte="%d-01-01 00:00:00" % year,
                               date_creation__lt="%d-12-31 23:59:59" % year)
for bill in bills.iterator():
    bill.saved_in_stats = False
    bill.save()

print "[%s] compute stats" % datetime.datetime.now().strftime("%H:%M")
Stat().update()

after = datetime.datetime.now()
diff = after - before
time = ""
if diff.seconds > 3600:
    # more than a hour
    hour = diff.seconds / 3600
    mn = (diff.seconds % 3600) / 60
    time = "%dh %dm" % (hour, mn)
else:
    mn = diff.seconds / 60
    sec = diff.seconds % 60
    time = "%dm %ds" % (mn, sec)
print "[%d] updated %d bills in %s" % (year, bills.count(), time)

