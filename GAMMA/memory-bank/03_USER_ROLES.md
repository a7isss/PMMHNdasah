# 👥 USER ROLES & PERMISSIONS - Hndasah PM System v3.0 (Gamma)

**Hierarchical Role-Based Access Control | Multi-Tenant Security**
**Implementation:** Complete | Frontend & Backend Integrated

---

## 🎯 **ROLE HIERARCHY OVERVIEW**

### **Role Structure:**
```
Portfolio Manager (Top Level - System Admin)
├── Project Manager (Project Oversight)
├── Procurement Manager (Final Approvals)
└── Engineer (Base Operations)
```

### **Key Characteristics:**
- **Hierarchical Permissions:** Higher roles inherit lower role permissions
- **Multi-Tenant Isolation:** Organization-based access control
- **WhatsApp Integration:** Phone number verification per user
- **Audit Trail:** All actions logged with user context

---

## 👑 **PORTFOLIO MANAGER**

### **Role Description:**
Highest level administrator with full system access. Responsible for:
- System configuration and workflow management
- User role assignments and organizational setup
- Procurement workflow customization
- Cross-project oversight and analytics

### **Permissions:**
```typescript
const PORTFOLIO_MANAGER_PERMISSIONS = [
  // User Management
  'users.*',                    // Full user CRUD
  'users.roles.assign',         // Change user roles
  'users.organizations.manage', // Organization management

  // Project Management
  'projects.*',                 // Full project access
  'projects.create',            // Create any project
  'projects.archive',           // Archive projects
  'projects.analytics.view',    // Portfolio analytics

  // Procurement System
  'procurement.*',              // Full procurement access
  'procurement.workflow.configure', // Modify approval workflows
  'procurement.approvals.override', // Override any approval

  // WhatsApp Integration
  'whatsapp.*',                 // Full messaging access
  'whatsapp.templates.manage',  // Manage message templates
  'whatsapp.analytics.view',    // Communication analytics

  // AI Insights
  'insights.*',                 // Full AI access
  'insights.configure',         // Configure AI models
  'insights.analytics.view',    // Advanced analytics

  // System Administration
  'system.settings.manage',     // System configuration
  'system.logs.view',           // System logs and audit
  'system.backup.manage',       // Data backup/restore
];
```

### **Frontend Access:**
- ✅ **Dashboard:** Full portfolio analytics and KPIs
- ✅ **User Management:** Complete user administration interface
- ✅ **Project Creation:** BOQ import and project setup
- ✅ **Procurement Config:** Workflow rule customization
- ✅ **System Settings:** Organization and system configuration

---

## 👨‍💼 **PROJECT MANAGER**

### **Role Description:**
Mid-level manager responsible for project execution and team coordination. Handles:
- Project planning and execution oversight
- Team member assignment and management
- Procurement approvals at project level
- Project performance monitoring and reporting

### **Permissions:**
```typescript
const PROJECT_MANAGER_PERMISSIONS = [
  // Project Management
  'projects.read.*',            // Read all projects
  'projects.create',            // Create new projects
  'projects.update.assigned',   // Update assigned projects
  'projects.delete.assigned',   // Delete assigned projects
  'projects.team.manage',       // Manage project teams

  // Task Management
  'tasks.*',                    // Full task CRUD
  'tasks.assign',               // Assign tasks to team members
  'tasks.bulk_operations',      // Bulk task operations

  // Procurement Approvals
  'procurement.read.*',         // Read all procurement requests
  'procurement.create',         // Create procurement requests
  'procurement.approve.level1', // First-level approvals
  'procurement.reject.level1',  // First-level rejections

  // Team Management
  'users.read.team',            // Read team member details
  'users.update.team',          // Update team member info
  'users.assign.projects',      // Assign users to projects

  // Reporting
  'reports.generate',           // Generate project reports
  'reports.export',             // Export project data
  'analytics.project.view',     // Project-specific analytics

  // Communication
  'whatsapp.send',              // Send WhatsApp messages
  'whatsapp.read.team',         // Read team communications
];
```

### **Frontend Access:**
- ✅ **Project Dashboard:** Assigned project oversight
- ✅ **Team Management:** User assignment and permissions
- ✅ **Procurement Approvals:** First-level approval workflow
- ✅ **Task Management:** Full task CRUD operations
- ✅ **Reporting:** Project reports and analytics

---

## 🛒 **PROCUREMENT MANAGER**

### **Role Description:**
Specialized role focused on procurement processes and final approvals. Manages:
- Final procurement approvals and rejections
- Procurement workflow monitoring
- Vendor and supplier relationship management
- Procurement analytics and optimization

### **Permissions:**
```typescript
const PROCUREMENT_MANAGER_PERMISSIONS = [
  // Procurement Management
  'procurement.*',              // Full procurement access
  'procurement.approve.final',  // Final approval authority
  'procurement.reject.final',   // Final rejection authority
  'procurement.workflow.monitor', // Monitor approval workflows

  // Vendor Management
  'vendors.read',               // Read vendor information
  'vendors.create',             // Add new vendors
  'vendors.update',             // Update vendor details
  'vendors.approve',            // Approve vendor relationships

  // Contract Management
  'contracts.read',             // Read contract details
  'contracts.create',           // Create procurement contracts
  'contracts.approve',          // Approve contract terms

  // Financial Oversight
  'procurement.budget.view',    // View procurement budgets
  'procurement.budget.approve', // Approve budget allocations
  'procurement.analytics.view', // Procurement analytics

  // Project Read Access
  'projects.read.procurement',  // Read projects for procurement context
  'tasks.read.procurement',     // Read tasks related to procurement

  // Communication
  'whatsapp.send.procurement',  // Procurement-specific messaging
  'notifications.procurement',  // Procurement notifications
];
```

### **Frontend Access:**
- ✅ **Procurement Dashboard:** Approval queue and workflow monitoring
- ✅ **Final Approvals:** Complete procurement request approvals
- ✅ **Vendor Management:** Supplier relationship management
- ✅ **Analytics:** Procurement performance and cost analysis
- ✅ **Contract Management:** Contract creation and approval

---

## 👷 **ENGINEER**

### **Role Description:**
Base-level operational role for project execution and basic operations. Handles:
- Daily project tasks and updates
- Procurement request initiation
- Project progress reporting
- Basic project communication

### **Permissions:**
```typescript
const ENGINEER_PERMISSIONS = [
  // Project Access
  'projects.read.assigned',     // Read assigned projects only
  'projects.update.status',     // Update project status
  'projects.progress.update',   // Update project progress

  // Task Management
  'tasks.read.assigned',        // Read assigned tasks
  'tasks.update.status',        // Update task status
  'tasks.progress.update',      // Update task progress
  'tasks.comments.add',         // Add task comments

  // Procurement Requests
  'procurement.create',         // Create procurement requests
  'procurement.read.own',       // Read own procurement requests
  'procurement.update.own',     // Update own requests
  'procurement.cancel.own',     // Cancel own requests

  // Communication
  'whatsapp.send.basic',        // Basic WhatsApp messaging
  'whatsapp.read.own',          // Read own communications
  'notifications.receive',      // Receive project notifications

  // Personal Profile
  'users.read.self',            // Read own profile
  'users.update.self',          // Update own profile
  'users.phone.update',         // Update phone/WhatsApp settings

  // Reporting
  'reports.read.assigned',      // Read reports for assigned projects
  'timesheets.submit',          // Submit time tracking
];
```

### **Frontend Access:**
- ✅ **Project Dashboard:** Assigned project status and tasks
- ✅ **Task Management:** Personal task updates and progress
- ✅ **Procurement Requests:** Create and track own requests
- ✅ **WhatsApp Integration:** Basic messaging for project communication
- ✅ **Time Tracking:** Personal time and progress reporting

---

## 🔐 **SECURITY IMPLEMENTATION**

### **Multi-Tenant Architecture:**
```typescript
interface User {
  id: string;
  email: string;
  role: UserRole;
  tenantId: string;           // Organization isolation
  permissions: string[];      // Computed permissions array
  phone?: string;             // WhatsApp integration
  whatsappEnabled?: boolean;  // Verification status
}
```

### **Permission Checking:**
```typescript
// Frontend permission checking
import { useAppSelector } from '@/lib/hooks';

const user = useAppSelector(state => state.auth.user);

const hasPermission = (permission: string): boolean => {
  if (user?.role === 'portfolio_manager') return true;
  return user?.permissions?.includes(permission) ?? false;
};

// Usage
if (hasPermission('projects.create')) {
  // Show create project button
}
```

### **Database Security:**
```sql
-- Row-Level Security (RLS) policies
CREATE POLICY user_tenant_isolation ON users
  FOR ALL USING (tenant_id = current_user_tenant());

CREATE POLICY project_access_control ON projects
  FOR SELECT USING (
    tenant_id = current_user_tenant() AND
    (user_role = 'portfolio_manager' OR
     user_id IN (SELECT user_id FROM project_assignments WHERE project_id = id))
  );
```

---

## 📱 **WHATSAPP INTEGRATION BY ROLE**

### **Portfolio Manager:**
- ✅ Full organization messaging access
- ✅ Template message management
- ✅ Communication analytics
- ✅ Bulk messaging capabilities

### **Project Manager:**
- ✅ Team communication management
- ✅ Project-specific messaging
- ✅ Status update broadcasts
- ✅ Client communication

### **Procurement Manager:**
- ✅ Vendor communication
- ✅ Procurement notifications
- ✅ Contract discussions
- ✅ Approval confirmations

### **Engineer:**
- ✅ Basic project messaging
- ✅ Task updates via WhatsApp
- ✅ Team coordination
- ✅ Status reporting

---

## 🔄 **ROLE TRANSITIONS & MANAGEMENT**

### **Role Assignment Process:**
1. **Portfolio Manager** creates user account
2. **Portfolio Manager** assigns initial role
3. **Role changes** require Portfolio Manager approval
4. **Audit trail** maintained for all role changes

### **Permission Inheritance:**
```typescript
const getPermissionsForRole = (role: UserRole): string[] => {
  const roleHierarchy = {
    portfolio_manager: PORTFOLIO_MANAGER_PERMISSIONS,
    project_manager: [...PROJECT_MANAGER_PERMISSIONS],
    procurement_manager: [...PROCUREMENT_MANAGER_PERMISSIONS],
    engineer: [...ENGINEER_PERMISSIONS],
  };

  return roleHierarchy[role] || [];
};
```

---

## 📊 **USAGE ANALYTICS BY ROLE**

### **Dashboard Customization:**
- **Portfolio Manager:** Organization-wide KPIs and analytics
- **Project Manager:** Project portfolio and team performance
- **Procurement Manager:** Procurement pipeline and approval metrics
- **Engineer:** Personal task completion and project progress

### **Notification Preferences:**
- **Portfolio Manager:** System alerts and strategic notifications
- **Project Manager:** Project milestones and team updates
- **Procurement Manager:** Approval requests and vendor communications
- **Engineer:** Task assignments and project updates

---

## 🚀 **ROLE-BASED UI COMPONENTS**

### **Conditional Rendering:**
```tsx
// Role-based component visibility
const CreateProjectButton = () => {
  const user = useAppSelector(state => state.auth.user);

  if (!hasPermission(user, 'projects.create')) {
    return null;
  }

  return <Button>Create Project</Button>;
};
```

### **Navigation Customization:**
```tsx
const getNavigationItems = (userRole: UserRole) => {
  const baseItems = ['Dashboard', 'Projects'];

  const roleSpecificItems = {
    portfolio_manager: ['Users', 'Analytics', 'Settings'],
    project_manager: ['Team', 'Reports', 'Procurement'],
    procurement_manager: ['Approvals', 'Vendors', 'Contracts'],
    engineer: ['Tasks', 'Time Tracking'],
  };

  return [...baseItems, ...roleSpecificItems[userRole]];
};
```

---

## 📈 **ROLE PERFORMANCE METRICS**

### **Portfolio Manager KPIs:**
- Organization project success rate
- Procurement approval efficiency
- User adoption and engagement
- System utilization metrics

### **Project Manager KPIs:**
- Project delivery on time/budget
- Team productivity metrics
- Procurement request approval time
- Client satisfaction scores

### **Procurement Manager KPIs:**
- Procurement cycle time
- Cost savings achieved
- Vendor performance ratings
- Contract compliance rates

### **Engineer KPIs:**
- Task completion rate
- Time tracking accuracy
- Procurement request quality
- Project contribution metrics

---

*Complete role-based access control system for Hndasah PM. Hierarchical permissions with multi-tenant security and WhatsApp integration.*
