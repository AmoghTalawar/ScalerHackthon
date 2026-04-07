from pydantic import BaseModel, Field


class Observation(BaseModel):
    """What the agent sees: a resume, job description, phase info, and accumulated context."""
    task_id: str = Field(description="Unique task identifier")
    difficulty: str = Field(description="easy | medium | hard")
    phase: int = Field(description="Current phase number (1-based)")
    total_phases: int = Field(description="Total phases for this task")
    job_title: str = Field(description="Title of the job posting")
    job_requirements: str = Field(description="Full job requirements text")
    candidate_resume: str = Field(description="Full candidate resume text")
    instructions: str = Field(description="Phase-specific instructions")
    context: str = Field(default="", description="Accumulated context from previous phases (actions, feedback)")


class Action(BaseModel):
    """The agent's structured review decision."""
    decision: str = Field(description="Phase-appropriate decision string")
    skills_match_score: float = Field(ge=0.0, le=1.0, description="How well skills match (0-1)")
    experience_match_score: float = Field(ge=0.0, le=1.0, description="How well experience matches (0-1)")
    education_match_score: float = Field(ge=0.0, le=1.0, description="How well education matches (0-1)")
    justification: str = Field(description="Brief justification for the decision")


class Reward(BaseModel):
    """Graded feedback with partial-progress signals."""
    total_score: float = Field(ge=0.0, le=1.0, description="Overall reward 0-1")
    decision_score: float = Field(ge=0.0, le=1.0, description="Reward for correct decision")
    skills_score: float = Field(ge=0.0, le=1.0, description="Reward for skills assessment accuracy")
    experience_score: float = Field(ge=0.0, le=1.0, description="Reward for experience assessment accuracy")
    education_score: float = Field(ge=0.0, le=1.0, description="Reward for education assessment accuracy")
    justification_score: float = Field(ge=0.0, le=1.0, description="Reward for justification quality")
    feedback: str = Field(description="Human-readable grading feedback")
