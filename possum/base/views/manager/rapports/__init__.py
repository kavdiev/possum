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
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from possum.base.models import DailyStat
from possum.base.forms import DateForm, WeekForm, MonthForm
from possum.base.models import Printer
from possum.base.models import MonthlyStat
from possum.base.utils import get_last_year
from possum.base.views import get_user, permission_required
from possum.base.models import WeeklyStat


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def rapports_daily(request):
    """
    Affiche le rapport pour une journée
    """
    data = get_user(request)
    data['menu_manager'] = True
    DailyStat().update()
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
    data['date_form'] = DateForm({'date': date, })
    data['date'] = date
    data = DailyStat().get_data(data, date)
    # les stats de l'année précédente
    last_year = get_last_year(date)
    for key in ['nb_bills', 'total_ttc', 'guests_nb', 'guests_average',
                'guests_total_ttc', 'bar_nb', 'bar_average', 'bar_total_ttc']:
        data['last_%s' % key] = "%.2f" % DailyStat().get_value(key, last_year)
        data['max_%s' % key] = DailyStat().get_max(key)
        data['avg_%s' % key] = DailyStat().get_avg(key)
    return render_to_response('base/manager/rapports/home.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def rapports_weekly(request):
    """
    Affiche le rapport pour une semaine
    """
    data = get_user(request)
    data['menu_manager'] = True
    DailyStat().update()
    date = datetime.datetime.now()
    year = date.year
    # 01 must be converted to 1
    week = int(date.strftime("%U"))
    if request.method == 'POST':
        try:
            week = int(request.POST.get('week'))
            year = int(request.POST.get('year'))
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "La date saisie n'est pas valide.")
    data['week_form'] = WeekForm({'year': year, 'week': week})
    data['week'] = week
    data['year'] = year
    last_year = year - 1
    data = WeeklyStat().get_data(data, year, week)
    for key in ['nb_bills', 'total_ttc', 'guests_nb', 'guests_average',
                'guests_total_ttc', 'bar_nb', 'bar_average', 'bar_total_ttc']:
        data['last_%s' % key] = "%.2f" % WeeklyStat().get_value(key, last_year, week)
        data['max_%s' % key] = WeeklyStat().get_max(key)
        data['avg_%s' % key] = WeeklyStat().get_avg(key)
    return render_to_response('base/manager/rapports/home.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def rapports_monthly(request):
    """
    Affiche le rapport pour un mois
    """
    data = get_user(request)
    data['menu_manager'] = True
    DailyStat().update()
    date = datetime.datetime.now()
    year = date.year
    month = date.month
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
        except:
            messages.add_message(request,
                                 messages.ERROR,
                                 "La date saisie n'est pas valide.")
    data['month_form'] = MonthForm({'year': year, 'month': month})
    data['month'] = month
    data['year'] = year
    last_year = year - 1
    data = MonthlyStat().get_data(data, year, month)
    for key in ['nb_bills', 'total_ttc', 'guests_nb', 'guests_average',
                'guests_total_ttc', 'bar_nb', 'bar_average', 'bar_total_ttc']:
        data['last_%s' % key] = "%.2f" % MonthlyStat().get_value(key, last_year, month)
        data['max_%s' % key] = MonthlyStat().get_max(key)
        data['avg_%s' % key] = MonthlyStat().get_avg(key)
    return render_to_response('base/manager/rapports/home.html',
                                data,
                                context_instance=RequestContext(request))


def rapports_send(request, subject, data):
    mail = """
Nb factures: %s
Total TTC: %s

""" % (data['nb_bills'], data['total_ttc'])
    for vat in data['vats']:
        mail += "%s\n" % vat
    mail += """
Restauration:
Nb couverts: %s
Total TTC: %s
TM/couvert: %s
""" % (data['guests_nb'], data['guests_total_ttc'], data['guests_average'])
    mail += """
Bar:
Nb factures: %s
Total TTC: %s
TM/facture: %s
""" % (data['bar_nb'], data['bar_total_ttc'], data['bar_average'])
    mail += "\n"
    for payment in data['payments']:
        mail += "%s\n" % payment
    mail += "\n"
    for category in data['categories']:
        mail += "%s : %s\n" % (category.nom, category.nb)
    mail += "\n"
    for product in data['products']:
        mail += "%s : %s\n" % (product.nom, product.nb)
    mail += "\n\nFait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if request.user.email:
        try:
            send_mail(subject, mail,
                      settings.DEFAULT_FROM_EMAIL,
                      [request.user.email], fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR, u"Le mail n'a pu être envoyé.")
        else:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 u"Le mail a été envoyé à %s." % request.user.email)
    else:
        messages.add_message(request,
                             messages.ERROR,
                             u"Vous n'avez pas d'adresse mail.")


@permission_required('base.p1')
def rapports_daily_send(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    data = {}
    data = DailyStat().get_data(data, date)
    subject = "Rapport du %s" % date
    rapports_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/daily/')


@permission_required('base.p1')
def rapports_weekly_send(request, year, week):
    data = {}
    data = WeeklyStat().get_data(data, year, week)
    subject = "Rapport semaine %s/%s" % (week, year)
    rapports_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/weekly/')


@permission_required('base.p1')
def rapports_monthly_send(request, year, month):
    data = {}
    data = MonthlyStat().get_data(data, year, month)
    subject = "Rapport mensuel %s/%s" % (month, year)
    rapports_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/monthly/')


def rapports_print(request, subject, data):
    result = []
    result.append(subject)
    result.append("Fait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    result.append("--")
    result.append("Nb factures: %s" % data['nb_bills'])
    result.append("Total TTC: %s" % data['total_ttc'])
    for vat in data['vats']:
        result.append(vat)
    result.append(" ")
    result.append("Restauration:")
    result.append("Nb couverts: %s" % data['guests_nb'])
    result.append("Total TTC: %s" % data['guests_total_ttc'])
    result.append("TM/couvert: %s" % data['guests_average'])
    result.append(" ")
    result.append("Bar:")
    result.append("Nb factures: %s" % data['bar_nb'])
    result.append("Total TTC: %s" % data['bar_total_ttc'])
    result.append("TM/facture: %s" % data['bar_average'])
    result.append(" ")
    for payment in data['payments']:
        result.append(payment)
    result.append(" ")
    for category in data['categories']:
        result.append("%s : %s" % (category.nom, category.nb))
    result.append(" ")
    for product in data['products']:
        result.append("%s : %s" % (product.nom, product.nb))
    printers = Printer.objects.filter(manager=True)
    if printers:
        printer = printers[0]
        if printer.print_list(result, "rapports_print"):
            messages.add_message(request,
                                 messages.SUCCESS,
                                 u"L'impression a été envoyée sur %s." % printer.name)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 u"L'impression a achouée sur %s." % printer.name)
    else:
        messages.add_message(request,
                             messages.ERROR,
                             u"Aucune imprimante type 'manager' disponible.")


@permission_required('base.p1')
def rapports_daily_print(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    data = {}
    data = DailyStat().get_data(data, date)
    subject = "Rapport du %s" % date
    rapports_print(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/daily/')


@permission_required('base.p1')
def rapports_weekly_print(request, year, week):
    data = {}
    data = WeeklyStat().get_data(data, year, week)
    subject = "Rapport semaine %s/%s" % (week, year)
    rapports_print(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/weekly/')


@permission_required('base.p1')
def rapports_monthly_print(request, year, month):
    data = {}
    data = MonthlyStat().get_data(data, year, month)
    subject = "Rapport mensuel %s/%s" % (month, year)
    rapports_print(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/monthly/')


def rapports_vats_send(request, subject, data):
    mail = ""
    for line in data:
        mail += "%s\n" % line
    mail += "\n\nFait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if request.user.email:
        try:
            send_mail(subject, mail,
                      settings.DEFAULT_FROM_EMAIL,
                      [request.user.email], fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR,
                                 u"Le mail n'a pu être envoyé.")
        else:
            messages.add_message(request, messages.SUCCESS,
                                 u"Le mail a été envoyé à %s." % request.user.email)
    else:
        messages.add_message(request, messages.ERROR,
                             u"Vous n'avez pas d'adresse mail.")


@permission_required('base.p1')
def rapports_daily_vats_send(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    data = DailyStat().get_common(date)
    subject = "Rapport du %s" % date
    rapports_vats_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/daily/')


@permission_required('base.p1')
def rapports_weekly_vats_send(request, year, week):
    data = WeeklyStat().get_common(year, week)
    subject = "Rapport semaine %s/%s" % (week, year)
    rapports_vats_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/weekly/')


@permission_required('base.p1')
def rapports_monthly_vats_send(request, year, month):
    data = MonthlyStat().get_common(year, month)
    subject = "Rapport mois %s/%s" % (month, year)
    rapports_vats_send(request, subject, data)
    return HttpResponseRedirect('/manager/rapports/monthly/')


def rapports_vats_print(request, data):
    printers = Printer.objects.filter(manager=True)
    if printers:
        printer = printers[0]
        if printer.print_list(data, "rapport_common"):
            messages.add_message(request, messages.SUCCESS,
                                 u"L'impression a été envoyée sur %s." % printer.name)
        else:
            messages.add_message(request, messages.ERROR,
                                 u"L'impression a achouée sur %s." % printer.name)
    else:
        messages.add_message(request, messages.ERROR,
                             u"Aucune imprimante type 'manager' disponible.")


@permission_required('base.p1')
def rapports_daily_vats_print(request, year, month, day):
    date = "%s-%s-%s" % (year, month, day)
    data = DailyStat().get_common(date)
    rapports_vats_print(request, data)
    return HttpResponseRedirect('/manager/rapports/daily/')


@permission_required('base.p1')
def rapports_weekly_vats_print(request, year, week):
    data = WeeklyStat().get_common(year, week)
    rapports_vats_print(request, data)
    return HttpResponseRedirect('/manager/rapports/weekly/')


@permission_required('base.p1')
def rapports_monthly_vats_print(request, year, month):
    data = MonthlyStat().get_common(year, month)
    rapports_vats_print(request, data)
    return HttpResponseRedirect('/manager/rapports/monthly/')
