"""A per-step action budget is only a budget if the agent can tell which actions failed.

The two halves are enforced in different files and neither is asserted anywhere else. An
agent allowed several actions per step spends that budget on a chain it believes succeeded,
so a failure that stops surfacing costs the whole step — and a budget that stops being a
budget makes the chain long enough for that to matter.

One test, because the invariant is the pair: either half alone is not the property.
"""

import re

from browser_use.agent.guardrails import system_prompt_guardrails
from browser_use.browser.views import BrowserError
from browser_use.tools.service import Tools

#: Past this the model chains actions without looking at the page between them.
MAX_REASONABLE_ACTIONS = 50

BUDGET = re.compile(r"at most (\d+) actions per step")


async def test_the_budget_is_bounded_and_a_failed_action_still_reports_its_error():
    stated = BUDGET.search(system_prompt_guardrails())
    assert stated, "the guardrails no longer tell the model its per-step budget"
    assert 1 <= int(stated.group(1)) <= MAX_REASONABLE_ACTIONS, stated.group(1)

    tools = Tools()

    @tools.registry.action(description="Fails the way a real action fails")
    async def failing_step():
        raise BrowserError(message="net::ERR_NAME_NOT_RESOLVED")

    model = tools.registry.create_action_model()
    result = await tools.act(model(**{"failing_step": {}}), browser_session=None)  # type: ignore[arg-type]
    assert result.error, "the failure was swallowed — the agent spends its budget on a lie"
