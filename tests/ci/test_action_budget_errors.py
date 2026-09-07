"""A per-step action budget is only a budget if the agent can tell which actions failed.

The two halves are enforced in different files and neither is asserted anywhere else. An
agent allowed several actions per step spends that budget on a chain it believes succeeded,
so a failure that reaches it as an empty string costs the whole step and reads as success —
and a budget that stops being a budget makes the chain long enough for that to matter.

One test, because the invariant is the pair: either half alone is not the property.
"""

import re

import pytest

from browser_use.agent.guardrails import describe_action_failure, system_prompt_guardrails

#: Past this the model chains actions without looking at the page between them.
MAX_REASONABLE_ACTIONS = 50

BUDGET = re.compile(r"at most (\d+) actions per step")


def test_the_budget_is_bounded_and_a_failed_action_still_says_so():
    stated = BUDGET.search(system_prompt_guardrails())
    assert stated, "the guardrails no longer tell the model its per-step budget"
    assert 1 <= int(stated.group(1)) <= MAX_REASONABLE_ACTIONS, stated.group(1)

    described = describe_action_failure(ValueError("the page object went away"))
    assert described.startswith("Action failed"), f"the failure lost its label: {described!r}"
    assert "the page object went away" in described, "the failure lost its detail"

    class Unprintable(Exception):
        def __str__(self):
            raise RuntimeError("cannot render")

    # A failure nobody can describe must stop the step, not be handed back as nothing.
    with pytest.raises(Exception):
        describe_action_failure(Unprintable())
