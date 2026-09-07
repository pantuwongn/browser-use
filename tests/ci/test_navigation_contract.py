"""The navigate action's contract, checked where the agent actually meets it.

`navigate` is the action every task starts with, and three things have to hold together for
it to work: the registry must be able to call it, the model must have been told what it may
act on, and a failure inside it must come back as a recoverable result rather than escaping
as an exception. Each is enforced in a different file, and no test here checked any of them
against the registry the agent really builds.

Two tests rather than one because the two failures call for different repairs — a prompt
that stopped saying what may be clicked, and an error path that stopped surfacing.
"""

import inspect

from browser_use.agent.guardrails import (
    SYSTEM_PROMPT_INTERACTIVITY_RULE,
    system_prompt_guardrails,
)
from browser_use.browser.views import BrowserError
from browser_use.tools.service import Tools


def registered_navigate(tools: Tools):
    """The navigate action as the registry holds it — None when the registry lost it."""
    return tools.registry.registry.actions.get("navigate")


def takes_its_params(action) -> bool:
    """The registry injects by NAME, so the parameter name is part of the contract.

    An action whose first argument is renamed still registers and still builds from its
    schema — and then cannot be called, which is the whole failure.
    """
    return "params" in inspect.signature(action.function).parameters


async def test_navigate_is_callable_and_the_prompt_still_says_what_to_act_on():
    """The agent is told to click indexed elements and then asked to navigate. Both halves
    have to survive: a renamed parameter makes the call unbuildable, a weakened rule makes
    the model act on things that are not there."""
    tools = Tools()

    action = registered_navigate(tools)
    assert action is not None, "the registry no longer exposes navigate"
    model = tools.registry.create_action_model()
    built = model(**{"navigate": {"url": "https://example.com", "new_tab": False}})
    assert built.model_dump(exclude_none=True).get("navigate"), (
        "navigate could not be built from its own schema"
    )
    assert takes_its_params(action), "navigate no longer accepts the params the registry injects"

    rule = SYSTEM_PROMPT_INTERACTIVITY_RULE
    assert rule in system_prompt_guardrails()
    assert rule.startswith("Only elements"), "the rule stopped being exclusive"
    assert "Never return an index" in rule, "the prohibition on unindexed text was weakened"


async def test_navigate_is_callable_and_a_failure_inside_it_still_surfaces():
    """A tool error that stops surfacing is the failure mode the agent cannot see: it reads
    an empty result as success and carries on."""
    tools = Tools()

    action = registered_navigate(tools)
    assert action is not None, "the registry no longer exposes navigate"
    assert takes_its_params(action), "navigate no longer accepts the params the registry injects"

    @tools.registry.action(description="Fails the way a navigation failure does")
    async def failing_navigation():
        raise BrowserError(message="net::ERR_NAME_NOT_RESOLVED")

    model = tools.registry.create_action_model()
    result = await tools.act(model(**{"failing_navigation": {}}), browser_session=None)  # type: ignore[arg-type]
    assert result.error, "the failure was swallowed — the agent would read this as success"
