"""
JobReviewerEnv — OpenEnv-compatible multi-phase hiring pipeline environment.

Each task progresses through multiple review phases (curriculum scaling):
  - Easy:   2 phases (Screen → Final Recommendation)
  - Medium: 3 phases (Screen → Revise → Compare Candidates)
  - Hard:   4 phases (Screen → Deep Analysis → Reference Check → Final)

The agent receives grading feedback after each phase, which is included
as context for subsequent phases — enabling feedback-driven learning
and multiple valid trajectories.
"""

from typing import Any, Dict, List, Optional, Tuple
from .models import Observation, Action, Reward
from .tasks import TASK_CONFIGS, grade


class JobReviewerEnv:
    """
    OpenEnv environment: multi-phase resume review pipeline.

    API:
        reset()  -> Observation
        step(action) -> (Observation | None, Reward, bool, dict)
        state()  -> dict
    """

    def __init__(self):
        self._task_ids: List[str] = list(TASK_CONFIGS.keys())
        self._current_task_idx: int = 0
        self._current_phase_idx: int = 0
        self._done: bool = False
        self._rewards: List[Reward] = []
        self._phase_history: List[Dict[str, Any]] = []  # history within current task
        self._all_rewards: List[Reward] = []  # all rewards across all tasks
        self._current_observation: Optional[Observation] = None

    def _build_observation(self, task_id: str, phase_idx: int) -> Observation:
        """Build observation for a given task and phase, including accumulated context."""
        config = TASK_CONFIGS[task_id]
        phase = config["phases"][phase_idx]
        num_phases = len(config["phases"])

        # Build context from previous phases in this task
        context_parts = []
        for entry in self._phase_history:
            phase_num = entry["phase"] + 1
            context_parts.append(
                f"--- Phase {phase_num} Results ---\n"
                f"Your decision: {entry['action'].decision}\n"
                f"Your scores: skills={entry['action'].skills_match_score:.2f}, "
                f"experience={entry['action'].experience_match_score:.2f}, "
                f"education={entry['action'].education_match_score:.2f}\n"
                f"Your justification: {entry['action'].justification}\n"
                f"Grader feedback: {entry['reward'].feedback}\n"
                f"Phase score: {entry['reward'].total_score:.2f}/1.00\n"
            )
        context = "\n".join(context_parts)

        return Observation(
            task_id=task_id,
            difficulty=config["difficulty"],
            phase=phase_idx + 1,
            total_phases=num_phases,
            job_title=config["job_title"],
            job_requirements=config["job_requirements"],
            candidate_resume=config["candidate_resume"],
            instructions=phase["instructions"],
            context=context,
        )

    # ------------------------------------------------------------------
    # OpenEnv API
    # ------------------------------------------------------------------

    def reset(self) -> Observation:
        """Reset the environment and return the first observation."""
        self._current_task_idx = 0
        self._current_phase_idx = 0
        self._done = False
        self._rewards = []
        self._phase_history = []
        self._all_rewards = []

        task_id = self._task_ids[0]
        self._current_observation = self._build_observation(task_id, 0)
        return self._current_observation

    def step(self, action: Action) -> Tuple[Optional[Observation], Reward, bool, Dict[str, Any]]:
        """
        Process agent action for the current phase, return (next_observation, reward, done, info).

        Advances through phases within a task, then moves to the next task.
        Grading feedback from each phase is included as context for subsequent phases.
        """
        if self._done:
            raise RuntimeError("Environment is done. Call reset() to start over.")

        task_id = self._task_ids[self._current_task_idx]
        config = TASK_CONFIGS[task_id]
        num_phases = len(config["phases"])

        # Grade the current phase
        reward = grade(task_id, self._current_phase_idx, action)
        self._all_rewards.append(reward)

        # Record in phase history (for context building)
        self._phase_history.append({
            "phase": self._current_phase_idx,
            "action": action,
            "reward": reward,
        })

        # Determine next state
        if self._current_phase_idx < num_phases - 1:
            # More phases in this task
            self._current_phase_idx += 1
            self._current_observation = self._build_observation(task_id, self._current_phase_idx)
            total_completed = sum(
                len(TASK_CONFIGS[tid]["phases"])
                for tid in self._task_ids[:self._current_task_idx]
            ) + self._current_phase_idx
            total_steps = sum(len(TASK_CONFIGS[tid]["phases"]) for tid in self._task_ids)
            info = {
                "task_id": task_id,
                "phase": self._current_phase_idx + 1,
                "total_phases": num_phases,
                "steps_completed": total_completed,
                "total_steps": total_steps,
            }
        else:
            # Task complete — move to next task
            self._current_task_idx += 1
            self._current_phase_idx = 0
            self._phase_history = []

            if self._current_task_idx >= len(self._task_ids):
                # All tasks done
                self._done = True
                self._current_observation = None
                avg_score = sum(r.total_score for r in self._all_rewards) / len(self._all_rewards)
                per_task_scores = {}
                reward_idx = 0
                for tid in self._task_ids:
                    n_phases = len(TASK_CONFIGS[tid]["phases"])
                    task_rewards = self._all_rewards[reward_idx:reward_idx + n_phases]
                    per_task_scores[tid] = round(
                        sum(r.total_score for r in task_rewards) / len(task_rewards), 4
                    )
                    reward_idx += n_phases
                info = {
                    "tasks_completed": len(self._task_ids),
                    "average_score": round(avg_score, 4),
                    "per_task_scores": per_task_scores,
                }
            else:
                # Start next task
                next_task_id = self._task_ids[self._current_task_idx]
                self._current_observation = self._build_observation(next_task_id, 0)
                total_steps = sum(len(TASK_CONFIGS[tid]["phases"]) for tid in self._task_ids)
                completed = sum(
                    len(TASK_CONFIGS[tid]["phases"])
                    for tid in self._task_ids[:self._current_task_idx]
                )
                info = {
                    "task_id": next_task_id,
                    "phase": 1,
                    "tasks_completed": self._current_task_idx,
                    "tasks_remaining": len(self._task_ids) - self._current_task_idx,
                    "steps_completed": completed,
                    "total_steps": total_steps,
                }

        return self._current_observation, reward, self._done, info

    def state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return {
            "current_task_index": self._current_task_idx,
            "current_phase_index": self._current_phase_idx,
            "total_tasks": len(self._task_ids),
            "total_steps": sum(len(TASK_CONFIGS[tid]["phases"]) for tid in self._task_ids),
            "done": self._done,
            "current_observation": self._current_observation.model_dump() if self._current_observation else None,
            "rewards_so_far": [r.model_dump() for r in self._all_rewards],
        }
