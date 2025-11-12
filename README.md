# DevFlow Chronicle

> AI-powered development workflow analyzer with Docker support

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-AI-orange.svg?style=for-the-badge)](https://www.anthropic.com/)

## Features

- ** AI-Powered Analysis**: Claude analyzes your git history intelligently
- ** Multiple Output Formats**: Standup, technical logs, weekly digests, insights
- ** Personal Style Matching**: Learns your writing style from commits
- ** Quality Scoring**: Rates commit quality with improvement suggestions
- ** Temporal Analysis**: Identifies productivity patterns
- ** Semantic Search**: Find similar past work (RAG preview!)
- ** Multi-Repository**: Analyze multiple projects
- ** Docker Ready**: Fully containerized for easy deployment
- ** Webhook Support**: Auto-generate reports on git push
- ** Smart Caching**: Reduces API costs

## Quick Start (Docker)

### 1. Setup

```bash
# Clone repository
git clone https://github.com/yourusername/devflow-chronicle.git
cd devflow-chronicle

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Build

```bash
docker-compose build
```

### 3. Run

```bash
# Analyze current directory
docker-compose up devflow

# Analyze specific repository
REPO_PATH=/path/to/your/repo docker-compose up devflow

# Generate specific formats
docker-compose run devflow /repo -f standup weekly
```

## Usage Examples

### Basic Analysis

```bash
# Current directory, default settings
docker-compose up devflow

# Custom commit limit
docker-compose run devflow /repo -n 50

# Specific formats only
docker-compose run devflow /repo -f standup insights
```

### With Configuration Presets

```bash
# Daily standup
docker-compose run devflow /repo --preset daily

# Weekly review
docker-compose run devflow /repo --preset weekly

# Performance review prep
docker-compose run devflow /repo --preset review
```

### Webhook Server (Auto-generate on push)

```bash
# Start webhook server
docker-compose up webhook

# Configure in GitHub:
# Settings → Webhooks → Add webhook
# URL: http://your-server:5000/webhook/analyze
# Content type: application/json
# Events: Just the push event
```

### Scheduled Analysis

```bash
# Run daily at 9 AM
docker-compose up scheduler
```

## Output Formats

### 1. Standup Report

Quick daily update format for team standups

- Yesterday's work
- Today's plans
- Blockers

### 2. Technical Log

Detailed technical documentation

- Technical decisions
- Implementation details
- Challenges and solutions

### 3. Weekly Digest

High-level summary for weekly updates

- Accomplishments
- Metrics and statistics
- Focus areas

### 4. Insights Report

AI-powered productivity analysis

- Work patterns
- Effectiveness observations
- Improvement suggestions

## ️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
CACHE_ENABLED=true
DEFAULT_COMMIT_LIMIT=20
SESSION_GAP_HOURS=3

# Webhook (optional)
WEBHOOK_ENABLED=false
WEBHOOK_PORT=5000

# Slack (optional)
SLACK_ENABLED=false
SLACK_TOKEN=xoxb-your-token
SLACK_CHANNEL=#standup
```

### Configuration Presets

Edit `config/presets.yaml` to customize presets:

```yaml
profiles:
  daily:
    commits: 10
    formats: [standup]
    style: casual

  weekly:
    commits: 50
    formats: [weekly, insights]
    style: formal
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env

# Run
python src/main.py
```

### Running Tests

```bash
pytest tests/ --cov=src
```

### Code Quality

```bash
# Format
black src/

# Lint
pylint src/

# Type check
mypy src/
```

## ️ Architecture

```
DevFlow Chronicle
├── Git Parser          # Extract commit data
├── Claude Analyzer     # AI-powered analysis
│   ├── Style Learning
│   ├── Categorization
│   ├── Quality Scoring
│   └── Insights Generation
├── Vector Search       # Semantic search (RAG preview)
├── Cache Manager       # API response caching
├── Narrative Generator # Output formatting
└── Multi-Repo Analyzer # Cross-project analysis
```

## Roadmap

- [x] Core analysis engine
- [x] Docker containerization
- [x] Multi-repository support
- [x] Webhook automation
- [x] Vector search (RAG preview)
- [ ] VS Code extension
- [ ] GitHub App
- [ ] Team dashboard
- [ ] ML-based predictions

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file

## Acknowledgments

- Built with [Claude](https://www.anthropic.com/) AI
- Powered by [Anthropic API](https://docs.anthropic.com/)
- Part of Claude Code Expert Learning Path

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/devflow-chronicle/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/devflow-chronicle/discussions)

---

**Built with ️ using Claude Code**
