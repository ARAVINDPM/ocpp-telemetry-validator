from validator import OCPPTelemetryValidator, TelemetryData

def test_valid_telemetry_passes():
    validator = OCPPTelemetryValidator()
    payload = {
        "connectorId": 1,
        "transactionId": 12345,
        "meterValue": {
            "voltage": 400.0,
            "current": 300.0,
            "power": 120.0,  # 400 * 300 / 1000 = 120 kW (perfect match)
            "temperature": 45.0,
            "soc": 65.0
        }
    }
    data = validator.parse_meter_values(payload)
    report = validator.validate_safety_boundaries(data)
    
    assert report["status"] == "PASSED"
    assert len(report["anomalies"]) == 0
    assert report["data"]["power_kw"] == 120.0
    print("test_valid_telemetry_passes: OK")

def test_over_current_triggers_warning():
    validator = OCPPTelemetryValidator(max_current_a=500.0)
    payload = {
        "connectorId": 1,
        "transactionId": 12346,
        "meterValue": {
            "voltage": 400.0,
            "current": 550.0,  # exceeds 500 A limit
            "power": 220.0,
            "temperature": 50.0
        }
    }
    data = validator.parse_meter_values(payload)
    report = validator.validate_safety_boundaries(data)
    
    assert report["status"] == "WARNING"
    assert any("OVER_CURRENT" in anomaly for anomaly in report["anomalies"])
    print("test_over_current_triggers_warning: OK")

def test_power_plausibility_failure():
    validator = OCPPTelemetryValidator()
    payload = {
        "connectorId": 1,
        "transactionId": 12347,
        "meterValue": {
            "voltage": 400.0,
            "current": 200.0,
            "power": 100.0,  # calculated is 80 kW (25% deviation)
            "temperature": 40.0
        }
    }
    data = validator.parse_meter_values(payload)
    report = validator.validate_safety_boundaries(data)
    
    assert report["status"] == "WARNING"
    assert any("POWER_PLAUSIBILITY_FAIL" in anomaly for anomaly in report["anomalies"])
    print("test_power_plausibility_failure: OK")

def test_missing_required_keys_raises_value_error():
    validator = OCPPTelemetryValidator()
    payload = {
        "connectorId": 1,
        # missing transactionId
        "meterValue": {
            "voltage": 400.0,
            "current": 200.0,
            "power": 80.0
        }
    }
    try:
        validator.parse_meter_values(payload)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Schema Validation Error" in str(e)
    print("test_missing_required_keys_raises_value_error: OK")

