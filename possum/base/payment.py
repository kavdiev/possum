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

class PaiementType(Nom):
    """Type de paiment"""
    fixed_value = models.BooleanField("ticket ?", default=False)
#    last_value = models.PositiveIntegerField("dernière valeur", default=0)

class Paiement(models.Model):
    """valeur_unitaire: pour gerer les montants des tickets restos"""
    #facture = models.ForeignKey('Facture', related_name="paiement-facture")
    type = models.ForeignKey('PaiementType', related_name="paiement-type")
#    montant = models.IntegerField("TTC")
#    valeur_unitaire = models.PositiveIntegerField(default=1)
    montant = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    valeur_unitaire = models.DecimalField(max_digits=9, decimal_places=2, default=1)
    date = models.DateTimeField('encaisser le', auto_now_add=True)
    nb_tickets = models.PositiveIntegerField(default=0)

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        if self.type.fixed_value:
            return u"%-20s % 8.2f €    (%d tickets x %5.2f €)" % ( \
                    self.type.nom, self.montant, self.nb_tickets, \
                    self.valeur_unitaire)
        else:
            return u"%-20s % 8.2f €" % (self.type.nom, self.montant)

    def __cmp__(self,other):
        return cmp(self.date.date,other.date.date)

    def show(self):
        return str(self)

