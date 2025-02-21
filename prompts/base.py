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

