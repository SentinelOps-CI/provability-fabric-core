"""Typed PF-Core validation errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PFCoreError(Exception):
    code: str
    message: str
    path: Optional[str] = None

    def __str__(self) -> str:
        if self.path:
            return f"{self.code}: {self.message} (at {self.path})"
        return f"{self.code}: {self.message}"


class MissingRequiredField(PFCoreError):
    def __init__(self, field: str, path: Optional[str] = None):
        super().__init__("MissingRequiredField", f"missing required field: {field}", path)


class InvalidSchemaVersion(PFCoreError):
    def __init__(self, expected: str, actual: str, path: Optional[str] = None):
        super().__init__(
            "InvalidSchemaVersion",
            f"expected {expected}, got {actual}",
            path,
        )


class InvalidDecision(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("InvalidDecision", message, path)


class InvalidPrincipal(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("InvalidPrincipal", message, path)


class InvalidAction(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("InvalidAction", message, path)


class InvalidHash(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("InvalidHash", message, path)


class UnsupportedEffect(PFCoreError):
    def __init__(self, effect: str, path: Optional[str] = None):
        super().__init__("UnsupportedEffect", f"unsupported effect: {effect}", path)


class UnsupportedCapability(PFCoreError):
    def __init__(self, capability: str, path: Optional[str] = None):
        super().__init__(
            "UnsupportedCapability",
            f"unsupported capability: {capability}",
            path,
        )


class AmbiguousMapping(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("AmbiguousMapping", message, path)


class PolicyRefNotFound(PFCoreError):
    def __init__(self, policy_ref: str, path: Optional[str] = None):
        super().__init__("PolicyRefNotFound", f"policy_ref not found: {policy_ref}", path)


class EvidenceRefNotFound(PFCoreError):
    def __init__(self, evidence_ref: str, path: Optional[str] = None):
        super().__init__(
            "EvidenceRefNotFound",
            f"evidence_ref not found: {evidence_ref}",
            path,
        )


class ContractPreconditionFailed(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("ContractPreconditionFailed", message, path)


class ContractPostconditionFailed(PFCoreError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__("ContractPostconditionFailed", message, path)
