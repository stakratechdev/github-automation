# 🚀 StakraTech AI Development Platform

Eine vollständig containerisierte, KI-gesteuerte Fullstack-Entwicklungsplattform für Flutter-Web-Anwendungen mit Cloudflare-Infrastruktur.

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#-überblick)
2. [Architektur](#-architektur)
3. [Schnellstart](#-schnellstart)
4. [Projektstruktur](#-projektstruktur)
5. [AI Agenten System](#-ai-agenten-system)
6. [StakraTech Design System](#-stakratech-design-system)
7. [Deployment](#-deployment)
8. [Entwicklung](#-entwicklung)
9. [Dokumentation](#-dokumentation)

---

## 🌟 Überblick

Diese Plattform kombiniert:

- **🤖 Multi-Agenten KI-System** - Automatisiert den gesamten Entwicklungsprozess
- **🎨 StakraTech Design System** - Dark-first, Electric Blue Gradient UI
- **🐦 Flutter Web** - Cross-platform mobile & web Apps
- **☁️ Cloudflare Infrastruktur** - Workers, Pages, D1 Database
- **🐳 Docker Containerisierung** - Vollständig containerisierte Entwicklung
- **🔄 GitHub Actions CI/CD** - Automatisierte Builds & Deployment

### Workflow

```
GitHub Issue → Requirements Engineer → Solution Architect 
    → Frontend/Backend Dev → QA Engineer → DevOps 
    → Cloudflare Pages Deployment
```

---

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Issues / Features                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              AI Agent Orchestrator (Claude Code)                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ .claude/agents/                                         │    │
│  │ ├── requirements-engineer.md  → Feature Specs          │    │
│  │ ├── solution-architect.md     → Tech Design           │    │
│  │ ├── frontend-dev.md           → Flutter UI             │    │
│  │ ├── backend-dev.md            → Cloudflare Workers    │    │
│  │ ├── qa-engineer.md           → Testing               │    │
│  │ └── devops.md                 → Deployment            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Containerisierte Agenten (Docker)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│  │ Requirements │ │ Frontend    │ │ Backend     │             │
│  │ Engineer     │ │ Agent       │ │ Agent       │             │
│  └─────────────┘ └─────────────┘ └─────────────┘             │
│  ┌─────────────┐ ┌─────────────┐                            │
│  │ QA Agent    │ │ DevOps      │                            │
│  └─────────────┘ └─────────────┘                            │
└─────────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare Infrastructure                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ Cloudflare   │ │ Cloudflare   │ │ Cloudflare   │         │
│  │ Pages        │ │ Workers      │ │ D1 Database  │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Schnellstart

### 1. Repository klonen

```bash
git clone https://github.com/stakratechdev/github-automation.git
cd github-automation
```

### 2. Umgebung konfigurieren

```bash
cp config/.env.example .env
# Bearbeiten Sie .env mit Ihren API-Keys
```

### 3. Docker starten

```bash
cd docker
docker compose up -d
```

### 4. Ersten Feature starten

```bash
# Mit Claude Code:
"Read .claude/agents/requirements-engineer.md and create a feature spec for user authentication"
```

---

## 📁 Projektstruktur

```
github-automation/
├── agents/                      # Docker-Agenten
│   ├── requirements_engineer/  # Requirements Engineer
│   ├── frontend_agent/         # Frontend Code Generator
│   ├── backend_agent/         # Backend Code Generator
│   └── qa_agent/              # QA & Testing Agent
├── common/                     # Shared Python modules
│   ├── config_loader.py        # Konfiguration
│   ├── event_types.py          # Event definitions
│   ├── mqtt_client.py          # MQTT Event Bus
│   ├── github_client.py        # GitHub API
│   └── llm_client.py           # LLM Integration
├── design/                     # Flutter Design System
│   ├── stakra_colors.dart     # Farbpalette
│   ├── stakra_typography.dart  # Typografie
│   ├── stakra_theme.dart       # Material3 Theme
│   └── stakra_components.dart  # Premium Components
├── .claude/                    # AI Agent Prompts
│   └── agents/
│       ├── requirements-engineer.md
│       ├── solution-architect.md
│       ├── frontend-dev.md
│       ├── backend-dev.md
│       ├── qa-engineer.md
│       └── devops.md
├── docker/                     # Containerisierung
│   ├── docker-compose.yml
│   └── mosquitto/
├── config/                     # Konfiguration
│   ├── config.yaml
│   └── .env.example
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── SECRETS.md
├── features/                   # Feature Specifications
│   └── README.md
└── README.md
```

---

## 🤖 AI Agenten System

### Verfügbare Agenten

| Agent | Beschreibung | Prompt |
|-------|-------------|--------|
| **Requirements Engineer** | Feature Specs mit interaktiven Fragen | `requirements-engineer.md` |
| **Solution Architect** | PM-freundliches Tech Design | `solution-architect.md` |
| **Frontend Developer** | Flutter UI mit StakraTech Design | `frontend-dev.md` |
| **Backend Developer** | Cloudflare Workers + D1 | `backend-dev.md` |
| **QA Engineer** | Testing & Validation | `qa-engineer.md` |
| **DevOps** | Cloudflare Pages Deployment | `devops.md` |

### Verwendung mit Claude Code

```bash
# 1. Feature Spec erstellen
"Read .claude/agents/requirements-engineer.md and create a feature spec for user authentication"

# 2. Tech Design erstellen
"Read .claude/agents/solution-architect.md and design architecture for /features/user-auth.md"

# 3. Frontend implementieren
"Read .claude/agents/frontend-dev.md and implement /features/user-auth.md"

# 4. Backend implementieren
"Read .claude/agents/backend-dev.md and implement /features/user-auth.md"

# 5. QA Tests schreiben
"Read .claude/agents/qa-engineer.md and test /features/user-auth.md"

# 6. Deployen
"Read .claude/agents/devops.md and deploy to Cloudflare Pages"
```

### Feature Specification Format

Alle Features werden in `/features/` gespeichert:

```
features/
├── PROJ-1-user-auth.md          # Feature Spec
├── PROJ-1-user-auth-tech.md     # Tech Design
├── PROJ-1-user-auth-test.md     # Test Results
└── README.md                     # Feature Overview
```

---

## 🎨 StakraTech Design System

### Farbpalette

```dart
import 'package:github_automation/design/stakra_colors.dart';

// Primary
STColors.primary        // #1E6CFF - Electric Blue
STColors.primaryDark    // #0D47A1
STColors.accent        // #00B3FF

// Backgrounds
STColors.background     // #0A0F1C
STColors.surface        // #111827

// Text
STColors.textPrimary    // #E5E7EB
STColors.textMuted     // #9CA3AF

// Gradient
STColors.primaryGradient
```

### Premium Components

```dart
import 'package:github_automation/design/stakra_components.dart';

// Gradient Button
STGradientButton(
    text: 'Get Started',
    onPressed: () => print('Clicked!'),
)

// Glass Card
STGlassCard(
    child: Column(
        children: [/* content */],
    ),
)

// KPI Card
STKpiCard(
    title: 'Active Users',
    value: '1,234',
    change: '+12%',
    icon: Icons.people,
)

// Issue Card
STIssueCard(
    number: '123',
    title: 'Implement OAuth2',
    status: 'ready_for_dev',
    labels: ['frontend', 'feature'],
    onTap: () => navigateToIssue(),
)

// Status Badge
STStatusBadge(status: 'in_progress')
```

### Theme Usage

```dart
import 'package:github_automation/design/stakra_theme.dart';

MaterialApp(
    theme: STTheme.dark(),
    home: HomeScreen(),
);
```

---

## ☁️ Deployment

### Cloudflare Pages

Die Plattform ist für **Cloudflare Pages** optimiert:

```bash
# Build
flutter build web --web-renderer html

# Deploy mit Wrangler
npx wrangler pages deploy ./build/web
```

### GitHub Actions CI/CD

Automatische Deployments bei Push auf `main`:

```yaml
# .github/workflows/ci-cd.yml
- name: Deploy to Cloudflare Pages
  uses: cloudflare/pages-action@v1
  with:
      apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      projectName: github-automation
      directory: build/web
```

### Environment Variables

```bash
# Erforderlich
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=

# Optional
SENTRY_DSN=
```

---

## 💻 Entwicklung

### Lokale Entwicklung

```bash
# Python Agenten
cd agents/requirements_engineer
pip install -r requirements.txt
python -m agents.requirements_engineer.agent

# Flutter Web
flutter pub get
flutter build web --web-renderer html
flutter run -d chrome
```

### Docker Entwicklung

```bash
# Alle Dienste starten
cd docker
docker compose up -d

# Logs anzeigen
docker compose logs -f

# Einzelne Dienste
docker compose exec requirements-engineer bash
```

### Testing

```bash
# Unit Tests
pytest tests/ -v --cov

# Integration Tests
docker compose exec requirements-engineer pytest tests/ -v

# Coverage Report
pytest --cov=common --cov-report=html
```

---

## 📖 Dokumentation

| Dokumentation | Beschreibung |
|--------------|-------------|
| [README.md](README.md) | Hauptübersicht |
| [.github/SECRETS.md](.github/SECRETS.md) | Secrets Management |
| [.claude/agents/*.md](.claude/agents/) | AI Agent Prompts |
| [design/](design/) | Flutter Design System |

### API Referenz

| Service | Endpoint | Beschreibung |
|---------|----------|-------------|
| GitHub API | `api.github.com` | Issue Management |
| MQTT | `mqtt-broker:1883` | Event Bus |
| Cloudflare | `api.cloudflare.com` | Workers & Pages |

---

## 🔐 Sicherheit

### Secrets Management

Alle Secrets werden über Umgebungsvariablen verwaltet:

```bash
# GitHub Secrets (Repository Settings)
GITHUB_TOKEN=
LLM_API_KEY=
CLOUDFLARE_API_TOKEN=

# Environment Variables (.env)
GITHUB_OWNER=stakratechdev
GITHUB_REPO=your-repo
```

### Security Best Practices

- ✅ Keine Secrets im Code
- ✅ Environment Variables für alles
- ✅ GitHub Secrets für CI/CD
- ✅ Cloudflare Workers mit minimalen Permissions

---

## 🛠️ Erweiterung

### Neuen Agenten hinzufügen

1. Prompt erstellen: `.claude/agents/new-agent.md`
2. Docker Agent erstellen: `agents/new_agent/`
3. Zu `docker-compose.yml` hinzufügen
4. CI/CD Pipeline aktualisieren

### Neue Features

```bash
# Feature Spec erstellen
"Read .claude/agents/requirements-engineer.md and create a feature spec for [Feature Name]"
```

---

## 📝 Lizenz

Interner Gebrauch. Alle Rechte vorbehalten.

---

## 🤝 Support

Bei Fragen:
- GitHub Issues erstellen
- Claude Code Agenten konsultieren
- Dokumentation in `.claude/agents/` lesen

---

**🚀 Built with StakraTech AI Development Platform**
