from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from pydantic import BaseModel, Field
from typing import List, Callable, Optional

class LLMMessage(BaseModel):
    role:              str = "assistant"
    content:           str
    content_delta:     Optional[str] = None
    response_finished: bool = False
    
class LLMProviderConfig(BaseModel):
    model:   str
    api_key: str
    
class AnthropicConfig(LLMProviderConfig):
    pass

class GoogleConfig(LLMProviderConfig):
    pass

class TogetherConfig(LLMProviderConfig):
    pass

class LLMConnector:
    def __init__(
        self, 
        anthropic: Optional[AnthropicConfig] = None,
        google: Optional[GoogleConfig] = None,
        together: Optional[TogetherConfig] = None,
        provider_priority: List[str] = ["anthropic", "google", "together"]
    ) -> None:
        self.google = google
        self.together = together
        self.anthropic = anthropic
        self.provider_priority = [p for p in provider_priority if getattr(self, p) is not None]
        
        if not self.provider_priority:
            raise ValueError("No valid providers configured in priority list")
        
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        if self.anthropic:
            self.clients["anthropic"] = AsyncAnthropic(api_key=self.anthropic.api_key)
        if self.together:
            self.clients["together"] = AsyncOpenAI(
                api_key=self.together.api_key,
                base_url="https://api.together.xyz/v1"
            )
        if self.google:
            self.clients["google"] = AsyncOpenAI(
                api_key=self.google.api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/"
            )

    async def _stream_openai(self, client: AsyncOpenAI, model: str, messages: List[dict], **kwargs):
        stream = await client.chat.completions.create(
            stream=True,
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2049),
            temperature=kwargs.get("temperature", 0.5),
        )
        async for chunk in stream:
            yield chunk.choices[0].delta.content
    
    async def _stream_anthropic(self, client: AsyncAnthropic, model: str, **kwargs):
        stream_params = dict(
            model=model,
            system=kwargs.get("system"),
            messages=kwargs.get("messages"),
            max_tokens=kwargs.get("max_tokens", 2049),
            temperature=kwargs.get("temperature", 0.5),
        )
        async with client.messages.stream(**stream_params) as stream:
            async for text in stream.text_stream:
                yield text
             
    async def _try_next_provider(self, current_index: int) -> tuple:
        if current_index >= len(self.provider_priority) - 1:
            raise Exception("All providers failed")
        next_provider = self.provider_priority[current_index + 1]
        return next_provider, self.clients[next_provider]
                
    async def stream(
        self, 
        system: Optional[str], 
        messages: List[dict], 
        max_tokens: int = 2049, 
        temperature: float=0.5,
        provider: Optional[str] = None
    ):
        output = []
        current_index = 0
        current_provider = provider if provider in self.provider_priority else self.provider_priority[0]
        
        while True:
            try:
                client = self.clients[current_provider]
                config: LLMProviderConfig = getattr(self, current_provider)
                
                if current_provider == "anthropic":
                    stream_func = self._stream_anthropic
                    kwargs = {"system": system, "messages": messages}
                else:
                    stream_func = self._stream_openai
                    kwargs = {"messages": [{"role": "system", "content": system}] + messages} if system else {"messages": messages}
                
                async for text in stream_func(client, config.model, max_tokens=max_tokens, temperature=temperature, **kwargs):
                    output.append(text)
                    yield LLMMessage(content_delta=text, content="".join(output))
                break
            except Exception:
                if provider:
                    raise Exception(f"Specified provider {provider} failed")
                try:
                    current_provider, _ = await self._try_next_provider(current_index)
                    current_index += 1
                    output = []
                except Exception as e:
                    raise Exception(f"All providers failed. Last error: {str(e)}")
        
        yield LLMMessage(content="".join(output), content_delta="", response_finished=True)
        
    async def generate(
        self, 
        messages: List[dict], 
        extractor_function: Optional[Callable] = None, 
        system: Optional[str] = None, 
        max_tokens: int = 2049, 
        enable_cache: bool = False,
        temperature: float = 0.3,
        provider: Optional[str] = None
    ):
        current_index = 0
        current_provider = provider if provider in self.provider_priority else self.provider_priority[0]
    
        while True:
            try:
                client: AsyncOpenAI|AsyncAnthropic = self.clients[current_provider]
                config: LLMProviderConfig = getattr(self, current_provider)
                if current_provider == "anthropic":
                    if enable_cache:
                        response = await client.beta.prompt_caching.messages.create(
                            model=config.model,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
                        )
                    else:
                        response = await client.messages.create(
                            model=config.model,
                            system=system,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                        )
                    response_text = response.content[0].text
                else:
                    if system:
                        messages = [{"role": "system", "content": system}] + messages
                    
                    _messages = []
                    for message in messages:
                        if isinstance(message['content'], list):
                            content = "\n\n".join([msg['text'] for msg in message['content']])
                            _messages.append({"role": message['role'], "content": content})
                        elif isinstance(message['content'], str):
                            _messages.append({"role": message['role'], "content": message['content']})
                    
                    messages = _messages    
                    response = await client.chat.completions.create(
                        model=config.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    response_text = response.choices[0].message.content
                break
            except Exception:
                if provider:
                    raise Exception(f"Specified provider {provider} failed")
                try:
                    current_provider, _ = await self._try_next_provider(current_index)
                    current_index += 1
                except Exception as e:
                    raise Exception(f"All providers failed. Last error: {str(e)}")         
        return extractor_function(response_text) if extractor_function else response_text
