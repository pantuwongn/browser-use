"""The constraints in our LLM prompts are behaviour, so they are pinned like behaviour.

A prompt is the only part of an agent that changes what the model does and is not covered by
any other test here: every test below this line builds its own SystemMessage, so the strings
the product actually ships are asserted nowhere. A constraint quietly dropped from one of
them survives the whole suite.

These assert the constraint clauses, not the whole prompt — wording is free to change, the
rules are not.
"""

from pathlib import Path

import browser_use

SOURCE = Path(browser_use.__file__).parent


def source_of(relative: str) -> str:
    return (SOURCE / relative).read_text(encoding='utf-8')


def test_element_finder_prompt_keeps_its_interactivity_rule():
    """Without it the model treats plain text as clickable and returns unusable indices."""
    assert 'Only elements with numeric indexes in [] are interactive' in source_of('actor/page.py')


def test_element_finder_prompt_keeps_its_no_match_rule():
    """Without it the model invents an index rather than reporting that nothing matched."""
    assert 'return None' in source_of('actor/page.py')
