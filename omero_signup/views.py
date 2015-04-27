#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2008-2014 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

''' A view functions is simply a Python function that takes a Web request and
returns a Web response. This response can be the HTML contents of a Web page,
or a redirect, or the 404 and 500 error, or an XML document, or an image...
or anything.'''

import copy
import os
import datetime
import Ice
import logging
import traceback
import json
import re

from django.conf import settings
from django.template import loader as template_loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from forms import AccountRequestForm,ChangePassword
from omeroweb.webclient.decorators import login_required
from omeroweb.webclient.decorators import render_response

from omero_signup import models

#import tree

logger = logging.getLogger(__name__)

logger.info("INIT '%s'" % os.getpid())

##############################################################################
# utils
def getSelectedGroups(conn, ids):
    if ids is not None and len(ids) > 0:
        return list(conn.getObjects("ExperimenterGroup", ids))
    return list()

def otherGroupsInitialList(groups, excluded_names=("user", "guest"),
                           excluded_ids=list()):
    formGroups = list()
    for gr in groups:
        flag = False
        if gr.name in excluded_names:
            flag = True
        if gr.id in excluded_ids:
            flag = True
        if not flag:
            formGroups.append(gr)
    formGroups.sort(key=lambda x: x.getName().lower())
    return formGroups

def checkExperimenter(conn, new_omename):

    experimenterList = list(conn.getObjects("Experimenter"))
    names = [e.omeName for e in experimenterList]
    if new_omename in names:
        return True
    else:
        return False


##############################################################################
# views control
@login_required(isAdmin=True)
@render_response()
def all_requests(request, conn=None, **kwargs):
    account_requests = models.Account.objects.all()
    context = {}
    context['requests'] = account_requests
    context['template'] = 'omero_signup/requests.html'
    return context

@login_required()
def create_request(request, action, conn=None, **kwargs):
    request.session.modified = True
    template = 'omero_signup/experimenter_form.html'
    error = None
    groups = list(conn.getObjects("ExperimenterGroup"))

    if action == "create":
        # this is what happens in webadmin
        # all i want to do is populate the account
        # this means checking that the fields are valid
        # and then instantiate the Account abject

        # note that email and name check are set here
        # pretty sure you need to be an admin to do this
        # all we are doing here is creating the account request
        # the actual account is generated when an admin is logged in
        my_groups = getSelectedGroups(
            conn,
            request.POST.getlist('other_groups'))
        initial = {'with_password': True,
                   'my_groups': my_groups,
                   'groups': otherGroupsInitialList(groups)}
        form = AccountRequestForm(
            initial=initial, data=request.REQUEST.copy())
        if form.is_valid():
            logger.debug("Create experimenter form:" +
                             str(form.cleaned_data))
            omename = form.cleaned_data['omename']
            first_name = form.cleaned_data['first_name']
            middle_name = form.cleaned_data['middle_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            institution = form.cleaned_data['institution']
            default_group = form.cleaned_data['default_group']
            other_groups = form.cleaned_data['other_groups']
            password = form.cleaned_data['password']

            new_account = models.Account()
            new_account.omename = omename
            new_account.first_name = first_name
            new_account.middle_name = middle_name
            new_account.last_name = last_name
            new_account.email = email
            new_account.password = password
            new_account.institution = institution
            new_account.default_group = default_group
            new_account.other_groups = json.dumps(other_groups)
            new_account.save()

            return HttpResponseRedirect("/omero_signup/requests")
    form = AccountRequestForm(initial={
        'with_password': True, 'active': False,
        'my_groups': [],
        'groups': otherGroupsInitialList(groups)})
    context = {}
    context['conn'] = conn
    context['form'] = form
    context['groups'] = []
    return render(request,template,context)

@login_required(isAdmin=True)
@render_response()
def manage_requests(request, action, account_id, conn=None, **kwargs):
    request.session.modified = True
    context = {}
    context['template'] = 'omero_signup/experimenter_form.html'
    error = None
    groups = list(conn.getObjects("ExperimenterGroup"))

    if action == "new":
        form = AccountRequestForm(initial={
            'with_password': True, 'active': False,
            'my_groups': [],
            'groups': otherGroupsInitialList(groups)})

        context['conn'] = conn
        context['form'] = form
        context['groups'] = []

    elif action == "inspect":

        groups = list(conn.getObjects("ExperimenterGroup"))
        account = get_object_or_404(models.Account, pk=account_id)
        experimenter_exists = checkExperimenter(conn, account.omename)  
        my_groups = getSelectedGroups(conn,[int(g) for g in json.loads(account.other_groups)])
        other_groups_ids = json.loads(account.other_groups)
        print account.password
        initial = {
            'omename': account.omename,
            'first_name': account.first_name,
            'middle_name': account.middle_name,
            'last_name': account.last_name,
            'email': account.email,
            'institution': account.institution,
            #'administrator': account.isAdmin(),
            'active': True,
            'default_group': account.default_group,
            'my_groups': my_groups,
            'other_groups': [g for g in json.loads(account.other_groups)],
            'groups': otherGroupsInitialList(groups)}
        form = AccountRequestForm(initial=initial)
        password_form = ChangePassword()
        context['conn'] = conn
        context['account_id'] = account_id
        context['form'] = form
        context['password_form'] = password_form
        context['groups'] = groups
        context['new_experimenter'] = experimenter_exists

    elif action == "validate":
        # now validate the account --> create a new omero account!
        account = get_object_or_404(models.Account, pk=account_id)
        name_check = conn.checkOmeName(request.REQUEST.get('omename'))
        email_check = conn.checkEmail(request.REQUEST.get('email'))
        my_groups = getSelectedGroups(
            conn,
            request.POST.getlist('other_groups'))
        initial = {'my_groups': my_groups,
                   'groups': otherGroupsInitialList(groups)}
        form = AccountRequestForm(initial=initial, data=request.REQUEST.copy(),
                                name_check=name_check,
                                email_check=email_check)
        print form.is_valid()
        if form.is_valid():
            logger.debug("Create experimenter form:" +
                         str(form.cleaned_data))
            omename = form.cleaned_data['omename']
            firstName = form.cleaned_data['first_name']
            middleName = form.cleaned_data['middle_name']
            lastName = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            institution = form.cleaned_data['institution']
            admin = form.cleaned_data['administrator']
            active = form.cleaned_data['active']
            defaultGroup = form.cleaned_data['default_group']
            otherGroups = form.cleaned_data['other_groups']
            password = account.password

            # default group
            # if default group was not selected take first from the list.
            if defaultGroup is None:
                defaultGroup = otherGroups[0]
            for g in groups:
                if long(defaultGroup) == g.id:
                    dGroup = g
                    break

            listOfOtherGroups = set()
            # rest of groups
            for g in groups:
                for og in otherGroups:
                    # remove defaultGroup from otherGroups if contains
                    if long(og) == long(dGroup.id):
                        pass
                    elif long(og) == g.id:
                        listOfOtherGroups.add(g)

            conn.createExperimenter(
                omename, firstName, lastName, email, admin, active,
                dGroup, listOfOtherGroups, password, middleName,
                institution)
            account.delete()
            context['template'] = "/webadmin/experimenters"
            return context
    return context

@login_required(isAdmin=True)
def manage_password(request, account_id, conn=None, **kwargs):
    template = "omero_signup/password.html"

    error = None
    if request.method == 'POST':
        password_form = ChangePassword(data=request.POST.copy())
        if not password_form.is_valid():
            error = password_form.errors
        else:
            old_password = password_form.cleaned_data['old_password']
            password = password_form.cleaned_data['password']
            if conn.isAdmin():
                account = get_object_or_404(models.Account, pk=account_id)
                account.password = password
                account.save()

    context = {'error': error, 'password_form': password_form, 'account_id': account_id}
    context['template'] = template
    return context

@login_required(isAdmin=True)
def delete_request(request, account_id, conn=None, **kwargs):
    print account_id
    account = get_object_or_404(models.Account, pk=account_id)
    if request.method == 'POST':
        account.delete()
        return HttpResponseRedirect('/omero_signup/requests')
    else:
        template = 'omero_signup/delete_request.html'
    return render(request, template, {})

def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))


