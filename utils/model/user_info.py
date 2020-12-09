from flask import g


def get_group():
    try:
        group_id = g.user.get('group').get('id')
        # print(group_id)
    except AttributeError:
        group_id = None
    return group_id


def get_group_name():
    try:
        group_id = g.user.get('group').get('name')
        # print(group_id)
    except AttributeError:
        group_id = None
    return group_id


def get_user():
    try:
        user_id = g.user.get('id')
        # print(user_id)
    except AttributeError:
        user_id = None
    return user_id


def get_user_name():
    try:
        user_id = g.user.get('name')
        # print(user_id)
    except AttributeError:
        user_id = None
    return user_id


def get_tenant():
    try:
        tenant_id = g.user.get('tenant_id')
    except AttributeError:
        tenant_id = None
    return tenant_id
