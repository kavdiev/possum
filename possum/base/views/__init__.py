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
from django.contrib.auth.context_processors import PermWrapper
from django.shortcuts import render, redirect
import logging
import os
from django.contrib.auth.decorators import login_required
from django.utils.functional import wraps
from possum.base.utils import create_default_directory
from possum.base.models import Config, Facture
from django.conf import settings


logger = logging.getLogger(__name__)


# TODO une création de dossier au millieu de la vue ?
# (Déplacer dans settings common ?)
create_default_directory()


def cleanup_payment(request):
    """Remove all variables used for a new payment
    """
    keys = ['is_left', 'left', 'right', 'type_selected', 'tickets_count',
            'ticket_value', 'init_montant']
    for key in keys:
        if key in request.session.keys():
            request.session.pop(key)


def remove_edition(request):
    """Remove 'bill_in_use' and update bill if found.
       This is use to reserve access to a bill.
    """
    if "bill_in_use" in request.session.keys():
        bill_id = request.session['bill_in_use']
        try:
            bill = Facture.objects.get(pk=bill_id)
        except Facture.DoesNotExist:
            logger("[%s] bill is not here!" % bill_id)
        else:
            bill.used_by()
            if "products_modified" in request.session.keys():
                # we update bill only once
                bill.update()
                bill.update_kitchen()
                request.session.pop("products_modified")
        request.session.pop("bill_in_use")
    cleanup_payment(request)
    return request


@login_required
def home(request):
    request = remove_edition(request)
    context = { 'menu_home': True, }
    return render(request, 'home.html', context)


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
                                     " les droits nécessaires (%s)." %
                                     perm.split('.')[1])
                return redirect('home')
        return wraps(view_func)(_wrapped_view)
    return decorator


@permission_required('base.p3')
def shutdown(request):
    context = { 'menu_home': True, }
    config = Config.objects.filter(key="default_shutdown")
    if config:
        cmd = config[0].value
    else:
        cmd = "sudo /sbin/shutdown -h now"

    if os.path.isfile(settings.LOCK_STATS):
        messages.add_message(request, messages.ERROR,
                             "Statistiques en cours de calcul,"
                             "réessayer plus tard")
    else:
        if request.method == 'POST':
            os.system(cmd)
            messages.add_message(request, messages.SUCCESS,
                                 "Serveur en cours d'arrêt")
            return redirect('home')
    return render(request, 'shutdown.html', context)
