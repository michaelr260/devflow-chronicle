---
description: Repository Information Overview
alwaysApply: true
---

# DevFlow Chronicle Information

## Summary

DevFlow Chronicle is an AI-powered development workflow analyzer that uses Claude AI to intelligently analyze git commit history and generate multiple report formats. It provides features like commit quality scoring, temporal analysis, semantic search, multi-repository support, webhook integration, and smart caching to reduce API costs.

## Structure

The repository is organized with:

- **src/**: Core Python modules including analyzers, parsers, generators, and managers
- **config/**: Configuration presets for different analysis profiles (daily, weekly, etc.)
- **tests/**: Test directory for pytest-based testing
- **.github/workflows/**: CI/CD pipeline configurations
- **Docker files**: Multi-stage Dockerfile and docker-compose configuration

## Language & Runtime

**Language**: Python
**Version**: Python 3.11
**Build System**: pip (Python package manager)
**Package Manager**: pip with requirements.txt

## Dependencies

**Main Dependencies**:

- `anthropic==0.72.0` - Claude AI API integration
- `gitpython==3.1.40` - Git repository parsing and analysis
- `sentence-transformers==2.2.2` - Vector embeddings for semantic search (RAG)
- `faiss-cpu==1.12.0` - Vector similarity search
- `numpy==1.24.3` - Numerical computing
- `flask==3.0.0` - Webhook server framework
- `gunicorn==21.2.0` - Production WSGI server
- `pyyaml==6.0.1` - YAML configuration parsing
- `python-dotenv==1.0.0` - Environment variable management
- `python-dateutil==2.8.2` - Date/time utilities
- `schedule==1.2.0` - Task scheduling
- `slack-sdk==3.23.0` - Slack integration (optional)

## Build & Installation

```bash
pip install -r requirements.txt
```

For Docker deployment:

```bash
docker-compose build
docker-compose up
```

## Docker

**Dockerfile**: `Dockerfile` (multi-stage build)
**Build Image**: `python:3.11-slim`
**Configuration**: Multi-stage optimization with builder stage for dependency installation and production stage with minimal footprint
**Entry Point**: `python src/main.py`
**Compose File**: `docker-compose.yml`

## Main Entry Point

**Primary Application**: `src/main.py` - Command-line interface for DevFlow Chronicle
**Key Modules**:

- `claude_analyzer.py` - Claude AI analysis engine
- `git_parser.py` - Git commit and history parsing
- `narrative_generator.py` - Report generation in multiple formats
- `quality_scorer.py` - Commit quality evaluation
- `cache_manager.py` - API response caching
- `webhook_server.py` - Flask-based webhook server for auto-generation
- `scheduler.py` - Scheduled analysis execution
- `multi_repo_analyzer.py` - Multi-repository analysis support
- `config.py` - Configuration management

## Configuration

**Environment Variables**: `.env` file with `ANTHROPIC_API_KEY`
**Configuration Presets**: `config/presets.yaml` - Defines profiles for daily, weekly, and custom analysis patterns

## Testing

**Framework**: pytest
**Coverage Tool**: pytest-cov
**Test Location**: `tests/` directory (currently no test files)
**Run Command**:

```bash
pytest tests/ --cov=src
```

**Code Quality Tools**:

- `black` - Code formatting
- `pylint` - Linting and code analysis

## Output Formats

The application generates multiple report types:

- Standup reports for daily reviews
- Technical logs for detailed changes
- Weekly digests for summaries
- Insights reports for patterns and metrics
