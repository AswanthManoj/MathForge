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
