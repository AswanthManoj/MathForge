TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE = """
# Topic:
{topic}

---
# Chapter Oerview:
{chapter_overview}

---
""".strip()


TOPIC_ONLY_TEMPLATE = """
# Topic:
{topic}

---
""".strip()


PARAMETERS_TEMPLATE = """
Here is the code:
```python
{code}
```

Here is sample input for the `solve_problem` function:
```python
{actual_params}
```

Now generate different parameter inputs suitable for the `solve_problem` function.
""".strip()

