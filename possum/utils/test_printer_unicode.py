#!/usr/bin/env python
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
import cups


conn = cups.Connection()
printer = ""
filename = "/tmp/test-printer"

fd = open(filename, 'w')
fd.write(u"test unicode :\n")
fd.write(u"éàè€ùœç\n")
fd.close()

if printer:
    conn = cups.Connection()
    conn.printFile(printer, filename, title="test", options={})
else:
    print "Select a printer and modify variable 'printer':"
    printers = conn.getPrinters()
    for printer in printers:
        print printer
