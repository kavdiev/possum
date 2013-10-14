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

from possum.base.stats import DailyStat, WeeklyStat, MonthlyStat
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

@permission_required('base.p2')
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

@permission_required('base.p2')
def categories(request):
    data = get_user(request)
    data['menu_carte'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render_to_response('base/carte/categories.html',
                    data,
                    context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_delete(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['current_cat'] = get_object_or_404(Categorie, pk=cat_id)
    data['categories'] = Categorie.objects.order_by('priorite', 'nom').exclude(id=cat_id)
    cat_report_id = request.POST.get('cat_report', '').strip()
    action = request.POST.get('valide', '').strip()
    if action == "Supprimer":
        # we have to report stats and products ?
        if cat_report_id:
            try:
                report = Categorie.objects.get(id=cat_report_id)
                # we transfert all statistics
                # TODO: report on WeeklyStat and MonthlyStat
                for stat in DailyStat.objects.filter(key="%s_category_nb" % cat_id):
                    category_nb, created = DailyStat.objects.get_or_create(
                            date=stat.date,
                            key="%s_category_nb" % report.id)
                    category_nb.value += stat.value
                    category_nb.save()
                    stat.delete()
                for stat in DailyStat.objects.filter(key="%s_category_value" % cat_id):
                    category_value, created = DailyStat.objects.get_or_create(
                            date=stat.date,
                            key="%s_category_value" % report.id)
                    category_value.value += stat.value
                    category_value.save()
                    stat.delete()
                # we transfert all products
                for product in Produit.objects.filter(categorie__id=cat_id):
                    product.categorie = report
                    product.save()
            except Categorie.DoesNotExist:
                logger.warning("[%s] categorie [%s] doesn't exist" % (data['user'].username, cat_report_id))
                messages.add_message(request, messages.ERROR, "La catégorie n'existe pas.")
                return HttpResponseRedirect('/carte/categories/%s/delete/' % cat_id)
        # now, we have to delete the categorie and remove all products remains
        for product in Produit.objects.filter(categorie__id=cat_id):
            DailyStat.objects.filter(key="%s_product_nb" % product.id).delete()
            DailyStat.objects.filter(key="%s_product_value" % product.id).delete()
            product.delete()
        DailyStat.objects.filter(key="%s_category_nb" % cat_id).delete()
        DailyStat.objects.filter(key="%s_category_value" % cat_id).delete()
        logger.info("[%s] categorie [%s] deleted" % (data['user'].username, data['current_cat'].nom))
        data['current_cat'].delete()
        return HttpResponseRedirect('/carte/categories/')
    elif action == "Annuler":
        return HttpResponseRedirect('/carte/categories/')
    return render_to_response('base/categories_delete.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_view(request, cat_id):
    data = get_user(request)
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    data['menu_carte'] = True
    products = Produit.objects.filter(categorie__id=cat_id)
    data['products_enable'] = products.filter(actif=True)
    data['products_disable'] = products.filter(actif=False)
    return render_to_response('base/carte/category.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_add(request):
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte/categories_add.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
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
            logger.info("[%s] new categorie [%s]" % (data['user'].username, name))
        except:
            logger.warning("[%s] new categorie failed: [%s] [%s]" % (data['user'].username, cat.priorite, cat.nom))
            messages.add_message(request, messages.ERROR, "La nouvelle catégorie n'a pu être créée.")
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir un nom pour la nouvelle catégorie.")
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p2')
def categories_name(request, cat_id):
    data = get_user(request)
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    return render_to_response('base/carte/name.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_color(request, cat_id):
    data = get_user(request)
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render_to_response('base/carte/color.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_less_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.set_less_priority(nb)
    logger.info("[%s] cat [%s] priority - %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_more_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.set_more_priority(nb)
    logger.info("[%s] cat [%s] priority + %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_surtaxable(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.surtaxable
    cat.surtaxable = new
    if cat.surtaxable:
        cat.disable_surtaxe = False
    cat.save()
    logger.info("[%s] cat [%s] surtaxable: %s" % (data['user'].username, cat.nom, cat.surtaxable))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_vat_takeaway(request, cat_id):
    data = get_user(request)
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    data['type_vat'] = 'TVA à emporter'
    data['url_vat'] = 'vat_takeaway'
    data['vats'] = VAT.objects.order_by('name')
    data['menu_carte'] = True
    return render_to_response('base/carte/categories/select_vat.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_set_vat_takeaway(request, cat_id, vat_id):
    data = get_user(request)
    category = get_object_or_404(Categorie, pk=cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_takeaway(vat)
    for product in Produit.objects.filter(categorie=category).iterator():
        product.update_vats()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_set_vat_onsite(request, cat_id, vat_id):
    data = get_user(request)
    category = get_object_or_404(Categorie, pk=cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_onsite(vat)
    for product in Produit.objects.filter(categorie=category).iterator():
        product.update_vats()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_vat_onsite(request, cat_id):
    data = get_user(request)
    data['menu_carte'] = True
    data['category'] = get_object_or_404(Categorie, pk=cat_id)
    data['type_vat'] = 'TVA sur place'
    data['url_vat'] = 'vat_onsite'
    data['vats'] = VAT.objects.order_by('name')
    return render_to_response('base/carte/categories/select_vat.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p2')
def categories_set_color(request, cat_id):
    data = get_user(request)
    color = request.POST.get('color', '').strip()
    cat = get_object_or_404(Categorie, pk=cat_id)
    if not cat.color or color != cat.color:
        logger.info("[%s] new categorie color [%s]" % (data['user'].username, cat.nom))
        cat.color = color
        try:
            cat.save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_set_name(request, cat_id):
    data = get_user(request)
    name = request.POST.get('name', '').strip()
    cat = get_object_or_404(Categorie, pk=cat_id)
    if name != cat.nom:
        logger.info("[%s] new categorie name: [%s] > [%s]" % (data['user'].username, cat.nom, name))
        cat.nom = name

    try:
        cat.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logger.warning("[%s] save failed for [%s]" % (data['user'].username, cat.nom))
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_set_kitchen(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.made_in_kitchen
    cat.made_in_kitchen = new
    cat.save()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)

@permission_required('base.p2')
def categories_disable_surtaxe(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.disable_surtaxe
    cat.disable_surtaxe = new
    if cat.disable_surtaxe:
        cat.surtaxable = False
    cat.save()
    return HttpResponseRedirect('/carte/categories/%s/' % cat_id)