"""
Multi-phase task definitions for Job Reviewer environment.

Each task is a multi-step hiring pipeline with curriculum scaling:
  - Easy  (2 phases): Screen → Revise with feedback
  - Medium (3 phases): Screen → Revise → Compare candidates
  - Hard  (4 phases): Screen → Deep analysis → Reference check integration → Final recommendation

Each phase has its own ground truth, scoring weights, and valid decisions.
This creates multiple trajectories, long-running episodes, and rich reward signals.
"""

from .models import Action

# ============================================================================
# CANDIDATE RESUMES & JOB DESCRIPTIONS
# ============================================================================

EASY_JOB_TITLE = "Junior Python Developer"
EASY_JOB_REQUIREMENTS = (
    "Requirements:\n"
    "- 1+ years of Python experience\n"
    "- Familiarity with Flask or Django\n"
    "- Basic SQL knowledge\n"
    "- Bachelor's degree in Computer Science or related field\n"
    "- Good communication skills"
)
EASY_CANDIDATE_RESUME = (
    "Name: Alice Johnson\n"
    "Education: B.Sc. Computer Science, State University (GPA 3.7)\n"
    "Experience:\n"
    "- Software Developer Intern, TechCorp (1.5 years)\n"
    "  - Built REST APIs with Flask and PostgreSQL\n"
    "  - Wrote unit tests with pytest, achieving 90% coverage\n"
    "- Freelance Web Developer (6 months)\n"
    "  - Developed Django web applications for small businesses\n"
    "Skills: Python, Flask, Django, SQL, PostgreSQL, Git, HTML/CSS\n"
    "Certifications: AWS Cloud Practitioner"
)

MEDIUM_JOB_TITLE = "Mid-Level Data Engineer"
MEDIUM_JOB_REQUIREMENTS = (
    "Requirements:\n"
    "- 3+ years of experience in data engineering or related role\n"
    "- Proficiency in Python and SQL\n"
    "- Experience with Apache Spark or similar big data frameworks\n"
    "- Knowledge of cloud platforms (AWS/GCP/Azure)\n"
    "- Experience with ETL pipelines and data warehousing\n"
    "- Bachelor's degree in CS, Engineering, or related field\n"
    "- Strong problem-solving skills"
)
MEDIUM_CANDIDATE_A_RESUME = (
    "Name: Bob Martinez\n"
    "Education: B.Sc. Mechanical Engineering, Tech Institute\n"
    "Experience:\n"
    "- Data Analyst, FinanceInc (2 years)\n"
    "  - Wrote complex SQL queries for business reporting\n"
    "  - Built Python scripts for data cleaning and automation\n"
    "  - Created dashboards using Tableau\n"
    "- Mechanical Engineer, ManufactureCo (1.5 years)\n"
    "  - Used MATLAB for simulation and analysis\n"
    "  - Managed production data pipelines (basic ETL)\n"
    "Skills: Python, SQL, Tableau, MATLAB, basic AWS (S3, EC2), Git\n"
    "Courses: Coursera Data Engineering Specialization (completed)"
)
MEDIUM_CANDIDATE_B_RESUME = (
    "Name: David Lee\n"
    "Education: Data Science Bootcamp (6 months), B.A. Economics, City College\n"
    "Experience:\n"
    "- Data Engineer, DataPipeCo (3 years)\n"
    "  - Built and maintained ETL pipelines processing 2TB daily using Python and Spark\n"
    "  - Managed data warehouse on AWS Redshift\n"
    "  - Implemented data quality monitoring with Great Expectations\n"
    "- Junior Analyst, ConsultingFirm (1 year)\n"
    "  - SQL analysis for client reporting\n"
    "Skills: Python, Apache Spark, SQL, AWS (Redshift, S3, Glue, EMR), Airflow, Docker\n"
    "Certifications: AWS Data Analytics Specialty"
)

HARD_JOB_TITLE = "Senior Frontend Engineer"
HARD_JOB_REQUIREMENTS = (
    "Requirements:\n"
    "- 5+ years of frontend development experience\n"
    "- Expert-level React and TypeScript\n"
    "- Experience with state management (Redux, MobX, or Zustand)\n"
    "- Strong CSS/SCSS skills and responsive design\n"
    "- Experience with testing frameworks (Jest, Cypress)\n"
    "- CI/CD experience\n"
    "- Bachelor's degree preferred\n"
    "- Excellent collaboration and mentoring skills"
)
HARD_CANDIDATE_RESUME = (
    "Name: Carol Zhang\n"
    "Education: M.Sc. Computer Science, MIT\n"
    "Experience:\n"
    "- Principal Engineer / Architect, BigTechCo (4 years)\n"
    "  - Led architecture for distributed microservices platform\n"
    "  - Managed team of 12 engineers across backend and infra\n"
    "  - Designed system handling 50M daily requests\n"
    "- Senior Software Engineer, StartupXYZ (2 years)\n"
    "  - Full-stack development with React and Node.js\n"
    "  - Implemented Redux state management and Jest testing\n"
    "  - Set up CI/CD pipelines with GitHub Actions\n"
    "- [1.5 year employment gap]\n"
    "- Software Engineer, WebAgency (1.5 years)\n"
    "  - Built responsive websites with React and SCSS\n"
    "  - Cypress end-to-end testing\n"
    "Skills: React, TypeScript, Redux, Node.js, Python, AWS, Kubernetes, "
    "System Design, SCSS, Jest, Cypress, CI/CD\n"
    "Note: Seeking a less stressful role after burnout recovery"
)

HARD_REFERENCE_CHECK = (
    "Reference Check Results:\n"
    "- BigTechCo Manager: 'Carol was one of our top engineers. She left voluntarily "
    "during a reorganization that eliminated her team. Her burnout was related to "
    "organizational chaos, not the technical work itself. She mentored 5 junior "
    "engineers who all received promotions within a year.'\n"
    "- StartupXYZ CTO: 'Carol built our entire frontend architecture from scratch. "
    "Her React and TypeScript skills are exceptional. She was the go-to person for "
    "all frontend architecture decisions and code reviews.'\n"
    "- Personal Reference: 'During her employment gap, Carol has been doing freelance "
    "React consulting and contributing to open-source React component libraries, "
    "staying current with latest React 19 patterns and Next.js App Router.'"
)

# ============================================================================
# PHASE DEFINITIONS
# ============================================================================

TASK_CONFIGS = {
    # ------------------------------------------------------------------
    # EASY: 2 phases — Screen → Final Recommendation
    # ------------------------------------------------------------------
    "easy_001": {
        "job_title": EASY_JOB_TITLE,
        "job_requirements": EASY_JOB_REQUIREMENTS,
        "candidate_resume": EASY_CANDIDATE_RESUME,
        "difficulty": "easy",
        "phases": [
            {
                # Phase 1: Initial Screening
                "instructions": (
                    "PHASE 1 of 2: INITIAL SCREENING\n\n"
                    "Perform an initial screening of this candidate against the job requirements.\n"
                    "Decision should be one of: SHORTLIST (strong match, proceed), "
                    "REJECT (clear misfit), or REVIEW (needs closer look).\n"
                    "Provide initial scores for skills, experience, and education match.\n"
                    "Justify your screening decision with specific evidence from the resume."
                ),
                "ground_truth": Action(
                    decision="SHORTLIST",
                    skills_match_score=0.95,
                    experience_match_score=0.85,
                    education_match_score=1.0,
                    justification="Candidate exceeds all requirements with relevant Python Flask Django experience and CS degree. Strong skills match with demonstrated REST API development SQL proficiency and testing. Recommend shortlisting for final review.",
                ),
                "weights": {"decision": 0.45, "skills": 0.20, "experience": 0.15, "education": 0.10, "justification": 0.10},
                "valid_decisions": ["SHORTLIST", "REJECT", "REVIEW"],
                "close_decisions": {"SHORTLIST": ["REVIEW"], "REVIEW": ["SHORTLIST"], "REJECT": []},
            },
            {
                # Phase 2: Final Recommendation (with feedback from Phase 1)
                "instructions": (
                    "PHASE 2 of 2: FINAL RECOMMENDATION\n\n"
                    "Based on your initial screening and the feedback provided below, "
                    "make your final hiring recommendation.\n"
                    "Decision should be one of: ACCEPT, REJECT, or MAYBE.\n"
                    "Refine your scores if needed based on the feedback.\n"
                    "Provide a comprehensive final justification addressing any points raised in the feedback."
                ),
                "ground_truth": Action(
                    decision="ACCEPT",
                    skills_match_score=0.95,
                    experience_match_score=0.85,
                    education_match_score=1.0,
                    justification="Candidate clearly exceeds all requirements. Strong Python skills with Flask and Django demonstrated through internship and freelance work. 1.5 years relevant experience building REST APIs. CS degree with excellent GPA. Communication skills evidenced through freelance client work. Recommend accepting this candidate.",
                ),
                "weights": {"decision": 0.40, "skills": 0.15, "experience": 0.15, "education": 0.10, "justification": 0.20},
                "valid_decisions": ["ACCEPT", "REJECT", "MAYBE"],
                "close_decisions": {"ACCEPT": ["MAYBE"], "MAYBE": ["ACCEPT"], "REJECT": []},
            },
        ],
    },

    # ------------------------------------------------------------------
    # MEDIUM: 3 phases — Screen → Revise → Compare candidates
    # ------------------------------------------------------------------
    "medium_001": {
        "job_title": MEDIUM_JOB_TITLE,
        "job_requirements": MEDIUM_JOB_REQUIREMENTS,
        "candidate_resume": MEDIUM_CANDIDATE_A_RESUME,
        "difficulty": "medium",
        "phases": [
            {
                # Phase 1: Initial Screening
                "instructions": (
                    "PHASE 1 of 3: INITIAL SCREENING\n\n"
                    "Perform an initial screening of this candidate against the job requirements.\n"
                    "This candidate is transitioning from a related field.\n"
                    "Decision should be one of: SHORTLIST, REJECT, or REVIEW.\n"
                    "Be strict: only score high for directly demonstrated, relevant skills.\n"
                    "Note any gaps between requirements and candidate qualifications."
                ),
                "ground_truth": Action(
                    decision="REVIEW",
                    skills_match_score=0.55,
                    experience_match_score=0.45,
                    education_match_score=0.7,
                    justification="Candidate has Python and SQL skills but lacks Spark and deep data engineering experience. Career changer transitioning from mechanical engineering with potential but gaps in key areas like big data frameworks and cloud platform depth. Needs review to assess transferable skills.",
                ),
                "weights": {"decision": 0.35, "skills": 0.20, "experience": 0.20, "education": 0.10, "justification": 0.15},
                "valid_decisions": ["SHORTLIST", "REJECT", "REVIEW"],
                "close_decisions": {"REVIEW": ["SHORTLIST"], "SHORTLIST": ["REVIEW"], "REJECT": []},
            },
            {
                # Phase 2: Revised Assessment (with feedback)
                "instructions": (
                    "PHASE 2 of 3: REVISED ASSESSMENT\n\n"
                    "Review the feedback from Phase 1 and revise your assessment.\n"
                    "Focus on transferable skills and learning trajectory.\n"
                    "Decision should be one of: ACCEPT, REJECT, or MAYBE.\n"
                    "Consider: Does the Coursera specialization compensate for lack of hands-on Spark?\n"
                    "Does mechanical engineering background add any analytical value?\n"
                    "Refine your scores and provide an updated justification."
                ),
                "ground_truth": Action(
                    decision="MAYBE",
                    skills_match_score=0.55,
                    experience_match_score=0.50,
                    education_match_score=0.70,
                    justification="After review candidate shows potential with Python SQL and basic AWS but still lacks direct Spark experience and deep data engineering background. Coursera specialization shows learning commitment but does not replace hands-on experience. Mechanical engineering provides analytical foundation. Worth considering but has gaps in key areas required for mid-level role.",
                ),
                "weights": {"decision": 0.30, "skills": 0.20, "experience": 0.20, "education": 0.10, "justification": 0.20},
                "valid_decisions": ["ACCEPT", "REJECT", "MAYBE"],
                "close_decisions": {"MAYBE": ["ACCEPT", "REJECT"], "ACCEPT": ["MAYBE"], "REJECT": ["MAYBE"]},
            },
            {
                # Phase 3: Comparative Decision (second candidate introduced)
                "instructions": (
                    "PHASE 3 of 3: COMPARATIVE ANALYSIS\n\n"
                    "A second candidate (David Lee) has applied for the same role.\n"
                    "Compare BOTH candidates and decide who is the stronger fit.\n\n"
                    "SECOND CANDIDATE RESUME:\n"
                    f"{MEDIUM_CANDIDATE_B_RESUME}\n\n"
                    "Decision should be one of: CANDIDATE_A (Bob Martinez), "
                    "CANDIDATE_B (David Lee), or BOTH_VIABLE.\n"
                    "Score the STRONGER candidate's fit (not a comparison score).\n"
                    "Justify your comparison with specific evidence from both resumes."
                ),
                "ground_truth": Action(
                    decision="CANDIDATE_B",
                    skills_match_score=0.85,
                    experience_match_score=0.80,
                    education_match_score=0.60,
                    justification="David Lee is the stronger candidate with 3 years direct data engineering experience building ETL pipelines with Spark and managing AWS Redshift warehouse. He has hands-on experience with key requirements including Spark Airflow and cloud platforms. Bob Martinez has potential as career changer but lacks direct data engineering experience and Spark skills. David stronger technical fit despite weaker formal education with bootcamp instead of CS degree.",
                ),
                "weights": {"decision": 0.25, "skills": 0.15, "experience": 0.15, "education": 0.10, "justification": 0.35},
                "valid_decisions": ["CANDIDATE_A", "CANDIDATE_B", "BOTH_VIABLE"],
                "close_decisions": {"CANDIDATE_B": ["BOTH_VIABLE"], "CANDIDATE_A": ["BOTH_VIABLE"], "BOTH_VIABLE": ["CANDIDATE_A", "CANDIDATE_B"]},
            },
        ],
    },

    # ------------------------------------------------------------------
    # HARD: 4 phases — Screen → Deep Analysis → Reference Check → Final
    # ------------------------------------------------------------------
    "hard_001": {
        "job_title": HARD_JOB_TITLE,
        "job_requirements": HARD_JOB_REQUIREMENTS,
        "candidate_resume": HARD_CANDIDATE_RESUME,
        "difficulty": "hard",
        "phases": [
            {
                # Phase 1: Initial Screening
                "instructions": (
                    "PHASE 1 of 4: INITIAL SCREENING\n\n"
                    "Perform an initial screening of this candidate.\n"
                    "Note: This candidate appears significantly overqualified, "
                    "has an employment gap, and mentions burnout.\n"
                    "Decision should be one of: SHORTLIST, REJECT, or REVIEW.\n"
                    "Flag any concerns about retention risk, overqualification, or red flags.\n"
                    "Be thorough — this is a complex case requiring careful analysis."
                ),
                "ground_truth": Action(
                    decision="REVIEW",
                    skills_match_score=0.90,
                    experience_match_score=0.70,
                    education_match_score=1.0,
                    justification="Candidate is technically excellent and overqualified with principal architect level experience applying for senior frontend role. Strong frontend skills from earlier roles but recent focus was backend and architecture. Employment gap with burnout note raises retention risk and commitment questions. Needs deeper review before proceeding.",
                ),
                "weights": {"decision": 0.25, "skills": 0.15, "experience": 0.15, "education": 0.10, "justification": 0.35},
                "valid_decisions": ["SHORTLIST", "REJECT", "REVIEW"],
                "close_decisions": {"REVIEW": ["SHORTLIST"], "SHORTLIST": ["REVIEW"], "REJECT": []},
            },
            {
                # Phase 2: Deep Analysis (focus on red flags)
                "instructions": (
                    "PHASE 2 of 4: DEEP ANALYSIS\n\n"
                    "Based on your screening and the feedback, perform a deep analysis.\n"
                    "Focus specifically on:\n"
                    "1. Retention risk — will an overqualified candidate stay in this role?\n"
                    "2. Skills currency — are frontend skills current despite recent backend focus?\n"
                    "3. Employment gap — what does the 1.5 year gap suggest?\n"
                    "4. Burnout — what are the implications for workload and long-term commitment?\n\n"
                    "Decision should be one of: LOW_RISK, MODERATE_RISK, or HIGH_RISK.\n"
                    "Score the candidate's CURRENT fit for this specific role.\n"
                    "Provide detailed analysis of each risk factor."
                ),
                "ground_truth": Action(
                    decision="MODERATE_RISK",
                    skills_match_score=0.80,
                    experience_match_score=0.65,
                    education_match_score=1.0,
                    justification="Moderate retention risk due to overqualification as principal architect applying for senior role. Frontend skills from earlier roles are strong with React TypeScript Redux Jest Cypress experience but 4 years of recent backend architecture focus means skills may need refreshing. Employment gap of 1.5 years combined with explicit burnout raises long-term commitment questions. However candidate explicitly seeks less stressful role which could mean genuine motivation for this position. Worth proceeding to reference check to clarify burnout context and current skill level.",
                ),
                "weights": {"decision": 0.20, "skills": 0.15, "experience": 0.15, "education": 0.05, "justification": 0.45},
                "valid_decisions": ["LOW_RISK", "MODERATE_RISK", "HIGH_RISK"],
                "close_decisions": {"MODERATE_RISK": ["LOW_RISK", "HIGH_RISK"], "LOW_RISK": ["MODERATE_RISK"], "HIGH_RISK": ["MODERATE_RISK"]},
            },
            {
                # Phase 3: Reference Check Integration
                "instructions": (
                    "PHASE 3 of 4: REFERENCE CHECK INTEGRATION\n\n"
                    "Reference check results have come in. Integrate this new information "
                    "into your assessment and determine if it changes your risk evaluation.\n\n"
                    f"{HARD_REFERENCE_CHECK}\n\n"
                    "Decision should be one of: UPGRADE (lower risk than before), "
                    "MAINTAIN (same risk level), or DOWNGRADE (higher risk).\n"
                    "Re-score the candidate considering the reference information.\n"
                    "Explain how the references change or confirm your previous analysis."
                ),
                "ground_truth": Action(
                    decision="UPGRADE",
                    skills_match_score=0.90,
                    experience_match_score=0.75,
                    education_match_score=1.0,
                    justification="References significantly alleviate concerns. Burnout was caused by organizational chaos not work itself which reduces long-term commitment risk. Manager confirms excellent mentoring of junior engineers aligning with collaboration requirements. CTO confirms exceptional frontend React TypeScript architecture skills are genuine and current. Freelance React consulting during gap means skills are not stale and candidate stayed current with latest patterns. Upgrading risk assessment as key concerns about skills currency and burnout cause are now addressed. Retention risk from overqualification remains but is mitigated by candidate explicitly wanting less stressful role.",
                ),
                "weights": {"decision": 0.20, "skills": 0.10, "experience": 0.15, "education": 0.05, "justification": 0.50},
                "valid_decisions": ["UPGRADE", "MAINTAIN", "DOWNGRADE"],
                "close_decisions": {"UPGRADE": ["MAINTAIN"], "MAINTAIN": ["UPGRADE", "DOWNGRADE"], "DOWNGRADE": ["MAINTAIN"]},
            },
            {
                # Phase 4: Final Recommendation
                "instructions": (
                    "PHASE 4 of 4: FINAL RECOMMENDATION\n\n"
                    "Make your final hiring recommendation based on ALL previous phases.\n"
                    "Synthesize your screening, deep analysis, and reference check findings.\n"
                    "Decision should be one of: ACCEPT, REJECT, or MAYBE.\n"
                    "Provide a comprehensive final justification that addresses:\n"
                    "- Technical fit and skills currency\n"
                    "- Retention risk and overqualification\n"
                    "- Employment gap and burnout context\n"
                    "- Reference check findings\n"
                    "- Overall recommendation with any conditions (e.g., interview focus areas)"
                ),
                "ground_truth": Action(
                    decision="ACCEPT",
                    skills_match_score=0.90,
                    experience_match_score=0.80,
                    education_match_score=1.0,
                    justification="Recommend accepting for interview. Technically excellent candidate with strong frontend skills confirmed by references. React TypeScript Redux experience from earlier roles plus recent freelance consulting shows current skills. References clarify burnout was organizational not work-related reducing commitment concerns. Overqualification retention risk remains but candidate explicitly seeks less stressful senior role suggesting genuine motivation. Employment gap productively spent on freelance and open-source work. Worth interviewing with focus on motivation expectations and long-term career goals to confirm fit. Strong mentoring skills align with team collaboration requirements.",
                ),
                "weights": {"decision": 0.25, "skills": 0.10, "experience": 0.10, "education": 0.05, "justification": 0.50},
                "valid_decisions": ["ACCEPT", "REJECT", "MAYBE"],
                "close_decisions": {"ACCEPT": ["MAYBE"], "MAYBE": ["ACCEPT"], "REJECT": []},
            },
        ],
    },
}


# ============================================================================
# GRADING
# ============================================================================

def _safe_float(value, default=0.0) -> float:
    """Convert any value to a pure Python float, handling None, strings, numpy types."""
    if value is None:
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp_grade(value: float) -> float:
    """Clamp grade to [0, 1] and ensure it's not exactly 0.0 or 1.0 for strict boundary checks."""
    value = max(0.0, min(1.0, value))
    if value <= 0.0:
        value = 0.001
    if value >= 1.0:
        value = 0.999
    return float(value)


def grade(task_id: str, phase_index: int, action: Action) -> "Reward":
    """Deterministic grader: compares agent action against phase-specific ground truth."""
    from .models import Reward

    config = TASK_CONFIGS[task_id]
    phase = config["phases"][phase_index]
    gt: Action = phase["ground_truth"]
    weights = phase["weights"]
    valid_decisions = phase["valid_decisions"]
    close_decisions = phase["close_decisions"]

    # Safely extract action fields with type coercion
    action_skills = _safe_float(action.skills_match_score)
    action_experience = _safe_float(action.experience_match_score)
    action_education = _safe_float(action.education_match_score)
    action_decision = (action.decision or "").upper().strip()
    action_justification = action.justification or ""

    gt_skills = _safe_float(gt.skills_match_score)
    gt_experience = _safe_float(gt.experience_match_score)
    gt_education = _safe_float(gt.education_match_score)
    gt_decision = gt.decision.upper().strip()

    # 1) Decision score
    if action_decision == gt_decision:
        decision_score = 1.0
    elif action_decision in close_decisions.get(gt_decision, []):
        decision_score = 0.4
    elif action_decision in valid_decisions:
        decision_score = 0.1
    else:
        decision_score = 0.0

    # 2) Numeric score closeness (1 - absolute error)
    skills_score = float(max(0.0, 1.0 - abs(action_skills - gt_skills)))
    experience_score = float(max(0.0, 1.0 - abs(action_experience - gt_experience)))
    education_score = float(max(0.0, 1.0 - abs(action_education - gt_education)))

    # 3) Justification score: keyword overlap with ground truth
    gt_keywords = set(gt.justification.lower().split())
    action_keywords = set(action_justification.lower().split())
    if len(gt_keywords) > 0:
        overlap = len(gt_keywords & action_keywords)
        justification_score = float(min(1.0, overlap / (len(gt_keywords) * 0.5)))
    else:
        justification_score = 1.0 if len(action_justification) > 10 else 0.0

    # 4) Weighted total
    total = float(
        weights["decision"] * decision_score
        + weights["skills"] * skills_score
        + weights["experience"] * experience_score
        + weights["education"] * education_score
        + weights["justification"] * justification_score
    )
    total = round(max(0.0, min(1.0, total)), 4)

    # Clamp all scores to strict (0, 1) boundaries and ensure pure float types
    decision_score = _clamp_grade(decision_score)
    skills_score = _clamp_grade(skills_score)
    experience_score = _clamp_grade(experience_score)
    education_score = _clamp_grade(education_score)
    justification_score = _clamp_grade(round(justification_score, 4))
    total = _clamp_grade(total)

    # Debug logging
    print(f"GRADE [{task_id} phase {phase_index}]: total={total} ({type(total).__name__}), "
          f"decision={decision_score}, skills={skills_score}, experience={experience_score}, "
          f"education={education_score}, justification={justification_score}")

    # Build feedback
    feedback_parts = []
    if decision_score < 1.0:
        feedback_parts.append(f"Expected decision '{gt_decision}', got '{action_decision}'.")
    if skills_score < 0.8:
        feedback_parts.append(f"Skills score off by {abs(action_skills - gt_skills):.2f}.")
    if experience_score < 0.8:
        feedback_parts.append(f"Experience score off by {abs(action_experience - gt_experience):.2f}.")
    if justification_score < 0.7:
        feedback_parts.append("Justification missing key points. Consider addressing: "
                              + ", ".join(list(gt_keywords - action_keywords)[:8]) + ".")
    if not feedback_parts:
        feedback_parts.append("Good evaluation overall.")

    return Reward(
        total_score=total,
        decision_score=decision_score,
        skills_score=skills_score,
        experience_score=experience_score,
        education_score=education_score,
        justification_score=justification_score,
        feedback=" ".join(feedback_parts),
    )


def _normalize_action(action) -> "Action":
    """
    Normalize an action to an Action model instance.
    Accepts: Action instance, dict, or any object with the required fields.
    Phase 2 validator may pass raw dicts instead of Pydantic models.
    """
    if isinstance(action, Action):
        return action
    if isinstance(action, dict):
        return Action(
            decision=str(action.get("decision", "")).upper().strip(),
            skills_match_score=_clamp_grade(_safe_float(action.get("skills_match_score", 0.5))),
            experience_match_score=_clamp_grade(_safe_float(action.get("experience_match_score", 0.5))),
            education_match_score=_clamp_grade(_safe_float(action.get("education_match_score", 0.5))),
            justification=str(action.get("justification", "")),
        )
    # Try attribute access as fallback (e.g. SimpleNamespace or other objects)
    return Action(
        decision=str(getattr(action, "decision", "")).upper().strip(),
        skills_match_score=_clamp_grade(_safe_float(getattr(action, "skills_match_score", 0.5))),
        experience_match_score=_clamp_grade(_safe_float(getattr(action, "experience_match_score", 0.5))),
        education_match_score=_clamp_grade(_safe_float(getattr(action, "education_match_score", 0.5))),
        justification=str(getattr(action, "justification", "")),
    )


def _get_phase_index(observation) -> int:
    """Safely extract 0-based phase index from observation (Pydantic model or dict)."""
    if observation is None:
        return 0
    if isinstance(observation, dict):
        return max(0, int(observation.get("phase", 1)) - 1)
    if hasattr(observation, "phase"):
        return max(0, int(observation.phase) - 1)
    return 0


# Per-task grader functions conforming to OpenEnv standard interface.
# Must accept (action, observation=None) and return a pure Python float in (0.0, 1.0).

def grade_easy_001(action, observation=None) -> float:
    """Grader for easy_001 task. Returns score strictly in (0.0, 1.0)."""
    try:
        action = _normalize_action(action)
        phase_index = _get_phase_index(observation)
        reward = grade("easy_001", phase_index, action)
        result = _clamp_grade(float(reward.total_score))
        print(f"GRADE [easy_001 phase={phase_index}]: {result} ({type(result).__name__})")
        assert isinstance(result, float), f"grade_easy_001 returned non-float: {type(result)}"
        assert 0.0 < result < 1.0, f"grade_easy_001 out of (0,1): {result}"
        return result
    except AssertionError:
        raise
    except Exception as e:
        print(f"GRADE ERROR [easy_001]: {e}")
        return 0.001


def grade_medium_001(action, observation=None) -> float:
    """Grader for medium_001 task. Returns score strictly in (0.0, 1.0)."""
    try:
        action = _normalize_action(action)
        phase_index = _get_phase_index(observation)
        reward = grade("medium_001", phase_index, action)
        result = _clamp_grade(float(reward.total_score))
        print(f"GRADE [medium_001 phase={phase_index}]: {result} ({type(result).__name__})")
        assert isinstance(result, float), f"grade_medium_001 returned non-float: {type(result)}"
        assert 0.0 < result < 1.0, f"grade_medium_001 out of (0,1): {result}"
        return result
    except AssertionError:
        raise
    except Exception as e:
        print(f"GRADE ERROR [medium_001]: {e}")
        return 0.001


def grade_hard_001(action, observation=None) -> float:
    """Grader for hard_001 task. Returns score strictly in (0.0, 1.0)."""
    try:
        action = _normalize_action(action)
        phase_index = _get_phase_index(observation)
        reward = grade("hard_001", phase_index, action)
        result = _clamp_grade(float(reward.total_score))
        print(f"GRADE [hard_001 phase={phase_index}]: {result} ({type(result).__name__})")
        assert isinstance(result, float), f"grade_hard_001 returned non-float: {type(result)}"
        assert 0.0 < result < 1.0, f"grade_hard_001 out of (0,1): {result}"
        return result
    except AssertionError:
        raise
    except Exception as e:
        print(f"GRADE ERROR [hard_001]: {e}")
        return 0.001
