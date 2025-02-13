import asyncio
import json, random
from asyncio import Semaphore
from datetime import datetime
from typing import Optional, Dict
from config import get_settings
from logic.sandbox import MathU, MCQType, DifficultyLevel
from logic.llm_connector import GoogleConfig, AnthropicConfig, TogetherConfig

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

async def generate_data(
    tagname: str, 
    description: Optional[str] = None, 
    max_retries: int = 3, 
    max_questions: int = 10, 
    max_concurrency: int = 3,
    output_filename: str = "output_result.json"
) -> Dict:
    results = {
        "questions": [],
        "tagname": tagname,
        "description": description,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_questions": max_questions * 3,  # 3 difficulty levels
            "generation_settings": {
                "max_retries": max_retries,
                "max_concurrency": max_concurrency
            }
        }
    }
    
    # Semaphore for concurrency control
    sem = Semaphore(max_concurrency)
    mcq_types = [MCQType.NUMERICAL, MCQType.SYMBOLIC, MCQType.STATEMENT]
    
    async def generate_single_question(
        difficulty_level: DifficultyLevel,
        mcq_type: MCQType,
        question_number: int
    ) -> Optional[dict]:
        async with sem:  # Control concurrency
            for attempt in range(max_retries):
                try:
                    output = await mathu.generate(
                        topic=tagname,
                        chapter_overview=description,
                        mcq_type=mcq_type,
                        temperature=random.choice([0.2, 0.3, 0.4, 0.5, 0.6]),
                        difficulty_level=difficulty_level,
                        provider=random.choice(["google", "together"]),
                    )
                    
                    question_data = {
                        "mcq_type": mcq_type.value,
                        "question": output.question,
                        "thoughts": output.thoughts,
                        "difficulty": difficulty_level.value,
                        "question_number": question_number,
                        "options": [option.model_dump() for option in output.options],
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "attempts": attempt + 1
                        }
                    }
                    
                    print(f"\nSuccessfully generated {difficulty_level.value} question {question_number}/{max_questions}")
                    print(f"MCQ Type: {mcq_type.value}")
                    print(f"Question: {output.question}")
                    
                    return question_data
                    
                except Exception as e:
                    print(f"Error generating {difficulty_level.value} question {question_number} "
                          f"(attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt == max_retries - 1:
                        print(f"Failed to generate question after {max_retries} attempts")
                        return None
                
                # Add small delay between retries
                await asyncio.sleep(1)
    
    async def generate_questions_for_difficulty(difficulty_level: DifficultyLevel) -> list:
        print(f"\nGenerating {difficulty_level.value.upper()} questions...")
        tasks = []
        
        for i in range(max_questions):
            mcq_type = mcq_types[i % len(mcq_types)]
            task = generate_single_question(
                difficulty_level=difficulty_level,
                mcq_type=mcq_type,
                question_number=i + 1
            )
            tasks.append(task)
        
        # Wait for all questions of this difficulty to complete
        questions = []
        for completed_task in asyncio.as_completed(tasks):
            question_data = await completed_task
            if question_data:
                questions.append(question_data)
                # Save progress after each successful generation
                results['questions'] = sorted(
                    questions, 
                    key=lambda x: (x['difficulty'], x['question_number'])
                )
                with open(output_filename, 'w') as f:
                    json.dump(results, f, indent=2)
                    
        return questions

    # Generate questions for all difficulty levels concurrently
    difficulty_tasks = [
        generate_questions_for_difficulty(level)
        for level in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
    ]
    
    # Wait for all difficulty levels to complete
    completed_questions = await asyncio.gather(*difficulty_tasks)
    
    # Combine and sort all questions
    all_questions = []
    for questions in completed_questions:
        all_questions.extend(questions)
    
    # Sort by difficulty and question number
    results['questions'] = sorted(
        all_questions,
        key=lambda x: (x['difficulty'], x['question_number'])
    )
    
    # Final save
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAll questions generated and saved to {output_filename}")
    return results

# Example usage:
async def main():
    await generate_data(
        tagname="Practical Applications of Heights and Distances",
        description="Shows how trigonometry can be used in various fields such as navigation, surveying and astronomy to measure heights and distances in real world situations.",
        max_retries=4,
        max_questions=10,
        max_concurrency=3,  # Adjust based on API rate limits
        output_filename="output_result_async.json"
    )

if __name__ == "__main__":
    asyncio.run(main())
