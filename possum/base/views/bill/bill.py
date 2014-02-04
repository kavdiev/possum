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
from possum.base.views import permission_required
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
    return redirect('billi_view', bill.id)


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
        return redirect('sold_cooking', bill_id, menu.id, product_sell.id)
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
    context = {'menu_bills': True, }
    context['need_auto_refresh'] = 30
    context['factures'] = Facture().non_soldees()
    return render(request, 'base/bill/home.html', context)


@permission_required('base.p3')
def bill_view(request, bill_id):
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
