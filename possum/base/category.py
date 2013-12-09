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

from possum.base.generic import Nom, Priorite
from possum.base.vat import VAT


class Categorie(Nom, Priorite):
    surtaxable = models.BooleanField("majoration terrasse", default=False)
    disable_surtaxe = models.BooleanField("peut enlever la surtaxe presente",
                                          default=False)
    made_in_kitchen = models.BooleanField(default=False)
    color = models.CharField(max_length=8, default="#ffdd82")
    vat_onsite = models.ForeignKey(VAT, null=True, blank=True,
                                   related_name="categorie-vat-onsite")
    vat_takeaway = models.ForeignKey(VAT, null=True, blank=True,
                                     related_name="categorie-vat-takeaway")

    def __cmp__(self, other):
        """ Classement par priorite_facture (plus la valeur est petite,
        plus elle est prioritaire), puis par nom_ihm en cas d'égalité. """
        if self.priorite == other.priorite:
            return cmp(self.nom, other.nom)
        else:
            return cmp(self.priorite, other.priorite)

    def set_vat_takeaway(self, vat):
        self.vat_takeaway = vat
        self.save()
        # il faut toujours faire un product.update_vats()

    def set_vat_onsite(self, vat):
        self.vat_onsite = vat
        self.save()
