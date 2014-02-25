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
#
from django.db import models
from generic import Nom
from config import Config


class PaiementType(Nom):
    """Type de paiment"""
    fixed_value = models.BooleanField("ticket ?", default=False)
#    last_value = models.PositiveIntegerField("dernière valeur", default=0)

    class Meta:
        app_label = 'base'
        ordering = ['nom']

    def get_default(self):
        """If exist, return default PaiementType for payment webpage
        """
        default = Config.objects.filter(key="default_type_payment")
        if default:
            try:
                payment = PaiementType.objects.get(id=default[0].value)
            except PaiementType.DoesNotExist:
                return None
            else:
                return payment
        else:
            return None

    def __unicode__(self):
        return self.nom


class Paiement(models.Model):
    """valeur_unitaire: pour gerer les montants des tickets restos"""
    # facture = models.ForeignKey('Facture', related_name="paiement-facture")
    type = models.ForeignKey(PaiementType, related_name="paiement-type")
    montant = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    valeur_unitaire = models.DecimalField(max_digits=9, decimal_places=2,
                                          default=1)
    date = models.DateTimeField('encaisser le', auto_now_add=True)
    nb_tickets = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'base'
        get_latest_by = 'date'

    def __unicode__(self):
        tmp = u"%s %.2f€" % (self.type, self.montant)
        if self.type.fixed_value:
            tmp += u" (%d tic. x %.2f€)" % (self.nb_tickets,
                                            self.valeur_unitaire)
        return tmp

    def __cmp__(self, other):
        return cmp(self.date.date, other.date.date)
