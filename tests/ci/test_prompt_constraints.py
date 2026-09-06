"""The constraints in our LLM prompts are behaviour, so they are pinned like behaviour.

A prompt is the only part of an agent that changes what the model does and is covered by no
other test here: every test below this line builds its own SystemMessage, so the strings the
product actually ships are asserted nowhere. A constraint quietly dropped from one of them
survives the whole suite.

The element-finder prompt is checked AGAINST THE REGISTRY it describes. The two drift apart
in both directions — a rule removed from the prompt, an action removed from the registry —
and either way the model is told something the tools will not honour. Reading the prompt
alone would catch half of that.

These assert the constraint clauses, not the whole prompt: wording stays free to change,
the rules do not.
"""

from pathlib import Path

import browser_use
from browser_use.tools.service import Tools

SOURCE = Path(browser_use.__file__).parent

#: The prompt describes a page the model acts on by index, and these are the actions that
#: make that description true: three that take an index, and the one that changes the page
#: they are indexed from. An agent missing any of them cannot do what the prompt says it can.
CORE_ACTIONS = ("click", "input", "scroll", "navigate")


def source_of(relative: str) -> str:
    return (SOURCE / relative).read_text(encoding="utf-8")


def test_element_finder_prompt_matches_the_registry_it_describes():
    """Without the rule the model treats plain text as clickable and returns dead indices."""
    registered = set(Tools().registry.registry.actions)
    missing = [name for name in CORE_ACTIONS if name not in registered]
    assert not missing, f"the prompt promises indexed actions the registry lost: {missing}"
    assert "Only elements with numeric indexes in [] are interactive" in source_of(
        "actor/page.py"
    )


def test_element_finder_prompt_keeps_its_no_match_rule():
    """Without it the model invents an index rather than reporting that nothing matched."""
    assert "return None" in source_of("actor/page.py")
