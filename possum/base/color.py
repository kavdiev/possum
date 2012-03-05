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

class Couleur(Nom):
    red = models.PositiveIntegerField(default=255)
    green = models.PositiveIntegerField(default=255)
    blue = models.PositiveIntegerField(default=255)

    def __unicode__(self):
        return "%s [%d / %d / %d]" % (self.nom, self.red, self.green, self.blue)

    def web(self):
        """Retourne la couleur sous la forme #ffe013
        """
        result = "#"
        for rgb in [self.red, self.green, self.blue]:
            tmp = hex(rgb).split('x')[1]
            if len(tmp) == 1:
                result += "0%s" % tmp
            elif len(tmp) == 2:
                result += tmp
            else:
                logging.warning("valeur trop grande")
        return result

    def set_from_rgb(self, color):
        """Set a color from a color like: #123454"""
        try:
            self.red = int(color[1:3], 16)
            self.green = int(color[3:5], 16)
            self.blue = int(color[5:7], 16)
            return True
        except:
            return False

