"""The two limits the model is told about, kept where both the prompt and the loop can read them.

The agent enforces a budget of actions per step and describes a page whose interactive parts
carry a numeric index. Both facts reach the model as words, and both are enforced elsewhere
as code — so the sentence and the number have to come from the same place or they drift
apart, and the model is told something the agent will not do.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

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


def describe_action_failure(error: BaseException) -> str:
    """What the agent is told when one of its actions fails.

    The step loop spends a budget of actions on a chain it believes succeeded, so a failure
    that reaches it as an empty string costs the rest of the step and reads as success in
    the trace. Kept beside the budget it interacts with.

    An error whose own rendering fails is logged and re-raised rather than described as
    nothing: a description nobody can read is worse than a step that stops.
    """
    detail = ""
    try:
        detail = str(error).strip()
    except Exception:
        logger.exception("an action failure could not be rendered")
        raise
    return f"Action failed: {detail}" if detail else "Action failed: no detail was reported."
