# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011, 2012, 2013 Sébastien Bonnegent
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


class VAT(models.Model):
    """name is a symbolic name
    tax is for example '19.6' for 19.6%
    value: is used to minimize operations (example: 0.196
    """
    name = models.CharField(max_length=32)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    value = models.DecimalField(max_digits=6, decimal_places=4, default=0)

    def __unicode__(self):
        return self.name

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    class Meta:
        ordering = ['name']

    def set_tax(self, tax):
        self.tax = tax
        self.value = Decimal(tax) / 100
        self.save()

    def get_tax_for(self, prize):
        """Retourne la part de taxe
        pour un prix HT
        """
        if self.tax:
            if prize:
                return Decimal(prize) * self.value
            else:
                return Decimal('0')
        else:
            return Decimal('0')

    def get_ttc_for(self, prize):
        """Retourne le prix TTC
        pour un prix HT
        """
        if self.tax:
            if prize:
                return Decimal(prize) * (1 + self.value)
            else:
                return Decimal('0')
        else:
            return prize
