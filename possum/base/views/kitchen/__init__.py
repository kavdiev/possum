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
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from possum.base.models import Facture
from possum.base.models import Follow


logger = logging.getLogger(__name__)


@login_required
def kitchen(request):
    """Affiche la liste plats qui ne sont pas encore
    préparés
    """
    context = { 'menu_kitchen': true, }
    liste = []
    for bill in Facture().non_soldees():
        if bill.following.count():
            bill.follow = bill.following.latest()
            if not bill.follow.done:
                if bill.category_to_follow:
                    category_to_follow = bill.category_to_follow
                    after = bill.get_products_for_category(category_to_follow)
                    bill.after = bill.reduce_sold_list(after)
                liste.append(bill)
    context['factures'] = liste
    context['need_auto_refresh'] = 60
    return render(request, 'kitchen/home.html', context)


@login_required
def follow_done(request, follow_id):
    """All is ready for this table ?
    """
    follow = get_object_or_404(Follow, pk=follow_id)
    follow.done = True
    follow.save()
    return redirect('kitchen')


@login_required
def kitchen_for_bill(request, bill_id):
    context = { 'menu_kitchen': true, }
    context['facture'] = get_object_or_404(Facture, pk=bill_id)
    if context['facture'].est_soldee():
        messages.add_message(request,
                             messages.ERROR,
                             "Cette facture a déjà été soldée.")
        return redirect('kitchen')
    return render(request, 'kitchen/view.html', context)
