import os
import uvicorn
from pathlib import Path
from typing import Optional
from config import get_settings
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.sandbox import MathForge, MCQType, DifficultyLevel
from src.llm_connector import GoogleConfig, AnthropicConfig, GroqConfig, OpenAIConfig, TogetherConfig

app = FastAPI(title="Synth Math Question Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize settings and MathU instance
settings = get_settings()
math_forge = MathForge(
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

class SolutionRequest(BaseModel):
    question: str = Field(
        ..., 
        description="The question thats needed to be solved for",
    )
    mcq_type: MCQType = Field(
        default=MCQType.NUMERICAL,
        description="Type of multiple choice question. Should be `numerical`, `symbolic` or `statement`",
        example=MCQType.NUMERICAL
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature parameter for LLM generation (0.2 to 1.0)",
        example=0.3,
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider to use (`google`, `anthropic`, or `together`)",
        example="google"
    )
    verify_solution: bool = Field(
        default=False,
        description="Enable by setting True to add a solution code verification layer",
        example=False
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "A ladder 10 meters long rests against a vertical wall. The foot of the ladder is 6 meters from the wall. Find the height reached by the ladder on the wall.",
                    "mcq_type": "numerical",
                    "temperature": 0.3,
                    "provider": "together",
                    "verify_solution": True
                },
                {
                    "question": "In a circle with center O, prove that the perpendicular from the center to a chord bisects the chord.",
                    "mcq_type": "symbolic",
                    "temperature": 0.5,
                    "provider": "google",
                    "verify_solution": False
                },
                {
                    "question": "If the distance between points A(3, 4) and B(6, 8) is 5 units, determine if this statement is true or false.",
                    "mcq_type": "statement",
                    "temperature": 0.4,
                    "provider": "google",
                    "verify_solution": True
                }
            ]
        }
    }

class QuestionsRequest(BaseModel):
    tagname: str = Field(
        ...,
        description="The topic or tag name for which questions need to be generated",
        example="Trigonometry"
    )
    description: str = Field(
        ...,
        description="Overview or description of the chapter/topic",
        example="Basic concepts of trigonometry including sine, cosine, and tangent"
    )
    num_questions: int = Field(
        default=30,
        description="Number of questions to be generated",
        example=30
    )
    mcq_type: MCQType = Field(
        default=MCQType.NUMERICAL,
        description="Type of multiple choice question. Should be `numerical`, `symbolic` or `statement`",
        example=MCQType.NUMERICAL
    )
    difficulty_level: str = Field(
        default=DifficultyLevel.EASY,
        description="Difficulty level of the questions to be generated",
        example=DifficultyLevel.EASY
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature parameter for LLM generation (0.2 to 1.0)",
        example=0.7
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider to use (`google`, `anthropic`, or `together`)",
        example="google"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tagname": "Trigonometry",
                    "description": "Basic concepts of trigonometry including sine, cosine, and tangent ratios in right triangles",
                    "mcq_type": "numerical",
                    "difficulty_level": "easy",
                    "temperature": 0.3,
                    "num_questions": 40,
                    "provider": "google"
                }
            ]
        }
    }

class MultiLevelQuestionsRequest(BaseModel):
    tagname: str = Field(
        ...,
        description="The topic or tag name for which questions need to be generated",
        example="Trigonometry"
    )
    description: str = Field(
        ...,
        description="Overview or description of the chapter/topic",
        example="Basic concepts of trigonometry including sine, cosine, and tangent"
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature parameter for LLM generation (0.2 to 1.0)",
        example=0.7
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider to use (`google`, `anthropic`, or `together`)",
        example="google"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tagname": "Trigonometry",
                    "description": "Basic concepts of trigonometry including sine, cosine, and tangent ratios in right triangles",
                    "temperature": 0.3,
                    "provider": "google"
                }
            ]
        }
    }

@app.get("/", response_class=FileResponse)
async def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "src", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

@app.post("/solve-question")
async def solve_question(request: SolutionRequest):
    try:
        result = await math_forge.generate_solution(
            question=request.question,
            mcq_type=request.mcq_type,
            provider=request.provider,
            temperature=request.temperature,
            verify_solution=request.verify_solution
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-questions")
async def generate_questions(request: QuestionsRequest):
    try:
        result = await math_forge.generate_questions(
            tagname=request.tagname,
            provider=request.provider,
            mcq_type=request.mcq_type,
            temperature=request.temperature,
            description=request.description,
            num_questions=request.num_questions,
            difficulty_level=request.difficulty_level,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate-multi-level-questions")
async def generate_multi_level_questions(request: MultiLevelQuestionsRequest):
    try:
        result = await math_forge.generate_multi_level_questions(
            tagname=request.tagname,
            provider=request.provider,
            temperature=request.temperature,
            description=request.description,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )
