"""Local model adapter. The model reads and drafts. It never produces a figure the engine relies on.

Every model task declares a JSON schema, and the local engine (studio.llm) is asked to
return output conforming to it. Results come back as *proposals* the user confirms; only
confirmed values enter engine calculations.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class ModelTask:
    name: str                  # e.g. "extract_term_sheet"
    instructions: str          # Jon's rules for this task, taken from the source SKILL/knowledge files
    schema: dict               # JSON schema the output must satisfy
    inputs: dict = field(default_factory=dict)


@dataclass
class Proposal:
    task: str
    data: dict
    status: str = "Proposed"   # Proposed -> Confirmed by a user, never by the model


class LocalModel:
    """Runs a ModelTask on whichever engine Settings resolves to (see studio.llm). A local engine keeps everything on the
    computer; Cloud AI, when the user switches it on for writing, sends the request to their own provider."""

    def __init__(self, settings: dict | None = None):
        from . import llm, store
        self.settings = settings or store.load_settings()
        self.engine, self.reason = llm.resolve(self.settings)

    def run(self, task: ModelTask, max_tokens: int = 2048) -> Proposal:
        from . import llm
        if not self.engine:
            raise llm.EngineError(self.reason)
        data = llm.chat(self.engine, task.instructions, json.dumps(task.inputs, ensure_ascii=False),
                        schema=task.schema, settings=self.settings, max_tokens=max_tokens)
        return Proposal(task.name, data)
