#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2014 University of Dundee.
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
#
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>, 2008.
#
# Version: 1.0
#

import logging

from django.conf import settings
from django import forms
from django.forms import ModelForm, Select
from django.forms.widgets import Textarea

from omeroweb.connector import Server
from omeroweb.custom_forms import NonASCIIForm

from omeroweb.webadmin.custom_forms import ServerModelChoiceField, GroupModelChoiceField
from omeroweb.webadmin.custom_forms import GroupModelMultipleChoiceField, OmeNameField
from omeroweb.webadmin.custom_forms import ExperimenterModelMultipleChoiceField, MultiEmailField
from omero_bookings.models import TrainingRequest, Microscope

logger = logging.getLogger(__name__)

class AccountRequestForm(NonASCIIForm):

    def __init__(self, name_check=False, email_check=False,
                 experimenter_is_me_or_system=False, *args, **kwargs):
        super(AccountRequestForm, self).__init__(*args, **kwargs)
        self.name_check = name_check
        self.email_check = email_check

        try:
            self.fields['other_groups'] = GroupModelMultipleChoiceField(
                queryset=kwargs['initial']['groups'],
                initial=kwargs['initial']['other_groups'], required=False,
                label="Groups")
        except:
            self.fields['other_groups'] = GroupModelMultipleChoiceField(
                queryset=kwargs['initial']['groups'], required=False,
                label="Groups")

        try:
            self.fields['default_group'] = GroupModelChoiceField(
                queryset=kwargs['initial']['my_groups'],
                initial=kwargs['initial']['default_group'],
                empty_label=u"", required=False)
        except:
            try:
                self.fields['default_group'] = GroupModelChoiceField(
                    queryset=kwargs['initial']['my_groups'],
                    empty_label=u"", required=False)
            except:
                self.fields['default_group'] = GroupModelChoiceField(
                    queryset=list(), empty_label=u"", required=False)

        if ('with_password' in kwargs['initial'] and
                kwargs['initial']['with_password']):
            self.fields['password'] = forms.CharField(
                max_length=50,
                widget=forms.PasswordInput(render_value=True,attrs={'size': 30,
                                                  'autocomplete': 'off'}))
            self.fields['confirmation'] = forms.CharField(
                max_length=50,
                widget=forms.PasswordInput(render_value=True,attrs={'size': 30,
                                                  'autocomplete': 'off'}))

            self.fields.keyOrder = [
                'omename', 'password', 'confirmation', 'first_name',
                'middle_name', 'last_name', 'email', 'institution',
                'administrator', 'active', 'default_group', 'other_groups']
        else:
            self.fields.keyOrder = [
                'omename', 'first_name', 'middle_name', 'last_name', 'email',
                'institution', 'administrator', 'active', 'default_group',
                'other_groups']
        if experimenter_is_me_or_system:
            self.fields['omename'].widget.attrs['readonly'] = True
            self.fields['omename'].widget.attrs['title'] = \
                "Changing of system username would be un-doable"
            self.fields['administrator'].widget.attrs['disabled'] = True
            self.fields['administrator'].widget.attrs['title'] = \
                "Removal of your own admin rights would be un-doable"
            self.fields['active'].widget.attrs['disabled'] = True
            self.fields['active'].widget.attrs['title'] = \
                "You cannot disable yourself"

    omename = OmeNameField(
        max_length=250,
        widget=forms.TextInput(attrs={'size': 30, 'autocomplete': 'off'}),
        label="Username")
    first_name = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={'size': 30, 'autocomplete': 'off'}))
    middle_name = forms.CharField(max_length=250, widget=forms.TextInput(
        attrs={'size': 30, 'autocomplete': 'off'}), required=False)
    last_name = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={'size': 30, 'autocomplete': 'off'}))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'size': 30, 'autocomplete': 'off'}),
        required=False)
    institution = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={'size': 30, 'autocomplete': 'off'}),
        required=False)
    administrator = forms.BooleanField(required=False)
    active = forms.BooleanField(required=False)

    def clean_confirmation(self):
        if (self.cleaned_data.get('password') or
                self.cleaned_data.get('confirmation')):
            if len(self.cleaned_data.get('password')) < 3:
                raise forms.ValidationError(
                    'Password must be at least 3 characters long.')
            if (self.cleaned_data.get('password') !=
                    self.cleaned_data.get('confirmation')):
                raise forms.ValidationError('Passwords do not match')
            else:
                return self.cleaned_data.get('password')

    def clean_omename(self):
        if self.name_check:
            raise forms.ValidationError('This username already exists.')
        return self.cleaned_data.get('omename')

    def clean_email(self):
        if self.email_check:
            raise forms.ValidationError('This email already exist.')
        return self.cleaned_data.get('email')

    def clean_default_group(self):
        if (self.cleaned_data.get('default_group') is None or
                len(self.cleaned_data.get('default_group')) <= 0):
            raise forms.ValidationError('No default group selected.')
        else:
            return self.cleaned_data.get('default_group')

    def clean_other_groups(self):
        if (self.cleaned_data.get('other_groups') is None or
                len(self.cleaned_data.get('other_groups')) <= 0):
            raise forms.ValidationError(
                'User must be a member of at least one group.')
        else:
            return self.cleaned_data.get('other_groups')
            
class TrainingRequestForm(forms.ModelForm):
    class Meta:
        model = TrainingRequest
        widgets = {
            'instrument': Select(),
        }

class MicroscopeForm(forms.ModelForm):
    class Meta:
        model = Microscope
        
class ChangePassword(NonASCIIForm):

    old_password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'size': 30, 'autocomplete': 'off'}),
        label="Current password")
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'size': 30, 'autocomplete': 'off'}),
        label="New password")
    confirmation = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'size': 30, 'autocomplete': 'off'}),
        label="Confirm password")

    def clean_confirmation(self):
        if (self.cleaned_data.get('password') or
                self.cleaned_data.get('confirmation')):
            if len(self.cleaned_data.get('password')) < 3:
                raise forms.ValidationError('Password must be at least 3'
                                            ' characters long.')
            if (self.cleaned_data.get('password') !=
                    self.cleaned_data.get('confirmation')):
                raise forms.ValidationError('Passwords do not match')
            else:
                return self.cleaned_data.get('password')

