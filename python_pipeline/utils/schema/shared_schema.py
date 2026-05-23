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
            "The EXACT module/package name derived from the file's directory path. "
            "Do NOT infer or rename based on content. "
            "Use the actual folder name the file lives in. "
            "Example: if filepath is '../input_code/gen/file.py' then module_name = 'gen'. "
            "If filepath is '../input_code/backend/src/controllers/file.js' then module_name = 'backend/src/controllers'. "
            "Never use semantic names like 'auth', 'agents', 'utils' unless that is the ACTUAL folder name. es: auth, database, api, utils, frontend/components"
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
    
    filepath: str = Field(
        description="Full relative file path"
    )
    module_name: str = Field(
        description=(
           "Top-level architectural subsystem of the project that this file "
            "belongs to. Represents the primary system boundary rather than "
            "a deep filesystem path. "
            "Examples: backend, frontend, agents, infrastructure, mobile_app."
        )
    )   
    architectural_submodule: Optional[str] = Field(
        description=(
            "Logical domain, feature area, or architectural subsystem inside "
            "the root module. This should represent meaningful business or "
            "technical grouping rather than raw folder structure. "
            "Examples: authentication, nlp_pipeline, payments, review_engine, "
            "dashboard, caching, analytics. "
            "Return NONE if no clear architectural submodule exists."
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


# ---------- CODE BASE SUMMARY ----------

class ArchitectureLayer(BaseModel):

    layer_name: str = Field(
        description=(
            "Name of the architectural layer or subsystem. "
            "Examples: frontend, backend, worker, infrastructure, ai_pipeline."
        )
    )

    purpose: str = Field(
        description=(
            "Responsibility and architectural purpose of this layer "
            "inside the overall system."
        )
    )

    involved_modules: list[str] = Field(
        description=(
            "Modules/services/packages participating in this layer."
        )
    )


class RuntimeComponent(BaseModel):

    component_name: str = Field(
        description=(
            "Name of a runtime service, infrastructure component, "
            "or deployable unit."
        )
    )

    responsibility: str = Field(
        description=(
            "Operational responsibility of this runtime component."
        )
    )

    dependencies: list[str] = Field(
        description=(
            "External systems, databases, queues, APIs, or services "
            "used by this component."
        )
    )


class CodebaseSummary(BaseModel):

    overall_purpose: str = Field(
        description=(
            "High level explanation of what the entire codebase/system does "
            "from both business and technical perspectives."
        )
    )

    architectural_style: str = Field(
        description=(
            "Primary architectural pattern or system design approach used "
            "in the codebase. "
            "Examples: monolith, microservices, event-driven, layered, "
            "client-server, distributed worker architecture."
        )
    )

    system_type: str = Field(
        description=(
            "Category of software system represented by the repository. "
            "Examples: SaaS platform, REST API backend, AI pipeline, "
            "developer tool, web application, distributed system."
        )
    )

    architecture_layers: list[ArchitectureLayer] = Field(
        description=(
            "Major architectural layers or subsystems composing the platform."
        )
    )

    core_modules: list[str] = Field(
        description=(
            "Most important modules/packages/services driving the system."
        )
    )

    high_level_execution_flow: str = Field(
        description=(
            "End-to-end explanation of how requests, data, jobs, "
            "or workflows move through the entire system."
        )
    )

    runtime_components: list[RuntimeComponent] = Field(
        description=(
            "Deployable runtime services, infrastructure pieces, "
            "workers, databases, or processing components."
        )
    )

    major_features: list[str] = Field(
        description=(
            "Most important business or technical capabilities "
            "provided by the platform."
        )
    )

    tech_stack: list[str] = Field(
        description=(
            "Primary languages, frameworks, databases, infrastructure tools, "
            "queues, AI systems, and libraries used in the codebase."
        )
    )

    key_integrations: list[str] = Field(
        description=(
            "External APIs, cloud services, databases, queues, "
            "or third-party systems integrated into the platform."
        )
    )

    shared_contracts_and_models: list[str] = Field(
        description=(
            "Important shared schemas, DTOs, interfaces, contracts, "
            "events, or reusable models used system-wide."
        )
    )

    cross_cutting_concerns: list[str] = Field(
        description=(
            "System-wide concerns implemented across multiple modules. "
            "Examples: authentication, logging, observability, retries, "
            "caching, monitoring, validation."
        )
    )

    scalability_strategy: Optional[str] = Field(
        default=None,
        description=(
            "High level scalability approach used by the system such as "
            "queues, workers, caching, horizontal scaling, async processing, "
            "batch processing, distributed execution."
        )
    )

    security_architecture: Optional[str] = Field(
        default=None,
        description=(
            "System-wide security model including authentication, "
            "authorization, trust boundaries, secret management, "
            "data protection, and API security."
        )
    )

    reliability_and_failure_handling: Optional[str] = Field(
        default=None,
        description=(
            "Important operational risks, bottlenecks, fault tolerance "
            "strategies, retry mechanisms, and failure recovery behavior."
        )
    )

    observability_and_monitoring: Optional[str] = Field(
        default=None,
        description=(
            "Logging, tracing, metrics, monitoring, debugging, "
            "and operational observability mechanisms used across the system."
        )
    )

    deployment_architecture: Optional[str] = Field(
        default=None,
        description=(
            "How the platform is deployed and executed operationally. "
            "Examples: docker-compose, kubernetes, serverless, monolithic VM."
        )
    )

    business_domain: Optional[str] = Field(
        default=None,
        description=(
            "Real-world business domain represented by the platform. "
            "Examples: fintech, food delivery, devtools, analytics, AI."
        )
    )

    engineering_complexity: str = Field(
        description=(
            "Overall architectural and operational complexity level "
            "of the system. "
            "Examples: simple_application, moderate_platform, "
            "distributed_platform, enterprise_scale."
        )
    )

    developer_onboarding_summary: str = Field(
        description=(
            "Concise explanation helping a new developer understand "
            "how the system is organized and where to start."
        )
    )

    tags: list[str] = Field(
        description=(
            "Searchable keywords representing the overall platform."
        )
    )

