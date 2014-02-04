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

import datetime
from django.contrib import messages
import logging
from django.shortcuts import render, redirect
from possum.base.models import Categorie
from possum.base.charts import get_chart_year_bar, get_chart_year_categories, \
    get_chart_year_guests, get_chart_year_payments, get_chart_year_products, \
    get_chart_year_ttc, get_chart_year_vats
from possum.base.models import DailyStat
from possum.base.forms import YearForm
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def charts_year(request, choice='ttc'):
    """
    chart1: pour un seul graphique
    chart2: pour 2 graphiques
    """
    context = { 'menu_manager': True, }
    context['cat_list'] = Categorie.objects.order_by('priorite', 'nom')
    year = datetime.datetime.now().year
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
        except:
            messages.add_message(request, messages.ERROR,
                                 "La date saisie n'est pas valide.")
    if choice == 'ttc':
        context['chart1'] = get_chart_year_ttc(year)
    elif choice == 'bar':
        context['chart1'] = get_chart_year_bar(year)
    elif choice == 'guests':
        context['chart1'] = get_chart_year_guests(year)
    elif choice == 'vats':
        context['chart1'] = get_chart_year_vats(year)
    elif choice == 'payments':
        context['chart2'] = get_chart_year_payments(year)
    elif choice == 'categories':
        context['chart2'] = get_chart_year_categories(year)
    else:
        try:
            cat = Categorie.objects.get(pk=choice)
        except Categorie.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 "Ce type de graphique n'existe pas.")
            return redirect('manager')
        else:
            context['chart2'] = get_chart_year_products(year, cat)
    context[choice] = True
    context['choice'] = choice
    context['year_form'] = YearForm({'year': year})
    context['year'] = year
    return render(request, 'base/manager/charts/home.html', context)
