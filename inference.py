#!/usr/bin/env python3
"""
Inference Script for Job Reviewer OpenEnv — Multi-Phase Hiring Pipeline
=======================================================================
MANDATORY
- Before submitting, ensure the following variables are defined:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

STDOUT FORMAT
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import json
import os
import sys
from typing import List, Optional

from openai import OpenAI
from dotenv import load_dotenv

from job_reviewer_env.env import JobReviewerEnv
from job_reviewer_env.models import Action

load_dotenv()

# --- Environment variables ---
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "deepseek-ai/DeepSeek-V3-0324"
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

BENCHMARK = "job-reviewer"


SYSTEM_PROMPT = """You are an expert HR recruiter and resume screener with years of experience in multi-stage hiring pipelines.

You are operating in a MULTI-PHASE review environment. Each candidate goes through multiple evaluation phases, and you will receive feedback after each phase that you must incorporate into subsequent phases.

You must return a JSON object with exactly these fields:
{
  "decision": "<phase-appropriate decision — see instructions>",
  "skills_match_score": <float 0.0-1.0>,
  "experience_match_score": <float 0.0-1.0>,
  "education_match_score": <float 0.0-1.0>,
  "justification": "<detailed justification>"
}

## Scoring Guidelines — be strict and precise:
- skills_match_score: Only count skills explicitly demonstrated. Missing key required skills = below 0.6. "Basic" or tangential skills are NOT proficiency.
- experience_match_score: Only count DIRECTLY relevant years/role. Career changers with adjacent experience = 0.4-0.6. Recent focus matters — if someone was doing backend for 4 years, their frontend score should reflect that their frontend skills are from earlier roles.
- education_match_score: Exact field match = 1.0. Related but different field = 0.6-0.8. Bootcamp = 0.5-0.7.

## Phase-Specific Guidelines:

### Screening Phases (SHORTLIST/REJECT/REVIEW):
- SHORTLIST: Strong match, clearly proceed
- REVIEW: Mixed signals, needs closer look
- REJECT: Clear misfit

### Risk Assessment Phases (LOW_RISK/MODERATE_RISK/HIGH_RISK):
- Evaluate retention risk, skills currency, employment gaps, burnout implications
- Be specific about each risk factor

### Reference Integration Phases (UPGRADE/MAINTAIN/DOWNGRADE):
- Assess how new information changes your previous evaluation
- Be explicit about what changed and why

### Comparison Phases (CANDIDATE_A/CANDIDATE_B/BOTH_VIABLE):
- Compare specific strengths and weaknesses
- Score the STRONGER candidate's fit

### Final Recommendation Phases (ACCEPT/REJECT/MAYBE):
- Synthesize all previous phases
- Address every concern raised in earlier feedback

## Justification Guidelines — be thorough:
- Reference specific skills, roles, and evidence from the resume
- For overqualified candidates: discuss retention risk, whether they are worth interviewing, focus on motivation and expectations
- For career changers: note potential but identify gaps in key areas
- For employment gaps: address long-term commitment questions
- For burnout: discuss implications and whether references clarify the context
- Comment on whether recent focus aligns with the role (e.g., frontend skills from earlier roles vs recent backend/architecture focus)
- Use precise language: "technically excellent", "retention risk", "employment gap", "commitment questions", "worth interviewing", "transferable skills"

## CRITICAL: Use the CONTEXT from previous phases!
If context from previous phases is provided, you MUST reference it and show how your assessment has evolved. Incorporate the grader feedback to improve your evaluation.

Return ONLY valid JSON, no markdown fences, no extra text."""


def build_user_prompt(obs) -> str:
    parts = [
        f"## Job Title: {obs.job_title}",
        f"\n## Job Requirements:\n{obs.job_requirements}",
        f"\n## Candidate Resume:\n{obs.candidate_resume}",
        f"\n## Phase {obs.phase} of {obs.total_phases} — Instructions:\n{obs.instructions}",
    ]

    if obs.context:
        parts.append(f"\n## Context from Previous Phases:\n{obs.context}")
        parts.append(
            "\nIMPORTANT: Use the feedback from previous phases to refine your assessment. "
            "Show how your evaluation has evolved based on new information and grader feedback."
        )

    parts.append(
        "\nAnalyze carefully. Be strict with scores. "
        "Address every relevant factor in your justification. "
        "Return your evaluation as a JSON object."
    )

    return "\n".join(parts)


def call_llm(obs) -> Action:
    """Call the LLM and parse the response into an Action."""
    global client, API_BASE_URL

    user_prompt = build_user_prompt(obs)

    response = None
    last_error = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=600,
            )
            break
        except Exception as exc:
            last_error = exc
            error_text = str(exc)
            if (
                attempt == 0
                and "Not allowed to POST" in error_text
                and "/v3/openai/v1/chat/completions" in error_text
            ):
                API_BASE_URL = "https://router.huggingface.co/v1"
                client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
                continue
            raise

    if response is None and last_error is not None:
        raise last_error

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    data = json.loads(raw)

    # Clamp scores to 0-1
    for key in ["skills_match_score", "experience_match_score", "education_match_score"]:
        data[key] = max(0.0, min(1.0, float(data[key])))

    # Normalize decision
    data["decision"] = data["decision"].upper().strip()

    return Action(**data)


# --- Logging helpers (matching required format) ---

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


def format_action(action: Action) -> str:
    """Format action as a compact string for logging."""
    return (
        f"{action.decision}"
        f"(skills={action.skills_match_score:.2f},"
        f"exp={action.experience_match_score:.2f},"
        f"edu={action.education_match_score:.2f})"
    )


def main():
    env = JobReviewerEnv()
    obs = env.reset()

    task_name = obs.task_id
    rewards: List[float] = []
    step_num = 0
    done = False
    last_error_str = None

    # [START] log
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    while not done:
        step_num += 1
        error_str = None

        try:
            action = call_llm(obs)
        except Exception as e:
            last_error_str = str(e)[:200]
            error_str = last_error_str
            action = Action(
                decision="MAYBE",
                skills_match_score=0.5,
                experience_match_score=0.5,
                education_match_score=0.5,
                justification=f"LLM call failed: {str(e)[:100]}",
            )

        next_obs, reward, done, info = env.step(action)
        rewards.append(reward.total_score)

        action_str = format_action(action)

        # [STEP] log
        log_step(step=step_num, action=action_str, reward=reward.total_score, done=done, error=error_str)

        obs = next_obs

    # Compute overall score (average of all step rewards, clamped to [0, 1])
    score = sum(rewards) / len(rewards) if rewards else 0.0
    score = min(max(score, 0.0), 1.0)

    # Determine success
    success = all(r > 0.0 for r in rewards) and last_error_str is None

    # [END] log
    log_end(success=success, steps=step_num, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
