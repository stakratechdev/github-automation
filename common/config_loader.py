"""
Configuration Loader for GitHub Automation Architecture.
Loads configuration from YAML files and environment variables.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub-specific configuration."""
    owner: str = "your-org"
    repo: str = "your-repo"
    token: str = ""
    api_url: str = "https://api.github.com"
    webhook_secret: str = ""


@dataclass
class MQTTConfig:
    """MQTT broker configuration."""
    broker: str = "mqtt://mqtt-broker:1883"
    username: str = ""
    password: str = ""
    client_id_prefix: str = "github-agent"
    topics: Dict[str, str] = field(default_factory=lambda: {
        "events": "github/automation/events",
        "status": "github/automation/status",
        "issues": "github/automation/issues"
    })


@dataclass
class LLMConfig:
    """LLM API configuration."""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000


@dataclass
class AgentLabels:
    """Labels configuration for an agent."""
    new: str = ""
    ready: str = ""
    in_progress: str = ""
    blocked: str = ""


@dataclass
class AgentConfig:
    """Individual agent configuration."""
    name: str = ""
    poll_interval: int = 60
    labels: AgentLabels = field(default_factory=AgentLabels)


@dataclass
class Config:
    """Main configuration container."""
    github: GitHubConfig = field(default_factory=GitHubConfig)
    mqtt: MQTTConfig = field(default_factory=MQTTConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        config = cls()
        
        if 'github' in data:
            config.github = GitHubConfig(**data['github'])
        
        if 'mqtt' in data:
            config.mqtt = MQTTConfig(**data['mqtt'])
        
        if 'llm' in data:
            config.llm = LLMConfig(**data['llm'])
        
        if 'agents' in data:
            for name, agent_data in data['agents'].items():
                if 'labels' in agent_data:
                    agent_data['labels'] = AgentLabels(**agent_data['labels'])
                config.agents[name] = AgentConfig(**agent_data)
        
        return config


def _resolve_env_vars(value: Any) -> Any:
    """Resolve environment variables in config values."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        return os.environ.get(env_var, "")
    return value


def _process_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process dictionary to resolve environment variables."""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _process_dict(value)
        elif isinstance(value, list):
            result[key] = [_resolve_env_vars(item) for item in value]
        else:
            result[key] = _resolve_env_vars(value)
    return result


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file. Defaults to config/config.yaml
        
    Returns:
        Config object with all settings
    """
    if config_path is None:
        config_path = os.environ.get(
            'CONFIG_PATH',
            str(Path(__file__).parent.parent / 'config' / 'config.yaml')
        )
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_file}")
        return Config()
    
    try:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Resolve environment variables
        data = _process_dict(data)
        
        config = Config.from_dict(data)
        logger.info(f"Configuration loaded from {config_file}")
        return config
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return load_config()
