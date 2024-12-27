import json

from core.data.dao.permission_dao import PermissionDAO
from core.data.dao.planner.facorty_dao import FactoryDAO
from core.data.dao.planner.line_dao import LineDAO
from core.data.dao.role_dao import RoleDAO
from core.data.dao.router_access_dao import RouterAccessDAO
from core.data.models.it_tool_orm_models import UserModel, PermissionModel, RoleModel, RouterAccessModel, \
    AccessLogModel, \
    ApiCallLogModel, FactoryModel, LineModel, WorkDayAuditModel, WorkDayModel, StateModel, ReasonModel, WorkHoursModel, \
    PlatformModel, WorkPlanModel, OutputModel
from core.data.repositroy.user_repository import UserRepository
from core.data.schemas.user_schema import UserCreate
from core.db.ie_tool_db import IETOOLDBConnection
from core.logger_manager import LoggerManager

logger_db = LoggerManager.get_logger(name="DatabaseLogger", log_file="config/logs/db.log", username="SYSTEM")


def create_tables():
    IETOOLDBConnection().create_table(UserModel)
    IETOOLDBConnection().create_table(PermissionModel)
    IETOOLDBConnection().create_table(RoleModel)
    IETOOLDBConnection().create_table(RouterAccessModel)
    IETOOLDBConnection().create_table(AccessLogModel)
    IETOOLDBConnection().create_table(ApiCallLogModel)

    IETOOLDBConnection().create_table(FactoryModel)
    IETOOLDBConnection().create_table(LineModel)
    IETOOLDBConnection().create_table(WorkDayAuditModel)
    IETOOLDBConnection().create_table(WorkDayModel)
    IETOOLDBConnection().create_table(StateModel)
    IETOOLDBConnection().create_table(ReasonModel)
    IETOOLDBConnection().create_table(WorkHoursModel)
    IETOOLDBConnection().create_table(PlatformModel)
    IETOOLDBConnection().create_table(WorkPlanModel)
    IETOOLDBConnection().create_table(OutputModel)


def crete_default_permissions():
    # Create default permissions
    dao = PermissionDAO(IETOOLDBConnection().get_session(), logger_db)
    permission_names = ["admin", "read", "edit", "delete"]

    for permission_name in permission_names:
        dao.get_or_create_permission(permission_name)


def create_default_roles():
    # Create default roles
    dao = RoleDAO(IETOOLDBConnection().get_session(), logger_db)
    role_names = ["admin", "user", "editor", "guest", "config"]

    for role_name in role_names:
        dao.get_or_create_role(role_name)

    # Add permissions to roles
    dao.add_permission_to_role("admin", "admin")
    dao.add_permission_to_role("admin", "read")
    dao.add_permission_to_role("admin", "edit")
    dao.add_permission_to_role("admin", "delete")
    dao.add_permission_to_role("admin", "config")

    dao.add_permission_to_role("user", "read")
    dao.add_permission_to_role("user", "edit")

    dao.add_permission_to_role("editor", "read")
    dao.add_permission_to_role("editor", "edit")
    dao.add_permission_to_role("editor", "delete")
    dao.add_permission_to_role("editor", "config")

    dao.add_permission_to_role("guest", "read")

    logger_db.info("Default roles and permissions created")


def create_default_router_access():
    # Create default router access
    dao = RouterAccessDAO(IETOOLDBConnection().get_session(), logger_db)

    route_patterns = [
        "/api/v1/all",
        "/api/v1/user",
        "/api/v1/role",
        "/api/v1/permission",
        "/api/v1/router-access",
        "/api/v1/access-log",
        "/api/v1/api-call-log",
    ]

    for route_pattern in route_patterns:
        dao.get_or_create_router_access(route_pattern)

    logger_db.info("Default router access created")


def create_admin_user():
    # Create default user
    repo = UserRepository(IETOOLDBConnection().get_session(), logger_db)
    user_data = UserCreate(username="iradi", password="sky-licht", role_name="admin")
    repo.create_user(user_data)
    user_data = UserCreate(username="guest", password="dante", role_name="guest")
    repo.create_user(user_data)
    logger_db.info("Default user and guest created")

    repo.add_route_to_user("iradi", "/api/v1/all", "admin")
    repo.add_route_to_user("guest", "/api/v1/user", "admin")
    repo.add_route_to_user("guest", "/api/v1/role", "admin")
    repo.add_route_to_user("guest", "/api/v1/permission", "admin")
    repo.add_route_to_user("guest", "/api/v1/router-access", "admin")


def get_user_by_username(username: str) -> UserModel:
    repo = UserRepository(IETOOLDBConnection().get_session(), logger_db)
    return repo.get_user_by_username(username)


def create_privileges_from_json():
    try:
        # Open permissions.json file
        with open('config/permissions_dict.json') as f:
            permissions = json.load(f)

        # Open roles.json file
        with open('config/roles_dict.json') as f:
            roles = json.load(f)

        # Create default permissions

        dao = PermissionDAO(IETOOLDBConnection().get_session(), logger_db)

        dao.create_all([PermissionModel(id=permissions['id'], name=permission["name"]) for permission in permissions])

        # Create default roles
        dao = RoleDAO(IETOOLDBConnection().get_session(), logger_db)
        dao.create_all([RoleModel(id=role['id'], name=role["name"]) for role in roles])

        # Add permissions to roles
        dao.add_permission_to_role("admin", "admin")
        dao.add_permission_to_role("admin", "read")
        dao.add_permission_to_role("admin", "edit")
        dao.add_permission_to_role("admin", "delete")

        dao.add_permission_to_role("user", "read")
        dao.add_permission_to_role("user", "edit")

        dao.add_permission_to_role("editor", "read")
        dao.add_permission_to_role("editor", "edit")
        dao.add_permission_to_role("editor", "delete")

        dao.add_permission_to_role("guest", "read")


    except FileNotFoundError:
        logger_db.error("permissions.json file not found")
        return


def create_factories_form_json():
    try:
        # Open permissions.json file
        with open('config/data/dict/factories_dict.json') as f:
            factories = json.load(f)

        # Create default permissions

        dao = FactoryDAO(IETOOLDBConnection().get_session(), logger_db)

        dao.create_all([FactoryModel(id=factory['id'], name=factory["name"]) for factory in factories])

    except FileNotFoundError:
        logger_db.error("factories.json file not found")
        return


def create_lines_from_json():
    try:
        # Open permissions.json file
        with open('config/data/dict/lines_dict.json') as f:
            lines = json.load(f)

        # Create default permissions

        dao = LineDAO(IETOOLDBConnection().get_session(), logger_db)
        dao.create_one_by_one([LineModel(id=line['id'], name=line["name"], factory_id=line['factory_id']) for line in lines])

    except FileNotFoundError:
        logger_db.error("lines.json file not found")
        return
