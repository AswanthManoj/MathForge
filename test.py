import asyncio
from config import get_settings
from logic.sandbox import MathU
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

async def main():
    topics = [
        "Involves directly applying the formula to find the mean from raw data or frequency distribution.",
        "Focuses on solving for specific trigonometric ratios using given information about angles or triangles.",
        "Problems involving finding missing frequencies in frequency distributions, given the mean, median or mode.",
        "Explains how to express one trigonometric ratio in terms of another using basic and reciprocal relationships.",
        "Teaches advanced techniques for reducing complex trigonometric expressions using known identities and algebra.",
        "Covers how to evaluate the value of a polynomial for a specific input by substituting the value of the variable.",
        "Explains the concept of the degree of a polynomial, which is the highest power of the variable in the polynomial.",
        "Teaches how to use the assumed mean method to simplify the calculation of the mean, especially with large data sets.",
        "Covers applying trigonometric identities and relationships to solve equations, verify equalities, and derive new formulas.",
        "Introduces primary trigonometric ratios such as sine, cosine, and tangent, focusing on their definitions and basic properties.",
        "Explains the geometric and mathematical definitions of trigonometric ratios in the context of right triangles and unit circles.",
        "Focuses on the relationship between trigonometric ratios and the angles of elevation or depression that can be used to find unknown distances.",
        "Focuses on using trigonometric ratios to solve practical problems involving heights and distances, including unknown lengths and angles.",
        "Addresses more complex problems that involve multiple right triangles, requiring the application of trigonometric principles and problem-solving skills",
        "Demonstrates how trigonometry can be applied in real-world situations to measure inaccessible heights and distances, fostering a practical understanding.",
    ]
    
    max_retries = 3
    providers = ["google", "anthropic", "together"]

    for topic in topics:
        current_provider_index = None
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                provider = providers[current_provider_index] if current_provider_index is not None else None
                output = await mathu.generate(
                    topic=topic,
                    is_numerical=False,
                    provider=provider
                )
                
                generated_options = []
                print(f"Topic: {topic}")
                print(f"Question: {output.question}")
                for i, option in enumerate(output.options, 1):
                    if (option.output_result not in generated_options):
                        print(f"{i}. Output result: {option.output_result} | Is correct: {option.is_correct}")
                        if not option.is_correct:
                            generated_options.append(option.output_result)
                        continue
                    raise Exception("Duplicate option found")
                
                # If successful, break the retry loop
                break
                
            except Exception as e:
                retry_count += 1
                current_provider_index = retry_count - 1 if retry_count <= len(providers) else None
                print(f"xxxxxxx Retry {retry_count} with provider {provider} xxxxxxx")
                
                if retry_count >= max_retries:
                    print(f"Max retries reached for topic: {topic}")
                    break
        
        print("-----"*5)

if __name__ == "__main__":
    asyncio.run(main())
