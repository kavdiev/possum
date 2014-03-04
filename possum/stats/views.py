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
from django.shortcuts import render, redirect
import logging
import datetime
from possum.base.views import permission_required
from possum.stats.models import Stat
from possum.base.forms import DateForm, WeekForm, MonthForm, YearForm
from django.contrib import messages
from django.core.mail import send_mail
from possum.base.models import Printer
from possum.base.models import Categorie, VAT, PaiementType, Produit
from chartit import PivotDataPool, PivotChart
from django.db.models import Avg


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


def send(request, subject, message):
    """Send an email
    """
    if request.user.email:
        try:
            send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL,
                      [request.user.email], fail_silently=False)
        except:
            messages.add_message(request, messages.ERROR,
                                 u"Le mail n'a pu être envoyé")
        else:
            messages.add_message(request, messages.SUCCESS,
                                 u"Mail envoyé à %s" % request.user.email)
    else:
        messages.add_message(request, messages.ERROR,
                             u"Vous n'avez pas d'adresse mail")


def print_msg(request, msg):
    """Print a msg to a printer
    """
    printers = Printer.objects.filter(manager=True)
    if printers:
        printer = printers[0]
        if printer.print_msg(msg):
            messages.add_message(request, messages.SUCCESS,
                                 u"L'impression a été envoyée sur %s" %
                                 printer.name)
        else:
            messages.add_message(request, messages.ERROR,
                                 u"L'impression a échouée sur %s" %
                                 printer.name)
    else:
        messages.add_message(request, messages.ERROR,
                             u"Aucune imprimante type 'manager' disponible")


def get_value(context, key):
    """Get value or give a default one
    """
    if key in context:
        return "%s\n" % context[key]
    else:
        return "0.00\n"


def prepare_full_output(context):
    """Prepare full output
    """
    logger.debug(context)
    msg = """
Nb factures: """
    msg += get_value(context, 'nb_bills')
    msg += "Total TTC: "
    msg += get_value(context, 'total_ttc')
    for vat in context['vats']:
        msg += "TTC %s: %.2f\n" % (vat, vat.nb)
    msg += """
Restauration:
Nb couverts: """
    msg += get_value(context, 'guests_nb')
    msg += "Total TTC: "
    msg += get_value(context, 'guests_total_ttc')
    msg += "TM/couvert: "
    msg += get_value(context, 'guests_average')
    msg += """
Bar:
Nb factures: """
    msg += get_value(context, 'bar_nb')
    msg += "Total TTC: "
    msg += get_value(context, 'bar_total_ttc')
    msg += "TM/facture: "
    msg += get_value(context, 'bar_average')
    msg += "\n"
    for payment in context['payments']:
        msg += "%s: %.2f\n" % (payment, payment.nb)
    msg += "\n"
    for category in context['categories']:
        msg += "%s: %s\n" % (category.nom, category.nb)
    msg += "\n"
    for product in context['products']:
        msg += "%s: %s\n" % (product.nom, product.nb)
    msg += "\nFait le %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    return msg


def prepare_vats_output(context):
    """Prepare VATS output
    """
    msg = "Total TTC: "
    msg += get_value(context, 'total_ttc')
    for vat in context['vats']:
        msg += "TTC %s: %.2f\n" % (vat, vat.nb)
    return msg


def get_subject(request):
    """Get subject for email
    """
    week = request.POST.get('week')
    month = request.POST.get('month')
    year = request.POST.get('year')
    date = request.POST.get('date')
    if week:
        subject = "Rapport semaine %s/%s" % (week, year)
    elif month:
        subject = "Rapport mensuel %s/%s" % (month, year)
    else:
        subject = "Rapport du %s" % date.strftime("%d/%m/%Y")
    return subject


def check_for_outputs(request, context):
    """Check if user wants some outputs
    """
    if context and request.method == 'POST':
        if "full_mail" in request.POST:
            subject = get_subject(request)
            msg = prepare_full_output(context)
            send(request, subject, msg)
        if "full_print" in request.POST:
            msg = get_subject(request)
            msg += prepare_full_output(context)
            print_msg(request, msg)
        if "vats_mail" in request.POST:
            subject = get_subject(request)
            msg = prepare_vats_output(context)
            send(request, subject, msg)
        if "vats_print" in request.POST:
            msg = get_subject(request)
            msg += prepare_vats_output(context)
            print_msg(request, msg)


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
    check_for_outputs(request, context)
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
    check_for_outputs(request, context)
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
    check_for_outputs(request, context)
    return render(request, 'stats/home.html', context)


def month_name(*t):
    """ Sert à trier les mois."""
    names = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jui',
             7: 'Jui', 8: 'Aou', 9: 'Sep', 10: 'Oct', 11: 'Nov',
             12: 'Dec'}
    month_num = int(t[0][0])
    logger.debug("names[%d] > [%s]" % (month_num, names[month_num]))
    return (names[month_num],)


def month_sort(*x):
    """x example: ((('Fev',), ('2',)),)
    """
    return (int(x[0][1][0]),)


def get_datapool_year(year, keys):
    logger.debug(keys)
    series = []
    objects = Stat.objects.filter(interval="m", year=year)
    for key in keys.keys():
        series.append({'options': {
            'source': objects.filter(key=key),
            'categories': 'month'},
            'terms': {keys[key]: Avg('value')}
            })
    return PivotDataPool(
            series=series,
            sortf_mapf_mts=(month_sort, month_name, True))


def get_chart(datasource, graph, keys, title, xaxis):
    """
    graph: line / pie
    """
    terms = [keys[x] for x in keys.keys()]
    return PivotChart(
                datasource=datasource,
                series_options=[{
                    'options': {
                        'type': graph,
                        'stacking': False
                        },
                    'terms': terms
                    }],
                chart_options={
                    'title': {
                        'text': title},
                    'credits': {
                        'enabled': False
                        },
                    'xAxis': {
                        'title': {
                            'text': xaxis}},
                    'yAxis': {
                        'title': {
                            'text': ''}},
                    })


def get_chart_year_products(year, category):
    charts = []
    keys_nb = {}
    keys_value = {}
    for product in Produit.objects.filter(categorie=category).iterator():
        name = "%s #%s" % (product.nom, product.id)
        key = "%s_product_nb" % product.id
        keys_nb[key] = name
        key = "%s_product_value" % product.id
        keys_value[key] = name
    try:
        datasource = get_datapool_year(year, keys_nb)
    except:
        return False
    title = u"Nombre de vente pour la catégorie [%s] en %s" % (category.nom,
                                                               year)
    charts.append(get_chart(datasource, 'line', keys_nb, title, "Mois"))
    try:
        datasource = get_datapool_year(year, keys_value)
    except:
        return False
    title = u"Valeur des ventes pour la catégorie [%s] en %s" % (category.nom,
                                                                 year)
    charts.append(get_chart(datasource, 'line', keys_value, title, "Mois"))
    return charts


def select_charts(request, context, choice, year):
    """Select and construct graphics
    """
    charts = []
    if choice == 'ttc':
        chart = {'title': "Total TTC pour l'année %s" % year, }
        chart['keys'] = {"total_ttc": 'total ttc',
                         "guests_total_ttc": 'restauration',
                         "bar_total_ttc": 'bar'}
        charts.append(chart)
    elif choice == 'bar':
        chart = {'title': "Activité bar pour l'année %s" % year, }
        chart['keys'] = {"bar_average": 'TM/facture',
                         "bar_nb": 'nb factures'}
        charts.append(chart)
    elif choice == 'guests':
        chart = {'title': "Activité restaurant pour l'année %s" % year, }
        chart['keys'] = {"guests_average": 'TM/couvert',
                         "guests_nb": 'nb couverts'}
        charts.append(chart)
    elif choice == 'vats':
        chart = {'title': "TTC des TVA pour l'année %s" % year, }
        chart['keys'] = {}
        for vat in VAT.objects.iterator():
            key = "%s_vat" % vat.id
            chart['keys'][key] = "%s" % vat
        charts.append(chart)
    elif choice == 'payments':
        chart1 = {'title': "Nombre de paiements par type pour l'année %s" %
                  year, }
        chart1['keys'] = {}
        chart2 = {'title': "Valeur des paiements par type pour l'année %s" %
                  year, }
        chart2['keys'] = {}
        for payment in PaiementType.objects.iterator():
            key = "%s_payment_nb" % payment.id
            chart1['keys'][key] = payment.nom
            key = "%s_payment_value" % payment.id
            chart2['keys'][key] = payment.nom
        charts.append(chart1)
        charts.append(chart2)
    elif choice == 'categories':
        chart1 = {'title': "Nombre de vente par catégorie pour l'année %s" %
                  year, }
        chart1['keys'] = {}
        chart2 = {'title': "Valeur des ventes par catégorie pour l'année %s" %
                  year, }
        chart2['keys'] = {}
        for cat in Categorie.objects.iterator():
            key = "%s_category_nb" % cat.id
            chart1['keys'][key] = cat.nom
            key = "%s_category_value" % cat.id
            chart2['keys'][key] = cat.nom
        charts.append(chart1)
        charts.append(chart2)
    else:
        try:
            category = Categorie.objects.get(pk=choice)
        except:
            messages.add_message(request, messages.ERROR,
                                 "Ce type de graphique n'existe pas.")
        else:
            chart1 = {'title': u"Nombre de vente pour la catégorie [%s] en %s"
                      % (category.nom, year), }
            chart1['keys'] = {}
            chart2 = {'title': u"Valeur des ventes pour la catégorie [%s] en "
                      "%s" % (category.nom, year), }
            chart2['keys'] = {}
            for product in Produit.objects.filter(categorie=category):
                name = "%s #%s" % (product.nom, product.id)
                key = "%s_product_nb" % product.id
                chart1['keys'][key] = name
                key = "%s_product_value" % product.id
                chart2['keys'][key] = name
            charts.append(chart1)
            charts.append(chart2)
    # if one chart, it is in context['chart1'] = chart
    # else, if two charts: context['chart2'] = [chart1, chart2]
    key = 'chart%d' % len(charts)
    context[key] = []
    for chart in charts:
        try:
            datasource = get_datapool_year(year, chart['keys'])
        except:
            logger.warning("datasource error with %s" % chart['title'])
        else:
            context[key].append(get_chart(datasource, 'line',
                                                   chart['keys'],
                                                   chart['title'],
                                                   "Mois"))
    return context


@permission_required('base.p1')
def charts(request, choice='ttc'):
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
    context = select_charts(request, context, choice, year)
    context[choice] = True
    context['choice'] = choice
    context['year_form'] = YearForm({'year': year})
    context['year'] = year
    return render(request, 'stats/charts.html', context)
