"""
FastAPI server for Hugging Face Space deployment.
Exposes /reset, /step, /state and standard OpenEnv endpoints.
"""

from fastapi import FastAPI
from job_reviewer_env.env import JobReviewerEnv
from job_reviewer_env.models import Action, Observation, Reward

app = FastAPI(
    title="Job Reviewer OpenEnv — Multi-Phase Hiring Pipeline",
    version="1.0.0",
)
env = JobReviewerEnv()


@app.get("/")
def root():
    return {"status": "ok", "environment": "job-reviewer", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return {
        "name": "job-reviewer",
        "description": (
            "Multi-phase hiring pipeline environment. An LLM agent evaluates candidates "
            "through progressive review stages with grading feedback fed back as context."
        ),
        "version": "1.0.0",
        "tasks": [
            {
                "id": "easy_001",
                "difficulty": "easy",
                "description": "2-phase pipeline: Screen → Final Recommendation",
                "grader": "job_reviewer_env.tasks:grade_easy_001",
            },
            {
                "id": "medium_001",
                "difficulty": "medium",
                "description": "3-phase pipeline: Screen → Revise → Compare candidates",
                "grader": "job_reviewer_env.tasks:grade_medium_001",
            },
            {
                "id": "hard_001",
                "difficulty": "hard",
                "description": "4-phase pipeline: Screen → Deep Analysis → Reference Check → Final",
                "grader": "job_reviewer_env.tasks:grade_hard_001",
            },
        ],
    }


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {
                "id": "easy_001",
                "difficulty": "easy",
                "description": "2-phase pipeline: Screen → Final Recommendation",
                "grader": "job_reviewer_env.tasks:grade_easy_001",
                "num_phases": 2,
            },
            {
                "id": "medium_001",
                "difficulty": "medium",
                "description": "3-phase pipeline: Screen → Revise → Compare candidates",
                "grader": "job_reviewer_env.tasks:grade_medium_001",
                "num_phases": 3,
            },
            {
                "id": "hard_001",
                "difficulty": "hard",
                "description": "4-phase pipeline: Screen → Deep Analysis → Reference Check → Final",
                "grader": "job_reviewer_env.tasks:grade_hard_001",
                "num_phases": 4,
            },
        ]
    }


@app.get("/schema")
def schema():
    return {
        "action": Action.model_json_schema(),
        "observation": Observation.model_json_schema(),
        "state": {
            "type": "object",
            "properties": {
                "current_task_index": {"type": "integer"},
                "current_phase_index": {"type": "integer"},
                "total_tasks": {"type": "integer"},
                "total_steps": {"type": "integer"},
                "done": {"type": "boolean"},
            },
        },
    }


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


@app.get("/reset")
def reset_get():
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
def step(action: Action):
    next_obs, reward, done, info = env.step(action)
    return {
        "observation": next_obs.model_dump() if next_obs else None,
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return env.state()
