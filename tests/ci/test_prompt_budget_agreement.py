"""The system prompt announces an action budget, and the agent enforces one. They must agree.

`system_prompt.md` tells the model "you are allowed to use a maximum of {max_actions} actions
per step" and the number is filled in from the agent's own setting. Nothing else here reads
the rendered prompt, so the sentence can lose its number, its meaning, or its place and every
test still passes — while the model is told a budget nobody enforces.

Rendered, not read from source: what the model is told is the only thing that matters, and
the template is filled in on the way.
"""

import re

from browser_use.agent.prompts import SystemPrompt

#: A budget past this stops being a budget: the model chains actions without looking at the
#: page between them, which is the behaviour the limit exists to prevent.
MAX_REASONABLE_ACTIONS = 50

BUDGET = re.compile(r"maximum of (\d+) actions per step")


def rendered() -> str:
    return SystemPrompt().get_system_message().content


def test_the_prompt_still_states_an_action_budget():
    assert BUDGET.search(rendered()), "the prompt no longer tells the model its action budget"


def test_the_announced_budget_is_a_budget():
    stated = BUDGET.search(rendered())
    assert stated, "the prompt no longer tells the model its action budget"
    actions = int(stated.group(1))
    assert 1 <= actions <= MAX_REASONABLE_ACTIONS, f"the prompt announces {actions} per step"
