# 🚀 MASTER PROMPT: WhatsApp-Integrated Civil Engineering PM System v3.0 (GAMMA)
## The Ultimate AI-Ready Architecture for Construction Project Management

**Version:** Gamma v3.0 - Production-Ready AI-First Architecture  
**Date:** November 2025  
**Target:** Zero-Defect Implementation by AI Coder  
**Scope:** Complete system rebuild with advanced AI/ML integration

---

## 📋 EXECUTIVE SUMMARY

Build the most advanced civil engineering project management system ever created, featuring:

- **🤖 AI-First Architecture**: Every component designed for AI integration
- **⚡ Hyper-Performance**: Sub-100ms response times globally
- **🔒 Zero-Trust Security**: Military-grade encryption and access control
- **📱 Immersive UX**: Revolutionary user experience with predictive interfaces
- **🔄 Real-Time Everything**: Live collaboration at quantum speeds
- **📊 Predictive Intelligence**: AI-driven project forecasting and risk management
- **🌐 Global Scale**: Instant deployment to 200+ countries
- **💰 Zero Downtime**: 99.999% uptime with automatic failover

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### Core Philosophy: AI as First-Class Citizen
Every component must be designed to feed clean, structured data to AI systems for:
- **Intent Classification**: Automatic task creation from WhatsApp messages
- **Risk Prediction**: ML models forecasting project delays and cost overruns
- **Resource Optimization**: AI-driven equipment and labor allocation
- **Quality Assurance**: Automated inspection analysis and defect detection
- **Schedule Optimization**: Dynamic CPM recalculation with AI insights

### Technology Stack: The Ultimate Modern Stack

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               PRESENTATION LAYER                               │
│            Next.js 15 + React 19 + TypeScript 5.3 + Tailwind 4.0              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  🎨 UI Framework: shadcn/ui v2.0 + Radix UI + Framer Motion             │   │
│  │  📊 Charts: Vis.js + D3.js v8 + Three.js for 3D Gantt                    │   │
│  │  🎯 State: Zustand v5 + TanStack Query v5 + SWR                         │   │
│  │  🔄 Real-time: Socket.io v5 + Supabase Realtime                         │   │
│  │  📱 PWA: Next.js PWA v10 + Service Workers                              │   │
│  │  🎭 Animations: Framer Motion v11 + React Spring                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │ HTTPS 3.0/WebSocket
┌─────────────────────────┴───────────────────────────────────────────────────────┘
│                             APPLICATION LAYER                                 │
│                      FastAPI v0.110 + Python 3.12                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  🚀 Framework: FastAPI + Pydantic v2.6 + SQLAlchemy 2.0                 │   │
│  │  🤖 AI Layer: OpenAI GPT-4V + Claude 3 Opus + Custom ML Models          │   │
│  │  📡 APIs: REST + GraphQL + gRPC + WebSockets                           │   │
│  │  🔄 Async: Native async/await with uvloop                               │   │
│  │  🎯 Scheduling: Google OR-Tools v9.8 + NetworkX + PuLP                 │   │
│  │  💰 Finance: Pandas 2.2 + NumPy 1.26 + Statsmodels                      │   │
│  │  📱 WhatsApp: Meta Cloud API v3 + Twilio + 360Dialog                    │   │
│  │  🔧 Background: Celery v6 + Redis Cluster + RabbitMQ                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │ PostgreSQL 16 Protocol
┌─────────────────────────┴───────────────────────────────────────────────────────┘
│                              DATA LAYER                                        │
│                    Supabase Enterprise + PostgreSQL 16                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  🗄️ Database: PostgreSQL 16 + TimescaleDB + PostGIS 3.4                │   │
│  │  🔍 Search: pgvector v0.7 + OpenSearch + Meilisearch                     │   │
│  │  📊 Analytics: ClickHouse + Supabase Analytics                          │   │
│  │  🔒 Security: Row Level Security + Encryption at Rest                   │   │
│  │  ⚡ Performance: Connection Pooling + Query Optimization                 │   │
│  │  💾 Storage: Supabase Storage + CDN + Edge Functions                     │   │
│  │  🤖 AI Ready: Vector embeddings + pgvector + Custom indexes             │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                          │ Global CDN
┌─────────────────────────┴───────────────────────────────────────────────────────┘
│                           INFRASTRUCTURE LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ☁️ Cloud: AWS/Global + Vercel + Railway + Supabase                     │   │
│  │  🚀 Deployment: Docker v26 + Kubernetes v1.29 + Terraform               │   │
│  │  📊 Monitoring: DataDog + Sentry + New Relic                            │   │
│  │  🔒 Security: AWS WAF + Cloudflare + Zero Trust                         │   │
│  │  📈 Scaling: Auto-scaling + Load Balancing + CDN                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 DETAILED REQUIREMENTS SPECIFICATION

### 1. AI Integration Architecture

#### 1.1 Data Pipeline for AI Models
Every user interaction must generate clean, structured data for AI processing:

```typescript
// AI Data Pipeline Interface
interface AIDataPayload {
  user_id: string;
  tenant_id: string;
  session_id: string;
  timestamp: Date;
  action_type: 'message' | 'task_update' | 'cost_entry' | 'schedule_change';
  raw_data: any;
  cleaned_data: AICleanedData;
  context: AIContext;
  metadata: AIMetadata;
}

interface AICleanedData {
  intent: 'task_create' | 'cost_report' | 'issue_alert' | 'status_update';
  entities: {
    dates: Date[];
    amounts: number[];
    locations: string[];
    people: string[];
    tasks: string[];
    materials: string[];
  };
  sentiment: 'positive' | 'negative' | 'neutral';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  confidence_score: number;
}

interface AIContext {
  project_phase: string;
  user_role: string;
  recent_actions: string[];
  project_status: string;
  risk_level: string;
}

interface AIMetadata {
  source: 'whatsapp' | 'web' | 'mobile' | 'api';
  device_type: string;
  location: GeoLocation;
  session_duration: number;
  error_logs: string[];
}
```

#### 1.2 AI Service Integration Points

```python
# AI Service Manager
class AIServiceManager:
    def __init__(self):
        self.openai = OpenAIClient()
        self.claude = AnthropicClient()
        self.custom_models = CustomMLModels()

    async def process_message(self, message: WhatsAppMessage) -> AIResponse:
        """Process incoming WhatsApp message with AI"""
        # 1. Clean and structure the data
        cleaned_data = await self.clean_message_data(message)

        # 2. Determine intent and extract entities
        intent_analysis = await self.analyze_intent(cleaned_data)

        # 3. Generate appropriate response
        response = await self.generate_response(intent_analysis)

        # 4. Update project state if needed
        await self.update_project_state(intent_analysis)

        return response

    async def clean_message_data(self, message: WhatsAppMessage) -> AICleanedData:
        """Clean raw message data for AI processing"""
        # Remove noise, normalize text, extract structured data
        pass

    async def analyze_intent(self, data: AICleanedData) -> IntentAnalysis:
        """Use ML models to classify message intent"""
        pass

    async def generate_response(self, analysis: IntentAnalysis) -> AIResponse:
        """Generate contextual response using GPT/Claude"""
        pass
```

### 2. Database Schema: AI-Optimized Design

#### 2.1 Core Tables with AI Integration

```sql
-- Projects Table with AI Embeddings
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_number VARCHAR(50) UNIQUE,
    contract_type VARCHAR(50) DEFAULT 'lump_sum',

    -- Location with PostGIS
    location GEOGRAPHY(POINT, 4326),
    address JSONB,
    site_boundaries GEOGRAPHY(POLYGON, 4326),

    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,
    status project_status DEFAULT 'planning',

    -- Financial
    budget_total DECIMAL(15,2) NOT NULL DEFAULT 0,
    actual_cost DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Progress & Risk
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    risk_level VARCHAR(20) DEFAULT 'low',
    health_score DECIMAL(5,2) GENERATED ALWAYS AS (
        -- AI-calculated health score
        calculate_project_health(id)
    ) STORED,

    -- AI Integration
    ai_insights JSONB DEFAULT '{}',
    risk_predictions JSONB DEFAULT '[]',
    embedding VECTOR(1536), -- OpenAI embeddings for semantic search
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B')
    ) STORED,

    -- Metadata
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    ai_metadata JSONB DEFAULT '{}',

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (end_date >= start_date),
    CHECK (actual_end_date >= actual_start_date OR actual_end_date IS NULL)
);

-- AI-Optimized Indexes
CREATE INDEX idx_projects_embedding ON projects USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_projects_location ON projects USING gist(location);
CREATE INDEX idx_projects_search ON projects USING gin(search_vector);
CREATE INDEX idx_projects_health ON projects(tenant_id, health_score DESC);
CREATE INDEX idx_projects_risk ON projects(tenant_id, risk_level, updated_at DESC);

-- Row Level Security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "projects_access" ON projects
    FOR ALL USING (auth.jwt() ->> 'tenant_id' = tenant_id::text);
```

#### 2.2 WhatsApp Messages with AI Analysis

```sql
CREATE TABLE whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES whatsapp_contacts(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id),

    -- Message Content
    direction message_direction NOT NULL,
    message_type message_type DEFAULT 'text',
    content TEXT,
    media_urls TEXT[],
    media_metadata JSONB DEFAULT '{}',

    -- WhatsApp Specific
    whatsapp_message_id VARCHAR(255),
    whatsapp_timestamp TIMESTAMPTZ,

    -- AI Analysis Results
    ai_processed BOOLEAN DEFAULT false,
    intent_classification VARCHAR(100),
    sentiment_score DECIMAL(3,2), -- -1 to 1
    urgency_level VARCHAR(20),
    extracted_entities JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),

    -- Context Linking
    related_task_id UUID REFERENCES tasks(id),
    related_cost_item_id UUID REFERENCES cost_items(id),
    conversation_context JSONB DEFAULT '{}',

    -- Response
    auto_response_sent BOOLEAN DEFAULT false,
    response_content TEXT,
    response_timestamp TIMESTAMPTZ,

    -- Delivery & Status
    delivery_status VARCHAR(20) DEFAULT 'sent',
    read_at TIMESTAMPTZ,
    error_message TEXT,

    -- Search & AI
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(content, '')), 'A')
    ) STORED,
    embedding VECTOR(1536),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI-Optimized Indexes
CREATE INDEX idx_messages_embedding ON whatsapp_messages USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_messages_intent ON whatsapp_messages(project_id, intent_classification, created_at DESC);
CREATE INDEX idx_messages_sentiment ON whatsapp_messages(project_id, sentiment_score);
CREATE INDEX idx_messages_unprocessed ON whatsapp_messages(project_id, ai_processed) WHERE ai_processed = false;
```

### 3. UI/UX Design Specification

#### 3.1 Core Pages Structure

```
📱 MAIN APPLICATION PAGES:

1. 🏠 Dashboard (/dashboard)
   - Real-time project health overview
   - AI-powered risk alerts
   - Live cost variance indicators
   - Upcoming task notifications
   - WhatsApp message summary

2. 📋 Projects (/projects)
   - Project grid/list with filters
   - Quick actions (create, edit, archive)
   - AI project insights sidebar
   - Bulk operations

3. 📊 Project Detail (/projects/[id])
   - Header with key metrics
   - Tabbed interface: Overview, Tasks, Costs, WhatsApp, Reports
   - Real-time updates
   - AI recommendations panel

4. ✅ Tasks (/projects/[id]/tasks)
   - Interactive Gantt chart (3D visualization)
   - Task list with drag-drop reordering
   - AI task priority suggestions
   - Bulk task operations

5. 💰 Costs (/projects/[id]/costs)
   - Cost breakdown by category
   - Budget vs actual charts
   - AI cost forecasting
   - Expense approval workflow

6. 💬 WhatsApp (/projects/[id]/whatsapp)
   - Live message threads
   - AI message analysis
   - Automated response suggestions
   - Bulk message operations

7. 📈 Reports (/projects/[id]/reports)
   - Custom report builder
   - AI-generated insights
   - Export capabilities
   - Scheduled reports

8. 👥 Team (/team)
   - User management
   - Role assignments
   - Permission matrix
   - Activity logs

9. ⚙️ Settings (/settings)
   - Tenant configuration
   - AI preferences
   - Integration settings
   - Security settings
```

#### 3.2 Component Library Specification

```typescript
// Core UI Components to Build

// 1. Project Health Card
interface ProjectHealthCardProps {
  project: Project;
  aiInsights: AIInsights;
  realTimeData: RealTimeMetrics;
  onAction: (action: string) => void;
}

// 2. Interactive Gantt Chart
interface GanttChartProps {
  tasks: Task[];
  dependencies: Dependency[];
  onTaskUpdate: (taskId: string, updates: Partial<Task>) => void;
  onDependencyCreate: (dependency: Dependency) => void;
  aiSuggestions: AISuggestion[];
}

// 3. WhatsApp Message Thread
interface MessageThreadProps {
  messages: WhatsAppMessage[];
  contact: WhatsAppContact;
  aiAnalysis: AIAnalysis[];
  onSendMessage: (content: string) => void;
  onAIResponse: (suggestion: AISuggestion) => void;
}

// 4. Cost Dashboard
interface CostDashboardProps {
  costItems: CostItem[];
  budget: Budget;
  aiForecast: CostForecast;
  onExpenseAdd: (expense: Expense) => void;
  onAlertAcknowledge: (alertId: string) => void;
}

// 5. AI Insights Panel
interface AIInsightsPanelProps {
  insights: AIInsight[];
  onInsightAction: (insightId: string, action: string) => void;
  onFeedback: (insightId: string, feedback: 'helpful' | 'not_helpful') => void;
}
```

#### 3.3 Design System Specification

```css
/* Tailwind Config Extension */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Civil Engineering Theme
        'construction': {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a'
        },
        'risk': {
          'low': '#10b981',
          'medium': '#f59e0b',
          'high': '#ef4444',
          'critical': '#7c2d12'
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
      }
    }
  }
}
```

### 4. API Specification

#### 4.1 REST API Endpoints

```typescript
// Core API Routes
const API_ROUTES = {
  // Projects
  projects: {
    list: 'GET /api/v1/projects',
    create: 'POST /api/v1/projects',
    detail: 'GET /api/v1/projects/{id}',
    update: 'PATCH /api/v1/projects/{id}',
    delete: 'DELETE /api/v1/projects/{id}',
    dashboard: 'GET /api/v1/projects/{id}/dashboard',
    ai_insights: 'GET /api/v1/projects/{id}/ai-insights'
  },

  // Tasks
  tasks: {
    list: 'GET /api/v1/projects/{project_id}/tasks',
    create: 'POST /api/v1/projects/{project_id}/tasks',
    bulk_update: 'PATCH /api/v1/projects/{project_id}/tasks/bulk',
    gantt: 'GET /api/v1/projects/{project_id}/gantt',
    ai_suggestions: 'GET /api/v1/projects/{project_id}/tasks/ai-suggestions'
  },

  // WhatsApp
  whatsapp: {
    send: 'POST /api/v1/whatsapp/send',
    messages: 'GET /api/v1/projects/{project_id}/whatsapp/messages',
    contacts: 'GET /api/v1/projects/{project_id}/whatsapp/contacts',
    ai_analysis: 'POST /api/v1/whatsapp/analyze',
    templates: 'GET /api/v1/whatsapp/templates'
  },

  // AI Services
  ai: {
    analyze_message: 'POST /api/v1/ai/analyze-message',
    predict_risks: 'POST /api/v1/ai/predict-risks',
    optimize_schedule: 'POST /api/v1/ai/optimize-schedule',
    forecast_costs: 'POST /api/v1/ai/forecast-costs'
  }
} as const;
```

#### 4.2 GraphQL Schema

```graphql
# GraphQL Schema for Advanced Queries
type Query {
  projects(
    where: ProjectWhereInput
    orderBy: [ProjectOrderByInput!]
    first: Int
    after: String
  ): ProjectConnection!

  project(id: ID!): Project

  tasks(
    where: TaskWhereInput
    orderBy: [TaskOrderByInput!]
    first: Int
    after: String
  ): TaskConnection!

  whatsappMessages(
    projectId: ID!
    where: MessageWhereInput
    orderBy: [MessageOrderByInput!]
    first: Int
    after: String
  ): MessageConnection!

  aiInsights(
    projectId: ID!
    type: AIInsightType
    limit: Int
  ): [AIInsight!]!
}

type Mutation {
  createProject(input: CreateProjectInput!): Project!
  updateProject(id: ID!, input: UpdateProjectInput!): Project!
  deleteProject(id: ID!): Boolean!

  createTask(input: CreateTaskInput!): Task!
  updateTask(id: ID!, input: UpdateTaskInput!): Task!
  bulkUpdateTasks(input: BulkUpdateTasksInput!): [Task!]!

  sendWhatsAppMessage(input: SendMessageInput!): WhatsAppMessage!
  processMessageWithAI(messageId: ID!): AIAnalysis!

  generateReport(input: GenerateReportInput!): Report!
}

type Subscription {
  projectUpdated(projectId: ID!): Project!
  taskUpdated(projectId: ID!): Task!
  whatsappMessageReceived(projectId: ID!): WhatsAppMessage!
  aiInsightGenerated(projectId: ID!): AIInsight!
}
```

### 5. Real-time Architecture

#### 5.1 WebSocket Implementation

```typescript
// WebSocket Manager
class WebSocketManager {
  private socket: Socket;
  private channels: Map<string, SubscriptionHandler>;

  constructor() {
    this.socket = io(process.env.NEXT_PUBLIC_WS_URL!);
    this.channels = new Map();
    this.setupEventHandlers();
  }

  subscribeToProject(projectId: string, handler: SubscriptionHandler) {
    this.socket.emit('subscribe', { projectId, userId: this.userId });
    this.channels.set(`project:${projectId}`, handler);
  }

  private setupEventHandlers() {
    this.socket.on('project:update', (data) => {
      const handler = this.channels.get(`project:${data.projectId}`);
      handler?.(data);
    });

    this.socket.on('task:update', (data) => {
      const handler = this.channels.get(`project:${data.projectId}`);
      handler?.(data);
    });

    this.socket.on('whatsapp:message', (data) => {
      const handler = this.channels.get(`project:${data.projectId}`);
      handler?.(data);
    });

    this.socket.on('ai:insight', (data) => {
      const handler = this.channels.get(`project:${data.projectId}`);
      handler?.(data);
    });
  }
}
```

#### 5.2 Supabase Real-time Integration

```typescript
// Real-time Data Subscriptions
function useRealtimeProject(projectId: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [messages, setMessages] = useState<WhatsAppMessage[]>([]);

  useEffect(() => {
    // Subscribe to project changes
    const projectChannel = supabase
      .channel(`project:${projectId}`)
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'projects',
          filter: `id=eq.${projectId}`
        },
        (payload) => {
          setProject(payload.new as Project);
        }
      )
      .subscribe();

    // Subscribe to task changes
    const tasksChannel = supabase
      .channel(`tasks:${projectId}`)
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'tasks',
          filter: `project_id=eq.${projectId}`
        },
        (payload) => {
          // Update tasks list
          fetchTasks();
        }
      )
      .subscribe();

    // Subscribe to WhatsApp messages
    const messagesChannel = supabase
      .channel(`messages:${projectId}`)
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'whatsapp_messages',
          filter: `project_id=eq.${projectId}`
        },
        (payload) => {
          setMessages(prev => [payload.new as WhatsAppMessage, ...prev]);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(projectChannel);
      supabase.removeChannel(tasksChannel);
      supabase.removeChannel(messagesChannel);
    };
  }, [projectId]);

  return { project, tasks, messages };
}
```

### 6. AI Integration Points

#### 6.1 Message Processing Pipeline

```python
class MessageProcessingPipeline:
    """Complete AI processing pipeline for WhatsApp messages"""

    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.urgency_detector = UrgencyDetector()
        self.response_generator = ResponseGenerator()
        self.project_updater = ProjectUpdater()

    async def process_message(self, message: WhatsAppMessage) -> ProcessingResult:
        """Complete message processing with AI"""

        # Step 1: Clean the text
        cleaned_text = await self.text_cleaner.clean(message.content)

        # Step 2: Classify intent
        intent = await self.intent_classifier.classify(cleaned_text)

        # Step 3: Extract entities
        entities = await self.entity_extractor.extract(cleaned_text)

        # Step 4: Analyze sentiment
        sentiment = await self.sentiment_analyzer.analyze(cleaned_text)

        # Step 5: Detect urgency
        urgency = await self.urgency_detector.detect(cleaned_text, intent, sentiment)

        # Step 6: Generate response if needed
        response = await self.response_generator.generate(
            intent, entities, sentiment, urgency, message.context
        )

        # Step 7: Update project state
        updates = await self.project_updater.update_from_message(
            intent, entities, message.project_id
        )

        return ProcessingResult(
            intent=intent,
            entities=entities,
            sentiment=sentiment,
            urgency=urgency,
            response=response,
            updates=updates
        )

class TextCleaner:
    """Clean and normalize text for AI processing"""

    async def clean(self, text: str) -> str:
        """Clean raw text input"""
        # Remove extra whitespace
        cleaned = ' '.join(text.split())

        # Normalize case
        cleaned = cleaned.lower()

        # Remove special characters but keep important punctuation
        cleaned = re.sub(r'[^\w\s.,!?-]', '', cleaned)

        # Remove repeated characters
        cleaned = re.sub(r'(.)\1{2,}', r'\1\1', cleaned)

        return cleaned.strip()

class IntentClassifier:
    """Classify message intent using ML models"""

    def __init__(self):
        self.model = None  # Load custom ML model or use OpenAI

    async def classify(self, text: str) -> str:
        """Classify the intent of the message"""
        # Use OpenAI or custom model to classify intent
        intents = [
            'task_create', 'task_update', 'task_complete',
            'cost_report', 'cost_overrun', 'cost_query',
            'issue_report', 'issue_resolve', 'issue_query',
            'status_request', 'status_update',
            'general', 'greeting', 'farewell'
        ]

        # Implementation would use ML model
        return 'task_update'  # Placeholder

class EntityExtractor:
    """Extract structured entities from text"""

    async def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities like dates, amounts, names"""
        entities = {
            'dates': self._extract_dates(text),
            'amounts': self._extract_amounts(text),
            'locations': self._extract_locations(text),
            'people': self._extract_people(text),
            'tasks': self._extract_tasks(text),
            'materials': self._extract_materials(text)
        }
        return entities

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        # Use regex and date parsing
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}\b'
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return dates

    def _extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts"""
        amount_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(amount_pattern, text)
        return [float(match.replace(',', '')) for match in matches]

    def _extract_locations(self, text: str) -> List[str]:
        """Extract location mentions"""
        # Simple keyword-based extraction
        locations = []
        location_keywords = ['site', 'location', 'area', 'zone', 'sector']
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in location_keywords and i < len(words) - 1:
                locations.append(words[i + 1])
        return locations

    def _extract_people(self, text: str) -> List[str]:
        """Extract person names"""
        # Use spaCy NER or simple patterns
        return []  # Placeholder

    def _extract_tasks(self, text: str) -> List[str]:
        """Extract task mentions"""
        task_keywords = ['task', 'work', 'job', 'activity', 'deliverable']
        sentences = text.split('.')
        tasks = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in task_keywords):
                tasks.append(sentence.strip())
        return tasks

    def _extract_materials(self, text: str) -> List[str]:
        """Extract material mentions"""
        material_keywords = ['concrete', 'steel', 'cement', 'sand', 'gravel', 'brick']
        materials = []
        for keyword in material_keywords:
            if keyword in text.lower():
                materials.append(keyword)
        return materials

### 7. Advanced Scheduling Engine

#### 7.1 CPM Calculation with AI Optimization

```python
class AISchedulingEngine:
    """Advanced scheduling with AI optimization"""

    def __init__(self):
        self.or_tools_solver = ORToolsSolver()
        self.network_analyzer = NetworkAnalyzer()
        self.ai_optimizer = AIOptimizer()

    async def calculate_critical_path_ai(self, tasks: List[Task]) -> Dict[str, Any]:
        """Calculate CPM with AI optimization suggestions"""

        # Basic CPM calculation
        cpm_result = await self.or_tools_solver.solve_cpm(tasks)

        # AI optimization suggestions
        ai_suggestions = await self.ai_optimizer.suggest_optimizations(
            tasks, cpm_result
        )

        # Risk analysis
        risk_analysis = await self._analyze_schedule_risks(tasks, cpm_result)

        return {
            'cpm_result': cpm_result,
            'ai_suggestions': ai_suggestions,
            'risk_analysis': risk_analysis,
            'optimized_schedule': await self._apply_ai_optimizations(
                tasks, ai_suggestions
            )
        }

    async def _analyze_schedule_risks(self, tasks: List[Task], cpm_result: Dict) -> Dict:
        """Analyze schedule risks using historical data"""

        # Calculate risk scores based on:
        # - Task dependencies
        # - Historical delay patterns
        # - Resource constraints
        # - Weather factors
        # - Supplier reliability

        risk_factors = {
            'dependency_risk': self._calculate_dependency_risk(tasks),
            'resource_risk': self._calculate_resource_risk(tasks),
            'weather_risk': self._calculate_weather_risk(tasks),
            'supplier_risk': self._calculate_supplier_risk(tasks)
        }

        overall_risk = sum(risk_factors.values()) / len(risk_factors)

        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'mitigation_suggestions': await self._generate_mitigation_suggestions(risk_factors)
        }

    async def _generate_mitigation_suggestions(self, risk_factors: Dict) -> List[str]:
        """Generate AI-powered mitigation suggestions"""
        suggestions = []

        if risk_factors['dependency_risk'] > 0.7:
            suggestions.append("Consider parallel execution of dependent tasks")
            suggestions.append("Add buffer time between critical dependencies")

        if risk_factors['resource_risk'] > 0.7:
            suggestions.append("Increase resource allocation for bottleneck tasks")
            suggestions.append("Consider resource leveling techniques")

        if risk_factors['weather_risk'] > 0.7:
            suggestions.append("Schedule weather-dependent tasks for optimal periods")
            suggestions.append("Create contingency plans for weather delays")

        return suggestions

### 8. Cost Analysis & Forecasting Engine

#### 8.1 AI-Powered Cost Forecasting

```python
class AICostForecaster:
    """AI-powered cost forecasting and analysis"""

    def __init__(self):
        self.time_series_model = TimeSeriesForecaster()
        self.risk_analyzer = CostRiskAnalyzer()
        self.market_analyzer = MarketAnalyzer()

    async def forecast_project_costs(self, project_id: str, forecast_horizon: int = 12) -> Dict:
        """Forecast project costs using AI models"""

        # Get historical cost data
        historical_data = await self._get_cost_history(project_id)

        # Apply time series forecasting
        forecast = await self.time_series_model.forecast(
            historical_data, forecast_horizon
        )

        # Analyze cost risks
        risk_analysis = await self.risk_analyzer.analyze_cost_risks(
            historical_data, forecast
        )

        # Market rate analysis
        market_rates = await self.market_analyzer.get_current_rates()

        # Generate insights
        insights = await self._generate_cost_insights(
            historical_data, forecast, risk_analysis, market_rates
        )

        return {
            'forecast': forecast,
            'risk_analysis': risk_analysis,
            'market_rates': market_rates,
            'insights': insights,
            'confidence_intervals': self._calculate_confidence_intervals(forecast)
        }

    async def _generate_cost_insights(self, historical: Dict, forecast: Dict,
                                    risk: Dict, market: Dict) -> List[Dict]:
        """Generate AI-powered cost insights"""

        insights = []

        # Trend analysis
        trend = self._analyze_cost_trend(historical)
        if trend['direction'] == 'increasing':
            insights.append({
                'type': 'warning',
                'title': 'Cost Trend Alert',
                'description': f'Costs are trending {trend["rate"]}% higher than planned',
                'recommendation': 'Review cost control measures and supplier contracts'
            })

        # Risk assessment
        if risk['overall_risk'] > 0.7:
            insights.append({
                'type': 'critical',
                'title': 'High Cost Risk',
                'description': f'Projected cost overrun risk: {risk["
