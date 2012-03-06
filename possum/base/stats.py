# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011, 2012 Sébastien Bonnegent
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

from django.db import models
from possum.base.log import LogType
from possum.base.category import Categorie
from possum.base.product import Produit
from possum.base.payment import PaiementType
from decimal import Decimal
import logging

class StatsJour(models.Model):
    """Modele pour les classes de statistiques."""
    date = models.DateField()
    valeur = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        get_latest_by = 'date'
        abstract = True

class StatsJourGeneral(StatsJour):
    """Les stats concernent un type
    (nb_couverts, nb_facture, nb_bar, ca_resto, ca_bar)"""
    type = models.ForeignKey('LogType',
                             null=True,
                             blank=True,
                             related_name="statsjour-logtype")

    def get_data(self, nom, date):
        """Cherche dans les stats, une donnee au nom et a la date
        indiquee et retourne sa valeur."""
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        try:
            stats = StatsJourGeneral.objects.get(date=date, type=log).valeur
            if stats:
                return stats
            else:
                return Decimal("0")
        except StatsJourGeneral.DoesNotExist:
            return Decimal("0")

    def get_max(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Max('valeur'))['valeur__max']
        if result:
            return result
        else:
            return Decimal("0")

    def get_avg(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Avg('valeur'))['valeur__avg']
        if result:
            return result
        else:
            return Decimal("0")

    def get_min(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Min('valeur'))['valeur__min']
        if result:
            return result
        else:
            return Decimal("0")


class StatsJourPaiement(StatsJour):
    """Les stats concernent les paiements :
    - nombre de paiements (ou nombre de tickets pour TR et ANCV)
    - montant total par paiement
    """
    paiement = models.ForeignKey('PaiementType',
                                null=True,
                                blank=True,
                                related_name="statsjour-paiement")
    nb = models.PositiveIntegerField(default=0)

class StatsJourProduit(StatsJour):
    """Les stats concernent un produit (nombre de produits vendus, CA)
    """
    produit = models.ForeignKey('Produit',
                                null=True,
                                blank=True,
                                related_name="statsjour-produit")
    nb = models.PositiveIntegerField(default=0)

class StatsJourCategorie(StatsJour):
    """Les stats concernent une categorie
    (CA genere par cette categorie)"""
    categorie = models.ForeignKey('Categorie',
                                  null=True,
                                  blank=True,
                                  related_name="statsjour-categorie")
    nb = models.PositiveIntegerField(default=0)

#class StatsSemaine(models.Model):
    #"""Statistique par semaine"""
    #annee = models.PositiveIntegerField(default=0)
    #semaine = models.PositiveIntegerField(default=0)
    #valeur = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    #class Meta:
        #abstract = True

#class StatsSemaineGeneral(StatsSemaine):
    #"""Les stats concernent un type
    #(nb_couverts, nb_facture, nb_bar, ca_resto, ca_bar)"""
    #type = models.ForeignKey('LogType',
                             #null=True,
                             #blank=True,
                             #related_name="statssemaine-logtype")

#class StatsSemaineProduit(StatsSemaine):
    #"""Les stats concernent un produit (nombre de produits vendus, CA)
    #"""
    #produit = models.ForeignKey('Produit',
                                #null=True,
                                #blank=True,
                                #related_name="statssemaine-produit")
    #nb = models.PositiveIntegerField(default=0)

#class StatsSemaineCategorie(StatsSemaine):
    #"""Les stats concernent une categorie
    #(CA genere par cette categorie)"""
    #categorie = models.ForeignKey('Categorie',
                                  #null=True,
                                  #blank=True,
                                  #related_name="statssemaine-categorie")

