"""
LLM Client for Code Generation.
Integrates with external LLM APIs (OpenAI, Anthropic).
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config_loader import LLMConfig, get_config

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    usage: Dict[str, int]
    success: bool
    error: Optional[str] = None
    
    @property
    def token_count(self) -> int:
        """Get total token count."""
        return self.usage.get('total_tokens', 0)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate content from prompt."""
        pass
    
    @abstractmethod
    def generate_code(
        self,
        prompt: str,
        context: str,
        **kwargs
    ) -> LLMResponse:
        """Generate code from prompt with context."""
        pass


class OpenAIClient(LLMProvider):
    """OpenAI API client."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize OpenAI client."""
        self.config = config or get_config().llm
        
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        self.base_url = "https://api.openai.com/v1"
    
    def _request(self, endpoint: str, data: Dict) -> Dict:
        """Make authenticated API request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate content using GPT model."""
        model = kwargs.get('model', self.config.model)
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            result = self._request("/chat/completions", data)
            
            content = result['choices'][0]['message']['content']
            
            return LLMResponse(
                content=content,
                model=result['model'],
                usage=result.get('usage', {}),
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=str(e)
            )
    
    def generate_code(
        self,
        prompt: str,
        context: str,
        **kwargs
    ) -> LLMResponse:
        """Generate code with context."""
        full_prompt = f"""
Context:
{context}

Task:
{prompt}

Please provide the code implementation following the coding guidelines.
Return only the code without additional explanations.
"""
        
        model = kwargs.get('model', self.config.model)
        temperature = 0.2  # Lower temperature for code generation
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert software developer. Generate clean, well-structured code following best practices."
                },
                {"role": "user", "content": full_prompt}
            ],
            "temperature": temperature,
            "max_tokens": self.config.max_tokens
        }
        
        try:
            result = self._request("/chat/completions", data)
            
            content = result['choices'][0]['message']['content']
            
            # Extract code block if present
            if "```" in content:
                # Get content between code blocks
                lines = content.split("```")
                if len(lines) >= 2:
                    # Get the first code block content
                    code_block = lines[1]
                    # Remove language identifier if present
                    if "\n" in code_block:
                        code_block = code_block.split("\n", 1)[1]
                    content = code_block.rstrip("\n```")
            
            return LLMResponse(
                content=content,
                model=result['model'],
                usage=result.get('usage', {}),
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=str(e)
            )


class AnthropicClient(LLMProvider):
    """Anthropic API client."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Anthropic client."""
        self.config = config or get_config().llm
        
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        self.base_url = "https://api.anthropic.com/v1"
    
    def _request(self, endpoint: str, data: Dict) -> Dict:
        """Make authenticated API request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(
                url,
                headers={
                    "x-api-key": self.config.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate content using Claude model."""
        model = kwargs.get('model', "claude-3-sonnet-20240229")
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens_to_sample": max_tokens
        }
        
        try:
            result = self._request("/complete", data)
            
            return LLMResponse(
                content=result['completion'],
                model=result['model'],
                usage={},
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=str(e)
            )
    
    def generate_code(
        self,
        prompt: str,
        context: str,
        **kwargs
    ) -> LLMResponse:
        """Generate code with context."""
        full_prompt = f"""
Context:
{context}

Task:
{prompt}

Please provide the code implementation following the coding guidelines.
Return only the code without additional explanations.
"""
        
        model = kwargs.get('model', "claude-3-sonnet-20240229")
        temperature = 0.2
        
        data = {
            "model": model,
            "prompt": full_prompt,
            "temperature": temperature,
            "max_tokens_to_sample": self.config.max_tokens
        }
        
        try:
            result = self._request("/complete", data)
            
            content = result['completion']
            
            # Extract code block if present
            if "```" in content:
                lines = content.split("```")
                if len(lines) >= 2:
                    code_block = lines[1]
                    if "\n" in code_block:
                        code_block = code_block.split("\n", 1)[1]
                    content = code_block.rstrip("\n```")
            
            return LLMResponse(
                content=content,
                model=result['model'],
                usage={},
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=str(e)
            )


class LLMClient:
    """
    Unified LLM client that supports multiple providers.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM client with configured provider."""
        self.config = config or get_config().llm
        self.provider: LLMProvider = self._create_provider()
    
    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider based on config."""
        provider = self.config.provider.lower()
        
        if provider == "openai":
            return OpenAIClient(self.config)
        elif provider == "anthropic":
            return AnthropicClient(self.config)
        else:
            logger.warning(f"Unknown provider: {provider}, defaulting to OpenAI")
            return OpenAIClient(self.config)
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate content from prompt."""
        return self.provider.generate(prompt, **kwargs)
    
    def generate_code(
        self,
        prompt: str,
        context: str = "",
        **kwargs
    ) -> LLMResponse:
        """
        Generate code from prompt.
        
        Args:
            prompt: Code generation prompt
            context: Repository context and guidelines
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated code
        """
        return self.provider.generate_code(prompt, context, **kwargs)
    
    def analyze_requirement(self, issue_body: str) -> Dict[str, Any]:
        """
        Analyze a requirements issue and extract key information.
        
        Args:
            issue_body: The issue description
            
        Returns:
            Dictionary with analysis results
        """
        prompt = f"""
Analyze the following software requirement and extract:
1. Functional requirements
2. Non-functional requirements
3. Dependencies
4. Suggested implementation approach
5. Potential risks or clarifications needed

Requirement:
{issue_body}

Provide your analysis in JSON format:
"""
        
        response = self.generate(prompt)
        
        if response.success:
            # Try to parse as JSON
            import json
            try:
                # Find JSON in response
                start = response.content.find('{')
                end = response.content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response.content[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            return {
                "raw_analysis": response.content,
                "needs_clarification": "?" in response.content or "unclear" in response.content.lower()
            }
        
        return {
            "error": response.error,
            "needs_clarification": True
        }
    
    def generate_clarification_questions(self, issue_body: str) -> List[str]:
        """
        Generate clarification questions for ambiguous requirements.
        
        Args:
            issue_body: The issue description
            
        Returns:
            List of questions to ask
        """
        prompt = f"""
The following software requirement is ambiguous or incomplete.
Generate a list of clarifying questions to help understand the requirement better.

Requirement:
{issue_body}

List 3-5 specific questions that would help clarify this requirement.
"""
        
        response = self.generate(prompt)
        
        if response.success:
            # Parse questions from response
            questions = []
            lines = response.content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    if line[0].isdigit():
                        line = line.split('.', 1)[-1].strip()
                    questions.append(line)
            return questions
        
        return ["Could you provide more details about this requirement?"]


def get_llm_client() -> LLMClient:
    """Factory function to get a configured LLM client."""
    return LLMClient()
