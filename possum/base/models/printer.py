# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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

from datetime import datetime
import os
import unicodedata
import cups
from django.conf import settings
from django.db import models


def sans_accent(message):
    """ Enlève les accents qui peuvent poser
    problème à l'impression."""
    return unicodedata.normalize("NFKD", unicode(message)).encode("ascii",
                                                                  "ignore")


class Printer(models.Model):
    """Printer model
    options: options used with pycups.printFile()
    header: you can add a text before the text to print
        (example: Restaurant name)
    width: largeur du ticket
    footer: same as header but after :)
    kitchen: used to print in kitchen
    billing: used to print bills
    manager: used to print rapport, ...
    """
    name = models.CharField(max_length=40)
    options = models.CharField(max_length=120)
    header = models.TextField(default="")
    footer = models.TextField(default="")
    width = models.PositiveIntegerField(default=27)
    kitchen = models.BooleanField(default=False)
    billing = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)

    class Meta:
        app_label = 'base'

    def __unicode__(self):
        return self.name

    def get_resume(self):
        """Usefull to have a brief resume:
        K : kitchen
        B : billing
        M : manager
        """
        result = ""
        if self.kitchen:
            result += "K"
        if self.billing:
            result += "B"
        if self.manager:
            result += "M"
        return result

    def get_available_printers(self):
        """Return a string list of availables printers
        """
        result = []
        try:
            conn = cups.Connection()
        except RuntimeError:
            return result
        printers = conn.getPrinters()
        for printer in printers:
            if Printer.objects.filter(name=printer).count() == 0:
                result.append(printer)
        return result

    def print_file(self, filename):
        try:
            conn = cups.Connection()
        except RuntimeError:
            return False
        if not os.path.exists(filename):
            return False
        title = filename.split("/")[-1]
        try:
            conn.printFile(self.name, filename, title=title, options={})
            return True
        except:
            return False

    def print_msg(self, msg):
        """Try to print a msg, we create a list with msg
        """
        list_to_print = msg.split("\n")
        return self.print_list(list_to_print, "possum")

    def print_list(self, list_to_print, name, with_header=False):
        '''
        Generate a print list from a list which contains informations
        in string and serveral business objects.
        '''
        path = "%s/%s-%s.txt" % (settings.PATH_TICKET, self.id, name)
        ticket_to_print = open(path, "w")
        if with_header:
            ticket_to_print.write(self.header)
        for line in list_to_print:
            ticket_to_print.write("{0}\n".format(sans_accent(line)))
        if with_header:
            ticket_to_print.write(self.footer)
        ticket_to_print.close()
        result = self.print_file(path)
        os.remove(path)
        return result

    def print_test(self):
        list_to_print = []
        list_to_print.append("> POSSUM Printing test !")
        list_to_print.append(datetime.now().strftime("> %H:%M %d/%m/%Y\n"))
        return self.print_list(list_to_print, "test")
