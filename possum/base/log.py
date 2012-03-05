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

class LogType(Nom):
    """Correspond au type de Log ainsi qu'au type de stats"""
#    pass
    description = models.CharField(max_length=200, blank=True)

class Log(models.Model):
    date = models.DateTimeField('creer le', auto_now_add=True)
    type = models.ForeignKey('LogType', related_name="log-logtype")

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return "[%s] %s" % (self.date.strftime("%H:%M %d/%m/%Y"), self.type.nom)

