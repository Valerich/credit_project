OWNER_FIELD_MAPPING = {
    'company': ['user', ],
    'borrower': ['company.user', ],
    'creditrequest': ['borrower.company.user',
                      'offer.company.user', ],
}

def is_owner(obj, user):
    model_name = obj._meta.model_name
    if model_name in OWNER_FIELD_MAPPING:
        owner_field_list = OWNER_FIELD_MAPPING[model_name]

        check_results = []
        for owner_firld in owner_field_list:
            check_obj = obj
            for field in owner_firld.split('.'):
                check_obj = getattr(check_obj, field)
            check_results.append(check_obj == user)

        return any(check_results)

    return False


def is_credit_organization_user(user):
    return hasattr(user, 'company') and user.company.is_credit_organization

def is_partner_user(user):
    return hasattr(user, 'company') and user.company.is_partner

