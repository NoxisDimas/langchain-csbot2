from fastapi import Request
from app.services.middleware.compliance import require_consent, request_pii_deletion


def _mk_request(headers_dict: dict[str, str]):
	scope = {"type": "http", "headers": [(k.encode(), v.encode()) for k, v in headers_dict.items()]}
	return Request(scope)


def test_require_consent_allows_default():
	req = _mk_request({})
	require_consent(req)


def test_require_consent_blocks_when_false():
	from fastapi import HTTPException
	req = _mk_request({"x-user-consent": "false"})
	try:
		require_consent(req)
	except HTTPException as e:
		assert e.status_code == 403


def test_request_pii_deletion_returns_true():
	assert request_pii_deletion("user-1") is True