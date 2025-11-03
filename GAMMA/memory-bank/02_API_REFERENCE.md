# 🔌 API REFERENCE - Hndasah PM System v3.0 (Gamma)

**Complete API Endpoint Documentation | RTK Query Integration Ready**
**Base URL:** `http://localhost:8000/api/v1`

---

## 🎯 **API OVERVIEW**

### **Architecture:**
- **RESTful API** with JSON responses
- **JWT Authentication** required for all endpoints
- **Role-based access control** with hierarchical permissions
- **Multi-tenant support** with organization isolation
- **RTK Query integration** for frontend state management

### **Authentication:**
```javascript
// Frontend Integration
import { useLoginMutation } from '@/lib/api/authApi';
const [login] = useLoginMutation();

// Usage
const result = await login({ email, password, phone }).unwrap();
```

---

## 👥 **AUTHENTICATION API**

### **POST /auth/login**
**Purpose:** User authentication with JWT token generation
```typescript
interface LoginRequest {
  email: string;
  password: string;
  phone?: string; // WhatsApp enabled phone number
}

interface LoginResponse {
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: 'portfolio_manager' | 'project_manager' | 'procurement_manager' | 'engineer';
    tenantId: string;
    phone?: string;
    whatsappEnabled?: boolean;
  };
  access_token: string;
  token_type: string;
}
```

### **POST /auth/register**
**Purpose:** New user registration
```typescript
interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
  role: UserRole;
}
```

### **GET /auth/me**
**Purpose:** Get current authenticated user details
**Auth Required:** ✅ JWT Token

---

## 👤 **USER MANAGEMENT API**

### **GET /users**
**Purpose:** List all users (role-based filtering)
**Auth Required:** ✅ Portfolio Manager / Project Manager
```typescript
interface UsersResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
}
```

### **GET /users/{userId}**
**Purpose:** Get specific user details
**Auth Required:** ✅ Any authenticated user

### **POST /users**
**Purpose:** Create new user
**Auth Required:** ✅ Portfolio Manager only

### **PUT /users/{userId}**
**Purpose:** Update user information
**Auth Required:** ✅ Portfolio Manager or self

### **DELETE /users/{userId}**
**Purpose:** Deactivate user account
**Auth Required:** ✅ Portfolio Manager only

### **PUT /users/{userId}/role**
**Purpose:** Change user role
**Auth Required:** ✅ Portfolio Manager only
```typescript
interface RoleUpdateRequest {
  role: 'portfolio_manager' | 'project_manager' | 'procurement_manager' | 'engineer';
}
```

---

## 📋 **PROJECT MANAGEMENT API**

### **GET /projects**
**Purpose:** List all projects with filtering
**Auth Required:** ✅ Role-based access
```typescript
interface ProjectsQuery {
  status?: 'active' | 'completed' | 'on_hold';
  page?: number;
  limit?: number;
  search?: string;
}

interface ProjectsResponse {
  projects: Project[];
  total: number;
  page: number;
  limit: number;
}
```

### **GET /projects/{projectId}**
**Purpose:** Get detailed project information
**Auth Required:** ✅ Project access permission

### **POST /projects**
**Purpose:** Create new project with BOQ import
**Auth Required:** ✅ Project Manager / Portfolio Manager
```typescript
interface CreateProjectRequest {
  name: string;
  description: string;
  budgetTotal: number;
  startDate: string;
  endDate: string;
  boqItems?: BOQItem[];
}

interface BOQItem {
  id: string;
  description: string;
  quantity: number;
  unit: string;
  rate: number;
  amount: number;
}
```

### **PUT /projects/{projectId}**
**Purpose:** Update project details
**Auth Required:** ✅ Project Manager / Portfolio Manager

### **DELETE /projects/{projectId}**
**Purpose:** Archive project
**Auth Required:** ✅ Portfolio Manager only

### **GET /projects/{projectId}/dashboard**
**Purpose:** Get project dashboard data
**Auth Required:** ✅ Project access permission

### **GET /projects/{projectId}/health**
**Purpose:** Get project health metrics
**Auth Required:** ✅ Project access permission

---

## 💰 **PROCUREMENT WORKFLOW API**

### **GET /procurement/requests**
**Purpose:** List procurement requests with filtering
**Auth Required:** ✅ Role-based access
```typescript
interface ProcurementRequestsQuery {
  status?: 'draft' | 'pending_pm_approval' | 'pending_procurement_approval' | 'approved' | 'rejected';
  projectId?: string;
  requesterId?: string;
  page?: number;
  limit?: number;
}
```

### **GET /procurement/requests/{requestId}**
**Purpose:** Get detailed procurement request
**Auth Required:** ✅ Request access permission

### **POST /procurement/requests**
**Purpose:** Create new procurement request
**Auth Required:** ✅ Engineer / Project Manager
```typescript
interface CreateProcurementRequest {
  projectId: string;
  title: string;
  description: string;
  estimatedCost: number;
  requiredBy: string;
  documents?: File[];
  category: string;
}
```

### **PUT /procurement/requests/{requestId}/approve**
**Purpose:** Approve procurement request at current level
**Auth Required:** ✅ Project Manager / Procurement Manager
```typescript
interface ApprovalRequest {
  approved: boolean;
  comments?: string;
  nextApproverRole?: 'project_manager' | 'procurement_manager';
}
```

### **GET /procurement/workflow**
**Purpose:** Get current workflow configuration
**Auth Required:** ✅ Any authenticated user

### **PUT /procurement/workflow**
**Purpose:** Update workflow rules (Portfolio Manager only)
**Auth Required:** ✅ Portfolio Manager only
```typescript
interface WorkflowConfiguration {
  approvalHierarchy: {
    engineer: string[];
    project_manager: string[];
    procurement_manager: string[];
  };
  autoEscalation: {
    enabled: boolean;
    daysThreshold: number;
  };
  costThresholds: {
    low: number;
    medium: number;
    high: number;
  };
}
```

---

## 🤖 **MCP INSIGHTS API**

### **GET /insights/projects/{projectId}**
**Purpose:** Get AI insights for specific project
**Auth Required:** ✅ Project access permission
```typescript
interface ProjectInsights {
  healthScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
  costVariance: number;
  scheduleVariance: number;
  predictedCompletion: string;
}
```

### **GET /insights/global**
**Purpose:** Get portfolio-wide insights
**Auth Required:** ✅ Portfolio Manager / Project Manager

### **GET /insights/risks/{projectId}**
**Purpose:** Get detailed risk analysis
**Auth Required:** ✅ Project access permission

### **GET /insights/costs/{projectId}/predictions**
**Purpose:** Get cost prediction models
**Auth Required:** ✅ Project access permission

### **GET /insights/schedule/{projectId}/analysis**
**Purpose:** Get schedule optimization analysis
**Auth Required:** ✅ Project access permission

---

## 📱 **WHATSAPP INTEGRATION API**

### **GET /whatsapp/contacts**
**Purpose:** Get WhatsApp contacts for organization
**Auth Required:** ✅ Any authenticated user

### **POST /whatsapp/messages**
**Purpose:** Send WhatsApp message
**Auth Required:** ✅ Any authenticated user
```typescript
interface SendMessageRequest {
  to: string; // Phone number
  message: string;
  messageType: 'text' | 'template';
}
```

### **GET /whatsapp/messages**
**Purpose:** Get message history
**Auth Required:** ✅ Any authenticated user
```typescript
interface MessagesQuery {
  contact?: string;
  limit?: number;
  offset?: number;
}
```

### **POST /whatsapp/templates**
**Purpose:** Send template message
**Auth Required:** ✅ Project Manager / Portfolio Manager

---

## 🔧 **RTK QUERY INTEGRATION**

### **Frontend Usage Patterns:**
```typescript
// Authentication
import { useLoginMutation, useGetCurrentUserQuery } from '@/lib/api/authApi';

// Projects
import { useGetProjectsQuery, useCreateProjectMutation } from '@/lib/api/projectsApi';

// Procurement
import { useGetProcurementRequestsQuery, useCreateProcurementRequestMutation } from '@/lib/api/procurementApi';

// Insights
import { useGetProjectInsightsQuery } from '@/lib/api/insightsApi';

// Users
import { useGetUsersQuery, useUpdateUserRoleMutation } from '@/lib/api/usersApi';
```

### **Error Handling:**
```typescript
const { data, error, isLoading } = useGetProjectsQuery();

if (error) {
  // Handle API errors
  if ('status' in error) {
    // FetchBaseQueryError
    console.error('API Error:', error.status, error.data);
  } else {
    // SerializedError
    console.error('RTK Error:', error.message);
  }
}
```

---

## 🔐 **SECURITY & AUTHORIZATION**

### **JWT Token Requirements:**
- **Header:** `Authorization: Bearer <token>`
- **Expiration:** 24 hours (configurable)
- **Refresh:** Automatic token refresh implemented

### **Role-Based Permissions:**
```typescript
const PERMISSIONS = {
  portfolio_manager: ['*'], // All permissions
  project_manager: [
    'projects.*',
    'procurement.approve_pm',
    'users.read',
    'insights.*'
  ],
  procurement_manager: [
    'procurement.approve_final',
    'procurement.read',
    'projects.read'
  ],
  engineer: [
    'projects.read_assigned',
    'procurement.create',
    'procurement.read_own'
  ]
};
```

### **Multi-Tenant Isolation:**
- **Database:** Row-Level Security (RLS) policies
- **API:** Automatic tenant filtering
- **Cache:** Tenant-specific caching

---

## 📊 **API RESPONSE FORMATS**

### **Standard Response:**
```typescript
interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
}
```

### **Paginated Response:**
```typescript
interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
```

### **Error Response:**
```typescript
interface ApiError {
  message: string;
  code: string;
  details?: any;
  timestamp: string;
}
```

---

## 🚀 **PERFORMANCE OPTIMIZATION**

### **Caching Strategy:**
- **RTK Query:** Automatic caching with invalidation
- **Redis:** Session and temporary data caching
- **CDN:** Static asset delivery

### **Rate Limiting:**
- **Authenticated:** 1000 requests/hour
- **Anonymous:** 100 requests/hour
- **WhatsApp:** 1000 messages/hour per organization

### **Database Optimization:**
- **Indexes:** Optimized for common query patterns
- **Connection Pooling:** Efficient database connections
- **Query Optimization:** EXPLAIN ANALYZE verified

---

## 🧪 **TESTING ENDPOINTS**

### **Health Check:**
```bash
GET /health
# Returns: {"status": "healthy", "timestamp": "..."}
```

### **API Documentation:**
```bash
GET /docs
# Interactive Swagger UI at /docs
```

### **Test Authentication:**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@whatsapppm.com","password":"demo123"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/projects
```

---

*Complete API reference for Hndasah PM system. All endpoints documented with TypeScript interfaces for frontend integration.*
