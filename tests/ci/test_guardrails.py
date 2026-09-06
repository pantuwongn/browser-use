"""The guardrail sentences the agent appends to its system prompt.

They carry the two facts the model is told and the agent enforces: how many actions it may
take in one step, and what on the page it may act on. One test, because they are one
sentence and one promise — the model reads them together, and a notice that keeps half of it
is not half correct.
"""

import re

from browser_use.agent.guardrails import (
    MAX_ACTIONS_PER_STEP,
    SYSTEM_PROMPT_INTERACTIVITY_RULE,
    system_prompt_guardrails,
)

#: Past this the budget has stopped being a budget: the model chains actions without looking
#: at the page between them, which is what the limit exists to prevent.
MAX_REASONABLE_ACTIONS = 50

BUDGET = re.compile(r"at most (\d+) actions per step")


def test_the_guardrails_state_the_budget_and_keep_the_interactivity_rule():
    notice = system_prompt_guardrails()

    stated = BUDGET.search(notice)
    assert stated, "the guardrails no longer tell the model its per-step budget"
    assert 1 <= int(stated.group(1)) <= MAX_REASONABLE_ACTIONS, stated.group(1)
    assert 1 <= MAX_ACTIONS_PER_STEP <= MAX_REASONABLE_ACTIONS, MAX_ACTIONS_PER_STEP

    rule = SYSTEM_PROMPT_INTERACTIVITY_RULE
    assert rule in notice
    assert rule.startswith("Only elements"), "the rule stopped being exclusive"
    assert "numeric index" in rule, "the rule no longer says what to act on"
    assert "Never return an index" in rule, "the prohibition on unindexed text was weakened"
    assert "never invent an index" in rule, "the prohibition on invented indices was weakened"
