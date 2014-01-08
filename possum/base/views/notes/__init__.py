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
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from possum.base.models import Note
from possum.base.views import get_user, permission_required
from possum.base.forms import NoteForm


logger = logging.getLogger(__name__)


def get_notes(request):
    data = get_user(request)
    data['menu_manager'] = True
    data['notes'] = Note.objects.all()
    return data


@permission_required('base.p1')
def home(request):
    data = get_notes(request)
#    return render_to_response('notes/home.html', data,
#                              context_instance=RequestContext(request))
    return render(request, 'notes/home.html', data)


@permission_required('base.p1')
def delete(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    note.delete()
    return redirect('notes_home')


@permission_required('base.p1')
def view(request, note_id=None):
    data = get_notes(request)
    if request.method == 'POST':
        if note_id:
            # note already exist
            note = get_object_or_404(Note, pk=note_id)
            data['note'] = NoteForm(request.POST, instance=note)
        else:
            # new note
            data['note'] = NoteForm(request.POST)
        if data['note'].is_valid():
            data['note'].save()
    else:
        if note_id:
            # note already exist
            note = get_object_or_404(Note, pk=note_id)
            data['note'] = NoteForm(instance=note)
        else:
            # new note
            data['note'] = NoteForm()
    return render_to_response('notes/home.html', data,
                              context_instance=RequestContext(request))

