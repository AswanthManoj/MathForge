from src.schema import MCQType
from typing import List, Optional, Tuple
from prompts.verifier import VERIFIER_INSTRUCTION
from prompts.distractor import DISTRACATOR_INSTRUCTION
from prompts.questionaire import QUESTION_GENERATION_INSTRUCTION
from src.utils import (extract_from_solver, remove_print_statements, 
safe_exec, format_result, extract_distractors, extract_from_verifier, extract_question)
from src.llm_connector import (LLMConnector, AnthropicConfig,  
TogetherConfig, MistralConfig, GroqConfig, OpenAIConfig, GoogleConfig)
from prompts.solver import SYMBOLIC_SOLVER_INSTRUCTION, STATEMENT_SOLVER_INSTRUCTION
from src.schema import SolverOutput, Option, FinalOutput, QuestionBank, DifficultyLevel
from prompts.base import INPUT_TEMPLATE, DISTRACTOR_TEMPLATE, VERIFIER_TEMPLATE, QUESTION_GENERATION_TEMPLATE


class MathU:
    def __init__(
        self, 
        max_tokens: int = 3049,
        temperature: float = 0.3,
        code_execution_timeout: int = 5,
        groq: GroqConfig | None = None,
        openai: OpenAIConfig | None = None,
        google: GoogleConfig | None = None,
        mistral: MistralConfig | None = None,
        together: TogetherConfig | None = None,
        anthropic: AnthropicConfig | None = None,
        provider_priority: List[str] = ["anthropic", "google", "together", "openai", "groq", "mistral"]
    ) -> None:
        self.llm = LLMConnector(
            groq=groq,
            openai=openai,
            google=google,
            mistral=mistral,
            together=together,
            anthropic=anthropic,
            provider_priority=provider_priority
        )
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.code_execution_timeout = code_execution_timeout

    async def execute_solution(self, code_output: SolverOutput):
        solve_function_namespace = await safe_exec(
            timeout=self.code_execution_timeout,
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
            code=remove_print_statements(code_output.code),
        )
        actual_params = solve_function_namespace.get('actual_params')
        solve_function = solve_function_namespace.get('solve_problem')
        correct_answer = solve_function(**actual_params)
        return format_result(correct_answer)
    
    async def generate_questions(
        self,
        tagname: str,
        description: str,
        temperature: float = 0.3,
        mcq_type: str = MCQType.NUMERICAL,
        difficulty_level: str = DifficultyLevel.EASY,
        provider: Optional[str] = None,
    ) -> QuestionBank:
        return await self.llm.generate(
            provider=provider,
            temperature=temperature,
            max_tokens=self.max_tokens,
            extractor_function=extract_question,
            system=QUESTION_GENERATION_INSTRUCTION,
            messages=[{
                "role": "user",
                "content": QUESTION_GENERATION_TEMPLATE.format(
                    topic=tagname, chapter_overview=description,
                    difficulty_level=difficulty_level, expected_answer_type=mcq_type
                )
            }]
        )

    async def generate_distractors(
        self,
        correct_answer: str,
        temperature: float = 0.3,
        provider: Optional[str] = None,
    ) -> List[Option]:
        distractors: List[str] = await self.llm.generate(
            provider=provider,
            temperature=temperature,
            max_tokens=self.max_tokens,
            system=DISTRACATOR_INSTRUCTION,
            extractor_function=extract_distractors,
            messages=[{
                "role": "user",
                "content": DISTRACTOR_TEMPLATE.format(correct_answer=correct_answer)
            }],
        )
        return [Option(is_correct=False, output_result=distractor) for distractor in distractors]
    
    async def verify_solution(
        self,
        question: str,
        mcq_type: MCQType,
        solution_code: str,
        correct_answer: str,
        temperature: float = 0.3,
        provider: Optional[str] = None
    ) -> Tuple[bool, SolverOutput]:
        return await self.llm.generate(
            provider=provider,
            temperature=temperature,
            max_tokens=self.max_tokens,
            system=VERIFIER_INSTRUCTION,
            extractor_function=extract_from_verifier,
            messages=[{
                "role": "user",
                "content": VERIFIER_TEMPLATE.format(
                    question=question, output_type=mcq_type,
                    code=solution_code, answer=correct_answer
                )
            }],
        )

    async def generate_solution(
        self,
        question: str,
        mcq_type: MCQType,
        temperature: float = 0.3,
        verify_solution: bool = False,
        provider: Optional[str] = None,
    ) -> FinalOutput:
        if mcq_type == MCQType.STATEMENT:
            system = STATEMENT_SOLVER_INSTRUCTION
        else:
            system = SYMBOLIC_SOLVER_INSTRUCTION
        
        code_output: SolverOutput = await self.llm.generate(
            system=system,
            provider=provider,
            temperature=temperature,
            max_tokens=self.max_tokens,
            extractor_function=extract_from_solver,
            messages=[{
                "role": "user",
                "content": INPUT_TEMPLATE.format(
                    question=question, output_type=mcq_type
                )
            }],
        )
        correct_answer = await self.execute_solution(code_output)
        if verify_solution:
            need_update, new_code_output = await self.verify_solution(
                question=question,
                mcq_type=mcq_type,
                provider=provider,
                temperature=temperature,
                correct_answer=correct_answer,
                solution_code=code_output.code,
            )
            if need_update:
                new_correct_answer = await self.execute_solution(code_output)
                if new_correct_answer != correct_answer:
                    code_output = new_code_output
                    correct_answer = new_correct_answer
                    
        wrong_options = await self.generate_distractors(correct_answer, temperature=temperature, provider=provider)

        return FinalOutput(
            question=question,
            thoughts=code_output.thoughts,
            correct_answer=correct_answer,
            options=[Option(is_correct=True, output_result=correct_answer)] + wrong_options,
        )

        