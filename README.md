# MathU

An AI-powered system for generating verifiable Multiple Choice Questions (MCQs) for 10th grade mathematics, with support for multiple LLM providers.

## Overview

MathU generates mathematically accurate questions with verifiable answers by:
- Creating grade-appropriate math problems with step-by-step solutions
- Generating multiple parameter variations to create answer options
- Validating solutions through secure code execution
- Supporting multiple LLM providers (Anthropic, Together, Google) with fallback

## Requirements

- Python 3.10+
- Astral UV (package manager)

## Installation

1. Install Astral UV if you haven't already:
```bash
pip install astral-uv
```

2. Clone the repository:
```bash
git clone <repository-url>
cd mathu
```

3. Installation dependencies:
```bash
uv sync
```

4. Create a `.env` file with your API keys:
```env
ANTHROPIC_API=your_anthropic_key
GOOGLE_API=your_google_key
TOGETHER_API=your_together_key
```

## Usage
Basic example:

```python
import asyncio
from sandbox import MathU
from config import get_settings
from llm_connector import GoogleConfig, AnthropicConfig, TogetherConfig


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
    output = await mathu.generate(
        topic="Word Problems on Time, Speed and Distance",
        chapter_overview="Your chapter overview here..."
    )
    print(output.question)
    for option in output.options:
        print(f"Result: {option.output_result}, Correct: {option.is_correct}")

if __name__ == "__main__":
    asyncio.run(main())
```