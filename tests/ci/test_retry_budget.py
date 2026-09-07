"""An action that keeps failing must eventually be abandoned, and the agent must be told.

Nothing else asserts either half. Without the ceiling the step retries the same broken call
until its action budget is gone; without the message the caller has nothing to act on and
retries anyway. The two are one property and are asserted together.
"""

import pytest

from browser_use.agent.guardrails import (
    MAX_CONSECUTIVE_FAILURES,
    SYSTEM_PROMPT_RETRY_RULE,
    retry_budget_exhausted,
)

#: A ceiling past this is not a ceiling: the step's action budget runs out first.
MAX_REASONABLE_RETRIES = 10


def test_repeated_failures_are_abandoned_and_the_agent_is_told_why():
    assert 1 <= MAX_CONSECUTIVE_FAILURES <= MAX_REASONABLE_RETRIES, MAX_CONSECUTIVE_FAILURES

    still_going = retry_budget_exhausted(0)
    assert "attempt(s) left" in still_going, f"no budget was reported: {still_going!r}"

    given_up = retry_budget_exhausted(MAX_CONSECUTIVE_FAILURES)
    assert given_up.startswith("Giving up"), f"the action was not abandoned: {given_up!r}"
    assert SYSTEM_PROMPT_RETRY_RULE in given_up, "the model was not told why"
    assert SYSTEM_PROMPT_RETRY_RULE.startswith("Never repeat"), "the rule stopped being a rule"

    # A count that cannot be read must stop the step, not be reported as a fresh budget.
    class Unreadable:
        def __int__(self):
            raise RuntimeError("cannot count")

    with pytest.raises(Exception):
        retry_budget_exhausted(Unreadable())
