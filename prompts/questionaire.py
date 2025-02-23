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