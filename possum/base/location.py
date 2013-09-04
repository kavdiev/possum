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
#
from django.db import models
from possum.base.generic import Nom

class Zone(Nom):
    surtaxe = models.BooleanField("zone surtaxée ?", default=False)
    prix_surtaxe = models.DecimalField(max_digits=4, decimal_places=2, default=0)
#    prix_surtaxe = models.PositiveIntegerField("surtaxe en centimes")

    def est_surtaxe(self):
#       logging.debug("surtaxe de %d centimes sur la zone %s" % (self.surtaxe))
        return self.surtaxe

    def tables(self):
        """Return list of tables for this zone."""
        return Table.objects.filter(zone=self)

class Table(Nom):
    zone = models.ForeignKey('Zone', related_name="table-zone")

    def est_surtaxe(self):
        if self.zone:
            result = self.zone.est_surtaxe()
        else:
            # par defaut, il n'y a pas de surtaxe
            result = False
        return result
