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

from possum.base.stats import StatsJourProduit, StatsJourCategorie
from possum.base.stats import StatsJourGeneral
from possum.base.stats import StatsJourPaiement
from possum.base.stats import get_current_working_day
from possum.base.bill import Facture, Suivi
from possum.base.models import Printer
from possum.base.product import Produit, ProduitVendu
from possum.base.payment import PaiementType, Paiement
from possum.base.category import Categorie
from possum.base.options import Cuisson, Sauce, Accompagnement
from possum.base.location import Zone, Table
from possum.base.vat import VAT
from possum.base.forms import DateForm

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
#from django.views.decorators.csrf import csrf_protect
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
from datetime import datetime

# Création des répertoires obligatoires
def create_default_directory():
    if not os.path.exists(settings.PATH_TICKET):
        os.makedirs(settings.PATH_TICKET)

###
# Cache management
###
def get_product_or_404(product_id):
    try:
        product = cache['products_by_id'][product_id]
    except KeyError:
        raise Http404
    else:
        return product

def get_category_or_404(category_id):
    try:
        category = cache['categories_by_id'][category_id]
    except KeyError:
        raise Http404
    else:
        return category

def cache_categories():
    if 'categories_by_id' not in cache:
        cache['categories_by_id'] = {}
    cache['categories'] = Categorie.objects.order_by('priorite', 'nom')
    for category in cache['categories']:
        cache['categories_by_id'][category.id] = category
        cache['categories_by_id']["%s" % category.id] = category

def cache_products():
    for category in cache['categories']:
        cache_products_for_category(category)

def cache_products_for_category(category):
    """We maintain a cache with category key as int and str.
    """
    if 'products' not in cache:
        cache['products'] = {}
    if 'products_disable' not in cache:
        cache['products_disable'] = {}
    if 'products_by_id' not in cache:
        cache['products_by_id'] = {}
    products = Produit.objects.filter(categorie=category)
    for product in products:
        cache['products_by_id'][product.id] = product
        cache['products_by_id']["%s" % product.id] = product
    enable = products.exclude(actif=False)
    cache['products'][category.id] = enable
    cache['products']["%s" % category.id] = enable
    disable = products.exclude(actif=True)
    cache['products_disable'][category.id] = disable
    cache['products_disable']["%s" % category.id] = disable

def init_cache_system():
    cache_categories()
    cache_products()
    if settings.DEBUG:
        from pprint import pprint
        pprint(cache)

def get_user(request):
    data = {}
    data['perms'] = PermWrapper(request.user)
    data['user'] = request.user
#    data.update(csrf(request))
    return data

def permission_required(perm, **kwargs):
    """This decorator redirect the user to '/'
    if he hasn't the permission.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.ERROR, "Vous n'avez pas"
                        " les droits nécessaires (%s)." % perm.split('.')[1])
                return HttpResponseRedirect('/')
        return wraps(view_func)(_wrapped_view)
    return decorator

@login_required
def home(request):
    data = get_user(request)

#    return render_to_response('base/home.html',
#            data,
#            context_instance=RequestContext(request))
    return HttpResponseRedirect('/bills/')

@login_required
def kitchen(request):
    data = get_user(request)
    data['menu_kitchen'] = True
    data['suivis'] = Suivi.objects.filter(facture__restant_a_payer__gt=0).order_by("-date")
    return render_to_response('base/kitchen/view.html',
            data,
            context_instance=RequestContext(request))

@permission_required('base.p6')
def carte(request):
    """This is not used.
    """
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_send(request):
    data = get_user(request)
    result = Produit().get_list_with_all_products()
    subject = "Carte complete"
    mail = ""
    for line in result:
        mail += "%s\n" % line
    if request.user.email:
        try:
            send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR, u"Le mail n'a pu être envoyé.")
        else:
            messages.add_message(request, messages.SUCCESS, u"Le mail a été envoyé à %s." % request.user.email)
    else:
        messages.add_message(request, messages.ERROR, u"Vous n'avez pas d'adresse mail.")
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_print(request):
    data = get_user(request)
    result = Produit().get_list_with_all_products()
    if result:
        printers = Printer.objects.filter(manager=True)
        if printers:
            printer = printers[0]
            if printer.print_list(result, "carte_complete"):
                messages.add_message(request, messages.SUCCESS, u"L'impression a été envoyée sur %s." % printer.name)
            else:
                messages.add_message(request, messages.ERROR, u"L'impression a achouée sur %s." % printer.name)
        else:
            messages.add_message(request, messages.ERROR, u"Aucune imprimante type 'manager' disponible.")
    else:
        messages.add_message(request, messages.ERROR, "Il n'y a rien dans la carte.")
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories(request):
    data = get_user(request)
    data['menu_carte'] = True
    data['categories'] = cache['categories']
    return render_to_response('base/carte/categories.html',
                    data,
                    context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_delete(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['current_cat'] = get_category_or_404(cat_id)
    data['categories'] = cache['categories'].exclude(id=cat_id)
    cat_report_id = request.POST.get('cat_report', '').strip()
    action = request.POST.get('valide', '').strip()
    if action == "Supprimer":
        # we have to report stats and products ?
        if cat_report_id:
            try:
                report = Categorie.objects.get(id=cat_report_id)
                # we transfert all statistics
                for stat in StatsJourCategorie.objects.filter(categorie__id=cat_id):
                    try:
                        new = StatsJourCategorie.objects.get(date=stat.date, categorie=report)
                        new.nb += stat.nb
                        new.valeur += stat.valeur
                        new.save()
                        stat.delete()
                    except StatsJourCategorie.DoesNotExist:
                        stat.categorie = report
                        stat.save()
                # we transfert all products
                for product in Produit.objects.filter(categorie__id=cat_id):
                    product.categorie = report
                    product.save()
            except Categorie.DoesNotExist:
                logging.warning("[%s] categorie [%s] doesn't exist" % (data['user'].username, cat_report_id))
                messages.add_message(request, messages.ERROR, "La catégorie n'existe pas.")
                return HttpResponseRedirect('/carte/categories/%s/delete/' % cat_id)
        # now, we have to delete the categorie and remove all products remains
        for product in Produit.objects.filter(categorie__id=cat_id):
            for stat in StatsJourProduit.objects.filter(produit=product):
                stat.delete()
            product.delete()
        for stat in StatsJourCategorie.objects.filter(categorie__id=cat_id):
            stat.delete()
        logging.info("[%s] categorie [%s] deleted" % (data['user'].username, data['current_cat'].nom))
        data['current_cat'].delete()
        cache_products_for_category(data['current_cat'])
        cache_categories()
        return HttpResponseRedirect('/carte/categories/')
    elif action == "Annuler":
        return HttpResponseRedirect('/carte/categories/')
    return render_to_response('base/categories_delete.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_view(request, cat_id):
    data = get_user(request)
    data['category'] = get_category_or_404(cat_id)
    data['menu_carte'] = True
    data['products_enable'] = cache['products'][cat_id]
    data['products_disable'] = cache['products_disable'][cat_id]
    return render_to_response('base/carte/category.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_add(request):
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte/categories_add.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_new(request):
    data = get_user(request)
    priority = request.POST.get('priority', '').strip()
    name = request.POST.get('name', '').strip()
    if name:
        cat = Categorie()
        cat.nom = name
        if priority:
            cat.priorite = priority
        try:
            cat.save()
            logging.info("[%s] new categorie [%s]" % (data['user'].username, name))
        except:
            logging.warning("[%s] new categorie failed: [%s] [%s]" % (data['user'].username, cat.priorite, cat.nom))
            messages.add_message(request, messages.ERROR, "La nouvelle catégorie n'a pu être créée.")
        else:
            cache_categories()
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir un nom pour la nouvelle catégorie.")
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_name(request, cat_id):
    data = get_user(request)
    data['category'] = get_category_or_404(cat_id)
    return render_to_response('base/carte/name.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_color(request, cat_id):
    data = get_user(request)
    data['category'] = get_category_or_404(cat_id)
    data['categories'] = cache['categories']
    return render_to_response('base/carte/color.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_less_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_category_or_404(cat_id)
    cat.set_less_priority(nb)
    cache_categories()
    logging.info("[%s] cat [%s] priority - %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_more_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_category_or_404(cat_id)
    cat.set_more_priority(nb)
    cache_categories()
    logging.info("[%s] cat [%s] priority + %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_surtaxable(request, cat_id):
    data = get_user(request)
    cat = get_category_or_404(cat_id)
    new = not cat.surtaxable
    cat.surtaxable = new
    if cat.surtaxable:
        cat.disable_surtaxe = False
    cat.save()
    cache_categories()
    logging.info("[%s] cat [%s] surtaxable: %s" % (data['user'].username, cat.nom, cat.surtaxable))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_vat_takeaway(request, cat_id):
    data = get_user(request)
    data['category'] = get_category_or_404(cat_id)
    data['type_vat'] = 'TVA à emporter'
    data['url_vat'] = 'vat_takeaway'
    data['vats'] = VAT.objects.all()
    data['menu_carte'] = True
    return render_to_response('base/carte/categories/select_vat.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_set_vat_takeaway(request, cat_id, vat_id):
    data = get_user(request)
    category = get_category_or_404(cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_takeaway(vat)
    cache_categories()
    for product in cache['products'][category.id].iterator():
        product.update_vats()
    for product in cache['products_disable'][category.id].iterator():
        product.update_vats()
    cache_products_for_category(category)
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_set_vat_onsite(request, cat_id, vat_id):
    data = get_user(request)
    category = get_category_or_404(cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_onsite(vat)
    cache_categories()
    for product in cache['products'][category.id].iterator():
        product.update_vats()
    for product in cache['products_disable'][category.id].iterator():
        product.update_vats()
    cache_products_for_category(category)
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_vat_onsite(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['category'] = get_category_or_404(cat_id)
    data['type_vat'] = 'TVA sur place'
    data['url_vat'] = 'vat_onsite'
    data['vats'] = VAT.objects.all()
    return render_to_response('base/carte/categories/select_vat.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def tables_zone_delete(request, zone_id):
    data = get_user(request)
    zone = get_object_or_404(Zone, pk=zone_id)
    Table.objects.filter(zone=zone).delete()
    zone.delete()
    return HttpResponseRedirect('/manager/tables/')

@permission_required('base.p7')
def tables_table_new(request, zone_id):
    data = get_user(request)
    zone = get_object_or_404(Zone, pk=zone_id)
    table = Table(zone=zone)
    table.save()
    return HttpResponseRedirect('/manager/tables/%s/%s/' % (zone.id, table.id))

@permission_required('base.p7')
def tables_zone_new(request):
    data = get_user(request)
    zone = Zone()
    zone.save()
    return HttpResponseRedirect('/manager/tables/%s/' % zone.id)

@permission_required('base.p7')
def tables_table(request, zone_id, table_id):
    data = get_user(request)
    data['table'] = get_object_or_404(Table, pk=table_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        data['table'].nom = name
        try:
            data['table'].save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/tables/')
    return render_to_response('base/manager/tables/table.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def tables_zone(request, zone_id):
    data = get_user(request)
    data['zone'] = get_object_or_404(Zone, pk=zone_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        data['zone'].nom = name
        try:
            data['zone'].save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        else:
            return HttpResponseRedirect('/manager/tables/')
    return render_to_response('base/manager/tables/zone.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def tables(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['zones'] = Zone.objects.all()
    return render_to_response('base/manager/tables/home.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def vats(request):
    data = get_user(request)
    data['vats'] = VAT.objects.all()
    data['menu_manager'] = True
    return render_to_response('base/manager/vats/home.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_view(request, product_id):
    data = get_user(request)
    data['product'] = get_product_or_404(product_id)
    data['menu_carte'] = True
    return render_to_response('base/carte/product.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def vats_view(request, vat_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['vat'] = get_object_or_404(VAT, pk=vat_id)
    return render_to_response('base/manager/vats/view.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def vats_change(request, vat_id):
    data = get_user(request)
    data['vat'] = get_object_or_404(VAT, pk=vat_id)
    data['menu_manager'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tax = request.POST.get('tax', '').strip().replace(',','.')
        if name:
            if tax:
                try:
                    data['vat'].name = name
                    data['vat'].save()
                    data['vat'].set_tax(tax)
                    for product in Produit.objects.filter(categorie__vat_onsite=data['vat']):
                        product.update_vats()
                    for product in Produit.objects.filter(categorie__vat_takeaway=data['vat']):
                        product.update_vats()
                    cache_products()
                except:
                    messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
                else:
                    return HttpResponseRedirect('/manager/vats/')

            else:
                messages.add_message(request, messages.ERROR, "Vous devez saisir un pourcentage de taxe.")
        else:
            messages.add_message(request, messages.ERROR, "Vous devez entrer un nom.")

    return render_to_response('base/manager/vats/change.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_new(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['category'] = get_category_or_404(cat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        billname = request.POST.get('billname', '').strip()
        prize = request.POST.get('prize', '').strip()
        if name:
            if billname:
                if prize:
                    try:
                        product = Produit(
                                nom=name, 
                                nom_facture=billname,
                                prix=prize)
                        product.set_category(data['category'])
                        product.save()
                    except:
                        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
                    else:
                        cache_products_for_category(product.categorie)
                        return HttpResponseRedirect('/carte/categories/%s/' % data['category'].id)
                else:
                    messages.add_message(request, messages.ERROR, "Vous devez saisir un prix.")
            else:
                messages.add_message(request, messages.ERROR, "Vous devez saisir un nom pour la facture.")
        else:
            messages.add_message(request, messages.ERROR, "Vous devez entrer un nom.")

    return render_to_response('base/carte/product_new.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def vat_new(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['vats'] = VAT.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tax = request.POST.get('tax', '').strip().replace(",",".")
        if name:
            if tax:
                try:
                    vat = VAT(name=name)
                    vat.set_tax(tax)
                    vat.save()
                except:
                    messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
                else:
                    return HttpResponseRedirect('/manager/vats/')

            else:
                messages.add_message(request, messages.ERROR, "Vous devez saisir un pourcentage de taxe.")
        else:
            messages.add_message(request, messages.ERROR, "Vous devez entrer un nom.")

    return render_to_response('base/manager/vats/new.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_set_color(request, cat_id):
    data = get_user(request)
    color = request.POST.get('color', '').strip()
    cat = get_category_or_404(cat_id)
    if not cat.color or color != cat.color:
        logging.info("[%s] new categorie color [%s]" % (data['user'].username, cat.nom))
        cat.color = color
        try:
            cat.save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        else:
            cache_categories()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def products_set_category(request, product_id, cat_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    category = get_category_or_404(cat_id)
    product.set_category(category)
    cache_products_for_category(product.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_category(request, product_id):
    data = get_user(request)
    data['product'] = get_product_or_404(product_id)
    data['menu_carte'] = True
    data['categories'] = cache['categories']
    return render_to_response('base/carte/product_category.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_del_produits_ok(request, product_id, sub_id):
    data = get_user(request)
    menu = get_product_or_404(product_id)
    sub = get_product_or_404(sub_id)
    menu.produits_ok.remove(sub)
    menu.save()
    cache_products_for_category(menu.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_select_produits_ok(request, product_id):
    data = get_user(request)
    data['product'] = get_product_or_404(product_id)
    data['menu_carte'] = True
    data['products'] = []
    for category in data['product'].categories_ok.iterator():
        for sub in cache['products'][category.id]:
            if sub not in data['product'].produits_ok.iterator():
                data['products'].append(sub)
    return render_to_response('base/carte/product_select_produits_ok.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_add_produits_ok(request, product_id, sub_id):
    data = get_user(request)
    menu = get_product_or_404(product_id)
    product = get_product_or_404(sub_id)
    menu.produits_ok.add(product)
    menu.save()
    cache_products_for_category(menu.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_del_categories_ok(request, product_id, cat_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    category = get_category_or_404(cat_id)
    product.categories_ok.remove(category)
    product.save()
    cache_products_for_category(product.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_add_categories_ok(request, product_id, cat_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    category = get_category_or_404(cat_id)
    product.categories_ok.add(category)
    product.save()
    cache_products_for_category(product.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_select_categories_ok(request, product_id):
    data = get_user(request)
    data['product'] = get_product_or_404(product_id)
    data['menu_carte'] = True
    data['categories'] = []
    for category in cache['categories'].iterator():
        if category not in data['product'].categories_ok.iterator() \
                and category != data['product'].categorie:
            data['categories'].append(category)
    return render_to_response('base/carte/product_select_categories_ok.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_cooking(request, product_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    new = not product.choix_cuisson
    product.choix_cuisson = new
    product.save()
    cache_products_for_category(product.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_enable(request, product_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    new = not product.actif
    product.actif = new
    product.save()
    cache_products_for_category(product.categorie)
    return HttpResponseRedirect('/carte/products/%s/' % product_id)

@permission_required('base.p6')
def products_change(request, product_id):
    data = get_user(request)
    product = get_product_or_404(product_id)
    data['menu_carte'] = True
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        billname = request.POST.get('billname', '').strip()
        prize = request.POST.get('prize', '').strip().replace(',','.')
        if name:
            if billname:
                if prize:
                    product = product.set_prize(prize)
                    product.nom = name
                    product.nom_facture = billname
                    try:
                        product.save()
                    except:
                        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
                    else:
                        cache_products_for_category(product.categorie)
                        return HttpResponseRedirect('/carte/products/%s/' % product.id)
                else:
                    messages.add_message(request, messages.ERROR, "Vous devez entrer un prix.")
            else:
                messages.add_message(request, messages.ERROR, "Vous devez saisir un nom pour la facture.")
        else:
            messages.add_message(request, messages.ERROR, "Vous devez saisir un nom.")
    data['product'] = product
    return render_to_response('base/carte/product_change.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_set_name(request, cat_id):
    data = get_user(request)
    name = request.POST.get('name', '').strip()
    cat = get_category_or_404(cat_id)
    if name != cat.nom:
        logging.info("[%s] new categorie name: [%s] > [%s]" % (data['user'].username, cat.nom, name))
        cat.nom = name

    try:
        cat.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for [%s]" % (data['user'].username, cat.nom))
    else:
        cache_categories()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_set_kitchen(request, cat_id):
    data = get_user(request)
    cat = get_category_or_404(pk=cat_id)
    new = not cat.made_in_kitchen
    cat.made_in_kitchen = new
    cat.save()
    cache_categories()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p6')
def categories_disable_surtaxe(request, cat_id):
    data = get_user(request)
    cat = get_category_or_404(cat_id)
    new = not cat.disable_surtaxe
    cat.disable_surtaxe = new
    if cat.disable_surtaxe:
        cat.surtaxable = False
    cat.save()
    cache_categories()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p5')
def pos(request):
    data = get_user(request)
    data['menu_pos'] = True
    return render_to_response('base/pos.html',
                                data,
                                context_instance=RequestContext(request))

@login_required
def jukebox(request):
    data = get_user(request)
    data['menu_jukebox'] = True
    return render_to_response('base/jukebox.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def credits(request):
    data = get_user(request)
    data['menu_manager'] = True
    return render_to_response('base/manager/credits.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def rapports(request):
    """try/except sont là pour le cas où les rapports sont demandés
    alors qu'il n'y a pas encore eu de facture ce jour"""
    data = get_user(request)
    data['menu_manager'] = True
    date = get_current_working_day()
    data['year'] = date.year
    data['month'] = date.month
    data['day'] = date.day
    for name in ['nb_invoices', 'total_ttc']:
        data[name] = StatsJourGeneral().get_data(name, date)
    data['vats'] = []
    for vat in VAT.objects.all():
        name = "%s_vat_only" % vat.id
        valeur = StatsJourGeneral().get_data(name, date)
        data['vats'].append("TVA % 6.2f%% : %.2f" % (vat.tax, valeur))
    # restaurant
    for name in ['nb_guests', 'guest_average', 'guests_total_ttc']:
        data[name] = StatsJourGeneral().get_data(name, date)
    # bar
    for name in ['nb_bar', 'bar_average', 'bar_total_ttc']:
        data[name] = StatsJourGeneral().get_data(name, date)
    # categories
    data['categories'] = []
    for category in cache['categories']:
        category.nb = StatsJourCategorie().get_data(category, date)
        data['categories'].append(category)
    # payments
    data['payments'] = []
    for payment_type in PaiementType.objects.all():
        data['payments'].append("%s : %.2f" % (
                payment_type.nom, 
                StatsJourPaiement().get_data(payment_type, date)))
    return render_to_response('base/manager/rapports/home.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def rapports_common_day_send(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    result = StatsJourGeneral().get_common_data(date)
    try:
        result = StatsJourGeneral().get_common_data(date)
    except:
        messages.add_message(request, messages.ERROR, "Les statistiques n'ont pu être récupérées.")
    else:
        subject = "Rapport journalier du %s" % date
        mail = ""
        for line in result:
            mail += "%s\n" % line
        if request.user.email:
            try:
                send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
            except:
                messages.add_message(request, messages.ERROR, u"Le mail n'a pu être envoyé.")
            else:
                messages.add_message(request, messages.SUCCESS, u"Le mail a été envoyé à %s." % request.user.email)
        else:
            messages.add_message(request, messages.ERROR, u"Vous n'avez pas d'adresse mail.")
    return HttpResponseRedirect('/manager/rapports/')

@permission_required('base.p7')
def rapports_common_day_print(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    result = StatsJourGeneral().get_common_data(date)
    try:
        result = StatsJourGeneral().get_common_data(date)
    except:
        messages.add_message(request, messages.ERROR, "Les statistiques n'ont pu être récupérées.")
    else:
        printers = Printer.objects.filter(manager=True)
        if printers:
            printer = printers[0]
            if printer.print_list(result, "rapport_common_%s" % date):
                messages.add_message(request, messages.SUCCESS, u"L'impression a été envoyée sur %s." % printer.name)
            else:
                messages.add_message(request, messages.ERROR, u"L'impression a achouée sur %s." % printer.name)
        else:
            messages.add_message(request, messages.ERROR, u"Aucune imprimante type 'manager' disponible.")
    return HttpResponseRedirect('/manager/rapports/')


@permission_required('base.p7')
def manager(request):
    data = get_user(request)
    data['menu_manager'] = True
    return render_to_response('base/manager/home.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def printers(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['printers'] = Printer.objects.all()
    return render_to_response('base/manager/printers.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def printer_add(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['printers'] = Printer().get_available_printers()
    return render_to_response('base/manager/printer_add.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def printer_added(request, name):
    """Save new printer"""
    data = get_user(request)
    printer = Printer(name=name)
    printer.save()
    return HttpResponseRedirect('/manager/printers/')

@permission_required('base.p7')
def printer_view(request, printer_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['printer'] = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        options = request.POST.get('options', '').strip()
        header = request.POST.get('header', '')
        footer = request.POST.get('footer', '')
        data['printer'].options = options
        data['printer'].header = header
        data['printer'].footer = footer
        try:
            data['printer'].save()
        except:
            messages.add_message(request, messages.ERROR, "Les informations n'ont pu être enregistrées.")
    return render_to_response('base/manager/printer_view.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def printer_select_width(request, printer_id):
    data = get_user(request)
    data['menu_manager'] = True
    data['printer'] = get_object_or_404(Printer, pk=printer_id)
    data['max'] = range(14, 120)
    return render_to_response('base/manager/printer_select_width.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def printer_set_width(request, printer_id, number):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    printer.width = number
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)

@permission_required('base.p7')
def printer_test_print(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    if printer.print_test():
        messages.add_message(request, messages.SUCCESS, "L'impression a été acceptée.")
    else:
        messages.add_message(request, messages.ERROR, "L'impression de test a achouée.")
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)

@permission_required('base.p7')
def printer_change_kitchen(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.kitchen
    printer.kitchen = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)

@permission_required('base.p7')
def printer_change_billing(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.billing
    printer.billing = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)

@permission_required('base.p7')
def printer_change_manager(request, printer_id):
    data = get_user(request)
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.manager
    printer.manager = new
    printer.save()
    return HttpResponseRedirect('/manager/printer/%s/' % printer_id)

@login_required
def profile(request):
    data = get_user(request)
    data['menu_profile'] = True
    data['perms_list'] = settings.PERMS
    old = request.POST.get('old', '').strip()
    new1 = request.POST.get('new1', '').strip()
    new2 = request.POST.get('new2', '').strip()
    if old:
        if data['user'].check_password(old):
            if new1 and new1 == new2:
                data['user'].set_password(new1)
                data['user'].save()
                data['success'] = "Le mot de passe a été changé."
                logging.info('[%s] password changed' % data['user'].username)
            else:
                data['error'] = "Le nouveau mot de passe n'est pas valide."
                logging.warning('[%s] new password is not correct' % data['user'].username)
        else:
            data['error'] = "Le mot de passe fourni n'est pas bon."
            logging.warning('[%s] check password failed' % data['user'].username)
    return render_to_response('base/profile.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users(request):
    data = get_user(request)
    data['perms_list'] = settings.PERMS
    data['menu_manager'] = True
    data['users'] = User.objects.all()
    for user in data['users']:
        user.permissions = [p.codename for p in user.user_permissions.all()]
    return render_to_response('base/manager/users.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users_new(request):
    data = get_user(request)
    # data is here to create a new user ?
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    if login:
        user = User()
        user.username = login
        user.first_name = first_name
        user.last_name = last_name
        user.email = mail
        try:
            user.save()
            logging.info("[%s] new user [%s]" % (data['user'].username, login))
            #users(request)
        except:
            #data['error'] = "Le nouvel utilisateur n'a pu être créé."
            logging.warning("[%s] new user failed: [%s] [%s] [%s] [%s]" % (data['user'].username, login, first_name, last_name, mail))
            messages.add_message(request, messages.ERROR, "Le nouveau compte n'a pu être créé.")
    return HttpResponseRedirect('/manager/users/')

@permission_required('base.p1')
def users_change(request, user_id):
    data = get_user(request)
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    user = get_object_or_404(User, pk=user_id)
    if login != user.username:
        logging.info("[%s] new login: [%s] > [%s]" % (data['user'].username, user.username, login))
        user.username = login
    if first_name != user.first_name:
        logging.info("[%s] new first name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.first_name, first_name))
        user.first_name = first_name
    if last_name != user.last_name:
        logging.info("[%s] new last name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.last_name, last_name))
        user.last_name = last_name
    if mail != user.email:
        logging.info("[%s] new mail for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.email, mail))
        user.email = mail

    try:
        user.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for [%s]" % (data['user'].username, user.username))
    return HttpResponseRedirect('/manager/users/')

@permission_required('base.p1')
def users_active(request, user_id):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    new = not user.is_active
    p1 = Permission.objects.get(codename="p1")
    if not new and p1.user_set.count() == 1 and p1 in user.user_permissions.all():
        messages.add_message(request, messages.ERROR, "Il doit rester au moins un compte actif avec la permission P1.")
        logging.warning("[%s] we must have at least one active user with P1 permission.")
    else:
        user.is_active = new
        user.save()
        logging.info("[%s] user [%s] active: %s" % (data['user'].username, user.username, user.is_active))
    return HttpResponseRedirect('/manager/users/')

@permission_required('base.p1')
def users_passwd(request, user_id):
    """Set a new random password for a user.
    """
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    passwd = UserManager().make_random_password(length=10)
    user.set_password(passwd)
    user.save()
    messages.add_message(request, messages.SUCCESS, "Le nouveau mot de passe l'utilisateur %s est : %s" % (user.username, passwd))
    logging.info("[%s] user [%s] new password" % (data['user'].username, user.username))
    return HttpResponseRedirect('/manager/users/')

@permission_required('base.p1')
def users_change_perm(request, user_id, codename):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    # little test because because user can do ugly things :)
    # now we are sure that it is a good permission
    if codename in settings.PERMS:
        perm = Permission.objects.get(codename=codename)
        if perm in user.user_permissions.all():
            if codename == 'p1' and perm.user_set.count() == 1:
                # we must have at least one person with this permission
                logging.info("[%s] user [%s] perm [%s]: at least should have one person" % (data['user'].username, user.username, codename))
                messages.add_message(request, messages.ERROR, "Il doit rester au moins 1 compte avec la permission P1.")
            else:
                user.user_permissions.remove(perm)
                logging.info("[%s] user [%s] remove perm: %s" % (data['user'].username, user.username, codename))
        else:
            user.user_permissions.add(perm)
            logging.info("[%s] user [%s] add perm: %s" % (data['user'].username, user.username, codename))
    else:
        logging.warning("[%s] wrong perm info : [%s]" % (data['user'].username, codename))
    return HttpResponseRedirect('/manager/users/')

@permission_required('base.p5')
def bill_new(request):
    """Create a new bill"""
    data = get_user(request)
    data['menu_bills'] = True
    bill = Facture()
    bill.save()
    return HttpResponseRedirect('/bill/%s/' % bill.id)

@permission_required('base.p5')
def bill_send_kitchen(request, bill_id):
    """Send in the kitchen"""
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.table:
        if bill.send_in_the_kitchen():
            if bill.table:
                msg = u"%s envoyée" % bill.table
            else:
                msg = u"Envoyé en cuisine"
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            messages.add_message(request, messages.ERROR, "Erreur dans l'envoi (imprimante ok?).")
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir une table.")
    return HttpResponseRedirect('/bill/%s/' % bill.id)

@permission_required('base.p5')
def bill_print(request, bill_id):
    """Print the bill"""
    data = get_user(request)
    data['menu_bills'] = True
    bill = get_object_or_404(Facture, pk=bill_id)
    if bill.is_empty():
        messages.add_message(request, messages.ERROR, "La facture est vide.")
    else:
        if Printer.objects.filter(billing=True).count() == 0:
            messages.add_message(request, messages.ERROR, "Aucune imprimante n'est configurée pour la facturation.")
        else:
            if not bill.print_ticket():
                messages.add_message(request, messages.ERROR, "L'impression a échouée.")
    return HttpResponseRedirect('/bill/%s/' % bill.id)

@permission_required('base.p5')
def table_select(request, bill_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['zones'] = Zone.objects.all()
    data['bill_id'] = bill_id
    return render_to_response('base/bill/select_a_table.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def table_set(request, bill_id, table_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    table = get_object_or_404(Table, pk=table_id)
    bill.set_table(table)
    data['facture'] = bill
    return render_to_response('base/bill/order.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def category_select(request, bill_id, category_id=None):
    """Select a category to add a new product on a bill."""
    data = get_user(request)
    data['menu_bills'] = True
    data['categories'] = cache['categories']
    if category_id:
        category = get_category_or_404(category_id)
    else:
        category = data['categories'][0]
    data['products'] = cache['products'][category.id]
    data['bill_id'] = bill_id
    return render_to_response('base/bill/categories.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def product_select_made_with(request, bill_id, product_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill'] = get_object_or_404(Facture, pk=bill_id)
    data['product'] = get_object_or_404(ProduitVendu, pk=product_id)
    data['categories'] = Categorie.objects.filter(made_in_kitchen=True)
    return render_to_response('base/bill/product_select_made_with.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def product_set_made_with(request, bill_id, product_id, category_id):
    data = get_user(request)
    product = get_object_or_404(ProduitVendu, pk=product_id)
    category = get_category_or_404(category_id)
    product.made_with = category
    product.save()
    return HttpResponseRedirect('/bill/%s/sold/%s/view/' % (bill_id, product.id))

@permission_required('base.p5')
def product_select(request, bill_id, category_id):
    """Select a product to add on a bill."""
    data = get_user(request)
    data['menu_bills'] = True
    bill = get_object_or_404(Facture, pk=bill_id)
    category = get_category_or_404(category_id)
    if not category.vat_onsite:
        messages.add_message(request, messages.ERROR, "La TVA sur place n'est pas définie!")
    if not category.vat_takeaway:
        messages.add_message(request, messages.ERROR, "La TVA à emporter n'est pas définie!")
    data['products'] = cache['products'][category.id]
    data['bill_id'] = bill_id
    return render_to_response('base/bill/products.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def subproduct_select(request, bill_id, sold_id, category_id):
    """Select a subproduct to a product."""
    data = get_user(request)
    data['menu_bills'] = True
    category = get_category_or_404(category_id)
    data['products'] = cache['products'][category.id]
    data['bill_id'] = bill_id
    data['sold_id'] = sold_id
    return render_to_response('base/bill/subproducts.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def sold_view(request, bill_id, sold_id):
    data = get_user(request)
    data['menu_bills'] = True
    data['bill_id'] = bill_id
    data['sold'] = get_object_or_404(ProduitVendu, pk=sold_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    return render_to_response('base/bill/sold.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def sold_delete(request, bill_id, sold_id):
    data = get_user(request)
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
        return HttpResponseRedirect('/bill/%s/sold/%s/category/%s/select/' % (bill_id, menu.id, category.id))

@permission_required('base.p5')
def subproduct_add(request, bill_id, sold_id, product_id):
    """Add a product to a bill. If this product contains others products,
    we have to add them too."""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    product = get_product_or_404(product_id)
    product_sell = ProduitVendu(produit=product)
    product_sell.made_with = product_sell.produit.categorie
    product_sell.save()
    menu = get_object_or_404(ProduitVendu, pk=sold_id)
    menu.contient.add(product_sell)
    if product.choix_cuisson:
        return HttpResponseRedirect('/bill/%s/sold/%s/%s/cooking/' % (bill_id, menu.id, product_sell.id))
    category = menu.getFreeCategorie()
    if category:
        return HttpResponseRedirect('/bill/%s/sold/%s/category/%s/select/' % (bill_id, menu.id, category.id))
    return HttpResponseRedirect('/bill/%s/category/%s/' % (bill_id, menu.produit.categorie.id))

@permission_required('base.p5')
def product_add(request, bill_id, product_id):
    """Add a product to a bill. If this product contains others products,
    we have to add them too."""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    product = get_product_or_404(product_id)
    product_sell = ProduitVendu(produit=product)
    product_sell.save()
    bill.add_product(product_sell)
    if product.est_un_menu():
        category = product_sell.getFreeCategorie()
        return HttpResponseRedirect('/bill/%s/sold/%s/category/%s/select/' % (bill_id, product_sell.id, category.id))
    if product.choix_cuisson:
        return HttpResponseRedirect('/bill/%s/sold/%s/cooking/' % (bill_id, product_sell.id))
    messages.add_message(request, messages.SUCCESS, "%s ok" % product.nom)
    return HttpResponseRedirect('/bill/%s/category/%s/' % (bill_id, product.categorie.id))

@permission_required('base.p5')
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
                return HttpResponseRedirect('/bill/%s/sold/%s/category/%s/select/' % (bill_id, menu.id, category.id))
        if old == None:
            # certainement un nouveau produit donc on veut retourner
            # sur le panneau de saisie des produits
            return HttpResponseRedirect('/bill/%s/category/%s/' % (bill_id, data['sold'].produit.categorie.id))
        else:
            return HttpResponseRedirect('/bill/%s/' % bill_id)
    return render_to_response('base/bill/cooking.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def couverts_select(request, bill_id):
    """List of couverts for a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['nb_couverts'] = range(35)
    data['bill_id'] = bill_id
    return render_to_response('base/bill/couverts.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def couverts_set(request, bill_id, number):
    """Set couverts of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.set_couverts(number)
    data['facture'] = bill
    return render_to_response('base/bill/order.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p3')
def factures(request):
    data = get_user(request)
    data['menu_bills'] = True
    data['factures'] = Facture().non_soldees()
    return render_to_response('base/bill/home.html',
                                data,
                                context_instance=RequestContext(request))

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
    result = int(left)*10+int(number)
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
    data = get_user(request)
    type_payment = get_object_or_404(PaiementType, pk=type_id)
    bill = get_object_or_404(Facture, pk=bill_id)
    montant = "%s.%s" % (left, right)
    if type_payment.fixed_value:
        result = bill.add_payment(type_payment, count, montant)
    else:
        result = bill.add_payment(type_payment, montant)
    if not result:
        messages.add_message(request, messages.ERROR, "Le paiement n'a pu être enregistré.")
    if bill.saved_in_stats:
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
    data['type_payments'] = PaiementType.objects.all()
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

@permission_required('base.p3')
def bill_view(request, bill_id):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=bill_id)
    if data['facture'].est_soldee():
        messages.add_message(request, messages.ERROR, "Cette facture a déjà été soldée.")
        return HttpResponseRedirect('/bills/')
    data['next'] = data['facture'].something_for_the_kitchen()
    data['suivis'] = Suivi.objects.filter(facture=data['facture']).order_by("-date")
    data['menu_bills'] = True
    return render_to_response('base/bill/order.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p3')
def bill_delete(request, bill_id):
    order = get_object_or_404(Facture, pk=bill_id)
    order.delete()
    return HttpResponseRedirect('/bills/')

@permission_required('base.p6')
def bill_onsite(request, bill_id):
    data = get_user(request)
    order = get_object_or_404(Facture, pk=bill_id)
    new = not order.onsite
    order.onsite = new
    order.save()
    order.compute_total()
    return HttpResponseRedirect('/bill/%s/' % bill_id)

@permission_required('base.p7')
def archives(request):
    data = get_user(request)
    data['menu_manager'] = True
    if request.method == 'POST':
        try:
            year = int(request.POST.get('date_year'))
            month = int(request.POST.get('date_month'))
            day = int(request.POST.get('date_day'))
            date = datetime(year, month, day)
        except:
            messages.add_message(request, messages.ERROR, "La date saisie n'est pas valide.")
            date = datetime.today()
    else:
        date = datetime.today()
    data['date_form'] = DateForm({'date': date, })
    data['factures'] = Facture().get_bills_for(date)
    data['date'] = date
    return render_to_response('base/manager/archives/home.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def archives_bill(request, bill_id):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=bill_id)
    if not data['facture'].est_soldee():
        messages.add_message(request, messages.ERROR, "Cette facture n'est pas encore soldée.")
        return HttpResponseRedirect('/manager/archives/')
    data['suivis'] = Suivi.objects.filter(facture=data['facture']).order_by("-date")
    data['menu_manager'] = True
    return render_to_response('base/manager/archives/invoice.html',
                                data,
                                context_instance=RequestContext(request))

create_default_directory()

# Possum Cache System
cache = {}

init_cache_system()
