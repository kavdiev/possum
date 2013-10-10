# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published 
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
from possum.base.models import VAT

class VATOnBill(models.Model):
    """VAT for a bill
    """
    vat = models.ForeignKey('VAT', related_name="bill-vat")
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __cmp__(self, other):
        return cmp(self.vat.name, other.vat.name)

    def __unicode__(self):
        return "%s: %s" % (self.vat.name, self.total)

