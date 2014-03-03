# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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


from django.db import models
from generic import Priorite, NomDouble


class Cuisson(NomDouble, Priorite):
    """Cuisson d'un produit"""
    color = models.CharField(max_length=8, default="#ffdd82")

    class Meta:
        app_label = 'base'

    def __cmp__(self, other):
        return cmp(self.priorite, other.priorite)

    def __unicode__(self):
        return self.nom


class Option(models.Model):
    """Toutes les options possibles pour un produit.
    """
    name = models.CharField(max_length=16, default="")

    class Meta:
        app_label = 'base'
        ordering = ['name']

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __unicode__(self):
        return self.name

