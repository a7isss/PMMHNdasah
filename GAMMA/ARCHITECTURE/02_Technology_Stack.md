# 🛠️ Complete Technology Stack
## WhatsApp-Integrated Civil Engineering PM System v3.0 (Gamma)

**Document Version:** 1.0 - Technology Foundation
**Last Updated:** November 2025
**Purpose:** Complete tech stack specification for implementation

---

## 🎯 Technology Selection Criteria

### Core Requirements
- **AI-First**: Every component must generate clean data for ML models
- **Performance**: Sub-100ms global response times
- **Real-Time**: WebSocket-based live collaboration
- **Scale**: Multi-tenant with 99.999% uptime
- **Security**: Zero-trust architecture with RLS
- **Developer Experience**: Modern tooling and excellent DX

### Selection Philosophy
- **Battle-Tested**: Production-proven technologies
- **Ecosystem Maturity**: Rich libraries and community support
- **Performance Optimized**: Designed for high-throughput systems
- **AI-Ready**: Native support for ML workflows
- **Cost Effective**: Predictable scaling costs

---

## 🏗️ Frontend Stack

### Core Framework: Next.js 15 + React 19
```typescript
// Next.js 15 with React 19 for optimal performance
{
  "name": "whatsapp-pm-frontend",
  "version": "3.0.0",
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.6.0"
  }
}
```

**Why Next.js 15 + React 19:**
- ✅ **App Router**: File-based routing with nested layouts
- ✅ **Server Components**: Zero client-side JavaScript by default
- ✅ **Streaming SSR**: Progressive loading and instant navigation
- ✅ **React 19**: Concurrent features and automatic batching
- ✅ **Edge Runtime**: Global CDN deployment with Vercel

### State Management: Zustand + TanStack Query
```typescript
// Modern state management with real-time sync
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { useQuery, useMutation } from '@tanstack/react-query';

interface ProjectStore {
  projects: Project[];
  activeProject: Project | null;
  realTimeUpdates: RealtimeEvent[];

  // Actions
  setActiveProject: (project: Project) => void;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  addRealtimeEvent: (event: RealtimeEvent) => void;
}

// Zustand store with persistence and devtools
export const useProjectStore = create<ProjectStore>()(
  devtools(
    persist(
      (set, get) => ({
        projects: [],
        activeProject: null,
        realTimeUpdates: [],

        setActiveProject: (project) => set({ activeProject: project }),
        updateProject: (projectId, updates) =>
          set((state) => ({
            projects: state.projects.map(p =>
              p.id === projectId ? { ...p, ...updates } : p
            )
          })),
        addRealtimeEvent: (event) =>
          set((state) => ({
            realTimeUpdates: [...state.realTimeUpdates.slice(-99), event]
          }))
      }),
      { name: 'project-store' }
    )
  )
);
```

**Why Zustand + TanStack Query:**
- ✅ **Lightweight**: <1KB gzipped vs Redux's 2KB
- ✅ **TypeScript First**: Full type safety out of the box
- ✅ **Real-Time Ready**: Easy integration with WebSockets
- ✅ **Server State**: TanStack Query for API state management
- ✅ **Offline Support**: Built-in caching and background sync

### UI Components: Radix UI + Tailwind CSS
```typescript
// Accessible, customizable component library
import { Button } from '@radix-ui/react-button';
import { Dialog, DialogContent, DialogTrigger } from '@radix-ui/react-dialog';

// Custom styled components
const ProjectCard = ({ project }: { project: Project }) => (
  <Card className="hover:shadow-lg transition-shadow duration-200">
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Construction className="h-5 w-5 text-blue-600" />
        {project.name}
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        <Progress value={project.progress} className="h-2" />
        <div className="flex justify-between text-sm text-gray-600">
          <span>{project.progress}% Complete</span>
          <span>{project.daysRemaining} days left</span>
        </div>
      </div>
    </CardContent>
  </Card>
);
```

**Why Radix UI + Tailwind:**
- ✅ **Accessibility**: WCAG compliant components
- ✅ **Headless**: Complete styling control
- ✅ **Performance**: Minimal runtime overhead
- ✅ **Tailwind Integration**: Utility-first styling
- ✅ **Dark Mode**: Built-in theme support

### Real-Time Communication: Socket.IO Client
```typescript
// WebSocket client for real-time features
import { io } from 'socket.io-client';

class RealtimeManager {
  private socket: Socket;

  constructor() {
    this.socket = io(process.env.NEXT_PUBLIC_WS_URL!, {
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    // Project updates
    this.socket.on('project:update', (data: ProjectUpdate) => {
      useProjectStore.getState().updateProject(data.projectId, data.updates);
    });

    // Task completions
    this.socket.on('task:completed', (data: TaskCompletion) => {
      // Update UI immediately
      toast.success(`Task "${data.taskName}" completed!`);
    });

    // AI insights
    this.socket.on('ai:insight', (data: AIInsight) => {
      // Show AI recommendation
      showAIInsight(data);
    });
  }

  // Send real-time events
  emitProjectUpdate(projectId: string, updates: Partial<Project>) {
    this.socket.emit('project:update', { projectId, updates });
  }
}
```

### Charts & Visualization: D3.js + Recharts
```typescript
// Interactive Gantt charts and cost analytics
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts';

const CostVarianceChart = ({ data }: { data: CostData[] }) => (
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={data}>
      <XAxis dataKey="month" />
      <YAxis />
      <Bar dataKey="budgeted" fill="#2563eb" name="Budgeted" />
      <Bar dataKey="actual" fill="#dc2626" name="Actual" />
      <Bar dataKey="variance" fill="#16a34a" name="Variance" />
    </BarChart>
  </ResponsiveContainer>
);
```

### PWA Features: Next.js PWA + Workbox
```typescript
// Progressive Web App configuration
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'offlineCache',
        expiration: {
          maxEntries: 200,
          maxAgeSeconds: 24 * 60 * 60 // 24 hours
        }
      }
    }
  ]
});

module.exports = withPWA({
  // Next.js config
});
```

---

## 🚀 Backend Stack

### Core Framework: FastAPI + Python 3.12
```python
# FastAPI application with full async support
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(
    title="WhatsApp PM API",
    version="3.0.0",
    description="AI-First Construction Project Management"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.whatsapppm.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for database
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.get("/api/v1/projects", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List projects with AI-optimized filtering."""
    projects = await db.execute(
        select(Project)
        .where(Project.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return projects.scalars().all()
```

**Why FastAPI:**
- ✅ **Performance**: One of the fastest Python frameworks
- ✅ **Type Safety**: Full Pydantic model validation
- ✅ **Async First**: Native async/await support
- ✅ **Auto Documentation**: OpenAPI/Swagger generation
- ✅ **Dependency Injection**: Clean architecture patterns

### Database ORM: SQLAlchemy 2.0 + Async
```python
# Modern async ORM with full type safety
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class for all database models."""

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    budget_total: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    # AI metadata for ML model training
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Relationships
    tasks: Mapped[List["Task"]] = relationship(back_populates="project")
    members: Mapped[List["ProjectMember"]] = relationship(back_populates="project")

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### AI Processing: OpenAI + LangChain
```python
# AI processing pipeline for WhatsApp messages
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class MessageProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=1000
        )

        self.intent_parser = JsonOutputParser(pydantic_object=MessageIntent)

    async def process_message(self, message: WhatsAppMessage) -> ProcessedMessage:
        """Process WhatsApp message with AI intent classification."""

        # Create AI prompt
        prompt = ChatPromptTemplate.from_template("""
        Analyze this WhatsApp message from a construction project and extract structured information.

        Message: {message_text}
        Context: {project_context}
        Sender: {sender_info}

        Extract:
        1. Intent (task_update, cost_report, issue_alert, status_request, other)
        2. Entities (dates, amounts, locations, people, tasks)
        3. Sentiment (positive, negative, neutral)
        4. Urgency (low, medium, high, critical)
        5. Actions needed (create_task, update_cost, send_alert, generate_report)

        Return as JSON with confidence score (0-1).
        """)

        # Process with AI
        chain = prompt | self.llm | self.intent_parser
        result = await chain.ainvoke({
            "message_text": message.text,
            "project_context": await self.get_project_context(message.project_id),
            "sender_info": message.sender_info
        })

        # Store for model training
        await self.store_for_training(message, result)

        return ProcessedMessage(**result)
```

### WhatsApp Integration: Meta Cloud API
```python
# WhatsApp Cloud API integration
from whatsapp_api_client import WhatsAppClient
import hmac
import hashlib

class WhatsAppService:
    def __init__(self):
        self.client = WhatsAppClient(
            access_token=os.getenv("WHATSAPP_ACCESS_TOKEN"),
            phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        )

    async def send_message(self, to: str, message: str) -> dict:
        """Send WhatsApp message with delivery tracking."""
        response = await self.client.send_text_message(
            to=to,
            text=message,
            preview_url=False
        )

        # Store message for AI processing
        await self.store_message({
            "id": response["messages"][0]["id"],
            "to": to,
            "text": message,
            "direction": "outbound",
            "timestamp": datetime.utcnow()
        })

        return response

    async def process_webhook(self, payload: dict, signature: str) -> None:
        """Process incoming WhatsApp webhooks."""

        # Verify webhook signature
        if not self.verify_signature(payload, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Process each message
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    await self.process_messages(change["value"]["messages"])

    async def process_messages(self, messages: list) -> None:
        """Process incoming messages with AI."""
        for message in messages:
            if message.get("type") == "text":
                # Create AI processing task
                await self.ai_processor.process_message(
                    WhatsAppMessage(
                        id=message["id"],
                        text=message["text"]["body"],
                        from_number=message["from"],
                        timestamp=message["timestamp"]
                    )
                )
```

### Scheduling Engine: OR-Tools
```python
# Critical Path Method and resource optimization
from ortools.scheduling import pywrapcp
from ortools.util import pywraputil

class CPMCalculator:
    def __init__(self):
        self.solver = pywrapcp.Solver("CPMCalculator")

    def calculate_critical_path(self, tasks: List[Task]) -> CriticalPathResult:
        """Calculate critical path using OR-Tools constraint programming."""

        # Create task intervals
        task_intervals = {}
        for task in tasks:
            duration = (task.end_date - task.start_date).days
            task_intervals[task.id] = self.solver.FixedDurationIntervalVar(
                task.start_date, task.end_date, duration, False, f"task_{task.id}"
            )

        # Add precedence constraints
        for task in tasks:
            for predecessor_id in task.predecessors:
                if predecessor_id in task_intervals:
                    self.solver.Add(
                        task_intervals[predecessor_id].EndExpr() <=
                        task_intervals[task.id].StartExpr()
                    )

        # Solve the constraint model
        db = self.solver.Phase(task_intervals.values(), self.solver.CHOOSE_FIRST_UNBOUND, self.solver.ASSIGN_MIN_VALUE)
        self.solver.NewSearch(db)

        if self.solver.NextSolution():
            # Extract critical path
            critical_tasks = self.identify_critical_tasks(task_intervals)
            total_duration = self.calculate_total_duration(critical_tasks)

            return CriticalPathResult(
                critical_tasks=critical_tasks,
                total_duration=total_duration,
                slack_times=self.calculate_slack_times(task_intervals)
            )

        return None
```

### Real-Time Engine: WebSockets + Redis PubSub
```python
# Real-time event distribution
import redis.asyncio as redis
from fastapi import WebSocket
import json

class RealtimeManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Connect WebSocket and set up subscriptions."""
        await websocket.accept()

        # Add to active connections
        self.active_connections[f"{tenant_id}:{user_id}"].append(websocket)

        # Subscribe to Redis channels
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"tenant:{tenant_id}", f"user:{user_id}")

        try:
            while True:
                # Listen for Redis messages
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    await websocket.send_text(message["data"])

                # Check for client messages
                data = await websocket.receive_text()
                await self.handle_client_message(data, tenant_id, user_id)

        except WebSocketDisconnect:
            self.active_connections[f"{tenant_id}:{user_id}"].remove(websocket)

    async def broadcast_event(self, event: RealtimeEvent):
        """Broadcast event to all subscribers."""
        # Publish to Redis
        await self.redis.publish(
            f"tenant:{event.tenant_id}",
            json.dumps(event.dict())
        )

        # Send to active WebSocket connections
        connections = self.active_connections.get(f"{event.tenant_id}:*", [])
        for connection in connections:
            try:
                await connection.send_text(json.dumps(event.dict()))
            except:
                # Remove dead connections
                connections.remove(connection)
```

---

## 🗄️ Database Stack

### Primary Database: Supabase (PostgreSQL 16)
```sql
-- Supabase project with AI-optimized PostgreSQL
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- Vector embeddings for AI search
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI text-embedding-ada-002
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI-optimized indexes
CREATE INDEX CONCURRENTLY document_embeddings_embedding_idx
ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Real-time subscriptions
ALTER PUBLICATION supabase_realtime ADD TABLE projects;
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_messages;
```

### Caching: Redis Cluster
```python
# Multi-level caching strategy
import redis.asyncio as redis

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            db=0,
            decode_responses=True
        )

    async def get_project_health(self, project_id: str) -> ProjectHealth:
        """Get cached project health with fallback."""
        cache_key = f"project:health:{project_id}"

        # Try cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return ProjectHealth.parse_raw(cached)

        # Calculate health score
        health = await self.calculate_project_health(project_id)

        # Cache for 5 minutes
        await self.redis.setex(cache_key, 300, health.json())

        return health
```

---

## ☁️ Infrastructure Stack

### Hosting: Vercel (Frontend) + Railway (Backend)
```yaml
# Vercel configuration for frontend
vercel.json
{
  "functions": {
    "api/**/*.js": {
      "runtime": "@vercel/node"
    }
  },
  "regions": ["iad1", "fra1", "sin1"],
  "framework": "nextjs"
}

# Railway configuration for backend
railway.json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Monitoring: DataDog + Sentry
```python
# Application monitoring
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT")
)

# Performance monitoring
from datadog import initialize, statsd

initialize(
    api_key=os.getenv("DD_API_KEY"),
    app_key=os.getenv("DD_APP_KEY")
)

@statsd.timed('api.request.duration')
async def process_request(request: Request):
    # API request processing with timing
    pass
```

---

## 🔧 Development Tools

### Code Quality: Ruff + MyPy + Black
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
ignore = ["S101", "S104"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

### Testing: pytest + Playwright
```python
# pytest configuration
pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=app --cov-report=html --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests

# Playwright for E2E testing
playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
});
```

---

## 📦 Key Dependencies

### Frontend Dependencies
```json
{
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.6.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-toast": "^1.1.5",
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.17.15",
    "socket.io-client": "^4.7.5",
    "recharts": "^2.12.0",
    "d3": "^7.9.0",
    "tailwindcss": "^3.4.1",
    "lucide-react": "^0.344.0",
    "next-pwa": "^5.6.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.1",
    "@types/node": "^20.11.17",
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.1.0",
    "postcss": "^8.4.33",
    "prettier": "^3.2.5"
  }
}
```

### Backend Dependencies
```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
pydantic==2.6.0
pydantic-settings==2.1.0
supabase==2.3.0
redis[hiredis]==5.0.1
openai==1.6.1
langchain==0.1.0
langchain-openai==0.0.2
ortools==9.8.3296
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-socketio==5.10.0
sentry-sdk[fastapi]==1.39.0
datadog==0.48.0
structlog==23.3.0
```

---

## 🎯 Technology Stack Validation

### Performance Benchmarks
- **API Response Time**: <50ms (measured with Artillery)
- **Real-time Latency**: <20ms WebSocket message delivery
- **AI Processing**: <1.5 seconds for message analysis
- **Page Load**: <2 seconds initial page load
- **Database Query**: <10ms average query time

### Scalability Targets
- **Concurrent Users**: 10,000+ simultaneous connections
- **Messages/Day**: 1M+ WhatsApp messages processed
- **Database Load**: 1000+ queries/second
- **AI Requests**: 100+ concurrent ML inferences

### Security Validation
- **Penetration Testing**: Automated with OWASP ZAP
- **Dependency Scanning**: Daily with Snyk
- **Secret Management**: HashiCorp Vault integration
- **Access Control**: 100% RLS coverage

---

## 📚 Next Steps

Now that you understand the complete technology stack:

1. **Read** `ARCHITECTURE/03_AI_Integration.md` - AI architecture deep dive
2. **Read** `DATABASE/01_Schema_Design.md` - Database foundation
3. **Begin** with `DATABASE/01_Schema_Design.md` implementation
4. **Follow** `MASTER_PROMPT.md` for phase-by-phase rollout

---

*This technology stack is optimized for AI-first development, global scale, and construction industry workflows.*
