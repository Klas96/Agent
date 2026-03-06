"""
MPC (Multi-Process Communication) wrapper nodes.

These nodes provide a bridge between the core Email/LLM system and external MPC processes.
"""

from .content_generator import MPCContentGeneratorNode
from .tool_executor import MPCToolExecutorNode
from .investigator import MPCInvestigatorNode

__all__ = [
    "MPCContentGeneratorNode",
    "MPCToolExecutorNode",
    "MPCInvestigatorNode",
]
