# ocpp-telemetry-validator

A learning prototype that parses OCPP 1.6 MeterValues-style payloads from high-power EV chargers and applies plausibility checks to the telemetry stream.

## Why

Charging networks exchange telemetry between chargers and backend systems over OCPP. Corrupt or implausible meter values (voltage, current, power) break billing, load management, and reporting downstream. This prototype explores how schema parsing plus simple physical plausibility rules can catch such defects at the interface. Validation rules check: P = V x I deviation within 5%, current limits for liquid-cooled cables at 500 A, voltage ranges (150-1000 V), and thermal limits (85 C). Built to understand the data quality problem, not to replace production tooling.

## What it does

- Parses OCPP MeterValues JSON payloads into typed TelemetryData objects
- Validates over-current conditions (CCS/HPC limit of 500 A)
- Checks voltage operating window (150 V to 1000 V)
- Verifies active power plausibility using P = V x I formula with 5% tolerance
- Enforces temperature safety thresholds (liquid-cooled connector cutoff at 85 C)
- Returns validation status (PASSED, WARNING, CRITICAL) with anomaly details

## Quickstart

```
git clone <repository>
cd ocpp-telemetry-validator
python3 -m pytest -q
```

Expected output:
```
4 passed
```

## Scope

This is a learning prototype exploring how to detect meter value defects at the OCPP interface boundary. It is not a production charger integration, does not implement roaming, payment, or full OCPP protocol support, and should not be used in live charging networks without substantial extension and validation.

## License

MIT
