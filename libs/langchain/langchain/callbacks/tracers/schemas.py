"""Schemas for tracers."""
from __future__ import annotations

import datetime
import warnings
from typing import Any, Dict, List, Optional
from uuid import UUID
from enum import Enum

from pydantic import model_validator, BaseModel, Field

# from langsmith.schemas import RunBase as BaseRunV2
from langchain.schema import LLMResult


class RunTypeEnumDep(str, Enum):
    """(Deprecated) Enum for run types. Use string directly."""

    tool = "tool"
    chain = "chain"
    llm = "llm"
    retriever = "retriever"
    embedding = "embedding"
    prompt = "prompt"
    parser = "parser"


def RunTypeEnum() -> RunTypeEnumDep:
    """RunTypeEnum."""
    warnings.warn(
        "RunTypeEnum is deprecated. Please directly use a string instead"
        " (e.g. 'llm', 'chain', 'tool').",
        DeprecationWarning,
    )
    return RunTypeEnumDep


class TracerSessionV1Base(BaseModel):
    """Base class for TracerSessionV1."""

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    name: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class TracerSessionV1Create(TracerSessionV1Base):
    """Create class for TracerSessionV1."""


class TracerSessionV1(TracerSessionV1Base):
    """TracerSessionV1 schema."""

    id: int


class TracerSessionBase(TracerSessionV1Base):
    """Base class for TracerSession."""

    tenant_id: UUID


class TracerSession(TracerSessionBase):
    """TracerSessionV1 schema for the V2 API."""

    id: UUID


class BaseRun(BaseModel):
    """Base class for Run."""

    uuid: str
    parent_uuid: Optional[str] = None
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    end_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None
    execution_order: int
    child_execution_order: int
    serialized: Dict[str, Any]
    session_id: int
    error: Optional[str] = None


class LLMRun(BaseRun):
    """Class for LLMRun."""

    prompts: List[str]
    response: Optional[LLMResult] = None


class ChainRun(BaseRun):
    """Class for ChainRun."""

    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    child_llm_runs: List[LLMRun] = Field(default_factory=list)
    child_chain_runs: List[ChainRun] = Field(default_factory=list)
    child_tool_runs: List[ToolRun] = Field(default_factory=list)


class ToolRun(BaseRun):
    """Class for ToolRun."""

    tool_input: str
    output: Optional[str] = None
    action: str
    child_llm_runs: List[LLMRun] = Field(default_factory=list)
    child_chain_runs: List[ChainRun] = Field(default_factory=list)
    child_tool_runs: List[ToolRun] = Field(default_factory=list)


# class RunBase(BaseModel):
#     """Base Run schema."""
#
#     id: UUID
#     name: str
#     start_time: datetime
#     run_type: str
#     """The type of run, such as tool, chain, llm, retriever,
#     embedding, prompt, parser."""
#     end_time: Optional[datetime] = None
#     extra: Optional[dict] = None
#     error: Optional[str] = None
#     serialized: Optional[dict]
#     events: Optional[List[Dict]] = None
#     inputs: dict
#     outputs: Optional[dict] = None
#     reference_example_id: Optional[UUID] = None
#     parent_run_id: Optional[UUID] = None
#     tags: Optional[List[str]] = None


class BaseRunV2(BaseModel):
    """Base Run schema."""

    id: UUID
    name: str
    start_time: datetime.datetime
    run_type: str
    """The type of run, such as tool, chain, llm, retriever,
    embedding, prompt, parser."""
    end_time: Optional[datetime.datetime] = None
    extra: Optional[dict] = None
    error: Optional[str] = None
    serialized: Optional[dict]
    events: Optional[List[Dict]] = None
    inputs: dict
    outputs: Optional[dict] = None
    reference_example_id: Optional[UUID] = None
    parent_run_id: Optional[UUID] = None
    tags: Optional[List[str]] = None


class Run(BaseRunV2):
    """Run schema for the V2 API in the Tracer."""

    execution_order: int
    child_execution_order: int
    child_runs: List[Run] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def assign_name(cls, values: dict) -> dict:
        """Assign name to the run."""
        if values.get("name") is None:
            if "name" in values["serialized"]:
                values["name"] = values["serialized"]["name"]
            elif "id" in values["serialized"]:
                values["name"] = values["serialized"]["id"][-1]
        return values


ChainRun.update_forward_refs()
ToolRun.update_forward_refs()

__all__ = [
    "BaseRun",
    "ChainRun",
    "LLMRun",
    "Run",
    "RunTypeEnumDep",
    "ToolRun",
    "TracerSession",
    "TracerSessionBase",
    "TracerSessionV1",
    "TracerSessionV1Base",
    "TracerSessionV1Create",
]
