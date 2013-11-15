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
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from possum.base.bill import Facture
from possum.base.payment import PaiementType, Paiement
from possum.base.views import get_user, permission_required
import logging

logger = logging.getLogger(__name__)


@permission_required('base.p3')
def bill_payment_set_right(request, bill_id, type_id, left, right, number, count):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['type_id'] = type_id
    result = number + right
    return HttpResponseRedirect('/bill/%s/payment/%s/%s.%s/%s/set/right/' % (
            bill_id, type_id, left, result, count))


@permission_required('base.p3')
def bill_payment_set_left(request, bill_id, type_id, left, right, number, count):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['type_id'] = type_id
    result = int(left) * 10 + int(number)
    return HttpResponseRedirect('/bill/%s/payment/%s/%d.%s/%s/set/' % (
            bill_id, type_id, result, right, count))


@permission_required('base.p3')
def bill_payment_delete(request, bill_id, payment_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    payment = get_object_or_404(Paiement, pk=payment_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.del_payment(payment)
    return HttpResponseRedirect('/bill/%s/' % bill_id)


@permission_required('base.p3')
def bill_payment_view(request, bill_id, payment_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['payment'] = get_object_or_404(Paiement, pk=payment_id)
    return render_to_response('base/bill/payment_view.html',
                                data,
                                context_instance=RequestContext(request))


@permission_required('base.p3')
def bill_payment_save(request, bill_id, type_id, left, right, count):
    """Enregistre le paiement
    """
    type_payment = get_object_or_404(PaiementType, pk=type_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    montant = "%s.%s" % (left, right)
    if type_payment.fixed_value:
        result = bill.add_payment(type_payment, count, montant)
    else:
        result = bill.add_payment(type_payment, montant)
    if not result:
        messages.add_message(request, messages.ERROR, "Le paiement n'a pu être enregistré.")
    if bill.est_soldee():
        messages.add_message(request, messages.SUCCESS, "La facture a été soldée.")
        return HttpResponseRedirect('/bills/')
    else:
        return HttpResponseRedirect('/bill/%s/' % bill_id)


@permission_required('base.p3')
def bill_payment_set(request, bill_id, type_id, left, right, count, part="left"):
    """if part == "left" alors on fait la partie gauche du nombre
    sinon on fait la partie droite
    """
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['type_id'] = type_id
    tmp = "%04d" % int(left)
    data['left'] = tmp[-4:]
    tmp = "%02d" % int(right)
    data['right'] = tmp[:2]
    data['count'] = count
    if part == "left":
        data["part"] = "left"
    else:
        data["part"] = "right"
    return render_to_response('base/bill/payment_set.html',
                                data,
                                context_instance=RequestContext(request))


@permission_required('base.p3')
def bill_payment_count(request, bill_id, type_id, left, right):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['type_id'] = type_id
    data['left'] = left
    data['right'] = right
    data['tickets_count'] = range(35)
    return render_to_response('base/bill/payment_count.html',
                                data,
                                context_instance=RequestContext(request))


@permission_required('base.p3')
def bill_payment(request, bill_id, type_id=-1, count=-1, left=0, right=0):
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.restant_a_payer == 0:
        messages.add_message(request, messages.ERROR, "Il n'y a rien à payer.")
        return HttpResponseRedirect('/bill/%s/' % bill.id)
    data['bill_id'] = bill_id
    data['type_payments'] = PaiementType.objects.order_by("nom")
    data['menu_bills'] = True
    data['left'] = left
    data['right'] = right
    if type_id > -1:
        data['type_selected'] = get_object_or_404(PaiementType, pk=type_id)
        if data['type_selected'].fixed_value:
            if count > 0:
                data['tickets_count'] = count
            else:
                data['tickets_count'] = 0
            data['ticket_value'] = "0.0"
        else:
            if left == 0 and right == 0:
                montant = u"%.2f" % bill.restant_a_payer
                (data['left'], data['right']) = montant.split(".")
    return render_to_response('base/bill/payment.html',
                                data,
                                context_instance=RequestContext(request))

