from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, Table, Boolean, DateTime, Index, Integer, Text, Float, \
    CheckConstraint, UniqueConstraint, func, JSON, DefaultClause
from sqlalchemy.orm import relationship

from core.auth.auth_utils import generate_custom_id
from core.db.ie_tool_db import Base

api_role_permissions = Table(
    "api_role_permissions",
    Base.metadata,
    Column("role_id", String(18), ForeignKey("api_roles.id"), primary_key=True),
    Column("permission_id", String(18), ForeignKey("api_permissions.id"), primary_key=True),
)


# api_user_route_role = Table(
#     "api_user_route_role",
#     Base.metadata,
#     Column("user_id", String(16), ForeignKey("api_users.id", ondelete="CASCADE"), primary_key=True),
#     Column("route_id", String(16), ForeignKey("api_router_access.id", ondelete="CASCADE"), primary_key=True),
#     Column("role_id", String(16), ForeignKey("api_roles.id", ondelete="CASCADE"), primary_key=True),
# )


class PermissionModel(Base):
    __tablename__ = "api_permissions"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String(50), unique=True, nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationship back to Role
    roles = relationship("RoleModel", secondary=api_role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<PermissionModel(name={self.name})>"


class RoleModel(Base):
    __tablename__ = "api_roles"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String(50), unique=True, nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationship to Permission (many-to-many)
    permissions = relationship("PermissionModel", secondary=api_role_permissions, back_populates="roles")
    # Many-to-many to PermissionModel (as you already have),
    # plus pivot relationship to user-route
    user_route_roles = relationship("UserRouteRoleModel", back_populates="role")

    def __repr__(self):
        return f"<RoleModel(name={self.name})>"


class UserModel(Base):
    __tablename__ = "api_users"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_suspended = Column(Boolean, default=False, nullable=False)  # Field to suspend users
    suspension_reason = Column(String(255), nullable=True)  # Reason for suspension
    suspension_end_time = Column(DateTime, nullable=True)  # End time for suspension
    api_call_limit = Column(Integer, default=10000, nullable=False)  # Maximum API calls allowed
    api_calls_made = Column(Integer, default=0, nullable=False)  # API calls made in the current period
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationship to UserRouteRole
    # user_routes = relationship("RouterAccessModel", secondary=api_user_route_role, back_populates="users")
    user_route_roles = relationship("UserRouteRoleModel", back_populates="user")
    # Index for performance
    __table_args__ = (
        Index("ix_api_users_username", "username", unique=True),  # Ensures unique index
    )

    def to_dict(self):
        return {
            "username": self.username,
            "is_suspended": self.is_suspended,
            "suspension_reason": self.suspension_reason,
            "api_calls_made": self.api_calls_made,
            "api_call_limit": self.api_call_limit,
            "user_routes": self._get_routes_with_roles(),
        }

    def _get_routes_with_roles(self):
        """
        Return a list of route dicts, each containing
        the role info (including permissions).
        """
        routes = []
        for user_route_role in self.user_route_roles:
            route_obj = user_route_role.route  # RouterAccessModel instance
            role_obj = user_route_role.role  # RoleModel instance

            # Build a dict for the route
            route_data = route_obj.to_dict()

            # Add the role info
            route_data["role"] = {
                "id": role_obj.id,
                "name": role_obj.name,
                "permissions": [perm.name for perm in role_obj.permissions]
            }

            routes.append(route_data)

        return routes

    def __repr__(self):
        return f"<UserModel(username={self.username}, is_suspended={self.is_suspended}, suspension_reason={self.suspension_reason}, api_calls_made={self.api_calls_made}, api_call_limit={self.api_call_limit})>"


class RouterAccessModel(Base):
    __tablename__ = "api_router_access"
    id = Column(String(16), primary_key=True, default=generate_custom_id)
    type = Column(String(50), nullable=False, default="api")
    route_pattern = Column(String, unique=True, nullable=False)
    allowed_ips = Column(Text, nullable=False, default="*")  # List of allowed IPs, "*" means all IPs allowed

    # Relationship to UserRouteRole
    # users = relationship("UserModel", secondary=api_user_route_role, back_populates="user_routes")
    user_route_roles = relationship("UserRouteRoleModel", back_populates="route")

    # Index for route pattern
    __table_args__ = (
        CheckConstraint("type IN ('api', 'second', 'webapp')", name='valid_type'),
        Index("ix_api_router_access_route_pattern", "route_pattern"),
    )

    def to_dict(self):
        return {
            "route_pattern": self.route_pattern,
            "allowed_ips": self.allowed_ips,
        }

    def __repr__(self):
        return f"<RouterAccessModel(route_pattern={self.route_pattern}, allowed_ips={self.allowed_ips})>"


class AccessLogModel(Base):
    __tablename__ = "api_access_logs"
    id = Column(String(16), primary_key=True, default=generate_custom_id)
    user_id = Column(String(16), ForeignKey("api_users.id", ondelete="CASCADE"))
    route = Column(String, nullable=False)
    ipaddress = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationship to User
    user = relationship("UserModel")

    def __repr__(self):
        return f"<AccessLogModel(route={self.route}, user_id={self.user_id}, success={self.success})>"


class ApiCallLogModel(Base):
    __tablename__ = "api_api_call_logs"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    user_id = Column(String(16), ForeignKey("api_users.id", ondelete="CASCADE"), nullable=False)
    route_access_id = Column(String(16), ForeignKey("api_router_access.id", ondelete="CASCADE"), nullable=False)
    request_method = Column(String(10), nullable=False)  # GET, POST, etc.
    request_data = Column(Text, nullable=True)  # Payload or query string
    response_status = Column(Integer, nullable=False)  # HTTP status code
    response_data = Column(Text, nullable=True)  # Response payload
    ipaddress = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    error_message = Column(Text, nullable=True)  # To store any error details
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationships
    user = relationship("UserModel")
    route_access = relationship("RouterAccessModel")

    # Index for performance
    __table_args__ = (
        Index("ix_api_api_call_logs_user_id", "user_id"),
        Index("ix_api_api_call_logs_timestamp", "timestamp"),
        Index("ix_api_api_call_logs_user_id_timestamp", "user_id", "timestamp"),
    )

    def __repr__(self):
        return f"<ApiCallLogModel(user_id={self.user_id}, route_access_id={self.route_access_id}, request_method={self.request_method}, response_status={self.response_status}, error_message={self.error_message})>"


class UserRouteRoleModel(Base):
    __tablename__ = 'api_user_route_role'

    user_id = Column(String(16), ForeignKey("api_users.id", ondelete="CASCADE"), primary_key=True)
    route_id = Column(String(16), ForeignKey("api_router_access.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(16), ForeignKey("api_roles.id", ondelete="CASCADE"), primary_key=True)

    # Bi-directional relationship to the main models
    user = relationship("UserModel", back_populates="user_route_roles")
    route = relationship("RouterAccessModel", back_populates="user_route_roles")
    role = relationship("RoleModel", back_populates="user_route_roles")

    def __repr__(self):
        return f"<UserRouteRoleModel(user_id={self.user_id}, route_id={self.route_id}, role_id={self.role_id})>"


# Planner ORM Models


class FactoryModel(Base):
    """
    A factory or manufacturing facility where production lines are located.
    """
    __tablename__ = 'planner_factory'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String, unique=True, nullable=False)

    # Potential concurrency or auditing field
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Example relationship if you want to link Factories to WorkDays:
    # work_days = relationship("PlannerWorkDay", back_populates="factory")

    def __repr__(self):
        return f"<PlannerFactory(name={self.name})>"


class LineModel(Base):
    __tablename__ = 'planner_lines'

    id = Column(String(16), primary_key=True, default=generate_custom_id, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    factory_id = Column(String(16), ForeignKey('planner_factory.id'), nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    # Relationship to Factory
    factory = relationship("FactoryModel")

    def __repr__(self):
        return f"<LineModel(name={self.name}, factory_id={self.factory_id})>"


class WorkDayAuditModel(Base):
    """
    Audit table to record changes made to the PlannerWorkDay table.
    """
    __tablename__ = 'planner_work_day_audit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation = Column(String(10), nullable=False)  # e.g., CREATE, UPDATE, DELETE
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    user_id = Column(String(16), nullable=False)  # User performing the action
    work_day_id = Column(String(16), nullable=False)  # ID of the related workday
    data = Column(Text, nullable=False)  # Serialized data representing the record's state

    def __repr__(self):
        return (
            f"<WorkDayAudit(operation={self.operation}, timestamp={self.timestamp}, "
            f"user_id={self.user_id}, work_day_id={self.work_day_id})>"
        )


class WorkDayModel(Base):
    """
    Represents a single day of work for a specific factory and production line.
    """
    __tablename__ = 'planner_work_day'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    str_date = Column(String(10), nullable=False)
    week = Column(Integer, nullable=False)
    line_id = Column(String(16), ForeignKey('planner_lines.id'), nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Unique constraint to avoid duplicates on the same day/line/factory
    __table_args__ = (
        UniqueConstraint('str_date', 'line_id', name='uq_planner_workday_date_factory_line'),
    )

    # Relationships
    line = relationship("LineModel")

    work_plans = relationship("WorkPlanModel", back_populates="work_day")
    hours = relationship("WorkHoursModel", back_populates="work_day")
    outputs = relationship("OutputModel", back_populates="work_day", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<PlannerWorkDay(date={self.date}, week={self.week}, "
            f"line={self.line})>"
        )


class StateModel(Base):
    """
    Represents the operational state of a line or machine. E.g., RUN, STOPPED, MAINTENANCE.
    """
    __tablename__ = 'planner_state'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<PlannerState(name={self.name})>"


class ReasonModel(Base):
    """
    Represents the reason for a particular state or downtime, e.g., Maintenance, Operator Break.
    """
    __tablename__ = 'planner_reason'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    description = Column(String, unique=True, nullable=False)
    rich_text = Column(Text, nullable=True)  # New field for additional rich text description

    def __repr__(self):
        return f"<PlannerReason(description={self.description})>"


class WorkHoursModel(Base):
    """
    Captures hour-by-hour status for a given work day.
    """
    __tablename__ = 'planner_work_hours'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    work_day_id = Column(Integer, ForeignKey('planner_work_day.id'), nullable=False)
    hour = Column(Integer, nullable=False)
    area = Column(String, nullable=False)
    state_id = Column(String(16), ForeignKey('planner_state.id'), nullable=False)
    reason_id = Column(String(16), ForeignKey('planner_reason.id'), nullable=True)

    __table_args__ = (
        CheckConstraint('hour >= 0 AND hour < 24', name='check_planner_workhours_hour_range'),
    )

    # Potential concurrency or auditing field
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    work_day = relationship("WorkDayModel", back_populates="hours")
    state = relationship("StateModel")
    reason = relationship("ReasonModel")

    def __repr__(self):
        return (
            f"<PlannerWorkHours(work_day_id={self.work_day_id}, hour={self.hour}, "
            f"area={self.area}, state_id={self.state_id}, reason_id={self.reason_id})>"
        )


class PlatformModel(Base):
    """
    Represents a product platform or model, including SKU, cost, and UPH.
    """
    __tablename__ = 'planner_platform'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    f_n = Column(Integer, nullable=False)
    platform = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    uph = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    in_service = Column(Boolean, nullable=False, default=True)
    components = Column(Integer, nullable=False)
    components_list_id = Column(String, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)

    # factory_id = Column(String(16), ForeignKey('planner_factory.id'), nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    __table_args__ = (
        Index('idx_planner_platform_cost_in_service', 'cost', 'in_service'),
    )

    work_plans = relationship("WorkPlanModel", back_populates="platform")

    def __repr__(self):
        return (
            f"<PlannerPlatform(id={self.id}, f_n={self.f_n}, platform={self.platform}, sku={self.sku}, "
            f"uph={self.uph}, cost={self.cost}, in_service={self.in_service})>"
        )


class WorkPlanModel(Base):
    """
    Represents a plan for a particular day, line, and platform combination:
    - The shift hours planned
    - The target OEE
    - The estimated or planned UPH
    """
    __tablename__ = 'planner_work_plan'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    work_day_id = Column(String(16), ForeignKey('planner_work_day.id'), nullable=False)
    platform_id = Column(String(16), ForeignKey('planner_platform.id'), nullable=False)
    line_id = Column(String(16), ForeignKey('planner_lines.id'), nullable=False)
    planned_hours = Column(Float, nullable=False)
    target_oee = Column(Float, nullable=False)
    uph_i = Column(Integer, nullable=False)
    start_hour = Column(Integer, nullable=False)
    end_hour = Column(Integer, nullable=False)
    str_date = Column(String(10), nullable=False)
    week = Column(Integer, nullable=False)
    head_count = Column(Integer, nullable=False)
    ft = Column(Integer, nullable=False)
    ict = Column(Integer, nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    __table_args__ = (
        CheckConstraint('start_hour >= 0 AND start_hour < 24', name='check_planner_workplan_start_hour'),
        CheckConstraint('end_hour > start_hour AND end_hour <= 24', name='check_planner_workplan_end_hour'),
        # target_oee must be between 0.1 and 1 (10% to 100%), planned_hours must be greater than 0
        CheckConstraint('target_oee >= 0.1 AND target_oee <= 1.0', name='check_planner_workplan_target_oee'),
        CheckConstraint('planned_hours > 0', name='check_planner_workplan_planned_hours'),
        Index('idx_planner_work_plan_line_date', 'line_id', 'str_date'),
    )

    line = relationship("LineModel")
    work_day = relationship("WorkDayModel", back_populates="work_plans")
    platform = relationship("PlatformModel", back_populates="work_plans")

    def __repr__(self):
        return (
            f"<PlannerWorkPlan(work_day_id={self.work_day_id}, platform_id={self.platform_id}, "
            f"line={self.line}, planned_hours={self.planned_hours}, "
            f"target_oee={self.target_oee}, uph_i={self.uph_i}, "
            f"start_hour={self.start_hour}, end_hour={self.end_hour}, week={self.week})>"
        )


class OutputModel(Base):
    """
    Represents the actual production output for a given work day and possibly line.
    """
    __tablename__ = 'planner_output'

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    work_day_id = Column(String(16), ForeignKey('planner_work_day.id'), nullable=False)
    smt_out = Column(Integer, nullable=False, default=0)
    packing = Column(Integer, nullable=False, default=0)
    shipping = Column(Integer, nullable=False, default=0)
    smt_out_scrap = Column(Integer, nullable=False, default=0)
    packing_scrap = Column(Integer, nullable=False, default=0)
    smt_out_availability = Column(Float, nullable=True)
    packing_availability = Column(Float, nullable=True)
    oee_achieved = Column(Float, nullable=True)

    work_day = relationship("WorkDayModel", back_populates="outputs")

    def __repr__(self):
        return (
            f"<PlannerOutput(work_day_id={self.work_day_id}, produced_units={self.packing}, "
            f"total_scrap={self.packing_scrap}, oee_achieved={self.oee_achieved})>"
        )


# Layout ORM Model


#
#  A R E A
#
class AreaModel(Base):
    __tablename__ = "layout_areas"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    index = Column(Integer)
    name = Column(String, nullable=False)
    section = Column(String)

    stations = relationship("StationModel", back_populates="area")

    def __repr__(self):
        return f"<Area(id={self.id}, name={self.name})>"


#
#  O P E R A T I O N
#
class OperationModel(Base):
    __tablename__ = "layout_operations"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    label = Column(String)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_automatic = Column(Boolean, default=False)

    stations = relationship("StationModel", back_populates="operation")

    def __repr__(self):
        return f"<Operation(id={self.id}, name={self.name})>"


#
#  C L U S T E R   T Y P E
#
class ClusterTypeModel(Base):
    __tablename__ = "layout_cluster_types"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String, nullable=False)

    station_clusters = relationship("StationClusterModel", back_populates="cluster_type")

    def __repr__(self):
        return f"<ClusterType(id={self.id}, name={self.name})>"


#
#  S T A T I O N   C L U S T E R
#
class StationClusterModel(Base):
    __tablename__ = "layout_station_clusters"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String, nullable=False)

    cluster_type_id = Column(
        String(16),
        ForeignKey("layout_cluster_types.id", ondelete="SET NULL"),
        nullable=True
    )

    cluster_type = relationship("ClusterTypeModel", back_populates="station_clusters")

    stations = relationship("StationModel", back_populates="station_cluster")

    def __repr__(self):
        return f"<StationCluster(id={self.id}, name={self.name})>"


#
#  M A C H I N E   T Y P E
#
class MachineType(Base):
    __tablename__ = "layout_machine_types"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    name = Column(String, nullable=False)
    model = Column(String)
    company = Column(String)
    image_url = Column(String)

    machines = relationship("MachineModel", back_populates="machine_type")

    def __repr__(self):
        return f"<MachineType(id={self.id}, name={self.name})>"


#
#  M A C H I N E
#
class MachineModel(Base):
    __tablename__ = "layout_machines"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    serial = Column(String, nullable=False)
    network_info = Column(JSON)  # If using Postgres

    # Foreign key to machine_types (assume you already have this)
    machine_type_id = Column(
        String(16),
        ForeignKey("layout_machine_types.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationship back to MachineType (assume you already have this)
    machine_type = relationship("MachineType", back_populates="machines")

    # ----- NEW RELATIONSHIPS -----
    # 1. Status logs
    machine_status_logs = relationship("MaintenanceMachineStatusLogModel", back_populates="machine")

    # 2. Repair logs
    machine_repair_logs = relationship("MaintenanceMachineRepairModel", back_populates="machine")

    # 3. Maintenance logs
    machine_maintenance_logs = relationship("MaintenanceMachineMaintenanceModel", back_populates="machine")

    # 4. Observations
    machine_observations = relationship("MaintenanceMachineObservationModel", back_populates="machine")

    def __repr__(self):
        return f"<MachineModel(id={self.id}, serial={self.serial})>"


#
#  L A Y O U T
#
class LayoutModel(Base):
    __tablename__ = "layouts"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    # Version auto-incremented for each change
    version = Column(Integer, default=1, nullable=True)
    # Add foreign key to line
    line_id = Column(String(16), ForeignKey('planner_lines.id'), nullable=False)
    user_id = Column(String(16), ForeignKey('api_users.id'), nullable=False)
    is_active = Column(Boolean, default=True, server_default=DefaultClause("1"), nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    stations = relationship("StationModel", back_populates="layout")
    line = relationship("LineModel", backref="layouts")
    user = relationship("UserModel", backref="layouts")

    def __repr__(self):
        return f"<Layout(id={self.id}, line={self.line})>"


#
#  S T A T I O N
#
class StationModel(Base):
    __tablename__ = "layout_stations"

    # Add a table-level constraint to ensure machine_id is unique
    __table_args__ = (
        UniqueConstraint('machine_id', name='uq_station_machine_id'),
    )

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    index = Column(Integer)

    operation_id = Column(
        String(16),
        ForeignKey("layout_operations.id", ondelete="SET NULL"),
        nullable=True
    )
    area_id = Column(
        String(16),
        ForeignKey("layout_areas.id", ondelete="SET NULL"),
        nullable=True
    )
    station_cluster_id = Column(
        String(16),
        ForeignKey("layout_station_clusters.id", ondelete="SET NULL"),
        nullable=True
    )
    machine_id = Column(
        String(16),
        ForeignKey("layout_machines.id", ondelete="SET NULL"),
        nullable=True
    )
    layout_id = Column(
        String(16),
        ForeignKey("layouts.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    operation = relationship("OperationModel", back_populates="stations")
    area = relationship("AreaModel", back_populates="stations")
    station_cluster = relationship("StationClusterModel", back_populates="stations")
    machine = relationship("MachineModel")  # One machine per station
    layout = relationship("LayoutModel", back_populates="stations")

    def __repr__(self):
        return f"<Station(id={self.id}, index={self.index})>"


class MaintenanceMachineStatusLogModel(Base):
    """
    Tracks changes in machine status over time.
    Example statuses might be: "Running", "Stopped", "NeedsParts", etc.
    """
    __tablename__ = "maintenance_machine_status_logs"

    id = Column(String(16), primary_key=True, default=generate_custom_id)

    machine_id = Column(
        String(16),
        ForeignKey("layout_machines.id", ondelete="SET NULL"),
        nullable=True
    )

    status = Column(String, nullable=False)  # e.g., "Stopped", "Running"
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text)  # free text describing the status reason, etc.

    # Relationship back to MachineModel
    machine = relationship("MachineModel", back_populates="machine_status_logs")

    def __repr__(self):
        return f"<MaintenanceMachineStatusLogModel(id={self.id}, status={self.status})>"


class MaintenanceMachineRepairModel(Base):
    """
    Tracks a machine's repair events.
    For example: replaced a broken belt, fixed a motor, etc.
    """
    __tablename__ = "maintenance_machine_repairs"

    id = Column(String(16), primary_key=True, default=generate_custom_id)

    machine_id = Column(
        String(16),
        ForeignKey("layout_machines.id", ondelete="SET NULL"),
        nullable=True
    )

    repair_description = Column(Text, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    # Possibly add columns like cost, repaired_by, etc.

    machine = relationship("MachineModel", back_populates="machine_repair_logs")

    def __repr__(self):
        return f"<MaintenanceMachineRepairModel(id={self.id}, machine_id={self.machine_id})>"


class MaintenanceMachineMaintenanceModel(Base):
    """
    Tracks scheduled or unscheduled maintenance logs.
    Could store type of maintenance, date performed, next due date, etc.
    """
    __tablename__ = "maintenance_machine_maintenance"

    id = Column(String(16), primary_key=True, default=generate_custom_id)

    machine_id = Column(
        String(16),
        ForeignKey("layout_machines.id", ondelete="SET NULL"),
        nullable=True
    )

    maintenance_type = Column(String, nullable=False)  # e.g., "Preventive", "Corrective"
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)  # e.g. "Replaced filter", "Lubricated belts"

    machine = relationship("MachineModel", back_populates="machine_maintenance_logs")

    def __repr__(self):
        return f"<MaintenanceMachineMaintenanceModel(id={self.id}, type={self.maintenance_type})>"


class MaintenanceMachineObservationModel(Base):
    """
    Stores free-form observations made by operators, technicians, etc.
    Example usage: notes about noise, temperature, performance anomalies, etc.
    """
    __tablename__ = "maintenance_machine_observations"

    id = Column(String(16), primary_key=True, default=generate_custom_id)

    machine_id = Column(
        String(16),
        ForeignKey("layout_machines.id", ondelete="SET NULL"),
        nullable=True
    )

    observed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    observation = Column(Text, nullable=False)  # free text

    # Possibly track who made the observation
    observed_by = Column(String, nullable=True)

    machine = relationship("MachineModel", back_populates="machine_observations")

    def __repr__(self):
        return f"<MaintenanceMachineObservationModel(id={self.id}, observation={self.observation[:20]})>"


# Line Balancing ORM Models

class LineBalanceModel(Base):
    __tablename__ = "ct_line_balances"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    str_date = Column(String(10), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    user_id = Column(String(16), ForeignKey("api_users.id"), nullable=False, index=True)
    layout_id = Column(String(16), ForeignKey("layouts.id"), nullable=False, index=True)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Constraints
    # One per week,layout
    __table_args__ = (
        CheckConstraint('week >= 0 AND week < 53', name='check_ct_line_balances_week'),
        UniqueConstraint('week', 'layout_id', name='uq_line_balance_date_layout'),
        Index('ix_week_layout', 'week', 'layout_id'),
    )

    # Relationships
    user = relationship("UserModel")
    layout = relationship("LayoutModel")

    takes = relationship("CycleTimeTakeModel", back_populates="line_balance", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<LineBalanceModel(id={self.id}, str_date={self.str_date})>"

class CycleTimeTakeModel(Base):
    __tablename__ = "ct_cycle_time_takes"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    work_plan_id = Column(String(16), ForeignKey("planner_work_plan.id"), nullable=False)
    line_balance_id = Column(String(16), ForeignKey("ct_line_balances.id"), nullable=False)
    user_id = Column(String(16), ForeignKey("api_users.id"), nullable=False)
    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Constraints

    # Relationships
    user = relationship("UserModel")
    line_balance = relationship("LineBalanceModel", back_populates="takes")
    records = relationship("CycleTimeRecordModel", back_populates="take", cascade="all, delete-orphan")
    work_plan = relationship("WorkPlanModel")

    def __repr__(self):
        return f"<CycleTimeTakeModel(id={self.id}, platform_id={self.work_plan_id})>"

class CycleTimeRecordModel(Base):
    __tablename__ = "ct_cycle_time_records"

    id = Column(String(16), primary_key=True, default=generate_custom_id)
    # JSON
    cycle_time = Column(JSON, nullable=False)
    user_id = Column(String(16), ForeignKey("api_users.id"), nullable=False)
    take_id = Column(String(16), ForeignKey("ct_cycle_time_takes.id"), nullable=False)
    station_id = Column(String(16), ForeignKey("layout_stations.id"), nullable=False)

    # Audit fields for creation and modification tracking
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Constraints

    # Relationships
    user = relationship("UserModel")
    take = relationship("CycleTimeTakeModel", back_populates="records")
    station = relationship("StationModel")

    def __repr__(self):
        return f"<CycleTimeRecordModel(id={self.id}, station_id={self.station_id})>"