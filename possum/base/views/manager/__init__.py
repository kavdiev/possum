# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
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

from django.template.context import RequestContext

from django.shortcuts import render_to_response

from possum.base.views import permission_required, get_user


@permission_required('base.p1')
def credits(request):
    data = get_user(request)
    data['menu_manager'] = True
    return render_to_response('base/manager/credits.html',
                              data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def manager(request):
    data = get_user(request)
    data['menu_manager'] = True
    return render_to_response('base/manager/home.html',
                              data,
                              context_instance=RequestContext(request))
