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

from django.shortcuts import render
from possum.base.models import Facture
from possum.base.views import permission_required, get_user
import os
from django.conf import settings



@permission_required('base.p1')
def credits(request):
    context = get_user(request)
    context['menu_manager'] = True
    return render(request, 'base/manager/credits.html', context)


@permission_required('base.p1')
def manager(request):
    context = get_user(request)
    context['menu_manager'] = True
    if os.path.isfile(settings.LOCK_STATS):
        context['working_on_update'] = True
    else:
        bills_to_update = Facture.objects.filter(saved_in_stats=False,
                                                 restant_a_payer=0)
        count = bills_to_update.exclude(produits__isnull=True).count()
#                                            ).exclude(produits__isnull=True
#                                                     ).count()
        if count:
            context['bills_to_update'] = count
    return render(request, 'base/manager/home.html', context)
