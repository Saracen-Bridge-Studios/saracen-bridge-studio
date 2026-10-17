"""Reading a script scene by scene with the local model (1.0.7).

Brand spotting, element tagging and the BFI script read all need the same thing: every scene of the script, with
its number and page as the breakdown counts them, read in order by the model, with a structured answer per scene.
The script is sent in groups of whole scenes sized to the engine's context (a scene longer than a group is split),
each labelled "[SCENE n, page p] heading", so every answer can point to an exact scene and page.

The scene numbers match the breakdown because both come from the same reader (script.scene_texts). If the
breakdown was made by an older reader, it is read again first (server.fresh_breakdown).
"""
from __future__ import annotations

import time

from . import llm, script


class Reading:
    """One pass of the model over a script."""

    def __init__(self, filename: str, data: bytes, breakdown: dict, settings: dict, mode: str | None = None,
                 progress=lambda msg: None, cancelled=lambda: False, share: float = 0.45):
        ms = llm.mode_settings(settings, mode)
        self.engine, why = llm.resolve(settings, ms["mode"])
        if not self.engine:
            raise llm.EngineError(why)
        self.mode, self.think = ms["mode"], bool(ms["think"])
        self.extra = 4000 if self.think else 0           # thinking spends tokens before the answer starts
        self.settings, self.progress, self.cancelled = settings, progress, cancelled
        self.scenes = script.scene_texts(filename, data)
        if not self.scenes:
            raise ValueError("The script has no scenes to read (no INT./EXT. headings found).")
        if len(self.scenes) != breakdown.get("scene_count"):
            raise ValueError(f"The script reads as {len(self.scenes)} scenes but its breakdown has {breakdown.get('scene_count')}. "
                             "Open the script in the Library so it is read again, then retry.")
        ctx = int(settings.get("ai_engine", {}).get("context", 16384))
        # the scenes plus instructions plus the answer must fit one slot's context: ~3.5 characters a token; thinking
        # (Deep) takes up to 4,000 tokens of the same context, so its groups are a quarter smaller
        self.chars = max(3000, min(40000, int(ctx * 3.5 * share * (0.75 if self.think else 1))))
        self.calls, self.t0 = 0, time.time()

    def batches(self) -> list[list[tuple[dict, str]]]:
        return script.scene_batches(self.scenes, self.chars)

    def ask(self, system: str, user: str, schema: dict, tokens: int, temperature: float = 0.2) -> dict:
        if self.cancelled():
            raise InterruptedError("Cancelled")
        self.calls += 1
        return llm.chat(self.engine, system, user, schema=schema, settings=self.settings, max_tokens=tokens + self.extra,
                        temperature=temperature, think=self.think, think_budget=self.extra or None)

    def over_scenes(self, system: str, intro: str, schema, tokens, label: str = "Reading scenes") -> list[tuple[list[dict], dict]]:
        """Each group of scenes with the model's answer for it. schema may be a function of the group's scenes (so
        an answer can only name scenes it was shown)."""
        out = []
        groups = self.batches()
        for i, group in enumerate(groups, 1):
            first, last = group[0][0]["number"], group[-1][0]["number"]
            self.progress(f"{label} {first}–{last} of {len(self.scenes)}" if first != last else f"{label} {first} of {len(self.scenes)}")
            text = "\n\n".join(item for _, item in group)
            shown = {}
            for sc, _ in group:                              # a long scene split in pieces appears once
                shown.setdefault(sc["number"], sc)
            sch = schema(list(shown.values())) if callable(schema) else schema
            budget = tokens(list(shown.values())) if callable(tokens) else tokens      # the answer grows with the scenes shown
            answer = self.ask(system, f"{intro}\n\nSCENES {first} TO {last} OF {len(self.scenes)}:\n\n{text}", sch, budget)
            out.append((list(shown.values()), answer))
        return out

    def made_with(self) -> dict:
        return {"engine": self.engine.kind, "model": self.engine.model, "mode": self.mode, "calls": self.calls,
                "scenes": len(self.scenes), "seconds": round(time.time() - self.t0, 1)}


def in_range(numbers, scenes: list[dict]) -> list[int]:
    """Scene numbers the model gave that belong to the group it was shown (others are dropped as misreads)."""
    allowed = {s["number"] for s in scenes}
    return [n for n in numbers if n in allowed]
