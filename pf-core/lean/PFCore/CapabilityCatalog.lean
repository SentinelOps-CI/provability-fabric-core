import PFCore.Basic
import PFCore.Principal

/-!
# PFCore.CapabilityCatalog

Pinned capability catalog and role-to-capability resolution (decidable, no axioms).
Derived from provability-fabric config export; see `adapters/provability-fabric/fixtures/capability_catalog.json`.
-/

namespace PFCore

structure Capability where
  id : CapabilityId
  effectKind : String
  resourcePattern : String
  deriving Repr, DecidableEq, Inhabited

/-- Pinned capability catalog (matches adapter export). -/
def catalogCapabilities : List Capability := [
  { id := "cap:file-read", effectKind := "file.read", resourcePattern := "/data/*" },
  { id := "cap:file-write", effectKind := "file.write", resourcePattern := "/data/*" },
  { id := "cap:network", effectKind := "network.egress", resourcePattern := "*" },
  { id := "cap:email-send", effectKind := "email.send", resourcePattern := "mailto:*" },
  { id := "cap:handoff", effectKind := "handoff.delegate", resourcePattern := "agent:*" },
  { id := "cap:mcp-invoke", effectKind := "mcp.invoke", resourcePattern := "mcp:*" },
  { id := "cap:mcp-alt", effectKind := "mcp.invoke", resourcePattern := "mcp:alt/*" },
  { id := "cap:lab-release", effectKind := "lab.release", resourcePattern := "lab:*" }
]

def roleCapabilityIds (r : Role) : List CapabilityId :=
  match r with
  | "file_reader" => ["cap:file-read"]
  | "file_admin" => ["cap:file-read", "cap:file-write"]
  | "network_user" => ["cap:network"]
  | "email_user" => ["cap:email-send"]
  | "handoff_delegate" => ["cap:handoff"]
  | "mcp_user" => ["cap:mcp-invoke"]
  | "lab_operator" => ["cap:lab-release"]
  | "agent" => ["cap:file-read", "cap:email-send", "cap:handoff", "cap:mcp-invoke"]
  | _ =>
    if r.startsWith "cap:" then [r] else []

def appendUniqueCapId (xs : List CapabilityId) (y : CapabilityId) : List CapabilityId :=
  if xs.any (· == y) then xs else xs ++ [y]

def foldUniqueCapIds (init : List CapabilityId) (more : List CapabilityId) : List CapabilityId :=
  more.foldl appendUniqueCapId init

def capabilityIdsFromRoles (roles : List Role) : List CapabilityId :=
  roles.foldl (fun acc r => foldUniqueCapIds acc (roleCapabilityIds r)) []

def allowedCapabilityIds (p : Principal) : List CapabilityId :=
  foldUniqueCapIds (capabilityIdsFromRoles p.roles) p.capabilities

def lookupCatalogCapability (id : CapabilityId) : Option Capability :=
  catalogCapabilities.find? (·.id == id)

def capabilityIds (cs : List Capability) : List CapabilityId :=
  cs.map (·.id)

def AllowedCapabilities (p : Principal) : List Capability :=
  (allowedCapabilityIds p).filterMap lookupCatalogCapability

end PFCore
