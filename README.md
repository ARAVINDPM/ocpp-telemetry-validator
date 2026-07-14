# ocpp-telemetry-validator

A lightweight Python prototype simulating an OCPP gateway that ingests and validates real-time charging telemetry data from High-Power Chargers (HPC).

This project demonstrates structured parsing and edge threshold verification for electric vehicle networks.

## Features
- Dataclass-based OCPP message parsing (`MeterValues.req`).
- Automated grid limit boundaries (liquid-cooled current limits at 500 A, voltage ranges, cable thermal limits).
- Power plausibility checks (P = V * I) with deviation alerts to detect sensor calibration drift.

## Run Tests
Run the test suite:
```bash
python3 -m pytest -q
```
