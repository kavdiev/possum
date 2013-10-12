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

from django.conf import settings
import datetime
import logging
import os

logger = logging.getLogger(__name__)

def nb_sorted(a, b):
    """Tri sur les categories et les produits pour avoir les plus vendus en premier
    """
    if b.nb < a.nb:
        return -1
    elif b.nb > a.nb:
        return 1
    else:
        return 0

def create_default_directory():
    ''' Création des répertoires obligatoires '''
    if not os.path.exists(settings.PATH_TICKET):
        os.makedirs(settings.PATH_TICKET)
        
def get_last_year(date):
    """Retourne le jour de l'année précédente
    afin de comparer les resultats des 2 journées
    date doit être au format datetime
    """
    try:
        return date - datetime.timedelta(days=364)
    except:
        return date

def month_name(*t):
    """ Sert à trier les mois."""
    logger.debug(t)
    names = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 
            5: 'Mai', 6: 'Jui', 7: 'Jui', 8: 'Aou', 
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    month_num = int(t[0][0])
    logger.debug("names[%d] > [%s]" % (month_num, names[month_num]))
    return (names[month_num], )

def month_sort(*x):
    logger.debug(x)
    return (int(x[0][1][0]),)
