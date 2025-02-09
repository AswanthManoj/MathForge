import asyncio
from logic.sandbox import MathU, remove_python_comments
from config import get_settings
from logic.llm_connector import GoogleConfig, AnthropicConfig, TogetherConfig


async def main():
    settings = get_settings()
    mathu = MathU(
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        anthropic=AnthropicConfig(
            api_key=settings.anthropic_api_key, 
            model=settings.anthropic_primary_model
        ),
        google=GoogleConfig(
            api_key=settings.google_api_key,
            model=settings.google_primary_model
        ),
        together=TogetherConfig(
            api_key=settings.together_api_key,
            model=settings.together_primary_model
        ),
        provider_priority=settings.provider_priority
    )
    
    output = await mathu.generate(topic="Explains how to express one trigonometric ratio in terms of another using basic and reciprocal relationships.")
    
    print(f"Question: {output.question}")
    for i, option in enumerate(output.options, 1):
        print(f"{i}. Output result: {option.output_result} | Is correct: {option.is_correct}")

if __name__ == "__main__":
    asyncio.run(main())