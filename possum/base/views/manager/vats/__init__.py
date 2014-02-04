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

from django.contrib import messages
import logging
from django.shortcuts import render, redirect, get_object_or_404
from possum.base.models import Produit
from possum.base.models import VAT
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def vats(request):
    context = {'menu_manager': True, }
    context['vats'] = VAT.objects.order_by('name')
    return render(request, 'base/manager/vats/home.html', context)


@permission_required('base.p1')
def vats_view(request, vat_id):
    context = {'menu_manager': True, }
    context['vat'] = get_object_or_404(VAT, pk=vat_id)
    return render(request, 'base/manager/vats/view.html', context)


def check_name_and_tax(request, name, tax):
    if not name:
        messages.add_message(request, messages.ERROR,
                             "Vous devez entrer un nom.")
    if not tax:
        messages.add_message(request, messages.ERROR,
                             "Vous devez saisir un pourcentage de taxe.")


@permission_required('base.p1')
def vats_change(request, vat_id):
    context = {'menu_manager': True, }
    context['vat'] = get_object_or_404(VAT, pk=vat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tax = request.POST.get('tax', '').strip().replace(',', '.')
        check_name_and_tax(request, name, tax)
        try:
            context['vat'].name = name
            context['vat'].save()
            context['vat'].set_tax(tax)
            for product in Produit.objects.filter(categorie__vat_onsite=context['vat']):
                product.update_vats()
            for product in Produit.objects.filter(categorie__vat_takeaway=context['vat']):
                product.update_vats()
        except:
            messages.add_message(request, messages.ERROR,
                                 "Les modifications n'ont pu être "
                                 "enregistrées.")
        else:
            return redirect('vats')
    return render(request, 'base/manager/vats/change.html', context)


@permission_required('base.p1')
def vat_new(request):
    context = {'menu_manager': True, }
    context['vats'] = VAT.objects.order_by('name')
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
                                 "Les modifications n'ont pu être "
                                 "enregistrées.")
        else:
            return redirect('vats')
    return render(request, 'base/manager/vats/new.html', context)
