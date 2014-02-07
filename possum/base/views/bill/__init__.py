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
from django.shortcuts import redirect
import logging
from django.shortcuts import render, get_object_or_404
from possum.base.models import Facture
from possum.base.models import Categorie
from possum.base.models import Zone, Table
from possum.base.models import Printer
from possum.base.models import Cuisson
from possum.base.models import Produit, ProduitVendu
from possum.base.models import PaiementType, Paiement
from possum.base.views import permission_required, remove_edition
from possum.base.models import Note
from possum.base.models import Option
from possum.base.forms import NoteForm


logger = logging.getLogger(__name__)


@permission_required('base.p3')
def bill_new(request):
    """Create a new bill"""
    context = {'menu_bills': True, }
    bill = Facture()
    bill.save()
    context['facture'] = bill
    return render(request, 'base/bill/bill.html', context)


@permission_required('base.p3')
def bill_send_kitchen(request, bill_id):
    """Send in the kitchen"""
    bill = get_object_or_404(Facture, pk=bill_id)
    erreur = False
    if not bill.table:
        erreur = True
        messages.add_message(request,
                             messages.ERROR,
                             "Vous devez choisir une table.")
    if not bill.couverts:
        erreur = True
        messages.add_message(request,
                             messages.ERROR,
                             "Vous devez indiquer le nombre de couverts.")
    if not erreur and not bill.send_in_the_kitchen():
        erreur = True
        messages.add_message(request,
                             messages.ERROR,
                             "Erreur dans l'envoi (imprimante ok?).")
    if not erreur:
        messages.add_message(request, messages.SUCCESS, u"%s envoyée" % 
                             bill.table)
    return redirect('bill_view', bill.id)


@permission_required('base.p3')
def bill_print(request, bill_id):
    """Print the bill"""
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.is_empty():
        messages.add_message(request, messages.ERROR, "La facture est vide.")
    else:
        printers = Printer.objects.filter(billing=True)
        if printers.count() == 0:
            messages.add_message(request, messages.ERROR, "Aucune imprimante "
                                 "n'est configurée pour la facturation.")
        else:
            if bill.print_ticket():
                messages.add_message(request,
                                     messages.SUCCESS,
                                     "Le ticket est imprimé.")
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     "L'impression a échouée.")
    return redirect('bill_view', bill.id)


@permission_required('base.p3')
def table_select(request, bill_id):
    """Select/modify table of a bill"""
    context = {'menu_bills': True, }
    context['zones'] = Zone.objects.all()
    context['bill_id'] = bill_id
    return render(request, 'base/bill/select_a_table.html', context)


@permission_required('base.p3')
def table_set(request, bill_id, table_id):
    """Select/modify table of a bill"""
    context = {'menu_bills': True, }
    bill = get_object_or_404(Facture, pk=bill_id)
    table = get_object_or_404(Table, pk=table_id)
    bill.set_table(table)
    context['facture'] = bill
    return render(request, 'base/bill/bill.html', context)


@permission_required('base.p3')
def category_select(request, bill_id, category_id=None):
    """Select a category to add a new product on a bill."""
    context = {'menu_bills': True, }
    context['categories'] = Categorie.objects.order_by('priorite', 'nom')
    context['bill'] = get_object_or_404(Facture, pk=bill_id)
    category = None
    if category_id:
        category = get_object_or_404(Categorie, pk=category_id)
    else:
        if context['categories']:
            category = context['categories'][0]
    context['products'] = Produit.objects.filter(categorie=category, actif=True)
    return render(request, 'base/bill/categories.html', context)


@permission_required('base.p3')
def product_select_made_with(request, bill_id, product_id):
    context = {'menu_bills': True, }
    context['bill'] = get_object_or_404(Facture, pk=bill_id)
    context['product'] = get_object_or_404(ProduitVendu, pk=product_id)
    context['categories'] = Categorie.objects.filter(made_in_kitchen=True)
    return render(request, 'base/bill/product_select_made_with.html', context)


@permission_required('base.p3')
def product_set_made_with(request, bill_id, product_id, category_id):
    product = get_object_or_404(ProduitVendu, pk=product_id)
    category = get_object_or_404(Categorie, pk=category_id)
    product.made_with = category
    product.save()
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.something_for_the_kitchen()
    return redirect('sold_view', bill_id, product.id)


@permission_required('base.p3')
def product_select(request, bill_id, category_id):
    """Select a product to add on a bill."""
    context = {'menu_bills': True, }
    category = get_object_or_404(Categorie, pk=category_id)
    if not category.vat_onsite:
        messages.add_message(request,
                             messages.ERROR,
                             "La TVA sur place n'est pas définie!")
    if not category.vat_takeaway:
        messages.add_message(request,
                             messages.ERROR,
                             "La TVA à emporter n'est pas définie!")
    context['products'] = Produit.objects.filter(categorie=category, actif=True)
    context['bill_id'] = bill_id
    return render(request, 'base/bill/products.html', context)


@permission_required('base.p3')
def subproduct_select(request, bill_id, sold_id, category_id):
    """Select a subproduct to a product."""
    context = {'menu_bills': True, }
    category = get_object_or_404(Categorie, pk=category_id)
    context['products'] = Produit.objects.filter(categorie=category, actif=True)
    context['bill_id'] = bill_id
    context['sold_id'] = sold_id
    return render(request, 'base/bill/subproducts.html', context)


@permission_required('base.p3')
def sold_view(request, bill_id, sold_id):
    context = {'menu_bills': True, }
    context['bill_id'] = bill_id
    context['sold'] = get_object_or_404(ProduitVendu, pk=sold_id)
    if request.method == 'POST':
        context['note'] = NoteForm(request.POST)
        if context['note'].is_valid():
            context['note'].save()
    else:
        context['note'] = NoteForm()
    context['notes'] = Note.objects.all()
    context['options'] = Option.objects.all()
    return render(request, 'base/bill/sold.html', context)


@permission_required('base.p3')
def sold_option(request, bill_id, sold_id, option_id):
    sold = get_object_or_404(ProduitVendu, pk=sold_id)
    option = get_object_or_404(Option, pk=option_id)
    if option in sold.options.all():
        sold.options.remove(option)
    else:
        sold.options.add(option)
    sold.save()
    return redirect('sold_view', bill_id, sold_id)


@permission_required('base.p3')
def sold_note(request, bill_id, sold_id, note_id):
    sold = get_object_or_404(ProduitVendu, pk=sold_id)
    note = get_object_or_404(Note, pk=note_id)
    if note in sold.notes.all():
        sold.notes.remove(note)
    else:
        sold.notes.add(note)
    sold.save()
    return redirect('sold_view', bill_id, sold_id)


@permission_required('base.p3')
def sold_delete(request, bill_id, sold_id):
    bill = get_object_or_404(Facture, pk=bill_id)
    sold = get_object_or_404(ProduitVendu, pk=sold_id)
    if sold in bill.produits.all():
        # it is a product
        bill.del_product(sold)
        bill.save()
        return redirect('bill_view', bill_id)
    else:
        # it as a subproduct in a menu
        menu = bill.produits.filter(contient=sold)[0]
        menu.contient.remove(sold)
        menu.save()
        category = sold.produit.categorie
        sold.delete()
        return redirect("subproduct_select", bill_id, menu.id, category.id)


@permission_required('base.p3')
def subproduct_add(request, bill_id, sold_id, product_id):
    """Add a product to a bill. If this product contains others products,
    we have to add them too."""
    product = get_object_or_404(Produit, pk=product_id)
    product_sell = ProduitVendu(produit=product)
    product_sell.made_with = product_sell.produit.categorie
    product_sell.save()
    menu = get_object_or_404(ProduitVendu, pk=sold_id)
    menu.contient.add(product_sell)
    if product.choix_cuisson:
        return redirect('sold_cooking', bill_id, product_sell.id)
    category = menu.getFreeCategorie()
    if category:
        return redirect("subproduct_select", bill_id, menu.id, category.id)
    return redirect('category_select', bill_id, menu.produit.categorie.id)


@permission_required('base.p3')
def product_add(request, bill_id, product_id):
    """Add a product to a bill. If this product contains others products,
    we have to add them too."""
    bill = get_object_or_404(Facture, pk=bill_id)
    product = get_object_or_404(Produit, pk=product_id)
    product_sell = ProduitVendu(produit=product)
    product_sell.save()
    bill.add_product(product_sell)
    if product.est_un_menu():
        category = product_sell.getFreeCategorie()
        return redirect('subproduct_select', bill_id, product_sell.id, category.id)
    if product.choix_cuisson:
        return redirect('sold_cooking', bill_id, product_sell.id)
    return redirect('category_select', bill_id, product.categorie.id)


@permission_required('base.p3')
def sold_cooking(request, bill_id, sold_id, cooking_id=-1, menu_id=-1):
    context = {'menu_bills': True, }
    context['sold'] = get_object_or_404(ProduitVendu, pk=sold_id)
    context['cookings'] = Cuisson.objects.order_by('priorite', 'nom')
    context['bill_id'] = bill_id
    if menu_id > -1:
        context['menu_id'] = menu_id
    if cooking_id > -1:
        cooking = get_object_or_404(Cuisson, pk=cooking_id)
        old = context['sold'].cuisson
        context['sold'].cuisson = cooking
        context['sold'].save()
        logger.debug("[S%s] cooking saved" % sold_id)
        if menu_id > -1:
            # this is a menu
            logger.debug("[S%s] is a subproduct of %s" % (sold_id, menu_id))
            menu = get_object_or_404(ProduitVendu, pk=menu_id)
            category = menu.getFreeCategorie()
            if category:
                logger.debug("[S%s] menu is not full" % menu_id)
                return redirect('subproduct_select', bill_id, menu.id,
                                category.id)
            else:
                logger.debug("[S%s] menu is full" % menu_id)
        if old == None:
            # certainement un nouveau produit donc on veut retourner
            # sur le panneau de saisie des produits
            return redirect('category_select', bill_id,
                            context['sold'].produit.categorie.id)
        else:
            return redirect('bill_view', bill_id)
    return render(request, 'base/bill/cooking.html', context)


@permission_required('base.p3')
def couverts_select(request, bill_id):
    """List of couverts for a bill"""
    context = {'menu_bills': True, }
    context['nb_couverts'] = range(43)
    context['bill_id'] = bill_id
    return render(request, 'base/bill/couverts.html', context)


@permission_required('base.p3')
def couverts_set(request, bill_id, number):
    """Set couverts of a bill"""
    context = {'menu_bills': True, }
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.set_couverts(number)
    context['facture'] = bill
    return render(request, 'base/bill/bill.html', context)


@permission_required('base.p3')
def bill_home(request):
    request = remove_edition(request)
    context = {'menu_bills': True, }
    context['need_auto_refresh'] = 30
    context['factures'] = Facture().non_soldees()
    return render(request, 'base/bill/home.html', context)


@permission_required('base.p3')
def bill_view(request, bill_id):
    """Get a bill."""
    request = remove_edition(request)
    context = {'menu_bills': True, }
    context['facture'] = get_object_or_404(Facture, pk=bill_id)
    if context['facture'].est_soldee():
        messages.add_message(request, messages.ERROR,
                             "Cette facture a déjà été soldée.")
        return redirect('bill_home')
    return render(request, 'base/bill/bill.html', context)


@permission_required('base.p3')
def bill_delete(request, bill_id):
    order = get_object_or_404(Facture, pk=bill_id)
    order.delete()
    return redirect('bill_home')


@permission_required('base.p3')
def bill_onsite(request, bill_id):
    order = get_object_or_404(Facture, pk=bill_id)
    order.set_onsite(not order.onsite)
    return redirect('bill_view', bill_id)


@permission_required('base.p3')
def bill_payment_delete(request, bill_id, payment_id):
    payment = get_object_or_404(Paiement, pk=payment_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.del_payment(payment)
    return redirect('bill_view', bill_id)


@permission_required('base.p3')
def bill_payment_view(request, bill_id, payment_id):
    context = { 'menu_bills': True, }
    context['bill_id'] = bill_id
    context['payment'] = get_object_or_404(Paiement, pk=payment_id)
    return render(request, 'payments/view.html', context)


@permission_required('base.p3')
def amount_payment(request):
    """Permet de définir le montant d'un paiement
    bill_id doit etre dans request.session
    """
    bill_id = request.session.get('bill_id', False)
    if not bill_id:
        messages.add_message(request, messages.ERROR, "Facture invalide")
        return redirect('bill_home')

    context = { 'menu_bills': True, }
    context['bill_id'] = bill_id
    context['left'] = request.session.get('left', "0000")
    context['right'] = request.session.get('right', "00")
    return render(request, 'payments/amount.html', context)
    

@permission_required('base.p3')
def amount_count(request):
    """Le nombre de tickets pour un paiement
    """
    bill_id = request.session.get('bill_id', False)
    if not bill_id:
        messages.add_message(request, messages.ERROR, "Facture invalide")
        return redirect('bill_home')

    context = { 'menu_bills': True, }
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
    if bill.in_use_by != request.user:
        messages.add_message(request, messages.ERROR, "Facture en cours"
                             " d'édition par %s" % request.user)
        return redirect('bill_view', bill.id)
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
#        bill.used_by()
#        if "bill_in_use" in request.session.keys():
#            request.session.pop("bill_in_use")
        remove_edition(request)
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
    """Only one user can add a payment or a products
    on a bill at a time.

    We use a key in request.session to update edition status
    for a bill.

    """
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.est_soldee():
        messages.add_message(request, messages.ERROR, "Il n'y a rien à payer.")
        return redirect('bill_view', bill.id)
    # on nettoie la variable
    if 'is_left' in request.session.keys():
        request.session.pop('is_left')
    if bill.in_use_by:
        if bill.in_use_by != request.user:
            messages.add_message(request, messages.ERROR,
                                 "Facture en cours d'édition par %s"
                                 % request.user)
            return redirect('bill_view', bill.id)
    else:
        if request.session.get('bill_in_use', None):
            if request.session['bill_in_use'] != bill_id:
                request = remove_edition(request)
        request.session['bill_in_use'] = bill_id
        bill.used_by(request.user)
    context = { 'menu_bills': True, }
    context['bill_id'] = bill_id
    request.session['bill_id'] = bill_id
    context['type_payments'] = PaiementType.objects.all()
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
