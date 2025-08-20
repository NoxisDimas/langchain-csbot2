import re
from typing import Tuple, Dict, Any

# Very basic redaction; replace with proper DLP in production.
PII_PATTERNS = {
	"email": re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"),
	"phone": re.compile(r"\+?\d[\d\s\-]{7,}\d"),
	"cc_partial": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}


def mask_pii(text: str) -> Tuple[str, Dict[str, Any]]:
	redactions: Dict[str, Any] = {"matches": []}
	masked = text
	for kind, pattern in PII_PATTERNS.items():
		def _repl(m):
			val = m.group(0)
			redactions["matches"].append({"type": kind, "value": val})
			return f"<{kind}_redacted>"
		masked = pattern.sub(_repl, masked)
	return masked, redactions