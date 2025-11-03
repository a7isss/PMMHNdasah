# Hndasah Backend

Hndasah PM System Backend - Multi-tenant project management with AI integration

## Features

- Multi-tenant architecture with isolated company data
- AI-powered message processing and insights
- WhatsApp integration for client communication
- Project management with task scheduling and Gantt charts
- Cost management and procurement workflows
- SuperAdmin dashboard for system management
- Real-time collaboration features

## Development

This project uses modern Python tooling with `uv` for dependency management.

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run the development server
uv run uvicorn src.hndasah_backend.main:app --reload
```

### Testing

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## API Documentation

When running the server, visit `/api/docs` for interactive API documentation.

## Deployment

This backend is configured for deployment on Railway with Nixpacks. The `railway.json` file contains the deployment configuration.
