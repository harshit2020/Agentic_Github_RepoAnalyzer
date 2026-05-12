from pydantic import BaseModel, Field
from typing import Optional


# ---------- SHARED MODELS ----------

class FunctionReference(BaseModel):
    symbol_id: str = Field(
        description=(
            "Globally unique identifier of a function/class/method. "
            "Format example: "
            "'src/auth/login.py::login_user' or "
            "'src/utils/cache.py::RedisCache.get'."
        )
    )

    role: str = Field(
        description=(
            "Short explanation of what this symbol does in the system."
        )
    )


class DependencyReference(BaseModel):
    filepath: str = Field(
        description="Relative path of the dependency file/module"
    )

    purpose: str = Field(
        description="Why this dependency/module exists and how it is used"
    )


# ---------- FILE LEVEL SUMMARY ----------

class FileLevelSummary(BaseModel):

    filename: str = Field(
        description="Name of the file"
    )

    filepath: str = Field(
        description="Full relative file path"
    )

    module_name: str = Field(
        description=(
            "Logical module/package this file belongs to. "
            "Examples: auth, database, api, utils, frontend/components"
        )
    )

    file_purpose: str = Field(
        description=(
            "High level explanation of why this file exists "
            "and what responsibility it handles in the project"
        )
    )

    architecture_role: str = Field(
        description=(
            "Role of this file in the architecture. "
            "Examples: controller, service, utility, middleware, "
            "worker, schema, component, hook, config, repository"
        )
    )

    important_symbols: list[FunctionReference] = Field(
        description=(
            "Most important functions/classes/components defined in this file"
        )
    )

    core_logic_flow: str = Field(
        description=(
            "Step-by-step explanation of the overall execution flow "
            "inside this file"
        )
    )

    internal_dependencies: list[str] = Field(
        description=(
            "Project-local files/modules/functions used by this file"
        )
    )

    external_dependencies: list[str] = Field(
        description=(
            "Third-party libraries/frameworks/packages imported in this file"
        )
    )

    public_api: list[str] = Field(
        description=(
            "Functions/classes/components exported or intended "
            "to be used by other files"
        )
    )

    side_effects: list[str] = Field(
        description=(
            "Important side effects such as database writes, "
            "network calls, file operations, logging, caching, "
            "event emission, etc"
        )
    )

    error_handling_strategy: str = Field(
        description=(
            "How this file handles errors, validation, retries, "
            "fallbacks, or exceptions"
        )
    )

    state_management: Optional[str] = Field(
        default=None,
        description=(
            "How application state/session/cache/global state "
            "is handled in this file if applicable"
        )
    )

    security_considerations: Optional[str] = Field(
        default=None,
        description=(
            "Authentication, authorization, sanitization, "
            "rate limiting, encryption, or security-sensitive logic"
        )
    )

    performance_notes: Optional[str] = Field(
        default=None,
        description=(
            "Caching, batching, async behavior, expensive operations, "
            "memory usage, or optimization details"
        )
    )

    tags: list[str] = Field(
        description=(
            "Searchable keywords developers may use to find this file"
        )
    )

    related_files: list[str] = Field(
        description=(
            "Other files tightly connected to this file logically"
        )
    )

    overall_complexity: str = Field(
        description=(
            "Overall importance/complexity classification. "
            "Examples: utility, feature_logic, core_system, critical_path"
        )
    )


class FileLevelSummaryList(BaseModel):
    summaries: list[FileLevelSummary] = Field(
        description="List of file level summaries"
    )



# ---------- MODULE LEVEL SUMMARY ----------

class ModuleLevelSummary(BaseModel):

    module_name: str = Field(
        description=(
            "Name of the module/package/subsystem"
        )
    )

    module_purpose: str = Field(
        description=(
            "High level business or technical purpose of the module"
        )
    )

    architectural_role: str = Field(
        description=(
            "Role of this module in overall system architecture"
        )
    )

    key_files: list[str] = Field(
        description=(
            "Most important files belonging to this module"
        )
    )

    key_symbols: list[FunctionReference] = Field(
        description=(
            "Most critical functions/classes/components in this module"
        )
    )

    execution_flow: str = Field(
        description=(
            "End-to-end flow of how data/control moves "
            "through this module"
        )
    )

    responsibilities: list[str] = Field(
        description=(
            "Major responsibilities handled by this module"
        )
    )

    inbound_dependencies: list[str] = Field(
        description=(
            "Other modules/files that depend on this module"
        )
    )

    outbound_dependencies: list[DependencyReference] = Field(
        description=(
            "External modules/services/packages this module depends on"
        )
    )

    shared_models_or_contracts: list[str] = Field(
        description=(
            "Shared DTOs, schemas, interfaces, database models, "
            "events, or contracts used across the system"
        )
    )

    cross_cutting_concerns: list[str] = Field(
        description=(
            "Logging, caching, auth, monitoring, retries, "
            "validation, observability, etc"
        )
    )

    scalability_notes: Optional[str] = Field(
        default=None,
        description=(
            "Scalability considerations such as async processing, "
            "horizontal scaling, queues, batching, caching"
        )
    )

    failure_points: Optional[list[str]] = Field(
        default=None,
        description=(
            "Potential bottlenecks, risks, or critical failure points"
        )
    )

    security_model: Optional[str] = Field(
        default=None,
        description=(
            "Authentication, authorization, data protection, "
            "or trust boundary handling in this module"
        )
    )

    integration_points: list[str] = Field(
        description=(
            "External APIs, databases, services, queues, "
            "or frontend/backend integrations"
        )
    )

    observability: Optional[str] = Field(
        default=None,
        description=(
            "Logging, tracing, metrics, monitoring, alerting details"
        )
    )

    business_domain: Optional[str] = Field(
        default=None,
        description=(
            "Real-world business/domain area this module represents"
        )
    )

    tags: list[str] = Field(
        description=(
            "Searchable keywords representing this module"
        )
    )

    module_complexity: str = Field(
        description=(
            "Importance and architectural criticality of this module. "
            "Examples: support_module, feature_module, "
            "core_platform, critical_infrastructure"
        )
    )


class ModuleLevelSummaryList(BaseModel):
    summaries: list[ModuleLevelSummary] = Field(
        description="List of module level summaries"
    )