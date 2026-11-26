from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchTopic:
    """Curated research topic definition for hybrid recommendation scoring."""

    id: str
    title: str
    description: str
    keywords: tuple[str, ...]
    domain_tags: tuple[str, ...]
    methodology_tags: tuple[str, ...]
    min_experience_level: str
    min_weekly_hours: int
    domain_weights: dict[str, float]
    dimension_weights: dict[str, float]


TOPIC_CATALOG: tuple[ResearchTopic, ...] = (
    # --- Artificial Intelligence & Machine Learning (ai_ml) ---
    ResearchTopic(
        id="ai_mechanistic_interpretability",
        title="Mechanistic Interpretability of Neural Networks",
        description=(
            "Investigating how deep neural networks and transformers represent concepts internally, "
            "using probing, sparse autoencoders, and circuit analysis to make model decisions transparent."
        ),
        keywords=("interpretability", "explainable ai", "pytorch", "transformers", "neural networks", "probing"),
        domain_tags=("ai_ml", "nlp"),
        methodology_tags=("empirical_experimentation", "theoretical_rigor"),
        min_experience_level="beginner",
        min_weekly_hours=10,
        domain_weights={"ai_ml": 0.85, "nlp": 0.35},
        dimension_weights={"empirical_experimentation": 0.7, "theoretical_rigor": 0.5},
    ),
    ResearchTopic(
        id="ai_efficient_finetuning",
        title="Parameter-Efficient Adaptation of Foundation Models",
        description=(
            "Studying low-rank adaptation, quantization, and distillation techniques that enable "
            "large pretrained models to adapt to specialized tasks under constrained compute budgets."
        ),
        keywords=("fine-tuning", "lora", "quantization", "foundation models", "deep learning", "efficiency"),
        domain_tags=("ai_ml", "systems_security"),
        methodology_tags=("applied_engineering", "empirical_experimentation"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"ai_ml": 0.8, "systems_security": 0.35},
        dimension_weights={"applied_engineering": 0.75, "empirical_experimentation": 0.65},
    ),
    ResearchTopic(
        id="ai_uncertainty_calibration",
        title="Uncertainty Quantification and Calibration in Deep Learning",
        description=(
            "Designing conformal prediction, Bayesian approximations, and calibration methods so "
            "machine learning models reliably signal when their predictions may be wrong."
        ),
        keywords=("uncertainty", "calibration", "conformal prediction", "statistics", "reliability", "ml"),
        domain_tags=("ai_ml", "data_science"),
        methodology_tags=("theoretical_rigor", "empirical_experimentation"),
        min_experience_level="intermediate",
        min_weekly_hours=10,
        domain_weights={"ai_ml": 0.8, "data_science": 0.45},
        dimension_weights={"theoretical_rigor": 0.8, "empirical_experimentation": 0.55},
    ),
    ResearchTopic(
        id="ai_multimodal_representation",
        title="Multimodal Representation Learning Across Vision and Text",
        description=(
            "Aligning visual, textual, and structured signals in shared embedding spaces for "
            "cross-modal retrieval, reasoning, and scientific document understanding."
        ),
        keywords=("multimodal", "vision-language", "embeddings", "contrastive learning", "deep learning"),
        domain_tags=("ai_ml", "nlp"),
        methodology_tags=("empirical_experimentation", "applied_engineering"),
        min_experience_level="intermediate",
        min_weekly_hours=12,
        domain_weights={"ai_ml": 0.8, "nlp": 0.5},
        dimension_weights={"empirical_experimentation": 0.75, "applied_engineering": 0.5},
    ),
    ResearchTopic(
        id="ai_reinforcement_safety",
        title="Safe Reinforcement Learning and Alignment Under Constraints",
        description=(
            "Developing policy optimization algorithms that respect explicit safety constraints, "
            "avoid reward hacking, and generalize reliably in sequential decision-making."
        ),
        keywords=("reinforcement learning", "ai safety", "optimization", "control", "alignment"),
        domain_tags=("ai_ml",),
        methodology_tags=("theoretical_rigor", "applied_impact"),
        min_experience_level="intermediate",
        min_weekly_hours=12,
        domain_weights={"ai_ml": 0.95},
        dimension_weights={"theoretical_rigor": 0.75, "applied_impact": 0.5},
    ),
    # --- Natural Language Processing & Information Retrieval (nlp) ---
    ResearchTopic(
        id="nlp_scientific_rag",
        title="Citation-Grounded Retrieval-Augmented Generation for Science",
        description=(
            "Building retrieval and verification pipelines that ground language model outputs in "
            "peer-reviewed scientific literature and detect unsupported claims or hallucinations."
        ),
        keywords=("rag", "information retrieval", "nlp", "citations", "hallucination", "scientific text"),
        domain_tags=("nlp", "ai_ml"),
        methodology_tags=("applied_engineering", "empirical_experimentation"),
        min_experience_level="none",
        min_weekly_hours=8,
        domain_weights={"nlp": 0.9, "ai_ml": 0.45},
        dimension_weights={"applied_engineering": 0.65, "empirical_experimentation": 0.65, "applied_impact": 0.5},
    ),
    ResearchTopic(
        id="nlp_low_resource_languages",
        title="Cross-Lingual Transfer for Low-Resource Languages",
        description=(
            "Improving syntactic parsing, machine translation, and information access for "
            "underrepresented languages using multilingual pretraining and data-efficient adaptation."
        ),
        keywords=("low-resource nlp", "multilingual", "translation", "linguistics", "transfer learning"),
        domain_tags=("nlp", "hci"),
        methodology_tags=("empirical_experimentation", "human_centered_inquiry"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"nlp": 0.9, "hci": 0.25},
        dimension_weights={"empirical_experimentation": 0.65, "human_centered_inquiry": 0.6, "applied_impact": 0.55},
    ),
    ResearchTopic(
        id="nlp_dense_retrieval_ranking",
        title="Neural Dense Retrieval and Hybrid Search Ranking",
        description=(
            "Combining lexical BM25 signals with learned bi-encoder and cross-encoder representations "
            "for high-precision, low-latency search over large document collections."
        ),
        keywords=("search", "information retrieval", "bm25", "dense retrieval", "ranking", "embeddings"),
        domain_tags=("nlp", "data_science"),
        methodology_tags=("empirical_experimentation", "applied_engineering"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"nlp": 0.85, "data_science": 0.35},
        dimension_weights={"empirical_experimentation": 0.75, "applied_engineering": 0.65},
    ),
    ResearchTopic(
        id="nlp_argument_mining",
        title="Automated Argument Mining and Claim Verification",
        description=(
            "Extracting structured claims, evidence spans, and reasoning chains from policy documents, "
            "news articles, and academic papers to support critical reading."
        ),
        keywords=("argument mining", "fact checking", "discourse", "nlp", "text classification"),
        domain_tags=("nlp", "data_science"),
        methodology_tags=("empirical_experimentation", "human_centered_inquiry"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"nlp": 0.85, "data_science": 0.4},
        dimension_weights={"empirical_experimentation": 0.6, "human_centered_inquiry": 0.55},
    ),
    ResearchTopic(
        id="nlp_benchmark_contamination",
        title="Evaluating Reasoning Robustness and Benchmark Contamination",
        description=(
            "Designing dynamic, contamination-resistant evaluation suites to distinguish genuine "
            "reasoning ability from memorization in large language models."
        ),
        keywords=("evaluation", "benchmarks", "llm", "reasoning", "nlp", "testing"),
        domain_tags=("nlp", "ai_ml"),
        methodology_tags=("empirical_experimentation", "theoretical_rigor"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"nlp": 0.75, "ai_ml": 0.6},
        dimension_weights={"empirical_experimentation": 0.85, "theoretical_rigor": 0.45},
    ),
    # --- Distributed Systems & Cybersecurity (systems_security) ---
    ResearchTopic(
        id="sys_distributed_ml_serving",
        title="Low-Latency Scheduling for Distributed ML Inference",
        description=(
            "Designing batching, KV-cache management, and request routing algorithms to serve "
            "large neural models efficiently across heterogeneous GPU clusters."
        ),
        keywords=("distributed systems", "inference", "scheduling", "gpu", "latency", "systems"),
        domain_tags=("systems_security", "ai_ml"),
        methodology_tags=("applied_engineering", "empirical_experimentation"),
        min_experience_level="intermediate",
        min_weekly_hours=12,
        domain_weights={"systems_security": 0.85, "ai_ml": 0.45},
        dimension_weights={"applied_engineering": 0.9, "empirical_experimentation": 0.6},
    ),
    ResearchTopic(
        id="sys_privacy_preserving_ml",
        title="Differential Privacy and Federated Learning Systems",
        description=(
            "Enabling collaborative model training across decentralized organizations while providing "
            "formal differential privacy guarantees against data reconstruction attacks."
        ),
        keywords=("privacy", "federated learning", "differential privacy", "security", "cryptography"),
        domain_tags=("systems_security", "ai_ml"),
        methodology_tags=("theoretical_rigor", "applied_engineering"),
        min_experience_level="intermediate",
        min_weekly_hours=10,
        domain_weights={"systems_security": 0.8, "ai_ml": 0.45},
        dimension_weights={"theoretical_rigor": 0.7, "applied_engineering": 0.6, "applied_impact": 0.5},
    ),
    ResearchTopic(
        id="sys_llm_prompt_security",
        title="Prompt Injection Defenses and Agentic Sandboxing",
        description=(
            "Analyzing privilege separation, capability-based access control, and runtime monitoring "
            "to secure tool-using AI agents against untrusted inputs."
        ),
        keywords=("cybersecurity", "sandboxing", "prompt injection", "access control", "security"),
        domain_tags=("systems_security", "nlp"),
        methodology_tags=("applied_engineering", "applied_impact"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"systems_security": 0.85, "nlp": 0.35},
        dimension_weights={"applied_engineering": 0.8, "applied_impact": 0.75},
    ),
    ResearchTopic(
        id="sys_cloud_fault_tolerance",
        title="Automated Fault Injection and Consensus Verification",
        description=(
            "Using deterministic simulation and property-based testing to uncover subtle race "
            "conditions and partition bugs in distributed storage and consensus protocols."
        ),
        keywords=("fault tolerance", "consensus", "distributed storage", "testing", "verification"),
        domain_tags=("systems_security",),
        methodology_tags=("applied_engineering", "theoretical_rigor"),
        min_experience_level="intermediate",
        min_weekly_hours=12,
        domain_weights={"systems_security": 0.95},
        dimension_weights={"applied_engineering": 0.85, "theoretical_rigor": 0.6},
    ),
    ResearchTopic(
        id="sys_software_supply_chain",
        title="Static Analysis for Software Supply Chain Security",
        description=(
            "Detecting malicious dependencies, vulnerable build pipelines, and anomalous package "
            "updates in open-source ecosystems using program analysis."
        ),
        keywords=("supply chain", "static analysis", "vulnerabilities", "cybersecurity", "devops"),
        domain_tags=("systems_security",),
        methodology_tags=("applied_engineering", "applied_impact"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"systems_security": 0.9},
        dimension_weights={"applied_engineering": 0.75, "applied_impact": 0.75},
    ),
    # --- Human-Computer Interaction & EdTech (hci) ---
    ResearchTopic(
        id="hci_human_ai_collaboration",
        title="Explainable Interfaces for Human-AI Decision Support",
        description=(
            "Studying how confidence indicators, feature attributions, and interactive explanations "
            "affect user trust, over-reliance, and decision quality in high-stakes workflows."
        ),
        keywords=("hci", "explainability", "user study", "human-ai", "trust", "interface design"),
        domain_tags=("hci", "ai_ml"),
        methodology_tags=("human_centered_inquiry", "applied_impact"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"hci": 0.9, "ai_ml": 0.35},
        dimension_weights={"human_centered_inquiry": 0.9, "applied_impact": 0.65},
    ),
    ResearchTopic(
        id="hci_adaptive_tutoring",
        title="Adaptive Scaffolding in Computing Education Platforms",
        description=(
            "Designing personalized hints, worked examples, and mastery tracking systems that help "
            "novice programmers build debugging skills without fostering dependency."
        ),
        keywords=("edtech", "education", "tutoring", "programming education", "scaffolding", "hci"),
        domain_tags=("hci", "nlp"),
        methodology_tags=("human_centered_inquiry", "applied_impact"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"hci": 0.9, "nlp": 0.25},
        dimension_weights={"human_centered_inquiry": 0.85, "applied_impact": 0.8},
    ),
    ResearchTopic(
        id="hci_accessible_interfaces",
        title="Accessible Data Visualization for Screen Reader Users",
        description=(
            "Creating multimodal sonification, tactile summaries, and keyboard-navigable chart "
            "structures so blind and low-vision researchers can explore complex datasets."
        ),
        keywords=("accessibility", "visualization", "assistive technology", "hci", "inclusive design"),
        domain_tags=("hci", "data_science"),
        methodology_tags=("human_centered_inquiry", "applied_engineering"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"hci": 0.9, "data_science": 0.3},
        dimension_weights={"human_centered_inquiry": 0.9, "applied_engineering": 0.5, "applied_impact": 0.75},
    ),
    ResearchTopic(
        id="hci_scientific_sensemaking",
        title="Interactive Literature Exploration and Sensemaking Tools",
        description=(
            "Building visual synthesis and citation-exploration workspaces that help early-stage "
            "researchers map unfamiliar fields and formulate testable hypotheses."
        ),
        keywords=("sensemaking", "literature review", "visualization", "ux", "research tools"),
        domain_tags=("hci", "nlp"),
        methodology_tags=("human_centered_inquiry", "applied_engineering"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"hci": 0.85, "nlp": 0.4},
        dimension_weights={"human_centered_inquiry": 0.85, "applied_engineering": 0.55},
    ),
    ResearchTopic(
        id="hci_algorithmic_fairness_ux",
        title="Participatory Auditing of Algorithmic Systems",
        description=(
            "Involving affected communities and domain practitioners in surfacing edge-case harms "
            "and fairness trade-offs in deployed machine learning systems."
        ),
        keywords=("participatory design", "fairness", "auditing", "ethics", "hci"),
        domain_tags=("hci", "data_science"),
        methodology_tags=("human_centered_inquiry", "applied_impact"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"hci": 0.8, "data_science": 0.45},
        dimension_weights={"human_centered_inquiry": 0.9, "applied_impact": 0.7},
    ),
    # --- Computational Biology & Healthcare (bio_health) ---
    ResearchTopic(
        id="bio_clinical_nlp",
        title="Clinical Entity Extraction and Longitudinal Patient Summarization",
        description=(
            "Structuring unstructured electronic health record notes into timelines of symptoms, "
            "medications, and outcomes while preserving clinical accuracy."
        ),
        keywords=("clinical nlp", "healthcare", "ehr", "medical", "biomedical", "text mining"),
        domain_tags=("bio_health", "nlp"),
        methodology_tags=("applied_impact", "empirical_experimentation"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"bio_health": 0.85, "nlp": 0.5},
        dimension_weights={"applied_impact": 0.85, "empirical_experimentation": 0.6},
    ),
    ResearchTopic(
        id="bio_protein_representation",
        title="Deep Learning for Protein Function and Mutation Effect Prediction",
        description=(
            "Using protein language models and structural graph representations to predict how "
            "amino acid variants affect stability, binding, and disease risk."
        ),
        keywords=("protein", "bioinformatics", "genomics", "graph neural networks", "computational biology"),
        domain_tags=("bio_health", "ai_ml"),
        methodology_tags=("empirical_experimentation", "theoretical_rigor"),
        min_experience_level="intermediate",
        min_weekly_hours=12,
        domain_weights={"bio_health": 0.85, "ai_ml": 0.5},
        dimension_weights={"empirical_experimentation": 0.75, "theoretical_rigor": 0.55},
    ),
    ResearchTopic(
        id="bio_medical_imaging_robustness",
        title="Domain Generalization in Medical Image Segmentation",
        description=(
            "Addressing scanner and hospital distribution shifts in radiology and pathology models "
            "so diagnostic tools remain accurate across diverse clinical sites."
        ),
        keywords=("medical imaging", "radiology", "segmentation", "domain shift", "healthcare ai"),
        domain_tags=("bio_health", "ai_ml"),
        methodology_tags=("empirical_experimentation", "applied_impact"),
        min_experience_level="intermediate",
        min_weekly_hours=10,
        domain_weights={"bio_health": 0.85, "ai_ml": 0.45},
        dimension_weights={"empirical_experimentation": 0.7, "applied_impact": 0.75},
    ),
    ResearchTopic(
        id="bio_single_cell_integration",
        title="Multi-Omics Integration for Single-Cell Transcriptomics",
        description=(
            "Developing statistical and latent-variable models to align gene expression and "
            "epigenetic measurements across thousands of individual cells."
        ),
        keywords=("single-cell", "genomics", "omics", "bioinformatics", "statistics", "biology"),
        domain_tags=("bio_health", "data_science"),
        methodology_tags=("theoretical_rigor", "empirical_experimentation"),
        min_experience_level="intermediate",
        min_weekly_hours=10,
        domain_weights={"bio_health": 0.9, "data_science": 0.4},
        dimension_weights={"theoretical_rigor": 0.65, "empirical_experimentation": 0.7},
    ),
    ResearchTopic(
        id="bio_digital_health_timeseries",
        title="Wearable Time-Series Modeling for Early Health Risk Detection",
        description=(
            "Analyzing continuous physiological sensor streams from consumer wearables to detect "
            "sleep, cardiovascular, or stress anomalies in real-world settings."
        ),
        keywords=("wearables", "time series", "digital health", "sensors", "healthcare"),
        domain_tags=("bio_health", "data_science"),
        methodology_tags=("applied_impact", "human_centered_inquiry"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"bio_health": 0.85, "data_science": 0.45},
        dimension_weights={"applied_impact": 0.8, "human_centered_inquiry": 0.55},
    ),
    # --- Data Science & Computational Social Science (data_science) ---
    ResearchTopic(
        id="ds_causal_inference_observational",
        title="Causal Inference Methods for Observational Policy Evaluation",
        description=(
            "Estimating heterogeneous treatment effects from large observational datasets using "
            "double machine learning, propensity weighting, and sensitivity analysis."
        ),
        keywords=("causal inference", "econometrics", "statistics", "policy", "observational data"),
        domain_tags=("data_science",),
        methodology_tags=("theoretical_rigor", "applied_impact"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"data_science": 0.95},
        dimension_weights={"theoretical_rigor": 0.8, "applied_impact": 0.7},
    ),
    ResearchTopic(
        id="ds_misinformation_networks",
        title="Network Dynamics of Information Diffusion Online",
        description=(
            "Modeling how claims, corrections, and communities evolve across social graphs using "
            "temporal network analysis and natural language embeddings."
        ),
        keywords=("social networks", "computational social science", "graph analysis", "diffusion"),
        domain_tags=("data_science", "nlp"),
        methodology_tags=("empirical_experimentation", "human_centered_inquiry"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"data_science": 0.85, "nlp": 0.35},
        dimension_weights={"empirical_experimentation": 0.65, "human_centered_inquiry": 0.65},
    ),
    ResearchTopic(
        id="ds_spatial_urban_analytics",
        title="Spatiotemporal Modeling for Urban Mobility and Climate Resilience",
        description=(
            "Combining satellite imagery, transit logs, and census data to forecast urban heat "
            "islands, transit demand, and equitable infrastructure access."
        ),
        keywords=("spatial data", "urban analytics", "gis", "forecasting", "climate", "data science"),
        domain_tags=("data_science",),
        methodology_tags=("applied_impact", "empirical_experimentation"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"data_science": 0.9},
        dimension_weights={"applied_impact": 0.85, "empirical_experimentation": 0.6},
    ),
    ResearchTopic(
        id="ds_synthetic_tabular_privacy",
        title="Utility-Preserving Synthetic Tabular Data Generation",
        description=(
            "Generating statistically faithful synthetic datasets for social and economic research "
            "while preventing re-identification of sensitive individual records."
        ),
        keywords=("synthetic data", "tabular data", "privacy", "statistics", "data science"),
        domain_tags=("data_science", "systems_security"),
        methodology_tags=("empirical_experimentation", "theoretical_rigor"),
        min_experience_level="beginner",
        min_weekly_hours=8,
        domain_weights={"data_science": 0.8, "systems_security": 0.4},
        dimension_weights={"empirical_experimentation": 0.7, "theoretical_rigor": 0.6},
    ),
    ResearchTopic(
        id="ds_reproducible_science_meta",
        title="Computational Reproducibility and Meta-Science Analytics",
        description=(
            "Auditing statistical power, code availability, and citation patterns across large "
            "scientific corpora to improve research reliability."
        ),
        keywords=("meta-science", "reproducibility", "bibliometrics", "statistics", "data science"),
        domain_tags=("data_science", "hci"),
        methodology_tags=("empirical_experimentation", "human_centered_inquiry"),
        min_experience_level="none",
        min_weekly_hours=6,
        domain_weights={"data_science": 0.85, "hci": 0.3},
        dimension_weights={"empirical_experimentation": 0.7, "human_centered_inquiry": 0.55},
    ),
)

TOPIC_MAP: dict[str, ResearchTopic] = {topic.id: topic for topic in TOPIC_CATALOG}
