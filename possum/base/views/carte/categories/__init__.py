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
from django.core.mail import send_mail
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from possum.base.models import Categorie
from possum.stats.models import Stat
from possum.base.models import Printer
from possum.base.models import Produit
from possum.base.models import VAT
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p2')
def categories_send(request):
    result = Produit().get_list_with_all_products()
    subject = "Carte complete"
    mail = ""
    for line in result:
        mail += "%s\n" % line
    if request.user.email:
        try:
            send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL,
                      [request.user.email], fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR,
                                 u"Le mail n'a pu être envoyé.")
        else:
            messages.add_message(request, messages.SUCCESS,
                                 u"Le mail a été envoyé à %s."
                                 % request.user.email)
    else:
        messages.add_message(request, messages.ERROR,
                             u"Vous n'avez pas d'adresse mail.")
    return redirect('categories')


@permission_required('base.p2')
def categories_print(request):
    result = Produit().get_list_with_all_products()
    if result:
        printers = Printer.objects.filter(manager=True)
        if printers:
            printer = printers[0]
            if printer.print_list(result, "carte_complete"):
                messages.add_message(request, messages.SUCCESS,
                                     u"L'impression a été envoyée sur %s." %
                                     printer.name)
            else:
                messages.add_message(request, messages.ERROR, u"L'impression"
                                     u" a échouée sur %s." % printer.name)
        else:
            messages.add_message(request, messages.ERROR, u"Aucune imprimante "
                                 u"type 'manager' disponible.")
    else:
        messages.add_message(request, messages.ERROR,
                             "Il n'y a rien dans la carte.")
    return redirect('categories')


@permission_required('base.p2')
def categories(request):
    context = {'menu_manager': True, }
    context['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render(request, 'base/carte/categories.html', context)


@permission_required('base.p2')
def categories_delete(request, cat_id):
    context = {'menu_manager': True, }
    context['current_cat'] = get_object_or_404(Categorie, pk=cat_id)
    context['categories'] = Categorie.objects.order_by('priorite', 'nom').exclude(id=cat_id)
    cat_report_id = request.POST.get('cat_report', '').strip()
    action = request.POST.get('valide', '').strip()
    if action == "Supprimer":
        products_list = Produit.objects.filter(categorie__id=cat_id)
        # we have to report stats and products ?
        if cat_report_id:
            try:
                report = Categorie.objects.get(id=cat_report_id)
                # we transfer all products
                for product in products_list:
                    product.categorie = report
                    product.save()
            except Categorie.DoesNotExist:
                logger.warning("[%s] categorie [%s] doesn't exist" % (
                               request.user.username, cat_report_id))
                messages.add_message(request, messages.ERROR, "La catégorie "
                                     "n'existe pas.")
                return redirect('categories_delete', cat_id)
            report_info = "from [%s] to [%s]" % (context['current_cat'],
                                                 report)
            logger.info("move stats %s" % report_info)
            for key in ["category_nb", "category_value"]:
                new_key = "%s_%" % (cat_report_id, key)
                for s in Stat.objects.filter(key="%s_%s" % (cat_id, key)):
                    new, created = Stat.objects.get_or_create(key=new_key,
                                                              year=s.year,
                                                              month=s.month,
                                                              week=s.week,
                                                              day=s.day,
                                                              interval=s.interval)
                    new.add_value(s.value)
                    s.delete()
            logger.info("copy products %s" % report_info)
            for product in products_list:
                new = product._clone_product()
                new.categorie = report
                new.update_vats(keep_clone=False)
                new.save()
        if products_list.count() == 0:
            context['current_cat'].delete()
            logger.info("[%s] categorie [%s] deleted" % (
                        request.user.username,
                        context['current_cat'].nom))
            return redirect('categories')
        else:
            messages.add_message(request, messages.ERROR, "La catégorie "
                                 "ne peux être supprimé, elle contient "
                                 "des produits")

    elif action == "Annuler":
        return redirect('categories')
    return render(request, 'base/categories_delete.html', context)


@permission_required('base.p2')
def categories_view(request, cat_id):
    context = {'menu_manager': True, }
    context['category'] = get_object_or_404(Categorie, pk=cat_id)
    products = Produit.objects.filter(categorie__id=cat_id)
    context['products_enable'] = products.filter(actif=True)
    context['products_disable'] = products.filter(actif=False)
    return render(request, 'base/carte/category.html', context)


@permission_required('base.p2')
def categories_add(request):
    context = {'menu_manager': True, }
    return render(request, 'base/carte/categories_add.html', context)


@permission_required('base.p2')
def categories_new(request):
    priority = request.POST.get('priority', '').strip()
    name = request.POST.get('name', '').strip()
    if name:
        cat = Categorie()
        cat.nom = name
        if priority:
            cat.priorite = priority
        try:
            cat.save()
            logger.info("[%s] new categorie [%s]" % (request.user.username,
                                                     name))
        except:
            logger.warning("[%s] new categorie failed: [%s] [%s]" % (
                           request.user.username, cat.priorite, cat.nom))
            messages.add_message(request, messages.ERROR, "La nouvelle "
                                 "catégorie n'a pu être créée.")
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir "
                             "un nom pour la nouvelle catégorie.")
    return redirect('categories')


@permission_required('base.p2')
def categories_name(request, cat_id):
    context = {'menu_manager': True, }
    context['category'] = get_object_or_404(Categorie, pk=cat_id)
    return render(request, 'base/carte/name.html', context)


@permission_required('base.p2')
def categories_color(request, cat_id):
    context = {'menu_manager': True, }
    context['category'] = get_object_or_404(Categorie, pk=cat_id)
    context['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render(request, 'base/carte/color.html', context)


@permission_required('base.p2')
def categories_less_priority(request, cat_id, nb=1):
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.set_less_priority(nb)
    logger.info("[%s] cat [%s] priority - %d" % (request.user.username,
                                                 cat.nom, nb))
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_more_priority(request, cat_id, nb=1):
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.set_more_priority(nb)
    logger.info("[%s] cat [%s] priority + %d" % (request.user.username,
                                                 cat.nom, nb))
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_surtaxable(request, cat_id):
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.surtaxable
    cat.surtaxable = new
    if cat.surtaxable:
        cat.disable_surtaxe = False
    cat.save()
    for product in Produit.objects.filter(categorie=cat).iterator():
        product.update_vats()
    logger.info("[%s] cat [%s] surtaxable: %s" % (request.user.username,
                cat.nom, cat.surtaxable))
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_vat_takeaway(request, cat_id):
    context = {'menu_manager': True, }
    context['category'] = get_object_or_404(Categorie, pk=cat_id)
    context['type_vat'] = 'TVA à emporter'
    context['url_vat'] = 'vat_takeaway'
    context['vats'] = VAT.objects.order_by('name')
    return render(request, 'base/carte/categories/select_vat.html', context)


@permission_required('base.p2')
def categories_set_vat_takeaway(request, cat_id, vat_id):
    category = get_object_or_404(Categorie, pk=cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_takeaway(vat)
    for product in Produit.objects.filter(categorie=category,
                                          actif=True).iterator():
        product.update_vats()
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_set_vat_onsite(request, cat_id, vat_id):
    category = get_object_or_404(Categorie, pk=cat_id)
    vat = get_object_or_404(VAT, pk=vat_id)
    category.set_vat_onsite(vat)
    for product in Produit.objects.filter(categorie=category,
                                          actif=True).iterator():
        product.update_vats()
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_vat_onsite(request, cat_id):
    context = {'menu_manager': True, }
    context['category'] = get_object_or_404(Categorie, pk=cat_id)
    context['type_vat'] = 'TVA sur place'
    context['url_vat'] = 'vat_onsite'
    context['vats'] = VAT.objects.order_by('name')
    return render(request, 'base/carte/categories/select_vat.html', context)


def update_colors():
    """Create/update a css file with all categories color
    """
    try:
        fd = open(settings.CAT_CSS, "w")
    except:
        messages.add_message(request, messages.ERROR, u"Le fichier %s ne peut "
                             u"être créé" % settings.CAT_CSS)
    else:
        fd.write("/* Auto generate file, do not update by hand */\n")
        for cat in Categorie.objects.iterator():
            if cat.color:
                fd.write(".cat_%s {background:%s;}\n" % (cat.id, cat.color))
        fd.close()
        logger.info("CSS for categories colors updated")


@permission_required('base.p2')
def categories_set_color(request, cat_id):
    color = request.POST.get('color', '').strip()
    cat = get_object_or_404(Categorie, pk=cat_id)
    if not cat.color or color != cat.color:
        logger.info("[%s] new categorie color [%s]" % (request.user.username,
                                                       cat.nom))
        cat.color = color
        try:
            cat.save()
        except:
            messages.add_message(request, messages.ERROR, "Les modifications "
                                 "n'ont pu être enregistrées.")
        else:
            update_colors()
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_set_name(request, cat_id):
    name = request.POST.get('name', '').strip()
    cat = get_object_or_404(Categorie, pk=cat_id)
    if name != cat.nom:
        logger.info("[%s] new categorie name: [%s] > [%s]" % (
                    request.user.username, cat.nom, name))
        cat.nom = name

    try:
        cat.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications "
                             "n'ont pu être enregistrées.")
        logger.warning("[%s] save failed for [%s]" % (
                       request.user.username, cat.nom))
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_set_kitchen(request, cat_id):
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.made_in_kitchen
    cat.made_in_kitchen = new
    cat.save()
    return redirect('categories_view', cat_id)


@permission_required('base.p2')
def categories_disable_surtaxe(request, cat_id):
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.disable_surtaxe
    cat.disable_surtaxe = new
    if cat.disable_surtaxe:
        cat.surtaxable = False
    cat.save()
    return redirect('categories_view', cat_id)
