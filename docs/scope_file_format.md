# Scope file format

A scope file is a JSON object. It is required for non-loopback targets.

```json
{
  "authorized_by": "string, required",
  "issued": "ISO date, optional",
  "expires": "ISO date, optional",
  "targets": ["string", "..."],
  "consent": "string, optional"
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `authorized_by` | Yes | Who authorized the scan |
| `issued` | No | When authorization was granted |
| `expires` | No | When it stops being valid (ISO 8601) |
| `targets` | Yes | Exact strings the scope covers |
| `consent` | No | Free-text consent statement |

## Matching

Targets are matched **exactly** against the `targets` list. No CIDR, no
wildcards. This is deliberate: predictable is safer than clever.

## Expiry

If `expires` is present and parses as a date in the past, the tool refuses
to run. If it cannot be parsed, the CLI proceeds but the malformed value is
still shown in the report so the operator can see it.