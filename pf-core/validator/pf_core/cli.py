"""PF-Core CLI: `pf core <command>`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping

from pf_core.audit import audit_boundary
from pf_core.compile import compile_observation
from pf_core.contracts import assert_trace_satisfies_contract, trace_satisfies_contract
from pf_core.deciders import event_safe, handoff_safe, trace_safe
from pf_core.emitter import emit_artifacts, emit_certificate
from pf_core.errors import PFCoreError
from pf_core.hash_chain import validate_hash_chain, validate_trace_hashes
from pf_core.schemas import load_registry, validate_object, validate_schema_files


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _emit(obj: Mapping[str, Any]) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def cmd_schema_check(args: argparse.Namespace) -> int:
    schemas_dir = Path(args.schemas)
    validate_schema_files(schemas_dir)
    print(f"OK: validated {len(list(schemas_dir.glob('*.schema.json')))} schemas")
    return 0


def cmd_validate_event(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    event = _load_json(Path(args.file))
    validate_object(event, registry)
    validate_hash_chain([event])
    safe = event_safe(event)
    result = {
        "valid": True,
        "decision": event.get("decision"),
        "event_safe": safe,
        "claim_class": "Lean-proved" if safe else "Operationally-checked",
    }
    _emit(result)
    return 0


def cmd_validate_trace(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    trace = _load_json(Path(args.file))
    validate_object(trace, registry)
    validate_trace_hashes(trace)
    print("OK: trace schema and hash chain valid")
    return 0


def cmd_compile_observation(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    obs = _load_json(Path(args.file))
    validate_object(obs, registry)
    event = compile_observation(obs)
    validate_object(event, registry)
    out = Path(args.output) if args.output else None
    if out:
        out.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: wrote event to {out}")
    else:
        _emit(event)
    return 0


def cmd_check_trace(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    trace = _load_json(Path(args.file))
    validate_object(trace, registry)
    validate_trace_hashes(trace)
    contract = _load_json(Path(args.contract)) if args.contract else {
        "schema_version": "pf-core.contract.v0",
        "name": "trace-safe",
        "pre": {},
        "post": {"require_event_safe": True},
        "invariant": {"require_trace_safe": True},
    }
    validate_object(contract, registry)
    safe = trace_safe(trace)
    contract_ok = trace_satisfies_contract(contract, trace)
    result = {
        "safe": safe,
        "contract_satisfied": contract_ok,
        "event_count": len(trace.get("events", [])),
    }
    if not safe:
        raise PFCoreError("UnsafeTrace", "trace failed safety decider")
    if not contract_ok:
        raise PFCoreError("ContractPostconditionFailed", "trace failed contract decider")
    if getattr(args, "lean_check", False):
        import subprocess

        lean_root = Path(args.schemas).parent.parent / "lean"
        proc = subprocess.run(
            ["lake", "build", "PFCore.Replay"],
            cwd=lean_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise PFCoreError("LeanReplayFailed", proc.stderr or proc.stdout)
        print("OK: Lean replay check passed")
    _emit(result)
    return 0


def cmd_emit_certificate(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    trace = _load_json(Path(args.trace))
    validate_object(trace, registry)
    validate_trace_hashes(trace)
    contract = _load_json(Path(args.contract)) if args.contract else {
        "schema_version": "pf-core.contract.v0",
        "name": "trace-safe",
        "pre": {},
        "post": {"require_event_safe": True},
        "invariant": {"require_trace_safe": True},
    }
    validate_object(contract, registry)
    assert_trace_satisfies_contract(contract, trace)
    cert = emit_certificate(trace, contract)
    validate_object(cert, registry)
    out = Path(args.output) if args.output else None
    if out:
        out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: wrote certificate to {out}")
    else:
        _emit(cert)
    return 0


def cmd_emit_artifacts(args: argparse.Namespace) -> int:
    obs = _load_json(Path(args.file))
    contract = _load_json(Path(args.contract)) if args.contract else None
    paths = emit_artifacts(
        obs,
        out_dir=Path(args.out_dir),
        schemas_dir=Path(args.schemas),
        contract=contract,
        runtime_id=args.runtime_id,
    )
    for name, path in paths.items():
        print(f"OK: {name} -> {path}")
    return 0


def cmd_audit_boundary(args: argparse.Namespace) -> int:
    root = Path(args.root)
    audit_boundary(root)
    print("OK: boundary audit passed")
    return 0


def cmd_validate_handoff(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.schemas))
    handoff = _load_json(Path(args.file))
    validate_object(handoff, registry)
    if not handoff_safe(handoff):
        raise PFCoreError("UnsafeHandoff", "handoff failed safety decider")
    print("OK: handoff safe")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pf")
    sub = parser.add_subparsers(dest="group", required=True)

    core = sub.add_parser("core", help="PF-Core commands")
    core_sub = core.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--schemas",
            default="pf-core/schemas",
            help="path to PF-Core JSON schemas",
        )

    p = core_sub.add_parser("schema-check", help="validate schema files")
    p.add_argument("--schemas", required=True)
    p.set_defaults(func=cmd_schema_check)

    p = core_sub.add_parser("validate-event", help="validate a single event")
    add_common(p)
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_validate_event)

    p = core_sub.add_parser("validate-trace", help="validate trace schema and hashes")
    add_common(p)
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_validate_trace)

    p = core_sub.add_parser("compile-observation", help="compile observation to event")
    add_common(p)
    p.add_argument("--file", required=True)
    p.add_argument("--output", help="write event JSON to path")
    p.set_defaults(func=cmd_compile_observation)

    p = core_sub.add_parser("check-trace", help="validate trace safety deciders")
    add_common(p)
    p.add_argument("--file", required=True)
    p.add_argument("--contract", help="contract JSON for satisfaction check")
    p.add_argument("--lean-check", action="store_true", help="optional Lean replay check")
    p.set_defaults(func=cmd_check_trace)

    p = core_sub.add_parser("emit-certificate", help="emit certificate for trace")
    add_common(p)
    p.add_argument("--trace", required=True)
    p.add_argument("--contract", help="contract JSON for contract_hash binding")
    p.add_argument("--output", help="write certificate JSON to path")
    p.set_defaults(func=cmd_emit_certificate)

    p = core_sub.add_parser("emit-artifacts", help="emit full adapter artifact set")
    add_common(p)
    p.add_argument("--file", required=True, help="runtime observation JSON")
    p.add_argument("--out-dir", required=True, help="output directory")
    p.add_argument("--contract", help="optional contract JSON")
    p.add_argument("--runtime-id", default="pf-core-adapter")
    p.set_defaults(func=cmd_emit_artifacts)

    p = core_sub.add_parser("audit-boundary", help="audit trusted boundary docs/code")
    p.add_argument("--root", default=".")
    p.set_defaults(func=cmd_audit_boundary)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.group != "core":
        parser.error("only `pf core` is supported")
    try:
        return args.func(args)
    except PFCoreError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
