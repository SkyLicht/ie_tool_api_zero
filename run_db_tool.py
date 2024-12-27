import argparse

from core.db.features import create_tables, crete_default_permissions, create_default_roles, create_admin_user, \
    create_default_router_access, get_user_by_username, create_factories_form_json, create_lines_from_json

if __name__ == "__main__":

    args = [
        'create_tables',
        'pop_permissions',
        'pop_roles',
        'pop_admin_user',
        'pop_router_access',
        'pop_factories',
        'pop_lines'
    ]
    parser = argparse.ArgumentParser(description='Manage database')
    parser.add_argument(
        '--action',
        type=str,
        choices=args,
        help='...'
    )


    arg = parser.parse_args()


    if arg.action == 'create_tables':
        create_tables()
    elif arg.action == 'pop_permissions':
        crete_default_permissions()
    elif arg.action == 'pop_roles':
        create_default_roles()
    elif arg.action == 'pop_admin_user':
        create_admin_user()
    elif arg.action == 'pop_router_access':
        create_default_router_access()
    elif arg.action == 'pop_factories':
        create_factories_form_json()
    elif arg.action == 'pop_lines':
        create_lines_from_json()
    else:
        print("Unknown command 1")