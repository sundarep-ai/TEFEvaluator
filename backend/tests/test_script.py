"""Standalone, Gemini-only harness that runs the full evaluation pipeline
against the fixtures in test_sample.py and prints the resulting scores.

This is NOT a pytest test — it makes real, paid API calls. Run it with both
`backend/` and `backend/tests/` importable:

    cd backend
    $env:PYTHONPATH="."; python tests/test_script.py     # PowerShell
    PYTHONPATH=. python tests/test_script.py             # bash

It reuses run.py's schema flattening, parsing and scoring so the harness and the
server cannot drift apart — the previous version duplicated those helpers and
had already diverged.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Reuse the production pipeline's helpers rather than re-implementing them.
from run import (
    fully_flatten_pydantic_schema,
    flatten_pydantic_schema,
    metrics_taskA,
    metrics_taskB,
    parse_json_response,
    extract_feedback_df,
    extract_feedback_summary,
    merge_criteria,
    build_judge_input,
)
import scoring
from model import TEFTaskAResponse, TEFTaskBResponse, TEFJudgeResponse
from prompt_taskA import (
    eval1_system_instruction_taskA, eval1_taskA_prompt,
    eval2_system_instruction_taskA, eval2_taskA_prompt,
    judge_system_instruction_taskA, judge_prompt_taskA,
)
from prompt_taskB import (
    eval1_system_instruction_taskB, eval1_taskB_prompt,
    eval2_system_instruction_taskB, eval2_taskB_prompt,
    judge_system_instruction_taskB, judge_prompt_taskB,
)
from test_sample import task_a_question, task_a_response, task_b_question, task_b_response

load_dotenv()

# Match ai_client.DEFAULT_MODELS["google"] so calibration reflects production.
MODEL = "gemini-3.6-flash"

client = genai.Client()


def generate(system_instruction, response_schema, contents, model=MODEL):
    """Single Gemini call with native schema enforcement."""
    return client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            max_output_tokens=16000,
        ),
        contents=contents,
    )


def _avg_rating(rows):
    ratings = [r["rating"] for r in rows if r["rating"] is not None]
    return sum(ratings) / len(ratings) if ratings else float("nan")


def run_section(label, question, response_text, prompts, schema, metrics):
    """Two independent evaluators plus a judge, for one section."""
    (eval1_system, eval1_template, eval2_system, eval2_template,
     judge_system, judge_template) = prompts
    word_count = len(response_text.split())

    # NOTE: the system instruction and the user content are DIFFERENT arguments.
    # The previous version passed the formatted content as `system_instruction`
    # for all four evaluator calls, so the encouraging/critical persona split
    # never took effect and any calibration derived from it was invalid.
    r1 = generate(
        system_instruction=eval1_system,
        response_schema=schema,
        contents=eval1_template.format(
            question=question, response=response_text, word_count=word_count
        ),
    )
    r2 = generate(
        system_instruction=eval2_system,
        response_schema=schema,
        contents=eval2_template.format(
            question=question, response=response_text, word_count=word_count
        ),
    )

    rows1 = extract_feedback_df(r1, metrics, f"{label} evaluator 1")
    rows2 = extract_feedback_df(r2, metrics, f"{label} evaluator 2")
    rating, *_ = extract_feedback_summary(rows1, rows2)
    criteria = merge_criteria(rows1, rows2, metrics)
    judge_justification, judge_recommendation, judge_originals, judge_corrections = build_judge_input(
        criteria
    )

    judge = generate(
        system_instruction=judge_system,
        response_schema=judge_output_schema,
        contents=judge_template.format(
            justification=judge_justification,
            recommendations=judge_recommendation,
            originals=judge_originals,
            corrections=judge_corrections,
        ),
    )
    return rating, judge, rows1, rows2


output_schema_taskA = fully_flatten_pydantic_schema(TEFTaskAResponse)
output_schema_taskB = fully_flatten_pydantic_schema(TEFTaskBResponse)
judge_output_schema = flatten_pydantic_schema(TEFJudgeResponse)


if __name__ == "__main__":
    rating_a, judge_a, rows_a1, rows_a2 = run_section(
        "Task A", task_a_question, task_a_response,
        (eval1_system_instruction_taskA, eval1_taskA_prompt,
         eval2_system_instruction_taskA, eval2_taskA_prompt,
         judge_system_instruction_taskA, judge_prompt_taskA),
        output_schema_taskA, metrics_taskA,
    )
    rating_b, judge_b, rows_b1, rows_b2 = run_section(
        "Task B", task_b_question, task_b_response,
        (eval1_system_instruction_taskB, eval1_taskB_prompt,
         eval2_system_instruction_taskB, eval2_taskB_prompt,
         judge_system_instruction_taskB, judge_prompt_taskB),
        output_schema_taskB, metrics_taskB,
    )

    report = scoring.score_report(rating_a, rating_b)

    print(f"\nModel: {MODEL}")
    print(f"Task A rating: {rating_a}   (eval1 {_avg_rating(rows_a1):.2f} / eval2 {_avg_rating(rows_a2):.2f})")
    print(f"Task B rating: {rating_b}   (eval1 {_avg_rating(rows_b1):.2f} / eval2 {_avg_rating(rows_b2):.2f})")
    print(f"Weighted rating (40/60): {report['rating']}")
    print(f"Score: {report['score']}/{report['scoreMax']}  "
          f"(NCLC {report['nclc']} band {report['bandFloor']}-{report['bandCeiling']})")
    print(f"CEFR {report['cefr']} · Express Entry eligible: {report['expressEntryEligible']} "
          f"(needs {report['expressEntryThreshold']}/450)")
    print(f"Section A: {report['sectionA']['score']}/450 NCLC {report['sectionA']['nclc']}   "
          f"Section B: {report['sectionB']['score']}/450 NCLC {report['sectionB']['nclc']}")
    print(f"\nTask A judge:\n{judge_a.text}")
    print(f"\nTask B judge:\n{judge_b.text}")
