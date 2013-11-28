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
from django.http import HttpResponseRedirect
import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from possum.base.bill import Facture
from possum.base.forms import DateForm
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)



@permission_required('base.p1')
def archives(request):
    data = get_user(request)
    data['menu_manager'] = True
    if request.method == 'POST':
        try:
            year = int(request.POST.get('date_year'))
            month = int(request.POST.get('date_month'))
            day = int(request.POST.get('date_day'))
            date = datetime.datetime(year, month, day)
        except:
            messages.add_message(request, messages.ERROR,
                                 "La date saisie n'est pas valide.")
            date = datetime.datetime.today()
    else:
        date = datetime.datetime.today()
    data['date_form'] = DateForm({'date': date, })
    data['factures'] = Facture().get_bills_for(date)
    data['date'] = date
    return render_to_response('base/manager/archives/home.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def archives_bill(request, bill_id):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=bill_id)
    if not data['facture'].est_soldee():
        messages.add_message(request, messages.ERROR,
                             "Cette facture n'est pas encore soldée.")
        return HttpResponseRedirect('/manager/archives/')
    data['menu_manager'] = True
    return render_to_response('base/manager/archives/invoice.html', data,
                              context_instance=RequestContext(request))
