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

import logging
logger = logging.getLogger(__name__)

from possum.base.daily_stat import DailyStat
from possum.base.weekly_stat import WeeklyStat
from possum.base.monthly_stat import MonthlyStat
from possum.base.bill import Facture
from possum.base.models import Printer
from possum.base.product import Produit, ProduitVendu
from possum.base.payment import PaiementType, Paiement
from possum.base.category import Categorie
from possum.base.options import Cuisson, Sauce, Accompagnement
from possum.base.location import Zone, Table
from possum.base.vat import VAT
from possum.base.forms import DateForm, WeekForm, MonthForm, YearForm

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.http import Http404
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import User, UserManager, Permission
from django.conf import settings
from django.contrib import messages
from django.utils.functional import wraps
from django.core.mail import send_mail
import os
import datetime
from possum.base.views import get_user, permission_required

@permission_required('base.p2')
def carte(request):
    """This is not used.
    """
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte.html',
                                data,
                                context_instance=RequestContext(request))

def is_valid_product(name, billname, prize):
    erreur = False
    if not name :
        erreur = True
        messages.add_message(request, messages.ERROR, "Vous devez saisir un nom.")
    if not billname :
        erreur = True
        messages.add_message(request, messages.ERROR, "Vous devez saisir un nom pour la facture.")
    if not prize :
        erreur = True
        messages.add_message(request, messages.ERROR, "Vous devez entrer un prix.")
    return not erreur

@permission_required('base.p2')
def products_view(request, product_id):
    data = get_user(request)
    data['product'] = get_object_or_404(Produit, pk=product_id)
    data['menu_carte'] = True
    return render_to_response('base/carte/product.html',
                                data,
                                context_instance=RequestContext(request))

def treat_product_new(request, category):
    name = request.POST.get('name', '').strip()
    billname = request.POST.get('billname', '').strip()
    prize = request.POST.get('prize', '').strip()
    if is_valid_product(name, billname, prize) :
        try:
            product = Produit(nom=name, nom_facture=billname, prix=prize)
            product.set_category(category)
            product.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/carte/categories/%s/' % category.id)
        
@permission_required('base.p2')
def products_new(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    if request.method == 'POST':
        treat_product_new(request, data['category'])
    return render_to_response('base/carte/product_new.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def products_set_category(request, product_id, cat_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    category = get_object_or_404(Categorie, pk=cat_id)
    product.set_category(category)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_category(request, product_id):
    data = get_user(request)
    data['product'] = get_object_or_404(Produit, pk=product_id)
    data['menu_carte'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render_to_response('base/carte/product_category.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def products_del_produits_ok(request, product_id, sub_id):
    data = get_user(request)
    menu = get_object_or_404(Produit, pk=product_id)
    sub = get_object_or_404(Produit, pk=sub_id)
    menu.produits_ok.remove(sub)
    menu.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_select_produits_ok(request, product_id):
    data = get_user(request)
    data['product'] = get_object_or_404(Produit, pk=product_id)
    data['menu_carte'] = True
    data['products'] = []
    for category in data['product'].categories_ok.iterator():
        for sub in Produit.objects.filter(categorie=category, actif=True).iterator():
            if sub not in data['product'].produits_ok.iterator():
                data['products'].append(sub)
    return render_to_response('base/carte/product_select_produits_ok.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def products_add_produits_ok(request, product_id, sub_id):
    data = get_user(request)
    menu = get_object_or_404(Produit, pk=product_id)
    product = get_object_or_404(Produit, pk=sub_id)
    menu.produits_ok.add(product)
    menu.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_del_categories_ok(request, product_id, cat_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    category = get_object_or_404(Categorie, pk=cat_id)
    product.categories_ok.remove(category)
    product.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_add_categories_ok(request, product_id, cat_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    category = get_object_or_404(Categorie, pk=cat_id)
    product.categories_ok.add(category)
    product.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_select_categories_ok(request, product_id):
    data = get_user(request)
    data['product'] = get_object_or_404(Produit, pk=product_id)
    data['menu_carte'] = True
    data['categories'] = []
    for category in Categorie.objects.order_by('priorite', 'nom').iterator():
        if category not in data['product'].categories_ok.iterator() \
                and category != data['product'].categorie:
            data['categories'].append(category)
    return render_to_response('base/carte/product_select_categories_ok.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def products_cooking(request, product_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    new = not product.choix_cuisson
    product.choix_cuisson = new
    product.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p2')
def products_enable(request, product_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    new = not product.actif
    product.actif = new
    product.save()
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

def treat_products_change(request, product_id):
    name = request.POST.get('name', '').strip()
    billname = request.POST.get('billname', '').strip()
    prize = request.POST.get('prize', '').strip().replace(',', '.')
    if is_valid_product(name, billname, prize) :
        product = product.set_prize(prize)
        product.nom = name
        product.nom_facture = billname
        try:
            product.save()
        except:
            messages.add_message(request, messages.ERROR,
                                 "Les modifications n'ont pu être enregistrées.")
            return HttpResponseRedirect('/carte/products/%s/' % product.id)

@permission_required('base.p2')
def products_change(request, product_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    data['menu_carte'] = True
    if request.method == 'POST':
        treat_product_change(request, product_id)
    data['product'] = product
    return render_to_response('base/carte/product_change.html',
                                data,
                                context_instance=RequestContext(request))
