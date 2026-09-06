"""The guardrail sentence the agent appends to its system prompt.

It carries the two facts the model is told and the agent enforces: how many actions it may
take in one step, and what on the page it may act on. Both are asserted here because both
reach the model as words while being enforced as code, and nothing else checks that the two
still say the same thing.
"""

import re

from browser_use.agent.guardrails import (
    SYSTEM_PROMPT_INTERACTIVITY_RULE,
    MAX_ACTIONS_PER_STEP,
    system_prompt_guardrails,
)

#: Past this the budget has stopped being a budget.
MAX_REASONABLE_ACTIONS = 50

BUDGET = re.compile(r"at most (\d+) actions per step")


def test_the_notice_states_a_budget_that_is_a_budget():
    stated = BUDGET.search(system_prompt_guardrails())
    assert stated, "the guardrail no longer tells the model its per-step budget"
    assert 1 <= int(stated.group(1)) <= MAX_REASONABLE_ACTIONS, stated.group(1)
    assert 1 <= MAX_ACTIONS_PER_STEP <= MAX_REASONABLE_ACTIONS, MAX_ACTIONS_PER_STEP


def test_the_notice_keeps_the_interactivity_rule():
    """Both halves: what may be acted on, and that the two prohibitions stay prohibitions.

    A rule that says an index "should rarely" be invented is not a rule. The model reads the
    modal, not the intent.
    """
    rule = SYSTEM_PROMPT_INTERACTIVITY_RULE
    assert rule in system_prompt_guardrails()
    assert "numeric index" in rule, "the rule no longer says what to act on"
    assert rule.startswith("Only elements"), "the rule stopped being exclusive"
    assert "Never return an index" in rule, "the prohibition on unindexed text was weakened"
    assert "never invent an index" in rule, "the prohibition on invented indices was weakened"
