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
from django.contrib.auth.models import User, UserManager, Permission
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from possum.base.views import permission_required


logger = logging.getLogger(__name__)


@login_required
def profile(request):
    context = {'menu_profile': True, }
    context['perms_list'] = settings.PERMS
    old = request.POST.get('old', '').strip()
    new1 = request.POST.get('new1', '').strip()
    new2 = request.POST.get('new2', '').strip()
    if old:
        if context['user'].check_password(old):
            if new1 and new1 == new2:
                context['user'].set_password(new1)
                context['user'].save()
                context['success'] = "Le mot de passe a été changé."
                logger.info('[%s] password changed' % context['user'].username)
            else:
                context['error'] = "Le nouveau mot de passe n'est pas valide."
                logger.warning('[%s] new password is not correct' %
                               context['user'].username)
        else:
            context['error'] = "Le mot de passe fourni n'est pas bon."
            logger.warning('[%s] check password failed' %
                           context['user'].username)
    return render(request, 'base/profile.html', context)


@permission_required('base.p1')
def users(request):
    context = {'menu_manager': True, }
    context['perms_list'] = settings.PERMS
    context['users'] = User.objects.all()
    for user in context['users']:
        user.permissions = [p.codename for p in user.user_permissions.all()]
    return render(request, 'base/manager/users.html', context)


@permission_required('base.p1')
def users_new(request):
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
            logger.info("[%s] new user [%s]" % (request.user.username, login))
        except:
            logger.warning("[%s] new user failed: [%s] [%s] [%s] [%s]" % (
                           request.user.username, login, first_name,
                           last_name, mail))
            messages.add_message(request, messages.ERROR, "Le nouveau compte "
                                 "n'a pu être créé.")
    return redirect('users')


@permission_required('base.p1')
def users_change(request, user_id):
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    user = get_object_or_404(User, pk=user_id)
    if login != user.username:
        logger.info("[%s] new login: [%s] > [%s]" % (
                    request.user.username, user.username, login))
        user.username = login
    if first_name != user.first_name:
        logger.info("[%s] new first name for [%s]: [%s] > [%s]" % (
                    request.user.username, user.username, user.first_name,
                    first_name))
        user.first_name = first_name
    if last_name != user.last_name:
        logger.info("[%s] new last name for [%s]: [%s] > [%s]" % (
                    request.user.username, user.username, user.last_name,
                    last_name))
        user.last_name = last_name
    if mail != user.email:
        logger.info("[%s] new mail for [%s]: [%s] > [%s]" % (
                    request.user.username, user.username, user.email, mail))
        user.email = mail

    try:
        user.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont"
                             " pu être enregistrées.")
        logger.warning("[%s] save failed for [%s]" % (request.user.username,
                                                      user.username))
    return redirect('users')


@permission_required('base.p1')
def users_active(request, user_id):
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
        logger.info("[%s] user [%s] active: %s" % (request.user.username,
                                                   user.username,
                                                   user.is_active))
    return redirect('users')


@permission_required('base.p1')
def users_passwd(request, user_id):
    """Set a new random password for a user.
    """
    user = get_object_or_404(User, pk=user_id)
    passwd = UserManager().make_random_password(length=10)
    user.set_password(passwd)
    user.save()
    messages.add_message(request, messages.SUCCESS, "Le nouveau mot de passe "
                         "est : %s" % passwd)
    logger.info("[%s] user [%s] new password" % (request.user.username,
                                                 user.username))
    return redirect('users')


@permission_required('base.p1')
def users_change_perm(request, user_id, codename):
    user = get_object_or_404(User, pk=user_id)
    # little test because because user can do ugly things :)
    # now we are sure that it is a good permission
    if codename in settings.PERMS:
        perm = Permission.objects.get(codename=codename)
        if perm in user.user_permissions.all():
            if codename == 'p1' and perm.user_set.count() == 1:
                # we must have at least one person with this permission
                logger.info("[%s] user [%s] perm [%s]: at least should have "
                            "one person" % (request.user.username,
                                            user.username, 
                                            codename))
                messages.add_message(request, messages.ERROR,
                                     "Il doit rester au moins 1 compte avec "
                                     "la permission P1.")
            else:
                user.user_permissions.remove(perm)
                logger.info("[%s] user [%s] remove perm: %s" % (
                            request.user.username,
                            user.username,
                            codename))
        else:
            user.user_permissions.add(perm)
            logger.info("[%s] user [%s] add perm: %s" % (
                        request.user.username,
                        user.username,
                        codename))
    else:
        logger.warning("[%s] wrong perm info: [%s]" % (request.user.username,
                                                        codename))
    return redirect('users')
