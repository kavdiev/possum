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

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from possum.base.models import Facture, Note, Option
from datetime import datetime

if Facture.objects.count():
    first_year = int(Facture.objects.all()[0].date_creation.year)
    last_year = int(Facture.objects.latest().date_creation.year) + 1
else:
    first_year = int(datetime.now().year)
    last_year = first_year + 1

weeks_choice = [(unicode(i), i) for i in range(54)]
months_choice = [(unicode(i), i) for i in range(1, 13)]
years_choice = [(unicode(i), i) for i in range(first_year, last_year)]
years_list = [i for i in range(first_year, last_year)]


class DateForm(forms.Form):
    date = forms.DateField(widget=SelectDateWidget(years=years_list))


class WeekForm(forms.Form):
    week = forms.ChoiceField(label="Semaine", choices=weeks_choice)
    year = forms.ChoiceField(label="Année", choices=years_choice)


class MonthForm(forms.Form):
    month = forms.ChoiceField(label="Mois", choices=months_choice)
    year = forms.ChoiceField(label="Année", choices=years_choice)


class YearForm(forms.Form):
    year = forms.ChoiceField(label="Année", choices=years_choice)


class LoginForm(forms.Form):
    """ Class LoginForm representing a form to log an User in. """
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(
                               attrs={'placeholder': 'identifiant:'}))
    password = forms.CharField(widget=forms.PasswordInput(
                               attrs={'placeholder': 'mot de passe:'}))


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
