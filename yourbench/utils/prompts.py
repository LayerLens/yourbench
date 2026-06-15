"""
This module contains the prompts for the pipeline stages.
"""

SUMMARIZATION_USER_PROMPT = """You are an AI assistant tasked with analyzing and summarizing documents from various domains. Your goal is to generate a concise yet comprehensive summary of the given document. Follow these steps carefully:

1. You will be provided with a document extracted from a website. This document may be very long and/or split into multiple contiguous sections. It may contain unnecessary artifacts such as links, HTML tags, or other web-related elements.

2. Here is the document to be summarized:
<document>
{document}
</document>

3. Before generating the summary, use a mental scratchpad to take notes as you read through the document. Enclose your notes within <scratchpad> tags. For example:

<scratchpad>
- Main topic: [Note the main subject of the document]
- Key points: [List important information across the entire document]
- Structure: [Note how the document is organized or chunked]
- Potential artifacts to ignore: [List any web-related elements that should be disregarded]
</scratchpad>

4. As you analyze the document:
   - Focus solely on the content, ignoring any unnecessary web-related elements.
   - Treat all sections or chunks as part of a single, continuous document.
   - Identify the main topic and key points from the entire input.
   - Pay attention to the overall structure and flow of the document.

5. After your analysis, generate a final summary that:
   - Captures the essence of the document in a concise manner.
   - Includes the main topic and key points.
   - Presents information in a logical and coherent order.
   - Is comprehensive yet concise, typically ranging from 3-5 sentences (unless the document is particularly long or complex).

6. Enclose your final summary within <final_summary> tags. For example:

<final_summary>
[Your concise and comprehensive summary of the document goes here.]
</final_summary>

Remember, your task is to provide a clear, accurate, and concise summary of the document's content, disregarding any web-related artifacts or unnecessary elements. For long documents, ensure your summary reflects the complete scope and structure of the content."""


QUESTION_GENERATION_SYSTEM_PROMPT_HEADER = """## Your Role

You are an expert benchmark author specializing in CLOSED-BOOK, factual-recall questions that test whether a model possesses the specific knowledge contained in a provided document. Your goal is to produce question-answer pairs that can only be answered correctly by someone who has actually read THIS specific text — never from general domain knowledge, common sense, or the wording of the question itself.

## Input Structure

Your input consists of:

<additional_instructions>
[Specific instructions, preferences, or constraints guiding the question creation.]
</additional_instructions>

<title>
[Document title]
</title>

<document_summary>
[Concise summary providing contextual background and overview.]
</document_summary>

<text_chunk>
[The single text segment to analyze.]
</text_chunk>

## Primary Objective

Your goal is to generate fact-anchored question-answer pairs from a single provided `<text_chunk>`. Each question must hinge on a concrete, document-specific detail stated in the chunk, so that ONLY a reader of this exact text can answer it correctly. Do not aim for "moderate complexity" or open-ended reflection — aim for specificity and verifiability.

### Context Fields:

- `<title>`: Contextualizes the content.
- `<document_summary>`: Brief overview providing contextual understanding.
- `<text_chunk>`: The sole source text for developing rich, meaningful questions.
- `<additional_instructions>`: Instructions that influence question style, content, and complexity.

## Analysis Phase

Conduct careful analysis within `<document_analysis>` XML tags, following these steps:

1. **Thoughtful Content Examination**
   - Carefully analyze the given text_chunk, identifying central ideas, nuanced themes, and significant relationships within it.

2. **Concept Exploration**
   - Consider implicit assumptions, subtle details, underlying theories, and potential applications of the provided information.

3. **Specificity Calibration**
   - Rate difficulty (1-10) by how strongly the question depends on this specific source: higher when only a reader of this chunk could answer, lower when a generalist could guess. Discard questions a model could answer without the document.

4. **Intentional Question Planning**
   - Plan how questions can invite deeper understanding, meaningful reflection, or critical engagement, ensuring each question is purposeful.

## Additional Instructions for Handling Irrelevant or Bogus Information

### Identification and Ignoring of Irrelevant Information:

- **Irrelevant Elements:** Explicitly disregard hyperlinks, advertisements, headers, footers, navigation menus, disclaimers, social media buttons, or any content clearly irrelevant or external to the core information of the text chunk.
- **Bogus Information:** Detect and exclude any information that appears nonsensical or disconnected from the primary subject matter.

### Decision Criteria for Question Generation:

- **Meaningful Content Requirement:** Only generate questions if the provided `<text_chunk>` contains meaningful, coherent, and educationally valuable content.
- **Complete Irrelevance:** If the entire `<text_chunk>` consists exclusively of irrelevant, promotional, web navigation, footer, header, or non-informational text, explicitly state this in your analysis and do NOT produce any question-answer pairs.

### Documentation in Analysis:

- Clearly document the rationale in the `<document_analysis>` tags when identifying irrelevant or bogus content, explaining your reasons for exclusion or inclusion decisions.
- Briefly justify any decision NOT to generate questions due to irrelevance or poor quality content.


## Question Generation Guidelines

### Required Question Characteristics:

- **Source-Dependent Specificity**: Each question MUST hinge on a specific fact, name, number, value, configuration, limit, default, or step that is stated in the `<text_chunk>`. A knowledgeable expert who has NOT read this document must be unable to answer it from general knowledge or from the question's own wording.
- **Closed-Book, Not Reasoning**: Do NOT generate questions that can be answered by reasoning, inference, or domain familiarity alone. Avoid generic framings such as "what are the benefits of X", "how does X enhance/improve Y", or "why is X important" — a capable model answers those without the document.
- **Verifiable Answer**: The answer must be concrete and checkable against the chunk (a fact, value, name, or short enumeration), not an open-ended essay.
- **Discriminating**: Favor details that a generic model would plausibly get wrong or omit — exact terminology, specific steps/counts/sequences, named components, thresholds, or described behaviors unique to this text.
- **Natural Phrasing**: Phrase questions naturally; do not reference "the document" or "the text" explicitly (the question stands on its own grammatically), but its ANSWER must still require this specific source.

### Question Types (in priority order):

Strongly prefer:
- Factual (specific stated facts)
- Clarification (precise meaning of a specific term/value as defined here)
- Edge-case (specific limits, defaults, exceptions stated in the text)
- True-False (about a specific stated claim)
- False-premise (contradicting a specific stated detail)

Avoid (these are answerable without the document):
- Analytical, Conceptual, Application-based, Counterfactual, Open-ended

(Use only the types that yield source-dependent, verifiable questions for this chunk.)"""

QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT = """## Output Structure

Present your final output as JSON objects strictly adhering to this Pydantic model within `<output_json>` XML tags:

```python
class QuestionAnswerPair(BaseModel):
    thought_process: str # Clear, detailed rationale for selecting question and analysis approach
    question_type: Literal["analytical", "application-based", "clarification",
                           "counterfactual", "conceptual", "true-false",
                           "factual", "open-ended", "false-premise", "edge-case"]
    question: str
    answer: str
    estimated_difficulty: int  # 1-10, calibrated according to additional instructions
    citations: List[str]  # Direct quotes from the text_chunk supporting the answer
```

## Output Format

Begin by thoughtfully analyzing the provided text_chunk within `<document_analysis>` XML tags. Then present the resulting JSON-formatted QuestionAnswerPairs clearly within `<output_json>` XML tags."""

QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT_MULTI = """## Output Structure

Present your final output as JSON objects strictly adhering to this Pydantic model within `<output_json>` XML tags:

```python
class MultipleChoiceQuestion(BaseModel):
    thought_process: str  # Rationale for the question and distractors
    question_type: Literal["analytical", "application-based", "clarification",
                           "counterfactual", "conceptual", "true-false",
                           "factual", "false-premise", "edge-case"]
    question: str
    answer: str  # One of "A", "B", "C", or "D"
    choices: List[str]  # Must contain exactly 4 items
    estimated_difficulty: int  # 1-10
    citations: List[str]  # Direct support from the text_chunk
```

## Output Format

Begin by thoughtfully analyzing the provided <text_chunk> within <document_analysis> XML tags. Your analysis should identify the key concepts, technical details, and reasoning opportunities found in the text.

Then present the resulting multiple-choice questions as valid JSON objects within <output_json> tags, strictly following this structure:

<document_analysis>
- Key concept: ...
- Important facts: ...
- Reasoning opportunities: ...
</document_analysis>

<output_json>
[
  {
    "thought_process": "This question targets understanding of how the chunk explains the purpose of semantic chunking in document processing. Distractors are phrased using near-synonyms or subtle distortions of the true concept.",
    "question_type": "conceptual",
    "question": "What is the primary reason for using semantic chunking in document preprocessing?",
    "choices": [
      "(A) To compress the document into fewer tokens.",
      "(B) To group content based on semantic similarity and token limits.",
      "(C) To translate the text into multiple languages.",
      "(D) To strip metadata and formatting from the input file."
    ],
    "answer": "B",
    "estimated_difficulty": 6,
    "citations": ["Semantic chunking partitions documents into coherent segments based on semantic similarity and token length constraints."]
  },
  ...
]
</output_json>"""

QUESTION_GENERATION_SYSTEM_PROMPT_FOOTER = """## Important Notes
- Strive to generate questions that inspire genuine curiosity, reflection, and thoughtful engagement.
- Maintain clear, direct, and accurate citations drawn verbatim from the provided text_chunk.
- Prioritize source-dependent specificity over complexity: every question must require a concrete detail from the text_chunk to answer.
- Each "thought_process" should state WHICH specific fact from the chunk the question tests and why a model without the document could not answer it.
- Ensure rigorous adherence to JSON formatting and the provided Pydantic validation model.
- Do not use meta-phrases like 'as per the text' or 'according to the document' in the question wording — phrase it naturally. This is about phrasing only: the question's ANSWER must still depend on this specific source, not on general knowledge.
"""

QUESTION_GENERATION_SYSTEM_PROMPT = (
    QUESTION_GENERATION_SYSTEM_PROMPT_HEADER
    + QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT
    + QUESTION_GENERATION_SYSTEM_PROMPT_FOOTER
)
QUESTION_GENERATION_SYSTEM_PROMPT_MULTI = (
    QUESTION_GENERATION_SYSTEM_PROMPT_HEADER
    + QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT_MULTI
    + QUESTION_GENERATION_SYSTEM_PROMPT_FOOTER
)

QUESTION_GENERATION_USER_PROMPT = """<title>
{title}
</title>

<document_summary>
{document_summary}
</document_summary>

<text_chunk>
{text_chunk}
</text_chunk>

<additional_instructions>
{additional_instructions}
</additional_instructions>"""


MULTI_HOP_QUESTION_GENERATION_SYSTEM_HEADER = """## Your Role

You are an expert benchmark author specialized in CLOSED-BOOK, factual-recall multi-hop questions. Your task is to craft questions that require combining SPECIFIC facts stated across multiple chunks of THIS document, so that only a reader of these exact texts can answer them. Each question must depend on concrete, document-specific details — not on general domain knowledge, reasoning, or the wording of the question itself.

## Input Structure

Your input will consist of these components:

<additional_instructions>
[Specific guidelines, preferences, or constraints influencing question generation.]
</additional_instructions>

<title>
[Document title]
</title>

<document_summary>
[A concise summary providing context and thematic overview.]
</document_summary>

<text_chunks>
<text_chunk_0>
[First text segment]
</text_chunk_0>
<text_chunk_1>
[Second text segment]
</text_chunk_1>
[Additional text segments as necessary]
</text_chunks>

## Primary Objective

Generate multi-hop question-answer pairs that require combining specific, stated facts from across multiple text chunks. Each question must hinge on concrete details (names, numbers, values, steps, behaviors) found in the chunks, so that only a reader of these exact texts can answer correctly. Do not aim for "moderate challenge" or open-ended reflection — aim for source-dependent specificity and verifiable answers.

### Context Fields:
- `<title>`: Document context
- `<document_summary>`: Broad contextual summary for orientation
- `<text_chunks>`: Source material to form integrative multi-hop questions
- `<additional_instructions>`: Specific instructions guiding the complexity and depth of questions

## Analysis Phase

Perform careful analysis within `<document_analysis>` XML tags:

1. **In-depth Text Analysis**
   - Thoughtfully read each text chunk.
   - Identify key themes, nuanced details, and subtle connections.
   - Highlight opportunities for insightful synthesis across multiple chunks.

2. **Reasoning Path Construction**
   - Construct potential pathways of multi-hop reasoning by connecting ideas, details, or implications found across text chunks.

3. **Specificity Calibration**
   - Rate difficulty (1-10) by how strongly the question depends on combining specific facts from these chunks: higher when only a reader of these texts could answer, lower when a generalist could guess. Discard questions answerable without the document.

4. **Strategic Question Selection**
   - Choose questions that naturally emerge from the depth and complexity of the content provided, prioritizing integrative reasoning and genuine curiosity.

## Question Generation Guidelines

### Question Characteristics
- **Multi-Hop Source Dependency**: Questions must require combining two or more SPECIFIC facts stated across the chunks. A model without these exact texts must be unable to answer from general knowledge.
- **Verifiable Answer**: The answer must be concrete and checkable against the chunks (facts, values, names, short enumerations), not an open-ended essay.
- **Closed-Book, Not Reasoning**: Avoid generic framings ("what are the benefits of…", "how does … improve …", "why is … important") that a capable model answers without the document.
- **Clarity & Precision**: Each question and answer communicates intent concisely and unambiguously.
- **Discriminating**: Favor combinations of specific terminology, steps, counts, components, or thresholds unique to these texts.

### Question Types (in priority order)
Strongly prefer: Factual, Clarification, Edge-case, True-False, False-premise — each anchored to specific stated facts that must be combined across chunks.
Avoid (answerable without the document): Analytical, Conceptual, Application-based, Counterfactual, Open-ended.


## **Filtering Irrelevant Content**:
  - **Ignore completely** any irrelevant, redundant, promotional, or unrelated content, including headers, footers, navigation links, promotional materials, ads, or extraneous hyperlinks frequently found in web extracts.
  - **Disregard entirely** chunks composed solely of such irrelevant content. Do **not** generate questions from these chunks.
  - When partially relevant content is mixed with irrelevant material within the same chunk, carefully extract only the meaningful, educationally relevant portions for your integrative analysis.

- **Evaluating Chunk Quality**:
  - If, upon careful analysis, a chunk does not provide sufficient meaningful context or substantial educational relevance, explicitly note this in the `<document_analysis>` section and refrain from generating questions based on it.

- **Prioritizing Quality and Relevance**:
  - Always prioritize the quality, clarity, and educational integrity of generated questions. Do not force questions from unsuitable content."""


MULTI_HOP_QUESTION_GENERATION_SYSTEM_FOOTER = """## Important Notes
- Prioritize source-dependent specificity: each question must require combining concrete facts stated across the chunks.
- Precisely cite verbatim excerpts from the text chunks for every fact used.
- In "thought_process", state which specific facts from which chunks are combined and why a model without these texts could not answer.
- Adhere strictly to JSON formatting and Pydantic validation requirements.
- Do not use meta-phrases like 'as per the text' or 'according to the document' in the question wording — phrase it naturally. This is about phrasing only: the question's ANSWER must still depend on these specific sources, not on general knowledge."""

MULTI_HOP_QUESTION_GENERATION_SYSTEM_PROMPT = (
    MULTI_HOP_QUESTION_GENERATION_SYSTEM_HEADER
    + QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT
    + MULTI_HOP_QUESTION_GENERATION_SYSTEM_FOOTER
)
MULTI_HOP_QUESTION_GENERATION_SYSTEM_PROMPT_MULTI = (
    MULTI_HOP_QUESTION_GENERATION_SYSTEM_HEADER
    + QUESTION_GENERATION_SYSTEM_PROMPT_OUTPUT_MULTI
    + MULTI_HOP_QUESTION_GENERATION_SYSTEM_FOOTER
)

MULTI_HOP_QUESTION_GENERATION_USER_PROMPT = """<title>
{title}
</title>

<document_summary>
{document_summary}
</document_summary>

<text_chunks>
{chunks}
</text_chunks>

<additional_instructions>
{additional_instructions}
</additional_instructions>"""


ZEROSHOT_QA_USER_PROMPT = """Answer the following question:

<question>
{question}
</question>

Enclose your full answer in <answer> XML tags. For example:

<answer>
[your answer here]
</answer>"""

GOLD_QA_USER_PROMPT = """Answer the following question:

<question>
{question}
</question>

Here is a summary of the document the question is asked from which may be helpful:

<document_summary>
{summary}
</document_summary>

And here is a relevant chunk of the document which may prove useful

<document>
{document}
</document>

Enclose your full answer in <answer> XML tags. For example:

<answer>
[your answer here]
</answer>"""

JUDGE_ANSWER_SYSTEM_PROMPT = """You will be provided with the summary of a document, a piece of text, a question generated from that text, and the correct or "gold" answer to the question. Additionally, you will receive two answers: Answer A and Answer B. Your task is to determine which of these answers is closer to the gold answer by assessing the overlap of key points between the ground truth and the two given answers.

# Steps

1. **Document Understanding**:
   - Analyze the provided document summary to grasp the context and main themes.

2. **Chunk Understanding**:
   - Examine the provided text (chunk) to understand its content.

3. **Question Understanding**:
   - Interpret the given question to fully comprehend what is being asked.

4. **Ground Truth Answer Understanding**:
   - Understand the provided ground truth answer, identifying its key points.

5. **Answer A Understanding**:
   - Analyze Answer A, identifying key points and assessing accuracy and factuality.

6. **Answer B Understanding**:
   - Examine Answer B, identifying key points and assessing accuracy and factuality.

7. **Similarity Comparison**:
   - Compare Answer A and the ground truth answer, noting similarities in key points.
   - Compare Answer B and the ground truth answer, noting similarities in key points.

8. **Final Similarity Analysis**:
   - Evaluate both answers based on the similarities identified and determine which is closer to the ground truth in terms of key points and factuality.

# Output Format

- Provide your final evaluation of which answer is closer to the ground truth within `<final_answer>` XML tags.
- Include a detailed analysis for each part within the designated XML tags: `<document_understanding>`, `<chunk_understanding>`, `<question_understanding>`, `<ground_truth_answer_understanding>`, `<answer_a_understanding>`, `<answer_b_understanding>`, `<similarity_comparison_answer_a>`, `<similarity_comparison_answer_b>`, and `<final_similarity_analysis>`.

# Examples

**Input**:
```xml
<document_summary>
[Summary]
</document_summary>

<piece_of_text>
[Text]
</piece_of_text>

<question>
[Question]
</question>

<gold_answer>
[Gold Answer]
</gold_answer>

<answer_a>
[Answer A]
</answer_a>

<answer_b>
[Answer B]
</answer_b>
```
**Output**:
```xml

<document_understanding>
Understanding of the summary including key themes
</document_understanding>

<chunk_understanding>
Analysis of the piece of text
</chunk_understanding>

<question_understanding>
Comprehension of the question being asked
</question_understanding>

<ground_truth_answer_understanding>
Key points from the gold answer
</ground_truth_answer_understanding>

<answer_a_understanding>
Key points and accuracy of Answer A
</answer_a_understanding>

<answer_b_understanding>
Key points and accuracy of Answer B
</answer_b_understanding>

<similarity_comparison_answer_a>
Comparison notes between Answer A and the gold answer
</similarity_comparison_answer_a>

<similarity_comparison_answer_b>
Comparison notes between Answer B and the gold answer
</similarity_comparison_answer_b>

<final_similarity_analysis>
Overall analysis determining the closer answer
</final_similarity_analysis>

<final_answer>
Answer X (where X is the option you pick)
</final_answer>
```

# Notes

- Always focus on key points and factual correctness as per the ground truth.
- Avoid any biases and rely solely on the evidence presented.
- Enclose all evaluations and analyses in the specified XML tags for clarity and structure."""

JUDGE_ANSWER_USER_PROMPT = """<document_summary>
{summary}
</document_summary>

<piece_of_text>
{chunk}
</piece_of_text>

<question>
{question}
</question>

<gold_answer>
{oracle_answer}
</gold_answer>

<answer_a>
{answer_a}
</answer_a>

<answer_b>
{answer_b}
</answer_b>"""

CHUNK_SUMMARIZATION_USER_PROMPT = """\
You are an expert note-taker.  Summarise the following document *chunk* in \
10-12 crisp sentences capturing only the information that will matter for a \
later global summary.

<chunk>
{chunk}
</chunk>

Wrap your output inside <chunk_summary> tags."""

COMBINE_SUMMARIES_USER_PROMPT = """\
You will receive a bullet-list of chunk-level summaries from the *same* \
document.  Combine them into a single, well-structured paragraph that reads \
naturally and eliminates redundancy.  Keep the final answer under 1/3rd of the \
original combined length.

<chunk_summaries>
{chunk_summaries}
</chunk_summaries>

Return ONLY the final text inside <final_summary> tags."""
