"""The agent's default step ceilings are a safety bound, so they are pinned like one.

An agent whose loop bound is raised does not fail — it runs, and the bill arrives later.
Nothing else in this suite asserts the shipped defaults, so a bound loosened by an order of
magnitude passes every test here.

The numbers are deliberately loose: this pins the ORDER OF MAGNITUDE, not the value, so
ordinary tuning is free and only a bound that stops being a bound fails.
"""

import inspect

from browser_use import Agent

#: A run that needs more steps than this is not a run that should finish unattended.
MAX_REASONABLE_STEPS = 2_000

#: One model call can be asked to act several times. Past this the agent stops checking the
#: page between actions, which is the behaviour the limit exists to prevent.
MAX_REASONABLE_ACTIONS_PER_STEP = 50


def default_of(func, name: str):
    parameter = inspect.signature(func).parameters[name]
    assert parameter.default is not inspect.Parameter.empty, f"{name} lost its default"
    return parameter.default


def test_agent_run_keeps_a_bounded_step_ceiling():
    steps = default_of(Agent.run, "max_steps")
    assert isinstance(steps, int)
    assert 1 <= steps <= MAX_REASONABLE_STEPS, f"max_steps default is {steps}"


def test_agent_keeps_a_bounded_actions_per_step():
    actions = default_of(Agent.__init__, "max_actions_per_step")
    assert isinstance(actions, int)
    assert 1 <= actions <= MAX_REASONABLE_ACTIONS_PER_STEP, f"default is {actions}"
