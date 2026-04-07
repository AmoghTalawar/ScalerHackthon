"""
FastAPI server for Hugging Face Space deployment.
Exposes /reset, /step, /state endpoints.
"""

from fastapi import FastAPI
from job_reviewer_env.env import JobReviewerEnv
from job_reviewer_env.models import Action

app = FastAPI(title="Job Reviewer OpenEnv — Multi-Phase Hiring Pipeline")
env = JobReviewerEnv()


@app.get("/")
def root():
    return {"status": "ok", "environment": "job-reviewer", "version": "1.0.0"}


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
