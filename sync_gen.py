import asyncio
from config import get_settings
from src.sandbox import MathU, MCQType
from src.llm_connector import (GoogleConfig, 
AnthropicConfig, GroqConfig, OpenAIConfig, TogetherConfig)


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
    openai=OpenAIConfig(
        api_key=settings.openai_api_key,
        model=settings.openai_primary_model
    ),
    groq=GroqConfig(
        api_key=settings.groq_api_key,
        model=settings.groq_primary_model
    ),
    provider_priority=settings.provider_priority
)


async def main():
    output = await mathu.generate_solution(
        question="Find the coordinates of the point that divides the line segment joining (-7, -3) and (4, 8) in the ratio 4:3 internally.",
        mcq_type=MCQType.NUMERICAL,
        temperature=0.3,
        verify_solution=True,
        provider="anthropic"
    )
    for i, option in enumerate(output.options, 1):
        print(f"{i}. {option.output_result} | is correct: {option.is_correct}")

if __name__ == "__main__":
    asyncio.run(main())
    
