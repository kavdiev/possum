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

from possum.base.generic import Nom


class Zone(Nom):
    """Un zone peut avoir une surtaxe par exemple dans le cas d'une majoration
    pour le service en terrasse. Dans ce cas, prix_surtaxe est ajouté au
    prix HT de tous les produits dans les categories 'surtaxable'.

    Il est possible d'indiquer une catégorie de produits qui désactive
    la surtaxe pour toute la commande (par exemple lorsque les clients
    mangent).
    """
    surtaxe = models.BooleanField("zone surtaxée ?", default=False)

    def is_surcharged(self):
#       logging.debug("surtaxe de %d centimes sur la zone %s" % (self.surtaxe))
        return self.surtaxe

    def tables(self):
        """Return list of tables for this zone."""
        return Table.objects.filter(zone=self)


class Table(Nom):
    """ TODO """

    zone = models.ForeignKey(Zone, related_name="table-zone")

    def is_surcharged(self):
        ''' By default there is no surcharge. '''
        if self.zone:
            result = self.zone.is_surcharged()
        else:
            result = False
        return result
