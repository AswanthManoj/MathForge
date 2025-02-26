# MathForge
A synthetic mathematics data generator built around code execution and symbolic computation.

## Overview
MathForge is an advanced mathematical question generation system that uses language models to create high-quality mathematical questions and corresponding solutions. Unlike traditional synthetic datasets that rely solely on language model responses, MathForge generates verified solutions through symbolic computation with Python.

## Key Features
- **Multi-level difficulty generation**: Easy, medium, and hard questions
- **Multiple answer types**: Numerical, symbolic, and statement-based responses
- **Code-based verification**: Solutions are generated as executable Python code using symbolic math libraries
- **Solution verification**: Optional verification layer to ensure solution correctness
- **Intelligent distractor generation**: Creates plausible wrong answers for MCQs
- **API-first design**: Fully accessible via REST API endpoints

## Requirements
- Python 3.10+
- Astral UV (package manager)

## Installation
1. Install Astral UV if you haven't already:
    ```bash
    pip install uv
    ```
    
2. Clone the repository:
    ```bash
    git clone https://github.com/your-username/MathForge.git
    cd mathforge
    ```

3. Install dependencies:
    ```bash
    uv sync
    ```

4. Create a `.env` file with your API keys:
    ```env
    ANTHROPIC_API=your_anthropic_key
    GOOGLE_API=your_google_key
    TOGETHER_API=your_together_key
    OPENAI_API=your_openai_key
    GROQ_API=your_groq_key
    ```
    
## Usage
### Using the API
Start the FastAPI server:
```bash
python app.py
```
The API will be available at `http://localhost:8000`


### API Endpoints
- **POST `/solve-question`**: Solve a specific math question and generate multiple-choice options
- **POST `/generate-questions`**: Generate a set of questions for a specific topic and difficulty level
- **POST `/generate-multi-level-questions`**: Generate questions across all difficulty levels with multiple output types
- **GET /health**: Health check endpoint

### Python Library Usage
```python
import asyncio
from config import get_settings
from src.sandbox import MathU, MCQType
from src.llm_connector import (GoogleConfig, 
AnthropicConfig, GroqConfig, OpenAIConfig, TogetherConfig)

settings = get_settings()
mathforge = MathU(
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

# Generate a solution for a specific question
async def solve_example():
    solution = await mathforge.generate_solution(
        question="A ladder 10 meters long rests against a vertical wall. The foot of the ladder is 6 meters from the wall. Find the height reached by the ladder on the wall.",
        mcq_type=MCQType.NUMERICAL,
        verify_solution=True
    )
    print(solution)

# Generate questions for a topic
async def generate_questions_example():
    questions = await mathforge.generate_questions(
        tagname="Trigonometry",
        description="Basic concepts of trigonometry including sine, cosine, and tangent",
        num_questions=5,
        difficulty_level="easy",
        mcq_type=MCQType.NUMERICAL
    )
    print(questions)

# Generate multi-level questions
async def generate_multi_level_example():
    multi_level_questions = await mathforge.generate_multi_level_questions(
        tagname="Calculus",
        description="Introduction to derivatives and basic differentiation rules"
    )
    print(multi_level_questions)

# Run the examples
asyncio.run(solve_example())
```

## How It Works
1. **Question Generation**: Creates questions based on topic and difficulty level
2. **Solution Generation**: Uses language models to:
    - Generate solution logic inside a `<thinking>` tag
    - Produce executable Python code using symbolic math libraries (sympy, numpy)

3. **Code Execution**: Runs the solution code to generate the correct answer
4. **Verification (Optional)**: Validates the solution against the question
5. **Distractor Generation**: Creates plausible wrong answers for MCQs
