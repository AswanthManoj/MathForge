INPUT_TEMPLATE = """<question>
{question}
</question>

<expected_output_type>{output_type}</expected_output_type>
"""

DISTRACTOR_TEMPLATE = """<correct_answer>{correct_answer}</correct_answer>"""


VERIFIER_TEMPLATE = """
<question>
{question}
</question>

<preffered_output_type>{output_type}</preffered_output_type>

<proposed_solution_code>
```python
{code}
```
<proposed_solution_code>

<answer>{answer}<answer>""".strip()


QUESTION_GENERATION_TEMPLATE = """<topic>{topic}</topic>

<chapter_overview>{chapter_overview}</chapter_overview>

<difficulty_level>{difficulty_level}</difficulty_level>

<expected_answer_type>{expected_answer_type}</expected_answer_type>"""

QUESTION_EXTENSION_ASSISTANT_TEMPLATE = """<questions>
{previous_questions}
<questions>
"""

QUESTION_EXTENSION_USER_TEMPLATE = """Using the previously generated questions as reference, generate "{n}" additional unique and diverse questions that meet the following criteria:

<topic>{topic}</topic>

<chapter_overview>{chapter_overview}</chapter_overview>

<difficulty_level>{difficulty_level}</difficulty_level>

<expected_answer_type>{expected_answer_type}</expected_answer_type>

The new questions should:
- Cover aspects or applications of the topic not already addressed in the existing questions
- Maintain the specified difficulty level
- Result in answers that match the expected answer type format
- Avoid repetition or similarity to the existing questions 
- Adhere to CBSE 10th grade mathematics curriculum standards

Please generate the questions and output them in the following XML format:

<questions>
<question></question>
<question></question>
...
</questions>

Ensure that the generated questions meaningfully expand upon and complement the existing question set while maintaining consistency in quality and relevance to the topic. The goal is to create a diverse set of "{n}" additional questions."""
