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

import datetime
from django.contrib import messages
import logging
from django.shortcuts import render, get_object_or_404, redirect
from possum.base.models import Facture
from possum.base.forms import DateForm
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def archives(request):
    context = { 'menu_manager': True, }
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
    context['date_form'] = DateForm({'date': date, })
    context['factures'] = Facture().get_bills_for(date)
    context['date'] = date
    return render(request, 'base/manager/archives/home.html', context)


@permission_required('base.p1')
def archives_bill(request, bill_id):
    context = { 'menu_manager': True, }
    bill = get_object_or_404(Facture, pk=bill_id)
    if not bill.est_soldee():
        messages.add_message(request, messages.ERROR,
                             "Cette facture n'est pas encore soldée.")
        return redirect('archives')
    context['bill'] = bill
    context['products_sold'] = bill.reduced_sold_list(bill.produits.all())
    return render(request, 'base/manager/archives/invoice.html', context)
