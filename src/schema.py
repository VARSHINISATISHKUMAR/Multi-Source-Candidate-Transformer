"""
Canonical schema for the Eightfold candidate transformer.
Pydantic gives us structure validation, type coercion, and a single
source of truth for what a "candidate" looks like at every stage.
"""
from __future__ import annotations
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

from typing import Literal

SourceType = Literal[
    "csv",
    "json",
    "txt",
    "pdf",
    "docx"
]

class ProvenanceEntry(BaseModel):
    source: SourceType
    value: Optional[Union[str, List[str]]] = None


class FieldValue(BaseModel):
    """One canonical field: its winning value + how we got there."""
    value: Optional[Union[str, List[str]]] = None
    confidence: float = 0.0
    provenance: List[ProvenanceEntry] = Field(default_factory=list)


class RawRecord(BaseModel):
    """A single record as extracted from ONE source, pre-merge."""
    source: SourceType
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class CanonicalCandidate(BaseModel):
    """Internal merged record — every field is a FieldValue, never a bare value."""
    full_name: FieldValue = Field(default_factory=FieldValue)
    email: FieldValue = Field(default_factory=FieldValue)
    phone: FieldValue = Field(default_factory=FieldValue)
    company: FieldValue = Field(default_factory=FieldValue)
    title: FieldValue = Field(default_factory=FieldValue)
    city: FieldValue = Field(default_factory=FieldValue)
    country: FieldValue = Field(default_factory=FieldValue)
    skills: FieldValue = Field(default_factory=FieldValue)


class OutputConfig(BaseModel):
    """Runtime config — what the caller wants the projected JSON to look like."""
    fields: List[str]
    include_confidence: bool = True
    include_provenance: bool = True
    on_missing: Literal["null", "omit", "error"] = "null"