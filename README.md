# GitHub Automation Architecture

Eine vollständig containerisierte, interne Fullstack-Automatisierungsarchitektur für GitHub-basierte Softwareentwicklung.

## 🚀 Übersicht

Diese Architektur implementiert ein Multi-Agenten-System, das den gesamten Entwicklungsprozess automatisiert, von der Anforderungsanalyse bis zur QA-Validierung.

### Hauptkomponenten

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Issues (Source)                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Requirements Engineer Agent                        │
│  • Analysiert neue Issues                                        │
│  • Stellt Klärungsfragen                                         │
│  • Markiert als "ready_for_dev"                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              MQTT Event Bus (Ereignissystem)                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Frontend  │   │   Backend   │   │    QA       │
│   Agent     │   │   Agent     │   │   Agent     │
│             │   │             │   │             │
│ • Generiert │   │ • Generiert │   │ • Validiert │
│   UI-Code   │   │   API-Code  │   │   Code      │
│ • Erstellt │   │ • Erstellt │   │ • Führt    │
│   Branches  │   │   Branches │   │   Tests    │
└─────────────┘   └─────────────┘   └─────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub PRs & Merge                           │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Projektstruktur

```
github_setup/
├── agents/                     # Agent-Implementierungen
│   ├── requirements_engineer/  # Requirements Engineer Agent
│   ├── frontend_agent/         # Frontend Code Generator
│   ├── backend_agent/          # Backend Code Generator
│   └── qa_agent/              # QA & Code Review Agent
├── common/                     # Gemeinsame Module
│   ├── config_loader.py        # Konfigurations-Management
│   ├── event_types.py          # Event & Status Definitionen
│   ├── mqtt_client.py          # MQTT Event Bus Client
│   ├── github_client.py        # GitHub API Client
│   └── llm_client.py           # LLM API Integration
├── config/                     # Konfigurationsdateien
│   ├── config.yaml             # Hauptkonfiguration
│   └── .env.example            # Umgebungsvariablen-Vorlage
├── docker/                     # Docker-Konfiguration
│   ├── docker-compose.yml      # Container-Orchestrierung
│   └── mosquitto/              # MQTT Broker Konfiguration
├── .github/
│   ├── workflows/              # GitHub Actions
│   │   └── ci-cd.yml           # CI/CD Pipeline
│   └── SECRETS.md              # Secrets Management Guide
└── tests/                     # Unit Tests
```

## 🛠️ Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- GitHub Personal Access Token
- LLM API Key (OpenAI oder Anthropic)

### Installation

1. **Repository klonen**
```bash
git clone <repository-url>
cd github_setup
```

2. **Umgebungsvariablen konfigurieren**
```bash
cp config/.env.example .env
# Bearbeiten Sie .env mit Ihren API-Keys
```

3. **Docker Container starten**
```bash
cd docker
docker compose up -d
```

4. **Status prüfen**
```bash
docker compose ps
```

## ⚙️ Konfiguration

### config/config.yaml

Die Hauptkonfigurationsdatei steuert alle Aspekte des Systems:

```yaml
github:
  owner: "your-org"
  repo: "your-repo"
  token: "${GITHUB_TOKEN}"

mqtt:
  broker: "mqtt://mqtt-broker:1883"

llm:
  provider: "openai"
  model: "gpt-4"

agents:
  requirements_engineer:
    poll_interval: 30
    labels:
      new: "needs-analysis"
      ready: "ready_for_dev"
```

## 🔄 Workflow

### 1. Issue erstellen

Erstellen Sie ein GitHub Issue mit der `needs-analysis` Label:

```markdown
## Titel
Neue Benutzer-Authentifizierung implementieren

## Beschreibung
Wir möchten eine OAuth2-Authentifizierung für Benutzer implementieren.
Benutzer sollen sich mit Google und GitHub anmelden können.
```

### 2. Requirements Engineer Agent

Der Agent analysiert das Issue und stellt automatisch Klärungsfragen:

```
🤖 Requirements Engineer Agent

Ich habe Ihre Anforderung analysiert und benötige einige Präzisierungen:

### ❓ Klärungsfragen:
1. Welche OAuth2-Provider sollen unterstützt werden?
2. Sollen bestehende Benutzerkonten migriert werden?
3. Welche Berechtigungen sind für die OAuth-Token erforderlich?
```

### 3. Antworten und Markieren

Nachdem Sie die Fragen beantwortet haben, markiert der Agent das Issue als `ready_for_dev`.

### 4. Code-Generierung

Je nach Label generieren spezialisierte Agenten den Code:

- **Frontend-Label**: Frontend-Agent erstellt Flutter-UI-Komponenten
- **Backend-Label**: Backend-Agent erstellt REST-API-Endpunkte

### 5. QA-Validierung

Der QA-Agent:
- Führt automatisierte Tests durch
- Validiert die Code-Qualität
- Erstellt Pull Requests

## 📡 Event-System (MQTT)

### Topics

| Topic | Beschreibung |
|-------|-------------|
| `github/automation/events` | Alle Agent-Events |
| `github/automation/status` | Statusänderungen |
| `github/automation/issues` | Issue-bezogene Events |

### Event-Typen

```python
EventType.ISSUE_CREATED    # Neues Issue erstellt
EventType.STATUS_CHANGED   # Status geändert
EventType.CODE_GENERATED   # Code generiert
EventType.CODE_COMMITTED    # Code committet
EventType.QA_PASSED         # QA bestanden
EventType.QA_FAILED         # QA nicht bestanden
```

## 🔐 Sicherheit

### Secrets-Management

Alle API-Keys und Tokens werden über Umgebungsvariablen verwaltet:

```bash
# Nie in Code oder Config committen!
GITHUB_TOKEN=ghp_...
LLM_API_KEY=sk-...
```

### GitHub Actions Secrets

Konfigurieren Sie Secrets in:
**Repository Settings → Secrets and variables → Actions**

Erforderliche Secrets:
- `GITHUB_TOKEN`
- `LLM_API_KEY`

## 🧪 Testing

### Unit Tests ausführen

```bash
cd agents/requirements_engineer
pip install -r requirements.txt
pytest tests/ -v
```

### Integrationstests

```bash
cd docker
docker compose up -d
# Warten Sie 30 Sekunden
docker compose exec requirements-engineer pytest tests/ -v
```

## 🚢 Deployment

### Produktions-Deployment

```bash
cd docker
docker compose pull
docker compose up -d
```

### CI/CD Pipeline

Die GitHub Actions Pipeline wird automatisch bei:
- Push auf `main` oder `develop`
- Pull Requests

ausgeführt und baut alle Agenten-Container.

## 📊 Monitoring

### Grafana Dashboard

Nach dem Start ist das Monitoring-Dashboard unter:
```
http://localhost:3000
```
verfügbar (Standard-Login: `admin`/`admin`).

### MQTT Websocket

Für Debugging können Sie MQTT-Nachrichten über:
```
http://localhost:9001
```
beobachten.

## 🔧 Erweiterung

### Neuen Agenten hinzufügen

1. Verzeichnis erstellen:
```bash
mkdir agents/new_agent
```

2. `agent.py` implementieren:
```python
from common.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def process_issue(self, issue):
        # Ihre Logik
        pass
```

3. Dockerfile erstellen
4. Zu `docker-compose.yml` hinzufügen

### LLM-Provider wechseln

In `config/config.yaml`:
```yaml
llm:
  provider: "anthropic"  # oder "openai"
  model: "claude-3-sonnet"
  api_key: "${LLM_API_KEY}"
```

## 📝 Lizenz

Interner Gebrauch. Alle Rechte vorbehalten.

## 🤝 Support

Bei Fragen oder Problemen:
- Issue im Repository erstellen
- Dokumentation in `.github/` konsultieren
