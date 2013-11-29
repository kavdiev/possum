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

import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import User, UserManager, Permission
from django.core.mail import send_mail
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
import logging
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.functional import wraps

from possum.base.bill import Facture
from possum.base.category import Categorie
from possum.base.forms import DateForm, WeekForm, MonthForm, YearForm
from possum.base.location import Zone, Table
from possum.base.models import Printer
from possum.base.options import Cuisson, Sauce, Accompagnement
from possum.base.payment import PaiementType, Paiement
from possum.base.product import Produit, ProduitVendu
from possum.base.vat import VAT
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)


# from django.views.decorators.csrf import csrf_protect

@permission_required('base.p1')
def tables_zone_delete(request, zone_id):
    data = get_user(request)
    zone = get_object_or_404(Zone, pk=zone_id)
    Table.objects.filter(zone=zone).delete()
    zone.delete()
    return HttpResponseRedirect('/manager/tables/')

@permission_required('base.p1')
def tables_table_new(request, zone_id):
    data = get_user(request)
    zone = get_object_or_404(Zone, pk=zone_id)
    table = Table(zone=zone)
    table.save()
    return HttpResponseRedirect('/manager/tables/%s/%s/' % (zone.id, table.id))

@permission_required('base.p1')
def tables_zone_new(request):
    data = get_user(request)
    zone = Zone()
    zone.save()
    return HttpResponseRedirect('/manager/tables/%s/' % zone.id)

@permission_required('base.p1')
def tables_table(request, zone_id, table_id):
    data = get_user(request)
    data['table'] = get_object_or_404(Table, pk=table_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        data['table'].nom = name
        try:
            data['table'].save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications "
                                 "n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/tables/')
    return render_to_response('base/manager/tables/table.html', data,
                              context_instance=RequestContext(request))

@permission_required('base.p1')
def tables_zone(request, zone_id):
    data = get_user(request)
    data['zone'] = get_object_or_404(Zone, pk=zone_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        data['zone'].nom = name
        try:
            data['zone'].save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications "
                                 "n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/tables/')
    return render_to_response('base/manager/tables/zone.html', data,
                              context_instance=RequestContext(request))

@permission_required('base.p1')
def tables(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['zones'] = Zone.objects.all()
    return render_to_response('base/manager/tables/home.html', data,
                              context_instance=RequestContext(request))
