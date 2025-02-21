import asyncio
from config import get_settings
from logic.sandbox import MathU, MCQType, DifficultyLevel
from logic.llm_connector import GoogleConfig, AnthropicConfig, TogetherConfig
import random
import json
from typing import Optional, Dict


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


async def generate_data(tagname: str, sub_topic: Optional[str] = None, description: Optional[str] = None, max_retries: int = 3, max_questions: int = 10, verify_solution: bool=False, output_filename: str="output_result.json") -> Dict:
    results = {
        "questions": [],
        "tagname": tagname,
        "sub_topic": sub_topic,
        "description": description,
    }
    filename = "output_result.json"
    easy, medium, hard = [], [], []
    mcq_types = [MCQType.NUMERICAL, MCQType.SYMBOLIC, MCQType.STATEMENT]
    
    async def generate_questions(target_list, difficulty_level):
        question_count = 0
        while len(target_list) < max_questions:
            mcq_type = mcq_types[question_count % len(mcq_types)]
            for attempt in range(max_retries):
                try:
                    output = await mathu.generate(
                        topic=tagname,
                        sub_topic=sub_topic,
                        chapter_overview=description,
                        mcq_type=mcq_type,
                        temperature=random.choice([0.2, 0.3, 0.4, 0.5, 0.6]),
                        difficulty_level=difficulty_level,
                        provider="anthropic", # random.choice(["google", "together"]),
                        verify_solution=verify_solution
                    )
                    question_data = {
                        "mcq_type": mcq_type,
                        "question": output.question,
                        "thoughts": output.thoughts,
                        "difficulty": difficulty_level,
                        "options": [option.model_dump() for option in output.options],
                    }
                    target_list.append(question_data)
                    results['questions'].append(question_data)
                    print(f"\nSuccessfully generated {difficulty_level.value} question {len(target_list)}/{max_questions}")
                    print(f"MCQ Type: {mcq_type.value}")
                    print(f"Question: {output.question}")
                    break
                except Exception as e:
                    print(f"Error generating {difficulty_level.value} question (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt == max_retries - 1:
                        print(f"Failed to generate question after {max_retries} attempts")
            
            question_count += 1
            with open(output_filename, 'w') as f:
                json.dump(results, f, indent=2)
    
    # Generate questions for each difficulty level
    print("\nGenerating EASY questions...")
    await generate_questions(easy, DifficultyLevel.EASY)
    
    print("\nGenerating MEDIUM questions...")
    await generate_questions(medium, DifficultyLevel.MEDIUM)
    
    print("\nGenerating HARD questions...")
    await generate_questions(hard, DifficultyLevel.HARD)

    
    print(f"\nAll questions generated and saved to {filename}")
    return results

# Example usage:
async def main():
    await generate_data(
        tagname="Practical Applications of Heights and Distances",
        description="Shows how trigonometry can be used in various fields such as navigation, surveying and astronomy to measure heights and distances in real world situations.",
        sub_topic=None,
        max_retries=4,
        max_questions=10,
        verify_solution=True,
        output_filename="output_result.json"
    )

if __name__ == "__main__":
    asyncio.run(main())