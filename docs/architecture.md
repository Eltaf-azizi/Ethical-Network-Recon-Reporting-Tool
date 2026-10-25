# Architecture

```
        +-----------------+
        |    cli.py       |
        +--------+--------+
                 |
    1. auth gate |  2. parse ports  3. resolve   4. scan   5. report
                 v
        +--------+--------+
        |    auth.py      |   (no network calls)
        +-----------------+
                 |
                 v
        +-----------------+        +-----------------+
        |   scanner.py    |<------>|  services.py    |
        +-----------------+        +-----------------+
                 |
                 v
        +-----------------+
        |   report.py     |   Jinja2 + filesystem
        +-----------------+
```

## Modules

| Module | Responsibility |
|---|---|
| `cli.py` | Argument parsing, orchestration, exit codes |
| `auth.py` | Authorization gate and scope-file validation |
| `scanner.py` | Async engine: semaphore + token bucket + per-port probe |
| `services.py` | Port → service map, banner grabbing, OS hint |
| `report.py` | Report data assembly, Jinja2 render, file output |
| `utils.py` | Port-spec parsing, duration formatting |
| `constants.py` | Defaults and magic numbers |
| `exceptions.py` | Custom exception types |

## Order of operations

The CLI deliberately does things in this order:

1. Parse arguments.
2. **Run the authorization gate.** No sockets opened, no DNS resolved.
3. Parse the port spec.
4. Resolve the target host (first network activity).
5. Scan.
6. Assemble report data.
7. Write HTML and optional JSON.