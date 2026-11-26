from dataclasses import dataclass, field
from typing import Any, Literal

QuestionType = Literal[
    "single_choice",
    "multiple_choice",
    "rating_scale",
    "scenario",
    "technical_preference",
]


@dataclass(frozen=True)
class QuestionOption:
    """Selectable option for choice, scenario, or technical preference questions."""

    id: str
    label: str
    description: str | None = None
    domain_weights: dict[str, float] = field(default_factory=dict)
    dimension_weights: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TriggerRule:
    """Condition determining when an adaptive follow-up question is unlocked."""

    source_question_id: str
    expected_values: tuple[str, ...] = ()
    min_rating: int | None = None


@dataclass(frozen=True)
class QuestionDefinition:
    """Immutable definition of an assessment question."""

    id: str
    prompt: str
    question_type: QuestionType
    category: str
    help_text: str | None = None
    options: tuple[QuestionOption, ...] = ()
    min_value: int | None = None
    max_value: int | None = None
    min_label: str | None = None
    max_label: str | None = None
    max_selections: int | None = None
    is_adaptive: bool = False
    trigger: TriggerRule | None = None
    rating_target_domain: str | None = None
    rating_target_dimension: str | None = None


QUESTION_BANK: tuple[QuestionDefinition, ...] = (
    QuestionDefinition(
        id="q_domains_interest",
        prompt="Which research areas spark your curiosity the most?",
        question_type="multiple_choice",
        category="Subject Interest",
        help_text="Select up to 3 areas you would enjoy exploring for several months.",
        max_selections=3,
        options=(
            QuestionOption(
                id="ai_ml",
                label="Artificial Intelligence & Machine Learning",
                description="Foundation models, representation learning, reasoning, and evaluation.",
                domain_weights={"ai_ml": 1.0, "data_science": 0.4},
            ),
            QuestionOption(
                id="nlp_ir",
                label="Natural Language Processing & Information Retrieval",
                description="Language understanding, semantic search, and scientific text mining.",
                domain_weights={"nlp": 1.0, "ai_ml": 0.5},
            ),
            QuestionOption(
                id="systems_sec",
                label="Distributed Systems, Cloud & Cybersecurity",
                description="Scalable infrastructure, privacy, verification, and systems reliability.",
                domain_weights={"systems_security": 1.0},
            ),
            QuestionOption(
                id="hci_edtech",
                label="Human-Computer Interaction & Educational Technology",
                description="Interactive tools, human-AI collaboration, and learning sciences.",
                domain_weights={"hci": 1.0},
            ),
            QuestionOption(
                id="bio_health",
                label="Computational Biology & Healthcare Informatics",
                description="Clinical decision support, genomics, and biomedical data analysis.",
                domain_weights={"bio_health": 1.0, "data_science": 0.4},
            ),
            QuestionOption(
                id="data_society",
                label="Data Science, Economics & Computational Social Science",
                description="Causal inference, policy modeling, and large-scale societal datasets.",
                domain_weights={"data_science": 1.0, "hci": 0.2},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_problem_solving_style",
        prompt="When approaching an open-ended problem, which mode of thinking energizes you most?",
        question_type="single_choice",
        category="Problem-Solving Preference",
        options=(
            QuestionOption(
                id="theoretical",
                label="Formalizing proofs, mathematical models, or theoretical guarantees",
                dimension_weights={"theoretical_rigor": 1.0, "empirical_experimentation": 0.2},
            ),
            QuestionOption(
                id="empirical",
                label="Designing experiments, running benchmarks, and analyzing real datasets",
                dimension_weights={"empirical_experimentation": 1.0, "applied_engineering": 0.5},
            ),
            QuestionOption(
                id="systems_building",
                label="Architecting and building working prototypes or research software",
                dimension_weights={"applied_engineering": 1.0, "empirical_experimentation": 0.4},
            ),
            QuestionOption(
                id="human_centered",
                label="Studying user behavior, conducting interviews, and evaluating real-world impact",
                dimension_weights={"human_centered_inquiry": 1.0},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_math_comfort",
        prompt="How comfortable are you engaging with formal mathematics (linear algebra, probability, optimization) in your research?",
        question_type="rating_scale",
        category="Skill Confidence",
        min_value=1,
        max_value=5,
        min_label="Prefer minimal math",
        max_label="Very comfortable with proofs & equations",
        rating_target_dimension="theoretical_rigor",
    ),
    QuestionDefinition(
        id="q_coding_comfort",
        prompt="How confident are you implementing and debugging research pipelines in code?",
        question_type="rating_scale",
        category="Skill Confidence",
        min_value=1,
        max_value=5,
        min_label="Still learning basics",
        max_label="Comfortable building end-to-end systems",
        rating_target_dimension="applied_engineering",
    ),
    QuestionDefinition(
        id="q_scenario_ambiguity",
        prompt="Scenario: Your initial hypothesis fails on a benchmark dataset. What is your preferred next step?",
        question_type="scenario",
        category="Methodology Preference",
        options=(
            QuestionOption(
                id="error_analysis",
                label="Perform systematic error analysis on failure cases and inspect data quality",
                dimension_weights={"empirical_experimentation": 1.0},
            ),
            QuestionOption(
                id="revisit_theory",
                label="Re-examine the mathematical assumptions to find where the model breaks down",
                dimension_weights={"theoretical_rigor": 1.0},
            ),
            QuestionOption(
                id="user_context",
                label="Check whether the benchmark metrics reflect real human or domain needs",
                dimension_weights={"human_centered_inquiry": 1.0},
            ),
            QuestionOption(
                id="iterate_architecture",
                label="Refactor the pipeline and test alternative architectures or baselines",
                dimension_weights={"applied_engineering": 1.0},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_technical_preference",
        prompt="Which technical artifact would you be proudest to produce at the end of a research project?",
        question_type="technical_preference",
        category="Technical Preference",
        options=(
            QuestionOption(
                id="benchmark_dataset",
                label="A curated, reproducible benchmark dataset and evaluation suite",
                domain_weights={"data_science": 0.6, "nlp": 0.4},
                dimension_weights={"empirical_experimentation": 0.9},
            ),
            QuestionOption(
                id="open_source_tool",
                label="An open-source library, interactive system, or deployed prototype",
                domain_weights={"systems_security": 0.6, "hci": 0.5},
                dimension_weights={"applied_engineering": 1.0},
            ),
            QuestionOption(
                id="theoretical_paper",
                label="A theoretical framework or formal analysis with provable bounds",
                domain_weights={"ai_ml": 0.5, "systems_security": 0.3},
                dimension_weights={"theoretical_rigor": 1.0},
            ),
            QuestionOption(
                id="empirical_study",
                label="An interdisciplinary empirical study with actionable domain insights",
                domain_weights={"bio_health": 0.6, "hci": 0.5, "data_science": 0.4},
                dimension_weights={"human_centered_inquiry": 0.9},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_application_impact",
        prompt="How important is it that your research has a direct, near-term real-world application?",
        question_type="rating_scale",
        category="Application Domain Preference",
        min_value=1,
        max_value=5,
        min_label="Purely foundational curiosity",
        max_label="Direct real-world impact is essential",
        rating_target_dimension="applied_impact",
    ),
    # --- Adaptive follow-up questions ---
    QuestionDefinition(
        id="q_followup_ai_nlp",
        prompt="Follow-up: Within AI/NLP, which research angle appeals to you more?",
        question_type="single_choice",
        category="Adaptive Follow-up",
        help_text="Shown because you selected AI/ML or NLP.",
        is_adaptive=True,
        trigger=TriggerRule(
            source_question_id="q_domains_interest",
            expected_values=("ai_ml", "nlp_ir"),
        ),
        options=(
            QuestionOption(
                id="efficiency_eval",
                label="Model efficiency, quantization, and rigorous evaluation",
                domain_weights={"ai_ml": 0.8},
                dimension_weights={"empirical_experimentation": 0.7, "applied_engineering": 0.6},
            ),
            QuestionOption(
                id="scientific_nlp",
                label="Scientific literature mining, RAG, and factual grounding",
                domain_weights={"nlp": 1.0},
                dimension_weights={"empirical_experimentation": 0.8},
            ),
            QuestionOption(
                id="interpretability",
                label="Explainability, interpretability, and alignment",
                domain_weights={"ai_ml": 0.9, "hci": 0.3},
                dimension_weights={"theoretical_rigor": 0.6, "human_centered_inquiry": 0.4},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_followup_systems",
        prompt="Follow-up: In Systems & Security, which layer would you rather investigate?",
        question_type="single_choice",
        category="Adaptive Follow-up",
        help_text="Shown because you selected Distributed Systems, Cloud & Cybersecurity.",
        is_adaptive=True,
        trigger=TriggerRule(
            source_question_id="q_domains_interest",
            expected_values=("systems_sec",),
        ),
        options=(
            QuestionOption(
                id="privacy_crypto",
                label="Privacy-preserving computation, access control, and security auditing",
                domain_weights={"systems_security": 1.0},
                dimension_weights={"theoretical_rigor": 0.6},
            ),
            QuestionOption(
                id="distributed_perf",
                label="Distributed scheduling, fault tolerance, and ML inference serving",
                domain_weights={"systems_security": 0.9, "ai_ml": 0.3},
                dimension_weights={"applied_engineering": 0.9},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_followup_human_bio",
        prompt="Follow-up: For Human-Centered or Health/Bio research, what data modality interests you most?",
        question_type="single_choice",
        category="Adaptive Follow-up",
        help_text="Shown because you selected HCI/EdTech, Bio/Health, or Computational Social Science.",
        is_adaptive=True,
        trigger=TriggerRule(
            source_question_id="q_domains_interest",
            expected_values=("hci_edtech", "bio_health", "data_society"),
        ),
        options=(
            QuestionOption(
                id="clinical_tabular",
                label="Structured clinical, longitudinal, or public-health datasets",
                domain_weights={"bio_health": 0.9, "data_science": 0.6},
            ),
            QuestionOption(
                id="user_studies",
                label="Interactive user studies, mixed-methods evaluation, and UX telemetry",
                domain_weights={"hci": 1.0},
            ),
            QuestionOption(
                id="policy_causal",
                label="Observational causal inference and socio-economic datasets",
                domain_weights={"data_science": 1.0},
            ),
        ),
    ),
    QuestionDefinition(
        id="q_followup_math_rigor",
        prompt="Follow-up: Since you enjoy formal math, would you like topics centered on optimization theory or statistical learning?",
        question_type="single_choice",
        category="Adaptive Follow-up",
        help_text="Shown because you rated mathematical comfort 4 or higher.",
        is_adaptive=True,
        trigger=TriggerRule(
            source_question_id="q_math_comfort",
            min_rating=4,
        ),
        options=(
            QuestionOption(
                id="yes_theory",
                label="Yes — include mathematically rigorous and theoretical directions",
                dimension_weights={"theoretical_rigor": 0.9},
            ),
            QuestionOption(
                id="balanced_applied",
                label="Prefer balanced topics that apply math to practical problems",
                dimension_weights={"empirical_experimentation": 0.7, "applied_engineering": 0.5},
            ),
        ),
    ),
)

QUESTION_MAP: dict[str, QuestionDefinition] = {q.id: q for q in QUESTION_BANK}


def _is_trigger_satisfied(trigger: TriggerRule, answers_by_qid: dict[str, Any]) -> bool:
    """Evaluate whether a question's adaptive trigger is satisfied by current answers."""
    if trigger.source_question_id not in answers_by_qid:
        return False

    source_answer = answers_by_qid[trigger.source_question_id]

    if trigger.min_rating is not None:
        return isinstance(source_answer, int) and source_answer >= trigger.min_rating

    if trigger.expected_values:
        if isinstance(source_answer, list):
            return any(val in trigger.expected_values for val in source_answer)
        if isinstance(source_answer, str):
            return source_answer in trigger.expected_values

    return False


def resolve_applicable_questions(answers_by_qid: dict[str, Any]) -> list[QuestionDefinition]:
    """Return ordered list of core questions plus any unlocked adaptive follow-ups."""
    applicable: list[QuestionDefinition] = []
    for question in QUESTION_BANK:
        if not question.is_adaptive:
            applicable.append(question)
        elif question.trigger is not None and _is_trigger_satisfied(
            question.trigger, answers_by_qid
        ):
            applicable.append(question)
    return applicable


def validate_answer_for_question(question: QuestionDefinition, answer: Any) -> Any:
    """Validate and normalize an answer against the question definition."""
    valid_option_ids = {opt.id for opt in question.options}

    if question.question_type in ("single_choice", "scenario", "technical_preference"):
        if not isinstance(answer, str) or answer not in valid_option_ids:
            raise ValueError(
                f"Answer for '{question.id}' must be one of: {sorted(valid_option_ids)}."
            )
        return answer

    if question.question_type == "multiple_choice":
        if not isinstance(answer, list) or len(answer) == 0:
            raise ValueError(
                f"Answer for '{question.id}' must be a non-empty list of option IDs."
            )
        deduped: list[str] = []
        for item in answer:
            if not isinstance(item, str) or item not in valid_option_ids:
                raise ValueError(
                    f"Invalid option '{item}' for '{question.id}'."
                )
            if item not in deduped:
                deduped.append(item)
        if question.max_selections is not None and len(deduped) > question.max_selections:
            raise ValueError(
                f"Select at most {question.max_selections} options for '{question.id}'."
            )
        return deduped

    if question.question_type == "rating_scale":
        if isinstance(answer, bool) or not isinstance(answer, int):
            raise ValueError(f"Answer for '{question.id}' must be an integer rating.")
        min_v = question.min_value if question.min_value is not None else 1
        max_v = question.max_value if question.max_value is not None else 5
        if answer < min_v or answer > max_v:
            raise ValueError(
                f"Rating for '{question.id}' must be between {min_v} and {max_v}."
            )
        return answer

    raise ValueError(f"Unsupported question type: {question.question_type}")
