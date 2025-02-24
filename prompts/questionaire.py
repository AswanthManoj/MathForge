QUESTION_GENERATION_INSTRUCTION = r'''You are tasked with generating diverse mathematics Multiple Choice Questions (MCQs) for 10th grade CBSE students. Your goal is to create questions that align with the provided topic, chapter overview, difficulty level, and expected answer type.

Before generating questions:
1. Carefully analyze the provided <topic>, <chapter_overview>, <difficulty_level>, and <expected_answer_type>
2. Think deeply about:
   - The core concepts within the topic appropriate for 10th grade CBSE
   - How to align questions with the specified difficulty level
   - Ways to ensure answers match the expected answer type (numerical/symbolic/statement)
   - Methods to maintain diversity in question types and avoid repetition
   - Appropriate complexity based on CBSE 10th grade curriculum standards
3. Document your analysis and planning in the <thoughts> tag

Rules for question generation:
- Generate exactly 30 unique questions
- Ensure each question tests a different aspect or application of the topic
- Questions should naturally lead to answers matching the specified answer type:
  * For numerical: Questions should require calculation with numerical answers
  * For symbolic: Questions should result in algebraic expressions or mathematical symbols
  * For statement: Questions should require theoretical or conceptual statement answers
- Maintain consistent difficulty level throughout
- Questions should be clear, unambiguous, and grade-appropriate
- Avoid repetitive patterns or similar question structures
- Do not include multiple choice options or solutions
- Each question should be tagged with <li> inside the <questions> tag

Your output must follow this exact format:
<thoughts>
[Detailed analysis of concepts, approach, and planning for question generation]
</thoughts>

<questions>
<li>[Question 1]</li>
<li>[Question 2]</li>
...
<li>[Question 30]</li>
</questions>

Remember to stay within the scope of CBSE 10th grade mathematics curriculum while ensuring questions are engaging and pedagogically sound.'''

MULTI_DIFFICULTY_QUESTION_GENERATION_INSTRUCTION = r'''You are tasked with generating comprehensive mathematics Multiple Choice Questions (MCQs) for 10th grade CBSE students. Your goal is to create a diverse set of questions across different difficulty levels and answer types based on the provided topic and chapter overview.

Input parameters:
<topic>[Topic name]</topic>
<chapter_overview>[Chapter overview text]</chapter_overview>

Before generating questions:
1. Analyze the topic and chapter overview thoroughly to identify:
   - Core concepts and sub-concepts
   - Progressive complexity levels (easy, medium, hard)
   - Opportunities for different types of answers (numerical, symbolic, statement)
   - Applications and real-world connections
   - Common misconceptions and learning challenges

2. For each difficulty level:
   - Easy: Focus on direct application of concepts, single-step solutions
   - Medium: Combine multiple concepts, require 2-3 step solutions
   - Hard: Test deeper understanding, require multi-step solutions and analysis

3. For each answer type:
   - Numerical: Questions requiring calculation with numerical answers
   - Symbolic: Questions resulting in algebraic expressions or mathematical symbols
   - Statement: Questions testing theoretical understanding or conceptual explanations

Rules for question generation:
- Generate 10 questions for each combination of difficulty level and answer type
- Ensure questions progressively increase in complexity within each difficulty level
- Make questions clear, unambiguous, and grade-appropriate
- Avoid repetitive patterns or similar question structures
- Do not include multiple choice options or solutions
- Each question should be tagged with <li> inside appropriate category tags

Generate the questions according to the following structure:

```xml
<easy-questions>
    <numerical-questions>
        <li>[Question written with markdown paragraph]</li>
        ...upto 10 questions
    </numerical-questions>
    <symbolic-questions>
        <li>[Question written with markdown paragraph]</li>
        ...upto 10 questions
    </symbolic-questions>
    <statement-questions>
        <li>[Question written with markdown paragraph]</li>
        ...upto 10 questions
    </statement-questions>
</easy-questions>

<medium-questions>
    [Same structure to cover numerical, symbolic and statement questions]
</medium-questions>

<hard-questions>
    [Same structure to cover numerical, symbolic and statement questions]
</hard-questions>
```

Remember to:
- Stay within CBSE 10th grade mathematics curriculum scope
- Ensure questions are pedagogically sound and engaging
- Maintain consistent difficulty levels within each category
- Create meaningful connections between concepts
- Test different cognitive skills (recall, understanding, application, analysis)'''
