# 📁 Backend Files Documentation - Hndasah PM System v3.0 (Gamma)

**Complete Backend Architecture Overview | File Purposes & Relationships**
**Status:** Production Deployed ✅ | November 5, 2025

---

## 🎯 **BACKEND OVERVIEW**

The backend is built with **FastAPI** and follows a modular, AI-first architecture designed for civil engineering project management. It features multi-tenant support, real-time capabilities, and comprehensive admin functionality.

### **Technology Stack:**
- **Framework:** FastAPI (async Python web framework)
- **Database:** PostgreSQL with SQLAlchemy 2.0 (async)
- **Cache:** Redis for session management and performance
- **Authentication:** JWT with role-based access control
- **Architecture:** Clean Architecture with dependency injection
- **Deployment:** Railway (production-ready)

---

## 📂 **ROOT DIRECTORY FILES**

### **Configuration & Build Files**
```
├── pyproject.toml          # Python project configuration (dependencies, scripts, metadata)
├── uv.lock                 # Dependency lock file (uv package manager)
├── requirements.txt        # Alternative dependency specification
├── railway.json           # Railway deployment configuration
├── Makefile               # Build automation and development commands
├── .gitignore             # Git ignore patterns for Python projects
├── README.md              # Project documentation and setup instructions
├── test_health.py         # Health check testing script
├── test_import.py         # Import testing and validation script
└── installation.md        # Installation and setup guide
```

### **Template Files (Copier)**
```
├── {{_copier_conf.answers_file}}.jinja    # Copier configuration template
├── development.md.jinja                   # Development guide template
├── LICENSE.jinja                         # License template
├── publishing.md                         # Publishing documentation
└── README.md.jinja                       # README template
```

### **Development Tools**
```
└── devtools/
    └── lint.py               # Custom linting and code quality tools
```

---

## 📂 **SOURCE CODE STRUCTURE (`src/hndasah_backend/`)**

### **Core Application Files**
```
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point, CORS, middleware, health checks
├── config.py                # Environment-based configuration with Pydantic settings
├── database.py              # SQLAlchemy async database connection, session management, health checks
└── 01_API_Design.md         # API design documentation and specifications
```

### **Authentication & Security**
```
├── routers/auth.py          # Authentication endpoints (login, superadmin login)
├── middleware/
│   ├── __init__.py
│   ├── auth_middleware.py   # JWT authentication middleware
│   └── tenant_middleware.py # Multi-tenant request routing
├── utils/
│   ├── __init__.py
│   ├── security.py          # Password hashing, JWT token management, encryption
│   ├── logging.py           # Structured logging configuration
│   └── email.py             # Email sending utilities
└── services/auth_service.py # Authentication business logic
```

### **Data Models & Schemas**
```
├── models/
│   ├── __init__.py
│   └── user.py              # Legacy user models (being phased out)
├── models/sqlalchemy/
│   ├── __init__.py          # SQLAlchemy model imports and relationships
│   ├── base.py              # Base SQLAlchemy model class
│   ├── user.py              # User model with authentication fields
│   ├── project.py           # Project model with BOQ integration
│   ├── task.py              # Task model with scheduling
│   ├── cost.py              # Cost tracking and procurement
│   └── whatsapp.py          # WhatsApp message and contact models
└── schemas/
    ├── __init__.py
    ├── base.py              # Base Pydantic schemas
    ├── user.py              # User request/response schemas
    ├── project.py           # Project CRUD schemas
    ├── task.py              # Task management schemas
    ├── cost.py              # Cost tracking schemas
    └── whatsapp.py          # WhatsApp integration schemas
```

### **API Endpoints (Routers)**
```
├── routers/
│   ├── __init__.py
│   ├── admin.py             # Superadmin dashboard endpoints (tenant/user management)
│   ├── auth.py              # Authentication endpoints
│   ├── projects.py          # Project CRUD operations
│   ├── tasks.py             # Task management and scheduling
│   ├── costs.py             # Cost tracking and procurement
│   ├── whatsapp.py          # WhatsApp integration endpoints
│   ├── ai.py                # AI insights and processing
│   └── websocket.py         # Real-time WebSocket connections
└── services/
    ├── __init__.py
    ├── ai_service.py                    # AI processing and insights
    ├── auth_service.py                  # Authentication business logic
    ├── baseline_service.py              # Project baseline management
    ├── conflict_resolution_service.py   # Task conflict detection/resolution
    ├── deadline_notification_service.py # Deadline monitoring and alerts
    ├── dependency_validation_service.py # Task dependency validation
    ├── earned_value_service.py          # EVM calculations
    ├── import_export_service.py         # BOQ import/export functionality
    ├── notification_service.py          # System notifications
    ├── reporting_service.py             # Report generation
    ├── scheduling_service.py            # Task scheduling algorithms
    └── task_service.py                  # Task business logic
```

---

## 📋 **DETAILED FILE DESCRIPTIONS**

### **Core Application (`main.py`)**
**Purpose:** FastAPI application entry point and configuration
- **FastAPI app initialization** with title, version, docs
- **CORS middleware** for frontend communication
- **Security middleware** (auth, tenant isolation)
- **Health check endpoint** (`/health`) with service status
- **Router registration** for all API endpoints
- **Lifespan management** (startup/shutdown events)
- **Global exception handling** and logging

### **Configuration (`config.py`)**
**Purpose:** Environment-based application settings
- **Pydantic settings** with environment variable support
- **Database configuration** (PostgreSQL with asyncpg)
- **JWT authentication** settings
- **WhatsApp integration** parameters
- **AI service** configuration (OpenAI, Anthropic)
- **Redis caching** settings
- **Feature flags** for optional components
- **Validation methods** for URLs and secrets

### **Database Layer (`database.py`)**
**Purpose:** SQLAlchemy async database management
- **Async engine creation** with connection pooling
- **Session management** with automatic cleanup
- **Table creation** and schema migrations
- **PostgreSQL extensions** (uuid-ossp, pgvector, postgis)
- **Redis connection** management
- **Health checks** for database and cache
- **Database statistics** and monitoring

### **Authentication (`routers/auth.py`, `services/auth_service.py`)**
**Purpose:** User authentication and authorization
- **JWT token generation** and validation
- **Password hashing** with bcrypt
- **Superadmin authentication** via environment variables
- **User registration** and login flows
- **Role-based access control**
- **Token refresh** mechanisms

### **Admin Dashboard (`routers/admin.py`)**
**Purpose:** Superadmin tenant and user management
- **Tenant CRUD operations** (create, list, update, delete)
- **User management** across all tenants
- **System statistics** and health monitoring
- **Role changes** and account deactivation
- **Audit logging** for admin actions

### **Project Management (`routers/projects.py`, `models/sqlalchemy/project.py`)**
**Purpose:** Civil engineering project lifecycle management
- **Project creation** with BOQ import
- **Budget calculation** from bill of quantities
- **Task generation** from BOQ items
- **Project health monitoring**
- **Multi-tenant project isolation**

### **Task Management (`routers/tasks.py`, `services/task_service.py`)**
**Purpose:** Construction task scheduling and tracking
- **Task CRUD operations** with dependencies
- **Gantt chart data** generation
- **Conflict detection** and resolution
- **Progress tracking** and updates
- **Deadline monitoring** and notifications

### **Procurement System (`routers/costs.py`, `models/sqlalchemy/cost.py`)**
**Purpose:** Construction procurement workflow
- **Cost tracking** and budget management
- **Procurement request** creation and approval
- **Hierarchical approval** workflows
- **Document management** for procurement
- **Vendor and contract** tracking

### **WhatsApp Integration (`routers/whatsapp.py`, `models/sqlalchemy/whatsapp.py`)**
**Purpose:** WhatsApp Business API integration
- **Message sending/receiving** via WhatsApp
- **Contact management** and verification
- **Webhook processing** for incoming messages
- **AI-powered message** analysis and responses
- **Real-time communication** workflows

### **AI Services (`services/ai_service.py`, `routers/ai.py`)**
**Purpose:** AI-powered insights and automation
- **Message intent classification** using LLMs
- **Project health analysis** and predictions
- **Risk assessment** algorithms
- **Cost forecasting** models
- **Schedule optimization** using OR-Tools

### **Middleware Layer**
**Purpose:** Cross-cutting concerns and request processing
- **Auth Middleware:** JWT validation on protected routes
- **Tenant Middleware:** Automatic tenant context injection
- **CORS handling** for frontend communication
- **Request logging** and performance monitoring
- **Security headers** and rate limiting

### **Utility Functions**
**Purpose:** Common functionality and helpers
- **Security Utils:** Password hashing, token generation
- **Logging:** Structured logging with context
- **Email:** SMTP email sending capabilities
- **Validation:** Input sanitization and checking

---

## 🔄 **ARCHITECTURAL PATTERNS**

### **Clean Architecture Implementation**
```
├── Presentation Layer (Routers)     # API endpoints, request/response handling
├── Application Layer (Services)     # Business logic, use cases, workflows
├── Domain Layer (Models/Schemas)    # Business entities, validation rules
└── Infrastructure Layer (Database)  # Data persistence, external APIs
```

### **Dependency Injection Pattern**
- **Settings injection** throughout the application
- **Database session** management via FastAPI dependencies
- **Service layer** with clear interfaces
- **Middleware composition** for cross-cutting concerns

### **Repository Pattern**
- **SQLAlchemy models** as data entities
- **Async session management** for database operations
- **Query optimization** and connection pooling
- **Migration support** for schema evolution

---

## 🚀 **DEPLOYMENT CONSIDERATIONS**

### **Railway-Specific Configuration**
- **Environment variables** for all sensitive data
- **Health checks** for container orchestration
- **Database auto-provisioning** via Railway
- **Redis caching** integration
- **SSL termination** handled by Railway

### **Production Optimizations**
- **Async/await** throughout for performance
- **Connection pooling** for database efficiency
- **Caching layers** for frequently accessed data
- **Structured logging** for observability
- **Error handling** with graceful degradation

---

## 📊 **FILE RELATIONSHIPS**

### **Request Flow Example:**
```
HTTP Request → main.py (CORS/routing) → middleware (auth/tenant) → router (endpoint) → service (business logic) → database (persistence) → response
```

### **Data Flow Example:**
```
User Login → auth.py (validation) → auth_service.py (verification) → user.py (model) → database.py (session) → JWT token generation
```

### **AI Processing Flow:**
```
WhatsApp Message → whatsapp.py (webhook) → ai_service.py (analysis) → task_service.py (creation) → database.py (storage) → notification_service.py (alerts)
```

---

## 🧪 **TESTING STRUCTURE**

### **Test Files**
```
├── test_health.py          # Health check validation
├── test_import.py          # Import and dependency testing
└── tests/
    └── test_placeholder.py # Test framework placeholder
```

### **Testing Strategy**
- **Health checks** for deployment validation
- **Import testing** to catch dependency issues
- **Unit tests** for individual functions
- **Integration tests** for API endpoints
- **End-to-end tests** for critical workflows

---

## 📈 **PERFORMANCE & MONITORING**

### **Built-in Monitoring**
- **Health endpoints** (`/health`) with service status
- **Structured logging** with request tracing
- **Database connection monitoring**
- **Redis cache performance tracking**
- **API response time measurement**

### **External Monitoring Integration**
- **Railway metrics** and logging dashboard
- **Application performance monitoring** (APM)
- **Error tracking** and alerting
- **Database performance** analysis

---

## 🔒 **SECURITY IMPLEMENTATION**

### **Authentication & Authorization**
- **JWT tokens** with configurable expiration
- **Password hashing** with bcrypt (12 rounds)
- **Role-based access control** (RBAC)
- **Multi-tenant data isolation**
- **Superadmin environment-based authentication**

### **Data Protection**
- **SQL injection prevention** via SQLAlchemy
- **Input validation** with Pydantic schemas
- **CORS policy** enforcement
- **Security headers** and HTTPS enforcement
- **Audit logging** for sensitive operations

---

## 🚀 **SCALING CONSIDERATIONS**

### **Horizontal Scaling**
- **Stateless API design** for load balancing
- **Database connection pooling** for efficiency
- **Redis clustering** support
- **Async processing** for I/O operations
- **Microservice-ready** architecture

### **Performance Optimizations**
- **Query optimization** and indexing
- **Caching strategies** for frequent data
- **Background job processing** for heavy tasks
- **CDN integration** for static assets
- **Database read replicas** for scaling

---

*Comprehensive backend file documentation for Hndasah PM system with detailed purposes, relationships, and architectural patterns.*
