"""The compaction prompt's completion rule, checked on the message the model is actually sent.

Compaction rewrites the agent's own memory of what it has done. The rule that a step counts
as complete only on explicit confirmation is what stops the summary from inventing progress —
and an agent that believes it already finished a step stops early, which reads as success.

Asserted on the SystemMessage the manager builds, not on the source text: the prompt reaching
the model is what matters, and the difference is everything the code does in between.
"""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from browser_use.agent.message_manager.service import MessageManager
from browser_use.agent.views import AgentStepInfo, MessageCompactionSettings
from browser_use.filesystem.file_system import FileSystem
from browser_use.llm import BaseChatModel, SystemMessage
from browser_use.llm.views import ChatInvokeCompletion

#: Clauses the summary cannot be trusted without. Wording is free; the rules are not.
REQUIRED = (
    "Only mark a step as completed if you see explicit success confirmation",
    "Never infer completion from context",
)


@pytest.mark.asyncio
async def test_compaction_prompt_keeps_its_completion_rules(tmp_path: Path):
    manager = MessageManager(
        task="test task",
        system_message=SystemMessage(content="system"),
        file_system=FileSystem(tmp_path),
    )
    llm = AsyncMock(spec=BaseChatModel)
    llm.ainvoke.return_value = ChatInvokeCompletion(completion="Compacted history", usage=None)

    compacted = await manager.maybe_compact_messages(
        llm=llm,
        settings=MessageCompactionSettings(compact_every_n_steps=1, trigger_char_count=0),
        step_info=AgentStepInfo(step_number=1, max_steps=10),
    )

    assert compacted is True
    sent = llm.ainvoke.await_args.args[0]
    instructions = next(m.content for m in sent if isinstance(m, SystemMessage))
    missing = [clause for clause in REQUIRED if clause not in instructions]
    assert not missing, f"the compaction prompt lost: {missing}"
