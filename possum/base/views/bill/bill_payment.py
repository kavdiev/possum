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
from django.http import HttpResponseRedirect
import logging
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from possum.base.models import Facture
from possum.base.models import PaiementType, Paiement
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p3')
def bill_payment_delete(request, bill_id, payment_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    payment = get_object_or_404(Paiement, pk=payment_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.del_payment(payment)
    return redirect('bill_view', bill_id)


@permission_required('base.p3')
def bill_payment_view(request, bill_id, payment_id):
    context = get_user(request)
    context['menu_bills'] = True
    context['bill_id'] = bill_id
    context['payment'] = get_object_or_404(Paiement, pk=payment_id)
    return render(request, 'payments/view.html', context)


@permission_required('base.p3')
def amount_payment(request):
    """Permet de définir le montant d'un paiement
    bill_id doit etre dans request.session
    """
    context = get_user(request)
    bill_id = request.session.get('bill_id', False)
    if not bill_id:
        messages.add_message(request, messages.ERROR, "Facture invalide")
        return redirect('bill_home')

    context['menu_bills'] = True
    context['bill_id'] = bill_id
    context['left'] = request.session.get('left', "0000")
    context['right'] = request.session.get('right', "00")
    return render(request, 'payments/amount.html', context)
    

@permission_required('base.p3')
def amount_count(request):
    """Le nombre de tickets pour un paiement
    """
    context = get_user(request)
    bill_id = request.session.get('bill_id', False)
    if not bill_id:
        messages.add_message(request, messages.ERROR, "Facture invalide")
        return redirect('bill_home')

    context['menu_bills'] = True
    context['bill_id'] = bill_id
    context['tickets_count'] = request.session.get('tickets_count', 1)
    context['range'] = range(1, 50)
    return render(request, 'payments/count.html', context)
    

def amount_payment_zero(request):
    """Permet d'effacer la partie gauche et droite
    """
    request.session['left'] = "0000"
    request.session['right'] = "00"
    request.session['is_left'] = True


@permission_required('base.p3')
def amount_payment_del(request):
    """Permet d'effacer la partie gauche et droite
    """
    amount_payment_zero(request)
    return redirect("amount_payment")


@permission_required('base.p3')
def amount_payment_right(request):
    """Permet de passer à la partie droite
    """
    request.session['is_left'] = False
    return redirect("amount_payment")


@permission_required('base.p3')
def amount_payment_add(request, number):
    """Permet d'ajouter un chiffre au montant
    """
    if request.session.get('init_montant', False):
        # if add a number with init_montant,
        # we should want enter a new number
        # so we del default montant
        amount_payment_zero(request)
        request.session.pop('init_montant')
    if request.session.get('is_left', True):
        key = 'left'
    else:
        key = 'right'
    value = int(request.session.get(key, 0))
    try:
        new = int(number)
    except:
        messages.add_message(request, messages.ERROR, "Chiffre invalide")
    else:
        result = value * 10 + new
        tmp = "%04d" % result
        if request.session.get('is_left', True):
            # on veut seulement les 4 derniers chiffres
            request.session['left'] = tmp[-4:]
        else:
            request.session['right'] = tmp[-2:]
    return redirect("amount_payment")
    

@permission_required('base.p3')
def type_payment(request, bill_id, type_id):
    type_payment = get_object_or_404(PaiementType, pk=type_id)
    request.session['type_selected'] = type_payment
    return redirect('prepare_payment', bill_id)


@permission_required('base.p3')
def payment_count(request, bill_id, number):
    try:
        request.session['tickets_count'] = int(number)
    except:
        messages.add_message(request, messages.ERROR, "Nombre invalide")
        return redirect('prepare_payment', bill_id)
    else:
        return redirect('prepare_payment', bill_id)


def cleanup_payment(request):
    """Remove all variables used for a new payment
    """
    keys = ['is_left', 'left', 'right', 'type_selected', 'tickets_count',
            'ticket_value', 'init_montant']
    for key in keys:
        if key in request.session.keys():
            request.session.pop(key)


@permission_required('base.p3')
def save_payment(request, bill_id):
    """Enregistre le paiement
    """
    bill = get_object_or_404(Facture, pk=bill_id)
    if request.session.get('type_selected', False):
        type_payment = request.session['type_selected']
    else:
        messages.add_message(request, messages.ERROR, "Paiement invalide")
        return redirect('prepare_payment', bill_id)
    if type(type_payment) != type(PaiementType()):
        messages.add_message(request, messages.ERROR, "Paiement invalide")
        return redirect('prepare_payment', bill_id)
    left = request.session.get('left', "0")
    right = request.session.get('right', "0")
    montant = "%s.%s" % (left, right)
    if type_payment.fixed_value:
        count = request.session.get('tickets_count', 1)
        try:
            result = bill.add_payment(type_payment, count, montant)
        except:
            messages.add_message(request, messages.ERROR, "Paiement invalide")
            return redirect('prepare_payment', bill_id)
    else:
        try:
            result = bill.add_payment(type_payment, montant)
        except:
            messages.add_message(request, messages.ERROR, "Paiement invalide")
            return redirect('prepare_payment', bill_id)
    if not result:
        messages.add_message(request,
                             messages.ERROR,
                             "Le paiement n'a pu être enregistré.")
        return redirect('prepare_payment', bill_id)
    cleanup_payment(request)
    if bill.est_soldee():
        messages.add_message(request,
                             messages.SUCCESS,
                             "La facture a été soldée.")
        return redirect('bill_home')
    else:
        messages.add_message(request,
                             messages.SUCCESS,
                             "Le paiement a été enregistré.")
        return redirect('prepare_payment', bill_id)


def init_montant(request, montant):
    """Init left/right with a montant in str"""
    (left, right) = montant.split(".")
    request.session['left'] = "%04d" % int(left)
    request.session['right'] = "%02d" % int(right)
    request.session['init_montant'] = True

@permission_required('base.p3')
def prepare_payment(request, bill_id):
    """Remplace bill_payment
    """
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.est_soldee():
        messages.add_message(request, messages.ERROR, "Il n'y a rien à payer.")
        return redirect('bill_view', bill.id)
    # on nettoie la variable
    if 'is_left' in request.session.keys():
        request.session.pop('is_left')
    context = get_user(request)
    context['bill_id'] = bill_id
    request.session['bill_id'] = bill_id
    context['type_payments'] = PaiementType.objects.all()
    context['menu_bills'] = True
    default = PaiementType().get_default()
    if request.session.get('type_selected', False):
        context['type_selected'] = request.session['type_selected']
    else:
        if default:
            request.session['type_selected'] = default
            context['type_selected'] = default
    context['left'] = request.session.get('left', "0000")
    context['right'] = request.session.get('right', "00")
    if context['left'] == "0000" and context['right'] == "00":
        init_montant(request, u"%.2f" % bill.restant_a_payer)
        context['left'] = request.session.get('left')
        context['right'] = request.session.get('right')
    context['tickets_count'] = request.session.get('tickets_count', 1)
    context['range'] = range(1, 15)
    context['ticket_value'] = request.session.get('ticket_value', "0.0")
    return render(request, 'payments/home.html', context)
