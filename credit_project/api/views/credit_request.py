from django.db.models.query_utils import Q
from rest_framework import permissions, status
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet

from credit_project.loans.models import CreditRequest
from credit_project.loans.tasks import CreateOfferRequestsTask
from ..permissions import (
    CreateForPartnerOrSuperUser,
    DeleteForSuperUser,
    DetailForOwnerOrSuperUser,
    EditForOwnerOrSuperUser,
    EditForSuperUserOrCreditOrganizationUser,
    ListForCompanyOrSuperUser,
)
from ..serializers import CreditRequestSerializer
from ..utils import is_partner_user, is_credit_organization_user, is_owner


class CreditRequestPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        # Список для суперпользователей, партнеров и кредитных организаций
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_superuser or hasattr(request.user, 'company')
        # Создание для суперпольвазотелей и партнеров
        elif request.method == 'POST':
            return request.user.is_superuser or is_partner_user(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        # Детаальная информация только для суперпользоваателей и хозяев
        print(request.method, request.user)
        if request.method == 'GET':
            return request.user.is_superuser or is_owner(obj, request.user)
        # Редактирование для суперпользоваателей
        # и кредитных оргаанизаций к которым нааправленаа заявкаа
        elif request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser or
                (
                    is_owner(obj, request.user) and
                    is_credit_organization_user(request.user)
                )
            )
        # Удаление для суперпользоваателей
        elif request.method == 'DELETE':
            return request.user.is_superuser
        return False

class CreditRequestViewSet(ModelViewSet):
    permission_classes = (ListForCompanyOrSuperUser,
                          DetailForOwnerOrSuperUser,
                          CreateForPartnerOrSuperUser,
                          DeleteForSuperUser,
                          EditForOwnerOrSuperUser,
                          EditForSuperUserOrCreditOrganizationUser, )
    serializer_class = CreditRequestSerializer

    search_fields = ('borrower__last_name',
                     'borrower__first_name',
                     'borrower__middle_name',
                     'borrower__phone_number',
                     'borrower__passport_number',)
    filter_fields = ['status', 'offer', 'borrower']

    def get_queryset(self):
        queryset = CreditRequest.objects.all()

        if not self.request.user.is_superuser:

            q_objects = Q()
            if is_partner_user(self.request.user):
                q_objects |= Q(
                    borrower__company_id=self.request.user.company.id)
            if is_credit_organization_user(self.request.user):
                q_objects |= Q(
                    offer__company_id=self.request.user.company.id)

            if q_objects:
                queryset = queryset.filter(q_objects)
            else:
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        borrower = serializer.validated_data['borrower']
        offer = serializer.validated_data.get('offer', None)
        CreateOfferRequestsTask().delay(
            borrower_id=borrower.id,
            offer_id=offer.id if offer else None,
        )
