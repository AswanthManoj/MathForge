import uvicorn
from typing import Optional
from config import get_settings
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from logic.sandbox import MathU, MCQType, DifficultyLevel
from logic.llm_connector import GoogleConfig, AnthropicConfig, TogetherConfig

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
mathu = MathU(
    max_tokens=settings.max_tokens,
    temperature=settings.temperature,
    code_execution_timeout=settings.code_execution_timeout,
    
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

class QuestionRequest(BaseModel):
    tagname: str = Field(
        description="The mathematical topic `TagName` for question generation",
        example="Finding mean from raw data in statistics"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional overview of the chapter context `Description`",
        example="This chapter covers measures of central tendency including mean, median, and mode"
    )
    sub_topic: Optional[str] = Field(
        default=None,
        description="Optional sub-topic to focus the question on to this specific concept",
        example="Measures of central tendency mean"
    )
    mcq_type: MCQType = Field(
        default=MCQType.NUMERICAL,
        description="Type of multiple choice question. Should be `numerical`, `symbolic` or `statement`",
        example=MCQType.NUMERICAL
    )
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="Difficulty level of the question. Should be `easy`, `medium` or `hard`",
        example=DifficultyLevel.EASY
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
                    "tagname": "Practical Applications of Heights and Distances",
                    "description": "Shows how trigonometry can be used in various fields such as navigation, surveying and astronomy to measure heights and distances in real world situations.",
                    "sub_topic": "Application of similarity of triangles in height and distance problems",
                    "mcq_type": "numerical",
                    "difficulty_level": "easy",
                    "temperature": 0.3,
                    "provider": "together",
                    "verify_solution": True
                },
                {
                    "tagname": "Circles and Geometric Constructions",
                    "description": "Investigates the relationships between tangent lines, secant lines, and circles, including theorems about their angles and lengths, while developing geometric reasoning and construction skills using compass and ruler.",
                    "sub_topic": "Tangents, Secants, and Their Properties",
                    "mcq_type": "symbolic",
                    "difficulty_level": "medium",
                    "temperature": 0.5,
                    "provider": "google",
                    "verify_solution": False
                },
                {
                    "tagname": "Coordinate Geometry Fundamentals",
                    "description": "Covers the application of algebraic methods to geometric problems, including finding distances between points, dividing line segments, and determining areas of geometric figures using coordinate systems.",
                    "sub_topic": "Distance Formula and Section Formula",
                    "mcq_type": "statement",
                    "difficulty_level": "hard",
                    "temperature": 0.4,
                    "provider": "google",
                    "verify_solution": True
                }
            ]
        }
    }

@app.post("/generate-question")
async def generate_question(request: QuestionRequest):
    # try:
        result = await mathu.generate(
            topic=request.tagname,
            sub_topic=request.sub_topic,
            chapter_overview=request.description,
            mcq_type=request.mcq_type,
            difficulty_level=request.difficulty_level,
            temperature=request.temperature,
            provider=request.provider,
            verify_solution=request.verify_solution
        )
        return result
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

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