from fastapi import Request, HTTPException
from typing import Optional

# Placeholder compliance hooks. These can be attached to routes as dependencies.

def require_consent(request: Request):
	consent = request.headers.get("X-User-Consent", "true").lower()
	if consent not in ("true", "1", "yes"):
		raise HTTPException(status_code=403, detail="Consent required")


def region_check(request: Request):
	# Example: enforce data residency or block certain regions.
	# Read IP/headers, map to region and decide. Currently permissive.
	return


def request_pii_deletion(user_id: Optional[str]) -> bool:
	# Hook to trigger PII deletion workflow in DB and integrated systems.
	# Return True if scheduled. Implement actual deletion with audit log and TTL policies.
	return True