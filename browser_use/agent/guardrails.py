"""The two limits the model is told about, kept where both the prompt and the loop can read them.

The agent enforces a budget of actions per step and describes a page whose interactive parts
carry a numeric index. Both facts reach the model as words, and both are enforced elsewhere
as code — so the sentence and the number have to come from the same place or they drift
apart, and the model is told something the agent will not do.
"""

from __future__ import annotations

#: Past this the model chains actions without looking at the page between them, which is the
#: behaviour the per-step budget exists to prevent.
MAX_ACTIONS_PER_STEP = 5

#: The part of the system prompt that says what may be acted on. Without it plain text reads
#: as clickable and the indices the model returns point at nothing.
SYSTEM_PROMPT_INTERACTIVITY_RULE = (
    "Only elements carrying a numeric index in square brackets are interactive. "
    "Never return an index for text that has none, and never invent an index that "
    "was not present in the browser state you were given."
)


def system_prompt_guardrails(max_actions: int = MAX_ACTIONS_PER_STEP) -> str:
    """The sentences appended to the system prompt, naming the budget the loop enforces."""
    return f"You may use at most {max_actions} actions per step. {SYSTEM_PROMPT_INTERACTIVITY_RULE}"
