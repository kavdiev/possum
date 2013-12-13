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

from django.contrib import messages
from django.contrib.auth.models import User, UserManager, Permission
from django.http import HttpResponseRedirect
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from possum.base.views import get_user, permission_required


logger = logging.getLogger(__name__)


@login_required
def profile(request):
    data = get_user(request)
    data['menu_profile'] = True
    data['perms_list'] = settings.PERMS
    old = request.POST.get('old', '').strip()
    new1 = request.POST.get('new1', '').strip()
    new2 = request.POST.get('new2', '').strip()
    if old:
        if data['user'].check_password(old):
            if new1 and new1 == new2:
                data['user'].set_password(new1)
                data['user'].save()
                data['success'] = "Le mot de passe a été changé."
                logger.info('[%s] password changed' % data['user'].username)
            else:
                data['error'] = "Le nouveau mot de passe n'est pas valide."
                logger.warning('[%s] new password is not correct' %
                               data['user'].username)
        else:
            data['error'] = "Le mot de passe fourni n'est pas bon."
            logger.warning('[%s] check password failed' %
                           data['user'].username)
    return render_to_response('base/profile.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def users(request):
    data = get_user(request)
    data['perms_list'] = settings.PERMS
    data['menu_manager'] = True
    data['users'] = User.objects.all()
    for user in data['users']:
        user.permissions = [p.codename for p in user.user_permissions.all()]
    return render_to_response('base/manager/users.html', data,
                              context_instance=RequestContext(request))


@permission_required('base.p1')
def users_new(request):
    data = get_user(request)
    # data is here to create a new user ?
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    if login:
        user = User()
        user.username = login
        user.first_name = first_name
        user.last_name = last_name
        user.email = mail
        try:
            user.save()
            logger.info("[%s] new user [%s]" % (data['user'].username, login))
        except:
            logger.warning("[%s] new user failed: [%s] [%s] [%s] [%s]" % (
                           data['user'].username, login, first_name,
                           last_name, mail))
            messages.add_message(request, messages.ERROR, "Le nouveau compte "
                                 "n'a pu être créé.")
    return HttpResponseRedirect('/manager/users/')


@permission_required('base.p1')
def users_change(request, user_id):
    data = get_user(request)
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    user = get_object_or_404(User, pk=user_id)
    if login != user.username:
        logger.info("[%s] new login: [%s] > [%s]" % (
                    data['user'].username, user.username, login))
        user.username = login
    if first_name != user.first_name:
        logger.info("[%s] new first name for [%s]: [%s] > [%s]" % (
                    data['user'].username, user.username, user.first_name,
                    first_name))
        user.first_name = first_name
    if last_name != user.last_name:
        logger.info("[%s] new last name for [%s]: [%s] > [%s]" % (
                    data['user'].username, user.username, user.last_name,
                    last_name))
        user.last_name = last_name
    if mail != user.email:
        logger.info("[%s] new mail for [%s]: [%s] > [%s]" % (
                    data['user'].username, user.username, user.email, mail))
        user.email = mail

    try:
        user.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont"
                             " pu être enregistrées.")
        logger.warning("[%s] save failed for [%s]" % (data['user'].username,
                                                      user.username))
    return HttpResponseRedirect('/manager/users/')


@permission_required('base.p1')
def users_active(request, user_id):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    new = not user.is_active
    p1 = Permission.objects.get(codename="p1")
    if not new and \
            p1.user_set.count() == 1 and \
            p1 in user.user_permissions.all():
        messages.add_message(request, messages.ERROR, "Il doit rester au "
                             "moins un compte actif avec la permission P1.")
        logger.warning("[%s] we must have at least one active user "
                       "with P1 permission.")
    else:
        user.is_active = new
        user.save()
        logger.info("[%s] user [%s] active: %s" % (data['user'].username,
                                                   user.username,
                                                   user.is_active))
    return HttpResponseRedirect('/manager/users/')


@permission_required('base.p1')
def users_passwd(request, user_id):
    """Set a new random password for a user.
    """
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    passwd = UserManager().make_random_password(length=10)
    user.set_password(passwd)
    user.save()
    messages.add_message(request, messages.SUCCESS, "Le nouveau mot de passe "
                         "de l'utilisateur %s est : %s" % (user.username, 
                                                           passwd))
    logger.info("[%s] user [%s] new password" % (data['user'].username,
                                                 user.username))
    return HttpResponseRedirect('/manager/users/')


@permission_required('base.p1')
def users_change_perm(request, user_id, codename):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    # little test because because user can do ugly things :)
    # now we are sure that it is a good permission
    if codename in settings.PERMS:
        perm = Permission.objects.get(codename=codename)
        if perm in user.user_permissions.all():
            if codename == 'p1' and perm.user_set.count() == 1:
                # we must have at least one person with this permission
                logger.info("[%s] user [%s] perm [%s]: at least should have "
                            "one person" % (data['user'].username,
                                            user.username, 
                                            codename))
                messages.add_message(request, messages.ERROR,
                                     "Il doit rester au moins 1 compte avec "
                                     "la permission P1.")
            else:
                user.user_permissions.remove(perm)
                logger.info("[%s] user [%s] remove perm: %s" % (
                            data['user'].username,
                            user.username,
                            codename))
        else:
            user.user_permissions.add(perm)
            logger.info("[%s] user [%s] add perm: %s" % (
                        data['user'].username,
                        user.username,
                        codename))
    else:
        logger.warning("[%s] wrong perm info : [%s]" % (data['user'].username,
                                                        codename))
    return HttpResponseRedirect('/manager/users/')
