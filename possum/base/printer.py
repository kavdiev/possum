# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
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
import os
import cups
from django.conf import settings
from datetime import datetime

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
    width = models.PositiveIntegerField(default=80)
    kitchen = models.BooleanField(default=False)
    billing = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)

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
        conn = cups.Connection()
        result = []
        printers = conn.getPrinters()
        for printer in printers:
            if Printer.objects.filter(name=printer).count() == 0:
                result.append(printer)
        return result

    def create_default_directory(self):
        if not os.path.exists(settings.PATH_TICKET):
            os.makedirs(settings.PATH_TICKET)

    def print_file(self, filename):
        conn = cups.Connection()
        if not os.path.exists(filename):
            return False
        title = filename.split("/")[-1]
        try:
            conn.printFile(self.name, filename, title=title, options={})
            return True
        except:
            return False

    def print_test(self):
        self.create_default_directory()
        path = "%s/test-%s.txt" % (settings.PATH_TICKET, self.id)
        fd = open(path, "w")
        fd.write(self.header)
        fd.write("> POSSUM Printing test !\n")
        fd.write(datetime.now().strftime("> %H:%M %d/%m/%Y\n"))
        fd.write(self.footer)
        fd.close()
        self.print_file(path)

