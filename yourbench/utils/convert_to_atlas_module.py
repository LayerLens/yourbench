from pathlib import Path
import json, textwrap
from datasets import load_from_disk


def _scorer_yaml(name: str) -> str:
    """Return the complete <name>.yaml text, nothing omitted."""
    return textwrap.dedent(
        f"""\
        name: {name}

        scorer:
          type: llm_judge
          options:
            regex_pattern: ''
            judge_model: google/gemini-2.5-flash-preview-05-20
            judge_prompt: |-
              Your job is to look at a question, a gold target, and a predicted answer, and then assign a grade of either ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"].
              First, I will give examples of each grade, and then you will grade a new example.

              The following are examples of CORRECT predicted answers.
              ```
              Question: What are the names of Barack Obama's children?
              Gold target: Malia Obama and Sasha Obama
              Predicted answer 1: sasha and malia obama
              Predicted answer 2: most people would say Malia and Sasha, but I'm not sure and would have to double check
              Predicted answer 3: Barack Obama has two daughters: Malia and Sasha.
              ```
              These predicted answers are all CORRECT because:
                  - They fully contain the important information in the gold target
                  - They do not contain information that contradicts the gold target
                  - Capitalization, punctuation, grammar, and order don't matter
                  - Hedging is okay if the correct answer is included without contradictions

              The following are examples of INCORRECT predicted answers.
              ```
              Question: What are the names of Barack Obama's children?
              Gold target: Malia and Sasha
              Predicted answer 1: Malia.
              Predicted answer 2: Malia, Sasha, and Susan.
              Predicted answer 3: Barack Obama does not have any children.
              ```
              These predicted answers are all INCORRECT because:
                  - They contain factual contradictions with the gold target
                  - Even hedged incorrect statements are considered incorrect

              The following are examples of NOT_ATTEMPTED predicted answers.
              ```
              Question: What are the names of Barack Obama's children?
              Gold target: Malia and Sasha
              Predicted answer 1: I don't know.
              Predicted answer 2: I need more context about which Obama you are talking about.
              Predicted answer 3: Barack Obama has two children, but I don't recall their names.
              ```
              These predicted answers are all NOT_ATTEMPTED because:
                  - They don't include the required information
                  - They don't contradict the gold target

              Important notes:
              - Numbers must match to the last significant figure in the gold target
              - Only information directly asked in the question is required
              - Information clearly inferred from the question can be omitted
              - Name typos are acceptable if the identity is clear

              Grade the following as either A (CORRECT), B (INCORRECT), or C (NOT_ATTEMPTED):
              ```
              Question: {{prompt}}
              Gold target: {{truth}}
              Predicted answer: {{response}}
              ```
              Return your response in this exact format:
              Grade: [A/B/C]

            criteria:
              grade:
                description: "Grade for the answer (A=CORRECT, B=INCORRECT, C=NOT_ATTEMPTED)"
                weight: 1.0
                pattern: "Grade: (?:\\\\[)?([ABC])(?:\\\\])?"
                type: mapped
                options:
                  A: 1.0  # CORRECT
                  B: 0.0  # INCORRECT
                  C: 0.0  # NOT_ATTEMPTED

        categories:
        - general
        subsets:
        - default
        """
    )


def _metadata_yaml(
    name: str,
    full_desc: str,
    short_desc: str,
    category: str,
    n_rows: int,
) -> str:
    return textwrap.dedent(
        f"""\
        name: {full_desc}
        key: {name}
        full_description: {full_desc}
        short_description: {short_desc}
        subsets:
        - default
        categories:
        - {category}
        key_takeaways:
        additional_insights:
        - ""
        prompt_count: {n_rows}
        """
    )


def convert_dataset(
    hf_path: str | Path,
    name: str,
    system_prompt: str,
    full_description: str = "Knowledge-oriented evaluation dataset",
    short_description: str = "Knowledge eval",
    category: str = "General",
    output_dir: str | Path = ".",
):
    """
    Convert a HF dataset with `question` and `ground_truth_answer` columns into:

        <output_dir>/<name>/
            ├─ <name>-formatted.jsonl
            ├─ <name>.yaml
            └─ metadata.yaml
    """
    ds = load_from_disk(str(hf_path))
    out_root = Path(output_dir).expanduser().resolve() / name
    out_root.mkdir(parents=True, exist_ok=True)

    # 1. formatted JSONL
    with (out_root / f"{name}-formatted.jsonl").open("w", encoding="utf-8") as f:
        for i, rec in enumerate(ds):
            f.write(
                json.dumps(
                    {
                        "id": f"{name}{i:06d}",
                        "input": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": rec["question"]},
                        ],
                        "truth": rec["ground_truth_answer"],
                        "subset": "default",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    # 2. scorer YAML
    (out_root / f"{name}.yaml").write_text(_scorer_yaml(name), encoding="utf-8")

    # 3. metadata YAML
    (out_root / "metadata.yaml").write_text(
        _metadata_yaml(
            name,
            full_description,
            short_description,
            category,
            len(ds),
        ),
        encoding="utf-8",
    )

    # print(f"✔ Export complete → {out_root}")
