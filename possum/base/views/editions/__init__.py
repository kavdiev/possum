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

import logging
from django.shortcuts import render, get_object_or_404, redirect
from possum.base.models import Facture
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@permission_required('base.p1')
def editions_home(request):
    context = {}
    context['bills'] = Facture.objects.exclude(in_use_by__isnull=True)
    return render(request, 'editions/home.html', context)


@permission_required('base.p1')
def editions_view(request, bill_id):
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.in_use_by = None
    bill.save()
    return redirect('editions_home')
