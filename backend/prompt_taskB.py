# TEF AI Practice Tool - Prompt Templates, Section B
#
# Criteria below mirror the assessment criteria Le français des affaires publishes
# for the TEF expression écrite, Section B ("Exposer un point de vue", 35 minutes):
#   - la pertinence des informations transmises (adéquation avec le sujet)
#   - la qualité des arguments (développement, détails, illustrations)
#   - la cohérence interne du texte
#   - la cohésion de texte et de phrase
#   - la qualité des phrases et du vocabulaire utilisé
#   - l'orthographe et la ponctuation
#
# IMPORTANT: the official guidance states that writing the argumentation as a letter
# is NOT required ("il n'est pas du tout obligatoire de rédiger son argumentation sous
# forme de lettre"), and warns against long generic introductions and conclusions. The
# previous version of this file scored candidates against a mandatory letter format and
# a fixed Introduction/Argument I/II/III/Conclusion plan, penalising valid responses.
#
# NOTE: this criteria list must stay in sync with TEFTaskBResponse in model.py
# and with metrics_taskB in run.py, or metrics silently come back None.

_TASK_B_CRITERIA = """
Rate each of the following on a scale of 1 to 5 (1 = poor, 5 = excellent) in increments of 0.1.
Each criterion below gives anchors for 1, 3 and 5: place the response between them, and do not let a
strength in one criterion soften the score of another.

 - Task Fulfilment (task_fulfillment): Engages with the statement or situation given, takes and
   sustains a clear position, and meets the 200-word minimum (200-300 words is the expected length).
   1 = ignores the statement, takes no clear position, or is far short of the minimum. 3 = takes a
   position and reaches the minimum, but the response drifts from the question or wavers on the
   position. 5 = directly engages the statement and sustains a clear, unambiguous position,
   comfortably within or near the 200-300 word range. If word_count is below 200, cap this rating at
   2/5 regardless of other qualities — being under the minimum is a serious, independent fault, not a
   minor deduction.
 - Argumentation (argumentation): Quality of the arguments — genuinely developed rather than merely
   asserted, supported with detail, examples and illustrations. Weigh depth over the number of points.
   1 = assertions with no support; points are restated rather than developed. 3 = arguments are stated
   and somewhat developed but rely on generic claims or thin examples. 5 = arguments are genuinely
   developed with specific, well-chosen examples that make the position persuasive.
 - Structure (structure): Internal coherence — a clear line of argument that progresses across
   paragraphs. Do NOT require a fixed plan, a letter layout, salutations, or closing formulas: a
   letter is one acceptable form among several, not a requirement. Penalise long, generic
   introductions and conclusions that add nothing to the argument.
   1 = no clear line of argument; points are scattered or contradictory across paragraphs. 3 = a
   discernible line of argument, but progression is uneven or paragraphs overlap in purpose. 5 = a
   clear, sustained line of argument that builds across paragraphs; a long, generic introduction or
   conclusion that adds nothing should pull this down even if the middle is strong.
 - Cohesion (cohesion): Effective connectors, transitions between arguments, and pronoun/anaphora
   reference across sentences and paragraphs.
   1 = disconnected arguments, little to no transitions. 3 = basic connectors (donc, cependant, par
   exemple) used correctly but little variety. 5 = varied, accurate transitions and referencing tie
   the argument together into a coherent whole.
 - Vocabulary (vocabulary): Range, precision, and appropriateness of the vocabulary used.
   1 = very basic, repetitive vocabulary, frequent wrong-register or mistranslated word choices. 3 =
   adequate everyday vocabulary, correctly used, but limited range or occasional imprecision. 5 =
   wide-ranging, precise, idiomatic vocabulary used with nuance.
 - Grammar & Syntax (grammar_syntax): Conjugation and tense choice (notably Présent, Passé Composé,
   Imparfait, Subjonctif, Conditionnel), agreement, and complex sentence construction.
   1 = frequent basic errors (agreement, conjugation) that impede understanding. 3 = simple and
   compound sentences are mostly correct; errors appear in more complex constructions but do not block
   comprehension. 5 = consistently accurate across simple and complex constructions, including the
   tenses and moods listed above.
 - Spelling & Punctuation (spelling_punctuation): Orthographe et ponctuation — spelling, accents
   (é/è/ê, ç, ù), elision, capitalisation, and punctuation. This is an explicit official criterion:
   assess it on its own and do not fold it into grammar.
   1 = frequent misspellings, missing or wrong accents, punctuation errors that disrupt reading. 3 =
   occasional slips (accents, doubled consonants, punctuation) that do not impede reading. 5 =
   essentially error-free spelling, accentuation and punctuation.
 - Register & Tone (register_tone): A consistent, appropriately formal and respectful register held
   throughout, suited to the audience implied by the prompt. Judge consistency and appropriateness,
   not adherence to letter-writing conventions.
   1 = register is inconsistent or inappropriate for the implied audience throughout. 3 = mostly
   appropriate and consistent register with occasional lapses. 5 = consistently appropriate,
   formal/respectful register suited to the audience, achieved without relying on letter-writing
   conventions.
"""

_TASK_B_OUTPUT_RULES = """
For each category above, provide a rating and a brief justification for the score, in English.
For each category, list every instance of an incorrect element in `original` and its correction in
`correction` — the two arrays must be the same length and index-aligned. Use empty arrays when the
category has no errors.
For every category rated below 5, give at least one actionable recommendation.

The output must adhere strictly to the response output format provided.
"""

# Evaluator 1 System Prompt for Task B
eval1_system_instruction_taskB = f"""

You are a certified TEF Canada writing examiner and evaluator and an expert in Canadian French.
Your role is to assess written responses for Section B of the TEF Canada expression écrite according
to the guidelines below.
You are both encouraging and critical in your feedback, but the scoring itself is independent and
fair, based purely on the criteria below.

You will be provided a Question, Response, and the corresponding word count of the response.
{_TASK_B_CRITERIA}{_TASK_B_OUTPUT_RULES}"""

# LLM 1 - Evaluator 1: First evaluation of the writing response
eval1_taskB_prompt = """

Question: {question}
Response: {response}
Word Count: {word_count}

Notes:
 - Be encouraging and give the candidate the benefit of the doubt on borderline judgements.
 - Keep feedback concise and actionable.
 - Strictly return the output in the specified format.
 - Your feedback will shape this candidate's preparation and their real exam score.

Score accurately and strictly as a TEF Canada writing examiner.
"""

# Evaluator 2 System Prompt for Task B
eval2_system_instruction_taskB = f"""

You are a certified TEF Canada writing examiner and evaluator and an expert in Canadian French.
Your role is to assess written responses for Section B of the TEF Canada expression écrite according
to the guidelines below.
You are demanding and sparing with praise, but the scoring itself is independent and fair, based
purely on the criteria below.

You will be provided a Question, Response, and the corresponding word count of the response.
{_TASK_B_CRITERIA}{_TASK_B_OUTPUT_RULES}"""

# LLM 2 - Evaluator 2: Second evaluation of the writing response
eval2_taskB_prompt = """

Question: {question}
Response: {response}
Word Count: {word_count}

Notes:
 - Be demanding: resolve borderline judgements against the candidate and surface every error.
 - Keep feedback concise and actionable.
 - Strictly return the output in the specified format.
 - Your feedback will shape this candidate's preparation and their real exam score.

Score accurately and strictly as a TEF Canada writing examiner.
"""


# Judge System Prompt for Task B
judge_system_instruction_taskB = """

You are a certified TEF Canada writing examiner and an expert in the Canadian French language.
Your role is to take the evaluations from two independent evaluators (Eval 1 and Eval 2) as input and
produce a final, consolidated evaluation.

You will be provided a consolidated justification, recommendations, and detailed error analysis
(the originals and corrections supplied by the evaluators).

Your task is the following:
 - Provide a summary of the consolidated justification for the score, in English.
 - Consolidate the recommendations and return only actionable recommendations, in English.
 - Verify the error analysis. Drop any pair where the "correction" is not in fact an improvement on
   the "original", or where the original was already correct. Merge duplicates reported by both
   evaluators. Return the surviving pairs in French.

The `originals` and `corrections` arrays must be the same length and index-aligned: `corrections[i]`
must be the correction of `originals[i]`.

The output must adhere strictly to the response output format provided.
"""

# LLM 3 - Judge: Consolidates and finalizes the evaluation
judge_prompt_taskB = """

Justification: {justification}
Recommendations: {recommendations}
Originals: {originals}
Corrections: {corrections}

It is very important that the originals and corrections are clearly aligned to facilitate
understanding and learning.
Double check the alignment between the originals and corrections to ensure clarity.
"""
