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
import logging
import datetime
from possum.base.views import permission_required
from possum.stats.models import Stat
from possum.base.forms import DateForm, WeekForm, MonthForm


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def update(request):
    """Update statistics
    """
    if Stat().update():
        messages.add_message(request, messages.SUCCESS,
                             "Les données sont à jour")
    else:
        messages.add_message(request, messages.ERROR,
                             "Les données ne peuvent être mis à jour")
    return redirect("manager")


@permission_required('base.p1')
def daily(request):
    """Show stats for a day
    """
    context = {'menu_manager': True, }
    date = datetime.datetime.now()
    if request.method == 'POST':
        try:
            year = int(request.POST.get('date_year'))
            month = int(request.POST.get('date_month'))
            day = int(request.POST.get('date_day'))
            date = datetime.datetime(year, month, day)
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "La date saisie n'est pas valide.")
    context['date_form'] = DateForm({'date': date, })
    context['date'] = date
    context = Stat().get_data_for_day(context)
    return render(request, 'stats/home.html', context)


@permission_required('base.p1')
def weekly(request):
    """Show stats for a week
    """
    context = {'menu_manager': True, }
    date = datetime.datetime.now()
    year = date.year
    week = date.isocalendar()[1]
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
            week = int(request.POST.get('week'))
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "La date saisie n'est pas valide.")
    context['week_form'] = WeekForm({'year': year, 'week': week})
    context['week'] = week
    context['year'] = year
    context = Stat().get_data_for_week(context)
    return render(request, 'stats/home.html', context)


@permission_required('base.p1')
def monthly(request):
    """Show stats for a month
    """
    context = {'menu_manager': True, }
    date = datetime.datetime.now()
    year = date.year
    month = date.month
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "La date saisie n'est pas valide.")
    context['month_form'] = MonthForm({'year': year, 'month': month})
    context['month'] = month
    context['year'] = year
    context = Stat().get_data_for_month(context)
    return render(request, 'stats/home.html', context)
