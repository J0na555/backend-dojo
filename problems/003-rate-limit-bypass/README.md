# Rate limiting can be bypassed by setting an arbitrary X-Forwarded-For header.
The API trusts client-supplied IP headers, letting a single attacker exhaust the rate-limit budget of other users.
