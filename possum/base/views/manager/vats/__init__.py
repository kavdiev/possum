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

from possum.base.product import Produit
from possum.base.vat import VAT
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)



@permission_required('base.p1')
def vats(request):
    data = get_user(request)
    data['vats'] = VAT.objects.order_by('name')
    data['menu_manager'] = True
    return render_to_response('base/manager/vats/home.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def vats_view(request, vat_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['vat'] = get_object_or_404(VAT, pk=vat_id)
    return render_to_response('base/manager/vats/view.html', data,
                              context_instance=RequestContext(request))


def check_name_and_tax(request, name, tax):
    if not name:
        messages.add_message(request, messages.ERROR,
                             "Vous devez entrer un nom.")
    if not tax:
        messages.add_message(request, messages.ERROR,
                             "Vous devez saisir un pourcentage de taxe.")


@permission_required('base.p1')
def vats_change(request, vat_id):
    data = get_user(request)
    data['vat'] = get_object_or_404(VAT, pk=vat_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tax = request.POST.get('tax', '').strip().replace(',', '.')
        check_name_and_tax(request, name, tax)
        try:
            data['vat'].name = name
            data['vat'].save()
            data['vat'].set_tax(tax)
            for product in Produit.objects.filter(categorie__vat_onsite=data['vat']):
                product.update_vats()
            for product in Produit.objects.filter(categorie__vat_takeaway=data['vat']):
                product.update_vats()
        except:
            messages.add_message(request, messages.ERROR,
                                 "Les modifications n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/vats/')
    return render_to_response('base/manager/vats/change.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def vat_new(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['vats'] = VAT.objects.order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tax = request.POST.get('tax', '').strip().replace(",", ".")
        check_name_and_tax(request, name, tax)
        try:
            vat = VAT(name=name)
            vat.set_tax(tax)
            vat.save()
        except:
            messages.add_message(request, messages.ERROR,
                                 "Les modifications n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/vats/')
    return render_to_response('base/manager/vats/new.html', data,
                              context_instance=RequestContext(request))
