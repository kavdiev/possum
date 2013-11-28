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

from django.contrib import messages
from django.http import HttpResponseRedirect
import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from possum.base.printer import Printer
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)



@permission_required('base.p1')
def home(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['printers'] = Printer.objects.all()
    return render_to_response('base/manager/printers.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def printer_add(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['printers'] = Printer().get_available_printers()
    return render_to_response('base/manager/printer_add.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def printer_added(request, name):
    """Save new printer"""
    data = get_user(request)
    printer = Printer(name=name)
    printer.save()
    return HttpResponseRedirect('/manager/printers/')


@permission_required('base.p1')
def printer_view(request, printer_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['printer'] = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        options = request.POST.get('options', '').strip()
        header = request.POST.get('header', '')
        footer = request.POST.get('footer', '')
        data['printer'].options = options
        data['printer'].header = header
        data['printer'].footer = footer
        try:
            data['printer'].save()
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Les informations n'ont pu être enregistrées.")
    return render_to_response('base/manager/printer_view.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def printer_select_width(request, printer_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['printer'] = get_object_or_404(Printer, pk=printer_id)
    data['max'] = range(14, 120)
    return render_to_response('base/manager/printer_select_width.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def printer_set_width(request, printer_id, number):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    printer.width = number
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)


@permission_required('base.p1')
def printer_test_print(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    if printer.print_test():
        messages.add_message(request, messages.SUCCESS, "L'impression a été acceptée.")
    else:
        messages.add_message(request, messages.ERROR, "L'impression de test a achouée.")
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)


@permission_required('base.p1')
def printer_change_kitchen(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.kitchen
    printer.kitchen = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)


@permission_required('base.p1')
def printer_change_billing(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.billing
    printer.billing = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)


@permission_required('base.p1')
def printer_change_manager(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.manager
    printer.manager = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)
