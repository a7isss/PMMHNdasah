"""
WebSocket router for WhatsApp PM System v3.0 (Gamma)
Real-time communication endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
import structlog
from typing import Optional
import json

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        key = f"{tenant_id}:{user_id}"

        if key not in self.active_connections:
            self.active_connections[key] = []

        self.active_connections[key].append(websocket)
        logger.info("WebSocket connected", tenant_id=tenant_id, user_id=user_id)

    def disconnect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Remove a WebSocket connection."""
        key = f"{tenant_id}:{user_id}"

        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)

            # Clean up empty lists
            if not self.active_connections[key]:
                del self.active_connections[key]

        logger.info("WebSocket disconnected", tenant_id=tenant_id, user_id=user_id)

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Broadcast message to all connections in a tenant."""
        for key, connections in self.active_connections.items():
            if key.startswith(f"{tenant_id}:"):
                for connection in connections:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error("Failed to send message to connection", error=str(e))

    async def send_to_user(self, tenant_id: str, user_id: str, message: dict):
        """Send message to specific user."""
        key = f"{tenant_id}:{user_id}"
        connections = self.active_connections.get(key, [])

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send message to user", error=str(e))

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    tenant_id: str = Query(None, description="Tenant ID (optional, extracted from token)")
):
    """
    WebSocket endpoint for real-time communication.

    Supports real-time updates for:
    - Project changes
    - Task updates
    - WhatsApp messages
    - AI insights
    - Notifications
    """
    user_id = None

    try:
        # Validate token and extract user info
        from ..utils.security import decode_token

        payload = decode_token(token)
        user_id = payload.get("user_id") or payload.get("sub")
        token_tenant_id = payload.get("tenant_id")

        # Use provided tenant_id or extract from token
        final_tenant_id = tenant_id or token_tenant_id

        if not user_id or not final_tenant_id:
            await websocket.close(code=4001)  # Unauthorized
            return

        # Connect to manager
        await manager.connect(websocket, final_tenant_id, user_id)

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                await handle_websocket_message(
                    message, websocket, final_tenant_id, user_id
                )

            except json.JSONDecodeError:
                # Invalid JSON
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        if user_id and final_tenant_id:
            manager.disconnect(websocket, final_tenant_id, user_id)

    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        if user_id and final_tenant_id:
            manager.disconnect(websocket, final_tenant_id, user_id)


async def handle_websocket_message(message: dict, websocket: WebSocket, tenant_id: str, user_id: str):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")

    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({
            "type": "pong",
            "timestamp": "2025-11-02T22:16:00Z"
        })

    elif message_type == "subscribe":
        # Handle subscription requests
        subscriptions = message.get("subscriptions", [])
        await websocket.send_json({
            "type": "subscribed",
            "subscriptions": subscriptions
        })

    elif message_type == "unsubscribe":
        # Handle unsubscription requests
        subscriptions = message.get("subscriptions", [])
        await websocket.send_json({
            "type": "unsubscribed",
            "subscriptions": subscriptions
        })

    else:
        # Unknown message type
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })


# Export the router
ws_router = router
