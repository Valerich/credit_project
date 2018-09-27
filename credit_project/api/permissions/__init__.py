from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from ..utils import is_owner, is_partner_user, is_credit_organization_user


class ListForCompanyOrSuperUser(IsAuthenticated):

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        is_superuser_or_has_company = request.user.is_superuser or hasattr(request.user, 'company')
        return is_authenticated and is_superuser_or_has_company


class ListForPartnerOrSuperUser(IsAuthenticated):

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        is_superuser_or_partner = request.user.is_superuser or is_partner_user(request.user)
        return is_authenticated and is_superuser_or_partner


class ListForCreditOrganizationOrSuperUser(IsAuthenticated):

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        is_superuser_or_partner = request.user.is_superuser or is_partner_user(request.user)
        return is_authenticated and is_superuser_or_partner


class DetailForOwnerOrSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or is_owner(obj, request.user)


class DeleteForSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_superuser
        return True


class EditForSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH'] and not request.user.is_superuser:
            return False
        return True


class EditForOwnerOrSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser or
                is_owner(obj, request.user)
            )
        return True


class EditForSuperUserOrCreditOrganizationUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser or
                is_credit_organization_user(request.user)
            )
        return True


class CreateForPartnerOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_superuser or is_partner_user(request.user)
        return True


class CreateForCreditOrganizationOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_superuser or is_credit_organization_user(request.user)
        return True
