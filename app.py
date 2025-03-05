import os
import time
import uvicorn
from pathlib import Path
from typing import List, Optional
import sbert_check, random
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
    num_questions_per_type: int = Field(
        default=5,
        description="Number of questions to be generated per mcq type",
        example=5
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
                    "provider": "google",
                    "num_questions_per_type": 4
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
        print(request)
        result = await math_forge.generate_solution(
            question=request.question,
            mcq_type=request.mcq_type,
            provider=request.provider,
            temperature=request.temperature,
            verify_solution=request.verify_solution
        )
        
        
#         result_mock = {
#   "thoughts": "The topic is Trigonometry, specifically focusing on basic trigonometric ratios (sine, cosine, tangent) in right-angled triangles. The difficulty level is easy, and the expected answer type is numerical. This means the questions should involve calculations that result in numerical answers.\n\nHere's my plan:\n\n1.  **Core Concepts:** Focus on the definitions of sin, cos, and tan (SOH CAH TOA). Questions will involve finding the values of these ratios given side lengths of right triangles, or finding side lengths given a ratio and another side.\n2.  **Difficulty:** \"Easy\" difficulty means using simple, whole number side lengths (e.g., Pythagorean triplets like 3-4-5, 5-12-13) and avoiding complex calculations or angles other than standard angles like 30, 45, 60 and 90 degrees. No trigonometric identities will be used.\n3.  **Answer Type:** Numerical answers mean the questions will be phrased to require calculation of a ratio value or a side length, resulting in a number.\n4.  **Diversity:** I'll vary the questions by:\n    *   Using different Pythagorean triplets.\n    *   Asking for sin, cos, or tan.\n    *   Sometimes providing the angle and a side, sometimes two sides.\n    *   Using different labels for the triangle's vertices (PQR, ABC, etc.).\n    *   Sometimes asking for a ratio, sometimes a side length.\n    *   Using diagrams and word problems.\n5. **CBSE 10th Grade Alignment:** The questions will strictly adhere to the 10th-grade CBSE curriculum, focusing only on basic trigonometric ratios in right triangles. No inverse trigonometric functions or other advanced concepts will be included.\n\nI will generate 30 unique questions, each testing a slightly different aspect of the core concepts, ensuring variety and avoiding repetition.",
#   "questions": [ "A tree casts a shadow of 24m. If the angle of elevation of the sun is θ, and tan θ = 7/24, what is the height of the tree?",
#     "If cos θ = 7/25 in a right-angled triangle, and the hypotenuse is 50, what is the length of the side adjacent to θ?",
#     "If sin A = 0.5 in a right-angled triangle, what is the value of cos A? (Express as a decimal rounded to three places)",
#     "In a right triangle XYZ, right-angled at Y, XY = 8 cm and YZ = 15 cm. What is the value of tan X?",
#     "A ladder leans against a wall, making an angle θ with the ground. If the ladder is 10m long and sin θ = 0.8, how high up the wall does the ladder reach?",
#     "In a right triangle ABC, right-angled at C, AC = 24 and BC= 7. What is tan B?",
#     "In a right triangle XYZ, right-angled at Y, XZ = 17 cm and cos X = 8/17. What is the length of XY?",
#     "A ramp makes an angle θ with the ground. If the ramp is 15m long and sin θ = 1/3, what is the vertical height of the ramp?",
#     "In a right-angled triangle, the side opposite to angle θ is 8 and the hypotenuse is 10. What is the value of sin θ?",
#     "In a right triangle XYZ, right-angled at Y, if YZ = 24 and XZ = 25, what is the value of tan X?"
#   ],
# }
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
        result.hard_questions.numerical = random.choices(result.hard_questions.numerical, request.num_questions_per_type)
        result.hard_questions.symbolic = random.choices(result.hard_questions.symbolic, request.num_questions_per_type)
        result.hard_questions.statement = random.choices(result.hard_questions.statement, request.num_questions_per_type)

        result.medium_questions.numerical = random.choices(result.medium_questions.numerical, request.num_questions_per_type)
        result.medium_questions.symbolic = random.choices(result.medium_questions.symbolic, request.num_questions_per_type)
        result.medium_questions.statement = random.choices(result.medium_questions.statement, request.num_questions_per_type)

        result.easy_questions.numerical = random.choices(result.easy_questions.numerical, request.num_questions_per_type)
        result.easy_questions.symbolic = random.choices(result.easy_questions.symbolic, request.num_questions_per_type)
        result.easy_questions.statement = random.choices(result.easy_questions.statement, request.num_questions_per_type)
        
        # time.sleep(1)
        mock_result = {
  "easy_questions": {
    "numerical": [
      "If sin A = 3/5, and A is an acute angle in a right triangle, what is the value of cos A?",
      "In a right triangle ABC, right-angled at B, if AB = 5 cm and BC = 12 cm, what is the value of tan A?",
      "If tan θ = 1, what is the value of θ in degrees, where θ is an acute angle?",
      "In a right triangle, the side opposite to angle θ is 8 units and the hypotenuse is 10 units. What is the value of sin θ?",
      "If cos B = 0.6, what is the value of sin B, assuming B is an acute angle?",
      "Given a right triangle with an angle α, where sin α = 0.8, find the value of cos α.",
      "In a right-angled triangle PQR, right-angled at Q, if PQ = 7 cm and PR = 25 cm, find the value of sin R.",
      "If sin X = 4/5, what is the value of cos X, where X is an acute angle?",
      "In a right triangle, the adjacent side to angle β is 9 units and the hypotenuse is 15 units. What is the value of cos β?",
      "If tan Y = 5/12, and Y is an acute angle in a right triangle, what is the value of sin Y / cos Y?"
    ],
    "symbolic": [
      "Express cos θ in terms of sin θ, where θ is an acute angle in a right triangle.",
      "If sin A = p, express tan A in terms of p, assuming A is an acute angle.",
      "Express sin θ in terms of cos θ, where θ is an acute angle.",
      "If tan B = q, express sin B in terms of q, assuming B is an acute angle.",
      "Write the relationship between sin A and cos A using the Pythagorean identity.",
      "If cos C = r, express tan C in terms of r, assuming C is an acute angle.",
      "Express tan x in terms of sin x and cos x.",
      "If sin Y = a/b, where a and b are sides of a right triangle, express cos Y in terms of a and b.",
      "Given tan Z = m/n, express sin Z in terms of m and n, assuming Z is acute.",
      "If cos P = x/y, express sin P in terms of x and y."
    ],
    "statement": [
      "In a right-angled triangle, what is the range of values for the sine of an acute angle?",
      "What is the trigonometric ratio that represents the ratio of the opposite side to the hypotenuse in a right-angled triangle?",
      "What is the trigonometric ratio defined as the adjacent side divided by the hypotenuse?",
      "Define the tangent of an angle in a right-angled triangle.",
      "As an acute angle in a right triangle increases, what happens to its sine value?",
      "In a right-angled triangle, if the sine of an angle is 1, what is the measure of that angle?",
      "What is the relationship between the sine of an angle and the cosine of its complementary angle?",
      "If the cosine of an acute angle is 0, what is the measure of the angle?",
      "What happens to the value of tan θ as θ approaches 90 degrees?",
      "Explain why sin θ is always less than or equal to 1 for any acute angle θ."
    ]
  },
  "medium_questions": {
    "numerical": [
      "In a right triangle ABC, right-angled at B, if sin A = 5/13, find the value of tan A + cos A.",
      "If tan θ = 8/15, find the value of (sin θ + cos θ).",
      "Given that sin A = 0.6 and cos A = 0.8, find the value of tan A + 1/tan A.",
      "In a right triangle PQR, right-angled at Q, PQ = 3 cm and PR = 5 cm. Find the value of sin R + cos R.",
      "If 5sin θ = 3, find the value of (sec θ + tan θ) / (sec θ - tan θ). Note: sec θ = 1/cos θ.",
      "In a right triangle, if sin A = 7/25, calculate the value of (1 + tan^2 A).",
      "If cos B = 1/2, find the value of 3sin B - 4sin^3 B.",
      "Given a right triangle with angle θ, where sin θ = 12/13, find the value of  cos θ + tan θ.",
      "In a right triangle ABC, right-angled at B, AB = 24 cm and BC = 7 cm. Calculate sin A + cos A.",
      "If 13sin A = 5, find the value of (5sin A - 2cos A) / tan A."
    ],
    "symbolic": [
      "If sin A = x and cos A = y, simplify the expression (tan A + 1/tan A) in terms of x and y.",
      "Simplify the expression: (sin A / cos A) + (cos A / sin A).",
      "If tan θ = a/b, express (sin θ + cos θ)^2 in terms of a and b.",
      "Simplify (1 - sin^2 A) / cos A.",
      "Express (1 + tan^2 A) in terms of cos A.",
      "Simplify (cos^2 A) / (1 - sin A) - sin A.",
      "Express sin^2 θ + cos^2 θ + tan^2 θ in terms of cos θ.",
      "If sin x = p and cos x = q, simplify p^2 + q^2.",
      "Simplify (1/cos^2 A) - tan^2 A.",
      "Express 1 + cot^2 A in terms of sin A. (Note: cot A = 1/tan A)"
    ],
    "statement": [
      "Explain why the value of tan A can be greater than 1, while sin A cannot.",
      "Explain the relationship between sin^2 A and cos^2 A.",
      "Describe how you would find the value of cos A if you know the value of sin A and that A is an acute angle.",
      "What happens to the value of cos θ as θ increases from 0° to 90°?",
      "Explain why sin(90° - A) = cos A for any acute angle A.",
      "How can you determine the value of tan A if you are given sin A and cos A?",
      "Explain the meaning of complementary angles in the context of sine and cosine.",
      "Is it possible for sin A to be equal to cos A for some acute angle A? If so, what is the value of A?",
      "Explain why the hypotenuse is always the longest side in a right-angled triangle, in relation to trigonometric ratios.",
      "Describe the relationship between the sides of a 30-60-90 right triangle and the trigonometric ratios of 30 and 60 degrees."
    ]
  },
  "hard_questions": {
    "numerical": [
      "If sin A + cos A = 7/5, and A is an acute angle, find the value of sin A * cos A.",
      "If tan θ = 2, find the value of (sin θ + cos θ) / (cos θ - sin θ).",
      "Given that 1 + sin^2 A = 3sin A cos A, find the value of tan A.",
      "In a right triangle ABC, right-angled at B, if sin A = cos A, find the value of 2tan A + cos^2 A.",
      "If 7sin^2 θ + 3cos^2 θ = 4, find the value of tan θ, where θ is an acute angle.",
      "If sin A + sin^2 A = 1, find the value of cos^2 A + cos^4 A.",
      "If tan x = 1/7 and tan y = 1/3, and x and y are acute angles, find the value of sin(x+y)/cos(x+y) without finding x and y individually. (Hint: Use the identity tan(x+y) = (tan x + tan y) / (1 - tan x * tan y))",
      "If cos θ - sin θ = 1/2, find the value of cos θ + sin θ, where θ is an acute angle.",
      "Given that sin A = 3/5, find the value of (tan A + sec A)^2. (Note: sec A = 1/cos A)",
      "If sin x + cos x = √2, find the value of sin x * cos x."
    ],
    "symbolic": [
      "Simplify: (1 + sin θ - cos θ) / (1 + sin θ + cos θ)  (Hint: Multiply numerator and denominator by (1 + sin θ - cos θ))",
      "Prove that (tan A + sec A - 1) / (tan A - sec A + 1) = (1 + sin A) / cos A.",
      "Simplify the expression: (sin^3 A + cos^3 A) / (sin A + cos A).",
      "If tan A = x, express sin 2A in terms of x. (Hint: sin 2A = 2sin A cos A)",
      "Simplify: (1 - tan^2 A) / (1 + tan^2 A) and express it in terms of cos 2A. (Hint: cos 2A = cos^2 A - sin^2 A)",
      "Express sin^4 A + cos^4 A in terms of sin 2A.",
      "Simplify: (sin A + cos A)^2 - 1.",
      "If tan θ = p/q, express (p sin θ - q cos θ) / (p sin θ + q cos θ) in terms of p and q.",
      "Simplify (sec A - tan A)(sec A + tan A).",
      "Prove that sin^2 A tan A + cos^2 A cot A + 2sin A cos A = tan A + cot A."
    ],
    "statement": [
      "Explain how the Pythagorean identity (sin^2 θ + cos^2 θ = 1) is derived from the Pythagorean theorem.",
      "Explain why the identity sin(90° - θ) = cos θ holds true for all acute angles θ, using a right-angled triangle.",
      "Describe a real-world application where understanding the relationship between sine, cosine, and tangent is useful.",
      "Explain the concept of \"angle of elevation\" and how it relates to trigonometric ratios.",
      "Explain the concept of \"angle of depression\" and how it relates to trigonometric ratios.",
      "Explain why the trigonometric ratios of 45 degrees are derived from an isosceles right triangle.",
      "How can you use trigonometric ratios to find the height of a tall object, given the distance to the object and the angle of elevation?",
      "Explain the limitations of using only sine, cosine, and tangent ratios for solving problems involving non-right triangles.",
      "Explain how trigonometric ratios can be used to find unknown side lengths in a right-angled triangle.",
      "Discuss the relationship between the unit circle and the trigonometric ratios of angles greater than 90 degrees (although this is beyond the 10th-grade syllabus, it tests deeper understanding)."
    ]
  }
}
        # return mock_result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    




class QuestionFilterRequest(BaseModel):
    existing_questions: List[str]
    new_questions: List[str]
    similarity_threshold: float = 0.8 # Default threshold, can be overridden in request

@app.post("/check-similar-questions")
async def filter_questions_endpoint(request: QuestionFilterRequest):
    """
    Endpoint to filter new questions based on semantic similarity to existing questions.
    """
    try:
        removed_questions = sbert_check.check_similar_questions(
            request.existing_questions,
            request.new_questions,
            request.similarity_threshold
        )
        return removed_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during question filtering: {str(e)}")
    
    
      
    

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
