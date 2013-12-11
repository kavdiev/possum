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

from possum.base.bill import Facture
from possum.base.category import Categorie
from possum.base.location import Zone, Table
from possum.base.models import Printer
from possum.base.options import Cuisson
from possum.base.product import Produit, ProduitVendu
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p3')
def bill_new(request):
    """Create a new bill"""
    data = get_user(request)
    data['menu_bills'] = True
    bill = Facture()
    bill.save()
    data['facture'] = bill
    return render_to_response('base/bill/bill.html', data,
                              context_instance=RequestContext(request))


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
    if not bill.send_in_the_kitchen():
        erreur = True
        messages.add_message(request,
                             messages.ERROR,
                             "Erreur dans l'envoi (imprimante ok?).")
    if not erreur:
        if bill.table:
            message = u"%s envoyée" % bill.table
        else:
            message = u"Envoyé en cuisine"
        messages.add_message(request, messages.SUCCESS, message)
    return HttpResponseRedirect('/bill/%s/' % bill.id)


@permission_required('base.p3')
def bill_print(request, bill_id):
    """Print the bill"""
    data = get_user(request)
    data['menu_bills'] = True
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
    return HttpResponseRedirect('/bill/%s/' % bill.id)


@permission_required('base.p3')
def table_select(request, bill_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['zones'] = Zone.objects.all()
    data['bill_id'] = bill_id
    return render_to_response('base/bill/select_a_table.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def table_set(request, bill_id, table_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    table = get_object_or_404(Table, pk=table_id)
    bill.set_table(table)
    data['facture'] = bill
    return render_to_response('base/bill/bill.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def category_select(request, bill_id, category_id=None):
    """Select a category to add a new product on a bill."""
    data = get_user(request)
    data['menu_bills'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    data['bill'] = get_object_or_404(Facture, pk=bill_id)
    category = None
    if category_id:
        category = get_object_or_404(Categorie, pk=category_id)
    else:
        if data['categories']:
            category = data['categories'][0]
    data['products'] = Produit.objects.filter(categorie=category, actif=True)
    return render_to_response('base/bill/categories.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def product_select_made_with(request, bill_id, product_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill'] = get_object_or_404(Facture, pk=bill_id)
    data['product'] = get_object_or_404(ProduitVendu, pk=product_id)
    data['categories'] = Categorie.objects.filter(made_in_kitchen=True)
    return render_to_response('base/bill/product_select_made_with.html',
                              data, context_instance=RequestContext(request))


@permission_required('base.p3')
def product_set_made_with(request, bill_id, product_id, category_id):
    # TODO request unused
    # data = get_user(request)
    product = get_object_or_404(ProduitVendu, pk=product_id)
    category = get_object_or_404(Categorie, pk=category_id)
    product.made_with = category
    product.save()
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.something_for_the_kitchen()
    return HttpResponseRedirect('/bill/%s/sold/%s/view/' % (bill_id,
                                                            product.id))


@permission_required('base.p3')
def product_select(request, bill_id, category_id):
    """Select a product to add on a bill."""
    data = get_user(request)
    data['menu_bills'] = True
    # bill = get_object_or_404(Facture, pk=bill_id) TODO unused
    category = get_object_or_404(Categorie, pk=category_id)
    if not category.vat_onsite:
        messages.add_message(request,
                             messages.ERROR,
                             "La TVA sur place n'est pas définie!")
    if not category.vat_takeaway:
        messages.add_message(request,
                             messages.ERROR,
                             "La TVA à emporter n'est pas définie!")
    data['products'] = Produit.objects.filter(categorie=category, actif=True)
    data['bill_id'] = bill_id
    return render_to_response('base/bill/products.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def subproduct_select(request, bill_id, sold_id, category_id):
    """Select a subproduct to a product."""
    data = get_user(request)
    data['menu_bills'] = True
    category = get_object_or_404(Categorie, pk=category_id)
    data['products'] = Produit.objects.filter(categorie=category, actif=True)
    data['bill_id'] = bill_id
    data['sold_id'] = sold_id
    return render_to_response('base/bill/subproducts.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def sold_view(request, bill_id, sold_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['sold'] = get_object_or_404(ProduitVendu, pk=sold_id)
    return render_to_response('base/bill/sold.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def sold_delete(request, bill_id, sold_id):
    # TODO request unused
    bill = get_object_or_404(Facture, pk=bill_id)
    sold = get_object_or_404(ProduitVendu, pk=sold_id)
    if sold in bill.produits.all():
        # it is a product
        bill.del_product(sold)
        bill.save()
        return HttpResponseRedirect('/bill/%s/' % bill_id)
    else:
        # it as a subproduct in a menu
        menu = bill.produits.filter(contient=sold)[0]
        menu.contient.remove(sold)
        menu.save()
        category = sold.produit.categorie
        sold.delete()
        redirect_url = '/bill/%s/sold/%s/category/%s/select/' % (bill_id,
                                                                 menu.id,
                                                                 category.id)
        return HttpResponseRedirect(redirect_url)


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
        redirect_url = '/bill/%s/sold/%s/%s/cooking/' % (bill_id,
                                                         menu.id,
                                                         product_sell.id)
        return HttpResponseRedirect(redirect_url)
    category = menu.getFreeCategorie()
    if category:
        redirect_url = '/bill/%s/sold/%s/category/%s/select/' % (bill_id,
                                                                 menu.id,
                                                                 category.id)
        return HttpResponseRedirect(redirect_url)
    redirect_url = '/bill/%s/category/%s/' % (bill_id,
                                              menu.produit.categorie.id)
    return HttpResponseRedirect(redirect_url)


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
        redirect_url = '/bill/%s/sold/%s/category/%s/select/' % (bill_id,
                                                                 product_sell.id,
                                                                 category.id)
        return HttpResponseRedirect(redirect_url)
    if product.choix_cuisson:
        redirect_url = '/bill/%s/sold/%s/cooking/' % (bill_id,
                                                      product_sell.id)
        return HttpResponseRedirect(redirect_url)
#    messages.add_message(request, messages.SUCCESS, "%s ok" % product.nom)
    redirect_url = '/bill/%s/category/%s/' % (bill_id,
                                              product.categorie.id)
    return HttpResponseRedirect(redirect_url)


@permission_required('base.p3')
def sold_cooking(request, bill_id, sold_id, cooking_id=-1, menu_id=-1):
    data = get_user(request)
    data['sold'] = get_object_or_404(ProduitVendu, pk=sold_id)
    data['cookings'] = Cuisson.objects.order_by('priorite', 'nom')
    data['bill_id'] = bill_id
    if cooking_id > -1:
        cooking = get_object_or_404(Cuisson, pk=cooking_id)
        old = data['sold'].cuisson
        data['sold'].cuisson = cooking
        data['sold'].save()
        if menu_id > -1:
            # this is a menu
            menu = get_object_or_404(ProduitVendu, pk=menu_id)
            category = menu.getFreeCategorie()
            if category:
                url = '/bill/%s/sold/%s/category/%s/select/' % (bill_id,
                      menu.id, category.id)
                return HttpResponseRedirect(url)
        if old == None:
            # certainement un nouveau produit donc on veut retourner
            # sur le panneau de saisie des produits
            return HttpResponseRedirect('/bill/%s/category/%s/' % (bill_id,
                                        data['sold'].produit.categorie.id))
        else:
            return HttpResponseRedirect('/bill/%s/' % bill_id)
    return render_to_response('base/bill/cooking.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def couverts_select(request, bill_id):
    """List of couverts for a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['nb_couverts'] = range(43)
    data['bill_id'] = bill_id
    return render_to_response('base/bill/couverts.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def couverts_set(request, bill_id, number):
    """Set couverts of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.set_couverts(number)
    data['facture'] = bill
    return render_to_response('base/bill/bill.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def factures(request):
    data = get_user(request)
    data['menu_bills'] = True
    data['factures'] = Facture().non_soldees()
    return render_to_response('base/bill/home.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def bill_view(request, bill_id):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=bill_id)
    if data['facture'].est_soldee():
        messages.add_message(request, messages.ERROR,
                             "Cette facture a déjà été soldée.")
        return HttpResponseRedirect('/bills/')
    data['menu_bills'] = True
    return render_to_response('base/bill/bill.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p3')
def bill_delete(request, bill_id):
    order = get_object_or_404(Facture, pk=bill_id)
    order.delete()
    return HttpResponseRedirect('/bills/')


@permission_required('base.p3')
def bill_onsite(request, bill_id):
    order = get_object_or_404(Facture, pk=bill_id)
    order.set_onsite(not order.onsite)
    return HttpResponseRedirect('/bill/%s/' % bill_id)
