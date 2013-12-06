# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011, 2012 Sébastien Bonnegent
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

from possum.base.generic import Nom, Priorite, NomDouble


class Cuisson(NomDouble, Priorite):
    """Cuisson d'un produit"""
    color = models.CharField(max_length=8, default="#ffdd82")

    def __cmp__(self, other):
        return cmp(self.priorite, other.priorite)


class Sauce(Nom):
    """Sauce d'un produit"""
    color = models.CharField(max_length=8, default="#ffdd82")


class Accompagnement(Nom):
    """Accompagnement d'un produit"""
    color = models.CharField(max_length=8, default="#ffdd82")
