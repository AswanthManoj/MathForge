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
        topic="Word Problems on Time, Speed and Distance using Quadratic Equations", 
        chapter_overview="""1. Distance-Time-Speed Relationship
   - Basic formula: Distance = Speed × Time
   - Relationship between relative speeds
   - Converting units (km/h to m/s etc.)
   - Average speed calculations

2. Key Mathematical Components:
   - Forming quadratic equations from word problems
   - Standard form ax² + bx + c = 0
   - Different methods of solving quadratic equations
   - Selecting meaningful solutions in context

3. Real-world Applications:
   - Vehicles traveling in same/opposite directions
   - Meeting and overtaking problems
   - Time taken for round trips
   - Speed variations in different mediums

4. Common Problem Types:
   - Finding meeting points of two vehicles
   - Calculating overtaking time
   - Round trip timing problems
   - Speed against/with current or wind

5. Problem-Solving Strategy:
   - Identifying the unknown variable
   - Setting up the quadratic equation
   - Solving using appropriate method
   - Validating solutions in context
   - Handling units consistently

6. Key Relationships:
   - Relative speed when moving in same direction = |speed1 - speed2|
   - Relative speed when moving in opposite direction = speed1 + speed2
   - For round trips: Total time = time(up) + time(down)
   - Average speed ≠ (speed1 + speed2)/2 for unequal time periods""")
    
    print(f"Question: {output.question}")
    for i, option in enumerate(output.options, 1):
        print(f"{i}. Output result: {option.output_result} | Is correct: {option.is_correct}")

if __name__ == "__main__":
    asyncio.run(main())