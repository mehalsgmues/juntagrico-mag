# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.db.models.query import Q

from juntagrico.models import Member


class AssignmentRequestDao:

    @staticmethod
    def all_approvers():
        perm = Permission.objects.get(codename='can_confirm_assignments')
        return Member.objects.filter(Q(user__groups__permissions=perm) |
                                     Q(user__user_permissions=perm)).distinct()

    @staticmethod
    def all_notified_on_unapproved_assignments():
        perm = Permission.objects.get(codename='notified_on_unapproved_assignments')
        return Member.objects.filter(Q(user__groups__permissions=perm) |
                                     Q(user__user_permissions=perm)).distinct()

