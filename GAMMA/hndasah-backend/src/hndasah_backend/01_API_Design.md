# 🚀 FastAPI Backend Design
## WhatsApp-Integrated Civil Engineering PM System v3.0 (Gamma)

**Version:** 1.0 - Complete API Specification
**Last Updated:** November 2025
**Purpose:** FastAPI implementation with AI integration

---

## 🎯 API Design Principles

### AI-First API Design
Every endpoint designed to generate clean data for AI processing:

```python
# AI-ready response structure
class AIReadyResponse(BaseModel):
    data: Any
    ai_metadata: AIMetadata
    processing_hints: ProcessingHints

    class AIMetadata:
        intent_type: str
        confidence_score: float
        entities_extracted: Dict[str, Any]
        sentiment: str

    class ProcessingHints:
        should_analyze: bool
        priority_level: str
        related_entities: List[str]
```

### Performance-First Architecture
- **Sub-100ms response times** for all endpoints
- **Async/await everywhere** for concurrent processing
- **Connection pooling** for database efficiency
- **Caching layers** (Redis + CDN)

---

## 🏗️ Application Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Environment configuration
├── database.py            # Database connection & session management
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── cost.py
│   └── whatsapp.py
├── schemas/               # Database schemas (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── cost.py
│   └── whatsapp.py
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── projects.py
│   ├── tasks.py
│   ├── costs.py
│   ├── whatsapp.py
│   └── ai.py
├── services/              # Business logic services
│   ├── __init__.py
│   ├── auth_service.py
│   ├── ai_service.py
│   ├── whatsapp_service.py
│   ├── project_service.py
│   └── notification_service.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── security.py
│   ├── ai_helpers.py
│   └── validation.py
├── middleware/            # Custom middleware
│   ├── __init__.py
│   ├── auth_middleware.py
│   ├── tenant_middleware.py
│   └── ai_middleware.py
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_projects.py
│   └── test_ai.py
└── alembic/               # Database migrations
    ├── versions/
    └── env.py
```

---

## 🔐 Authentication & Authorization

### JWT-Based Authentication

```python
# Authentication service
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            tenant_id: str = payload.get("tenant_id")
            if email is None or tenant_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await self.user_repo.get_by_email_and_tenant(email, tenant_id)
        if user is None:
            raise credentials_exception
        return user
```

### Multi-Tenant Middleware

```python
# Tenant resolution middleware
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract tenant from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                tenant_id = payload.get("tenant_id")
                if tenant_id:
                    request.state.tenant_id = tenant_id
            except JWTError:
                pass

        # Extract tenant from subdomain (fallback)
        host = request.headers.get("host", "")
        if ".whatsapppm.com" in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "app":
                request.state.tenant_id = subdomain

        response = await call_next(request)
        return response
```

---

## 📊 Core API Endpoints

### Authentication Endpoints

```python
# Auth router
@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "tenant_id": str(user.tenant_id)}
    )

    # Update last login
    await db.execute(
        update(User).where(User.id == user.id).values(last_login_at=datetime.utcnow())
    )
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Register new user (admin only)."""
    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        tenant_id=current_user.tenant_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role or "member"
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
```

### Projects API

```python
# Projects router
@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """List projects with filtering and search."""
    query = select(Project).where(Project.tenant_id == current_user.tenant_id)

    # Apply filters
    if status:
        query = query.where(Project.status == status)

    # Apply search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term)
            )
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    projects = result.scalars().all()

    return projects

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new project."""
    # Validate dates
    if project_data.end_date <= project_data.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # Create project
    db_project = Project(
        **project_data.dict(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )

    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    # Add creator as project member
    project_member = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role="owner",
        assigned_by=current_user.id
    )

    db.add(project_member)
    await db.commit()

    # Generate AI insights for new project
    await ai_service.analyze_new_project(db_project)

    return db_project

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed project information."""
    # Check permissions
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get project with related data
    query = select(Project).options(
        selectinload(Project.tasks),
        selectinload(Project.members),
        selectinload(Project.cost_items)
    ).where(Project.id == project_id)

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project information."""
    # Check permissions
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")

    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(project)

    # Trigger AI analysis for project changes
    await ai_service.analyze_project_update(project)

    return project
```

### WhatsApp Integration API

```python
# WhatsApp router
@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    signature: str = Header(None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db)
):
    """Handle WhatsApp webhooks."""
    # Verify webhook signature
    if not whatsapp_service.verify_signature(await request.body(), signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse webhook payload
    payload = await request.json()

    # Process messages
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "messages":
                messages = change["value"].get("messages", [])
                for message in messages:
                    await process_whatsapp_message(message, db)

    return {"status": "ok"}

async def process_whatsapp_message(message: dict, db: AsyncSession):
    """Process incoming WhatsApp message."""
    # Extract message data
    message_data = WhatsAppMessageCreate(
        whatsapp_message_id=message["id"],
        from_number=message["from"],
        content=message.get("text", {}).get("body", ""),
        whatsapp_timestamp=datetime.fromtimestamp(int(message["timestamp"])),
        direction="inbound"
    )

    # Find or create contact
    contact = await whatsapp_service.get_or_create_contact(message_data.from_number, db)

    # Create message record
    db_message = WhatsAppMessage(
        contact_id=contact.id,
        **message_data.dict()
    )

    db.add(db_message)
    await db.commit()

    # Trigger AI processing
    await ai_service.process_message(db_message, db)

@router.post("/whatsapp/send", response_model=WhatsAppMessageResponse)
async def send_whatsapp_message(
    message_data: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send WhatsApp message."""
    # Check if user has access to the project
    if message_data.project_id:
        if not await check_project_access(message_data.project_id, current_user, db):
            raise HTTPException(status_code=403, detail="Not authorized to send messages for this project")

    # Send message via WhatsApp API
    result = await whatsapp_service.send_message(
        to=message_data.to_number,
        message=message_data.content,
        project_id=message_data.project_id
    )

    # Store outbound message
    db_message = WhatsAppMessage(
        contact_id=result["contact_id"],
        project_id=message_data.project_id,
        direction="outbound",
        content=message_data.content,
        whatsapp_message_id=result["message_id"],
        created_by=current_user.id
    )

    db.add(db_message)
    await db.commit()

    return db_message
```

### AI Services API

```python
# AI router
@router.post("/ai/analyze-message", response_model=AIAnalysisResponse)
async def analyze_message(
    request: AIMessageAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze WhatsApp message with AI."""
    # Get message from database
    result = await db.execute(
        select(WhatsAppMessage).where(WhatsAppMessage.id == request.message_id)
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Check permissions
    if not await check_message_access(message, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to analyze this message")

    # Perform AI analysis
    analysis = await ai_service.analyze_message(message)

    # Update message with analysis results
    message.intent_classification = analysis.intent
    message.sentiment_score = analysis.sentiment_score
    message.urgency_level = analysis.urgency
    message.extracted_entities = analysis.entities
    message.confidence_score = analysis.confidence
    message.ai_processed = True

    await db.commit()

    return analysis

@router.get("/ai/project-insights/{project_id}", response_model=AIInsightsResponse)
async def get_project_insights(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated insights for project."""
    # Check permissions
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Generate insights
    insights = await ai_service.generate_project_insights(project_id, db)

    return insights

@router.post("/ai/generate-response", response_model=AIResponseSuggestion)
async def generate_ai_response(
    request: AIResponseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered response suggestion."""
    # Get conversation context
    context_messages = await whatsapp_service.get_conversation_context(
        request.contact_id, request.project_id, limit=10, db=db
    )

    # Generate response
    suggestion = await ai_service.generate_response_suggestion(
        context_messages, request.user_message, request.intent
    )

    return suggestion
```

---

## 🤖 AI Integration Services

### Message Processing Pipeline

```python
class AIService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()

    async def process_message(self, message: WhatsAppMessage, db: AsyncSession) -> AIAnalysis:
        """Complete AI processing pipeline for WhatsApp messages."""

        # Step 1: Clean and prepare text
        cleaned_text = await self._clean_text(message.content)

        # Step 2: Classify intent
        intent_analysis = await self.intent_classifier.classify(cleaned_text)

        # Step 3: Extract entities
        entities = await self.entity_extractor.extract(cleaned_text)

        # Step 4: Analyze sentiment
        sentiment = await self.sentiment_analyzer.analyze(cleaned_text)

        # Step 5: Determine urgency
        urgency = await self._calculate_urgency(intent_analysis, sentiment, entities)

        # Step 6: Generate insights
        insights = await self._generate_insights(intent_analysis, entities, message.project_id, db)

        # Step 7: Auto-actions if needed
        await self._perform_auto_actions(intent_analysis, entities, message, db)

        return AIAnalysis(
            intent=intent_analysis.intent,
            confidence=intent_analysis.confidence,
            entities=entities,
            sentiment=sentiment.score,
            urgency=urgency,
            insights=insights,
            auto_actions_performed=len(await self._get_auto_actions(intent_analysis))
        )

    async def _clean_text(self, text: str) -> str:
        """Clean and normalize text for AI processing."""
        # Remove extra whitespace, normalize case, etc.
        return text.strip().lower()

    async def _calculate_urgency(self, intent: IntentAnalysis, sentiment: SentimentAnalysis, entities: Dict) -> str:
        """Calculate message urgency based on multiple factors."""
        urgency_score = 0

        # Intent-based urgency
        if intent.intent in ['issue_report', 'cost_overrun', 'task_failed']:
            urgency_score += 3
        elif intent.intent in ['status_request', 'cost_query']:
            urgency_score += 1

        # Sentiment-based urgency
        if sentiment.label == 'negative':
            urgency_score += 2

        # Time-sensitive entities
        if 'dates' in entities and len(entities['dates']) > 0:
            urgency_score += 1

        # Determine urgency level
        if urgency_score >= 4:
            return 'critical'
        elif urgency_score >= 3:
            return 'high'
        elif urgency_score >= 2:
            return 'medium'
        else:
            return 'low'

    async def _generate_insights(self, intent: IntentAnalysis, entities: Dict, project_id: UUID, db: AsyncSession) -> List[Dict]:
        """Generate actionable insights from message analysis."""
        insights = []

        if intent.intent == 'task_complete':
            insights.append({
                'type': 'task_completion',
                'message': 'Task completion detected',
                'action': 'update_task_status',
                'entities': entities.get('tasks', [])
            })

        elif intent.intent == 'cost_report':
            insights.append({
                'type': 'cost_entry',
                'message': 'Cost information detected',
                'action': 'create_cost_entry',
                'entities': entities.get('amounts', [])
            })

        elif intent.intent == 'issue_report':
            insights.append({
                'type': 'risk_alert',
                'message': 'Potential issue detected',
                'action': 'create_risk_alert',
                'entities': entities.get('issues', [])
            })

        return insights

    async def _perform_auto_actions(self, intent: IntentAnalysis, entities: Dict, message: WhatsAppMessage, db: AsyncSession):
        """Perform automatic actions based on message analysis."""
        actions = await self._get_auto_actions(intent)

        for action in actions:
            if action == 'create_task':
                await self._auto_create_task(entities, message.project_id, db)
            elif action == 'update_cost':
                await self._auto_update_cost(entities, message.project_id, db)
            elif action == 'send_notification':
                await self._auto_send_notification(intent, message, db)

    async def _get_auto_actions(self, intent: IntentAnalysis) -> List[str]:
        """Determine which auto-actions to perform."""
        actions = []

        if intent.intent == 'task_create' and intent.confidence > 0.8:
            actions.append('create_task')
        elif intent.intent == 'cost_report' and intent.confidence > 0.8:
            actions.append('update_cost')
        elif intent.intent in ['issue_report', 'cost_overrun'] and intent.confidence > 0.7:
            actions.append('send_notification')

        return actions
```

### Project Health Analysis

```python
class ProjectAIService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_project_health(self, project_id: UUID, db: AsyncSession) -> ProjectHealthAnalysis:
        """Generate comprehensive project health analysis."""

        # Get project data
        project_data = await self._get_project_data(project_id, db)

        # Analyze schedule performance
        schedule_analysis = await self._analyze_schedule_performance(project_data)

        # Analyze budget performance
        budget_analysis = await self._analyze_budget_performance(project_data)

        # Analyze risk factors
        risk_analysis = await self._analyze_risk_factors(project_data)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            schedule_analysis, budget_analysis, risk_analysis
        )

        # Calculate overall health score
        health_score = self._calculate_health_score(
            schedule_analysis, budget_analysis, risk_analysis
        )

        return ProjectHealthAnalysis(
            project_id=project_id,
            health_score=health_score,
            schedule_analysis=schedule_analysis,
            budget_analysis=budget_analysis,
            risk_analysis=risk_analysis,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )

    async def _analyze_schedule_performance(self, project_data: Dict) -> ScheduleAnalysis:
        """Analyze project schedule performance."""
        # Calculate schedule variance
        planned_duration = (project_data['end_date'] - project_data['start_date']).days
        actual_duration = (project_data.get('actual_end_date', datetime.utcnow().date()) - project_data['start_date']).days
        schedule_variance = ((actual_duration - planned_duration) / planned_duration) * 100

        # Analyze task completion rates
        completed_tasks = len([t for t in project_data['tasks'] if t['status'] == 'completed'])
        total_tasks = len(project_data['tasks'])
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        # Identify critical path delays
        critical_path_delay = await self._calculate_critical_path_delay(project_data['tasks'])

        return ScheduleAnalysis(
            variance_percentage=schedule_variance,
            completion_rate=completion_rate,
            critical_path_delay=critical_path_delay,
            status='on_track' if schedule_variance < 10 else 'at_risk' if schedule_variance < 20 else 'delayed'
        )

    async def _analyze_budget_performance(self, project_data: Dict) -> BudgetAnalysis:
        """Analyze project budget performance."""
        budget_total = project_data['budget_total']
        actual_cost = project_data['actual_cost']

        if budget_total > 0:
            budget_variance = ((actual_cost - budget_total) / budget_total) * 100
        else:
            budget_variance = 0

        # Analyze cost trends
        cost_trend = await self._analyze_cost_trend(project_data['cost_items'])

        # Forecast final cost
        cost_forecast = await self._forecast_final_cost(project_data)

        return BudgetAnalysis(
            variance_percentage=budget_variance,
            trend=cost_trend,
            forecast=cost_forecast,
            status='under_budget' if budget_variance < -5 else 'on_budget' if budget_variance < 5 else 'over_budget'
        )

    async def _generate_recommendations(self, schedule: ScheduleAnalysis, budget: BudgetAnalysis, risk: RiskAnalysis) -> List[Recommendation]:
        """Generate AI-powered recommendations."""
        recommendations = []

        # Schedule recommendations
        if schedule.status == 'delayed':
            recommendations.append(Recommendation(
                type='schedule',
                priority='high',
                title='Address Schedule Delays',
                description='Project is behind schedule. Consider resource reallocation or scope adjustments.',
                actions=['review_critical_path', 'optimize_resource_allocation', 'update_milestones']
            ))

        # Budget recommendations
        if budget.status == 'over_budget':
            recommendations.append(Recommendation(
                type='budget',
                priority='high',
                title='Control Cost Overruns',
                description='Project costs are exceeding budget. Implement cost control measures.',
                actions=['review_cost_items', 'optimize_procurement', 'update_budget_forecast']
            ))

        # Risk recommendations
        if risk.overall_score > 0.7:
            recommendations.append(Recommendation(
                type='risk',
                priority='medium',
                title='Mitigate Project Risks',
                description='Multiple risk factors identified. Implement mitigation strategies.',
                actions=['review_risk_factors', 'develop_contingency_plans', 'increase_monitoring']
            ))

        return recommendations
```

---

## 🔄 Real-Time Features

### WebSocket Implementation

```python
# WebSocket manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.redis = RedisManager()

    async def connect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Handle WebSocket connection."""
        await websocket.accept()

        connection_key = f"{tenant_id}:{user_id}"
        self.active_connections[connection_key].append(websocket)

        try:
            while True:
                # Keep connection alive and handle client messages
                data = await websocket.receive_text()
                await self.handle_client_message(data, tenant_id, user_id)
        except WebSocketDisconnect:
            self.active_connections[connection_key].remove(websocket)

    async def broadcast_to_project(self, project_id: str, event: Dict):
        """Broadcast event to all project members."""
        # Get project members
        project_members = await self.get_project_members(project_id)

        # Send to all active connections
        for member_id in project_members:
            connection_key = f"{event['tenant_id']}:{member_id}"
            connections = self.active_connections.get(connection_key, [])

            for connection in connections:
                try:
                    await connection.send_json(event)
                except:
                    # Remove dead connections
                    connections.remove(connection)

        # Also publish to Redis for cross-instance communication
        await self.redis.publish(f"project:{project_id}", json.dumps(event))

    async def handle_client_message(self, data: str, tenant_id: str, user_id: str):
        """Handle messages from clients."""
        try:
            message = json.loads(data)

            if message['type'] == 'subscribe':
                # Handle subscription requests
                await self.handle_subscription(message, tenant_id, user_id)
            elif message['type'] == 'ping':
                # Handle ping/pong for connection health
                await self.send_pong(tenant_id, user_id)
        except json.JSONDecodeError:
            # Invalid JSON
            pass

# FastAPI WebSocket endpoint
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    tenant_id: str = Query(...)
):
    """WebSocket endpoint for real-time communication."""
    try:
        # Validate token and get user
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=4001)
            return

        # Connect to WebSocket manager
        await ws_manager.connect(websocket, tenant_id, user_id)

    except JWTError:
        await websocket.close(code=4001)
```

### Supabase Real-Time Integration

```python
# Real-time subscriptions
class RealtimeService:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

    async def subscribe_to_project(self, project_id: str, callback: Callable):
        """Subscribe to project changes."""
        channel = self.supabase.channel(f'project:{project_id}')

        channel.on(
            'postgres_changes',
            {
                'event': '*',
                'schema': 'public',
                'table': 'projects',
                'filter': f'id=eq.{project_id}'
            },
            callback
        ).subscribe()

        return channel

    async def subscribe_to_tasks(self, project_id: str, callback: Callable):
        """Subscribe to task changes."""
        channel = self.supabase.channel(f'tasks:{project_id}')

        channel.on(
            'postgres_changes',
            {
                'event': '*',
                'schema': 'public',
                'table': 'tasks',
                'filter': f'project_id=eq.{project_id}'
            },
            callback
        ).subscribe()

        return channel

    async def subscribe_to_messages(self, project_id: str, callback: Callable):
        """Subscribe to WhatsApp message changes."""
        channel = self.supabase.channel(f'messages:{project_id}')

        channel.on(
            'postgres_changes',
            {
                'event': '*',
                'schema': 'public',
                'table': 'whatsapp_messages',
                'filter': f'project_id=eq.{project_id}'
            },
            callback
        ).subscribe()

        return channel
```

---

## 📊 Performance Optimization

### Caching Strategy

```python
# Multi-level caching
class CacheManager:
    def __init__(self):
        self.redis = RedisManager()
        self.memory_cache = MemoryCache()

    async def get_project_data(self, project_id: str, user_id: str) -> Dict:
        """Get project data with caching."""
        cache_key = f"project:{project_id}:user:{user_id}"

        # Check memory cache first
        data = await self.memory_cache.get(cache_key)
        if data:
            return data

        # Check Redis cache
        data = await self.redis.get(cache_key)
        if data:
            # Populate memory cache
            await self.memory_cache.set(cache_key, data, ttl=300)
            return data

        # Fetch from database
        data = await self.fetch_project_data(project_id, user_id)

        # Cache in Redis (5 minutes) and memory (1 minute)
        await self.redis.setex(cache_key, 300, json.dumps(data))
        await self.memory_cache.set(cache_key, data, ttl=60)

        return data

    async def invalidate_project_cache(self, project_id: str):
        """Invalidate all caches for a project."""
        # Get all cache keys for this project
        project_keys = await self.redis.keys(f"project:{project_id}:*")

        # Delete from Redis
        if project_keys:
            await self.redis.delete(*project_keys)

        # Note: Memory cache invalidation would need separate handling
```

### Database Optimization

```python
# Optimized queries with proper indexing
class OptimizedQueries:
    @staticmethod
    async def get_project_dashboard_data(tenant_id: UUID, user_id: UUID, db: AsyncSession) -> List[Dict]:
        """Optimized dashboard query."""
        query = text("""
            SELECT
                p.id, p.name, p.status, p.progress_percentage, p.health_score,
                p.budget_total, p.actual_cost,
                COUNT(t.id) as total_tasks,
                COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
                SUM(c.actual_amount) as total_cost_incurred,
                MAX(wm.created_at) as last_message_at
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            LEFT JOIN cost_items c ON p.id = c.project_id
            LEFT JOIN whatsapp_messages wm ON p.id = wm.project_id
            INNER JOIN project_members pm ON p.id = pm.project_id
            WHERE p.tenant_id = :tenant_id
              AND pm.user_id = :user_id
              AND pm.is_active = true
              AND p.status IN ('active', 'planning')
            GROUP BY p.id, p.name, p.status, p.progress_percentage, p.health_score, p.budget_total, p.actual_cost
            ORDER BY p.health_score DESC, p.updated_at DESC
            LIMIT 50
        """)

        result = await db.execute(query, {"tenant_id": tenant_id, "user_id": user_id})
        return result.mappings().all()

    @staticmethod
    async def search_projects_ai(query_embedding: List[float], tenant_id: UUID, user_id: UUID, db: AsyncSession) -> List[Dict]:
        """AI-powered semantic search for projects."""
        query = text("""
            SELECT
                p.id, p.name, p.description,
                1 - (p.embedding <=> :query_embedding) as semantic_similarity,
                ts_rank(p.search_vector, plainto_tsquery('english', 'construction project')) as text_rank,
                CASE WHEN p.project_manager_id = :user_id THEN 1 ELSE 0 END as is_manager
            FROM projects p
            INNER JOIN project_members pm ON p.id = pm.project_id
            WHERE p.tenant_id = :tenant_id
              AND pm.user_id = :user_id
              AND pm.is_active = true
              AND 1 - (p.embedding <=> :query_embedding) > 0.7
            ORDER BY (semantic_similarity * 0.6 + text_rank * 0.3 + is_manager * 0.1) DESC
            LIMIT 20
        """)

        result = await db.execute(query, {
            "query_embedding": query_embedding,
            "tenant_id": tenant_id,
            "user_id": user_id
        })
        return result.mappings().all()
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Example unit tests
@pytest.mark.asyncio
async def test_create_project():
    """Test project creation."""
    project_data = ProjectCreate(
        name="Test Project",
        budget_total=100000,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31)
    )

    # Mock database
    mock_db = AsyncMock()

    # Call service
    result = await project_service.create_project(project_data, mock_db, test_user)

    # Assertions
    assert result.name == "Test Project"
    assert result.tenant_id == test_user.tenant_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_ai_message_processing():
    """Test AI message processing pipeline."""
    message = WhatsAppMessage(content="Task completed successfully")

    # Mock AI service
    mock_ai = AsyncMock()
    mock_ai.process_message.return_value = AIAnalysis(
        intent="task_complete",
        confidence=0.95,
        entities={"tasks": ["task"]},
        sentiment=0.8,
        urgency="low"
    )

    # Process message
    result = await ai_service.process_message(message, mock_db)

    # Assertions
    assert result.intent == "task_complete"
    assert result.confidence > 0.9
    mock_ai.process_message.assert_called_once_with(message, mock_db)
```

### Integration Tests

```python
# API integration tests
def test_create_project_api(client, test_user_token):
    """Test project creation via API."""
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Integration Test Project",
            "budget_total": 50000,
            "start_date": "2025-01-01",
            "end_date": "2025-06-01"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Integration Test Project"
    assert "id" in data

def test_whatsapp_webhook_processing(client, whatsapp_signature):
    """Test WhatsApp webhook processing."""
    webhook_payload = {
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "id": "test_message_id",
                        "from": "1234567890",
                        "text": {"body": "Hello from WhatsApp"},
                        "timestamp": "1638360000"
                    }]
                }
            }]
        }]
    }

    response = client.post(
        "/api/v1/whatsapp/webhook",
        json=webhook_payload,
        headers={"X-Hub-Signature-256": whatsapp_signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

### Performance Tests

```python
# Load testing
@pytest.mark.asyncio
async def test_api_performance(benchmark):
    """Test API performance under load."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Benchmark project listing
        result = await benchmark(
            client.get,
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {test_token}"}
        )

        assert result.status_code == 200
        # Assert response time < 100ms
        assert result.elapsed < timedelta(milliseconds=100)
```

---

## 🚀 Deployment Configuration

### Railway Deployment

```yaml
# railway.toml
[build]
builder = "
