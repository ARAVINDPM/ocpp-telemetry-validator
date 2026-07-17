"""Validates OCPP MeterValues telemetry from high-power EV chargers against electrical safety boundaries."""
import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class TelemetryData:
    connector_id: int
    transaction_id: int
    voltage_v: float
    current_a: float
    power_kw: float
    temperature_c: Optional[float] = None
    soc_percent: Optional[float] = None

class OCPPTelemetryValidator:
    """
    Validates high-power charging (HPC) session telemetry based on the OCPP 1.6/2.0.1 MeterValues.req schema,
    enforcing electrical safety limits and grid boundary conditions.
    """
    
    def __init__(self, max_current_a: float = 500.0, max_temp_c: float = 85.0):
        """Initializes validator with electrical safety thresholds."""
        self.max_current_a = max_current_a
        self.max_temp_c = max_temp_c
        
    def parse_meter_values(self, payload: Dict[str, Any]) -> TelemetryData:
        """
        Parses raw OCPP MeterValues JSON payload into typed TelemetryData.
        Raises ValueError if required fields are missing.
        """
        try:
            connector_id = int(payload["connectorId"])
            transaction_id = int(payload["transactionId"])
            
            # Extract sample values (typically stored in a nested array under meterValue)
            # For simplicity in this validator, flat mapping is implemented.
            meter_val = payload["meterValue"]
            
            voltage = float(meter_val.get("voltage", 0.0))
            current = float(meter_val.get("current", 0.0))
            power = float(meter_val.get("power", 0.0))
            
            temp = meter_val.get("temperature")
            temperature = float(temp) if temp is not None else None
            
            soc = meter_val.get("soc")
            soc_percent = float(soc) if soc is not None else None
            
            return TelemetryData(
                connector_id=connector_id,
                transaction_id=transaction_id,
                voltage_v=voltage,
                current_a=current,
                power_kw=power,
                temperature_c=temperature,
                soc_percent=soc_percent
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Schema Validation Error: Missing or invalid keys. Details: {str(e)}")

    def validate_safety_boundaries(self, data: TelemetryData) -> Dict[str, Any]:
        """
        Validates electrical and physical limits:
        - Over-current protection (CCS limit of 500 A)
        - Voltage operating window (150 V to 1000 V)
        - Active power plausibility (P = V * I within 5% tolerance)
        - Temperature limits (Liquid-cooled connector cutoff at 85 C)
        """
        anomalies = []
        status = "PASSED"
        
        # 1. Over-current check
        if data.current_a > self.max_current_a:
            anomalies.append(f"OVER_CURRENT: {data.current_a} A exceeds safety threshold of {self.max_current_a} A.")
            status = "WARNING"
            
        # 2. Voltage range check
        if not (150.0 <= data.voltage_v <= 1000.0):
            anomalies.append(f"VOLTAGE_OUT_OF_BOUNDS: {data.voltage_v} V is outside the target window of 150 V - 1000 V.")
            status = "WARNING"
            
        # 3. Active power calculation validation (P = V * I)
        # Power in kW should equal (V * I) / 1000. Allow 5% tolerance for instrumentation/sampling delays.
        calculated_power_kw = (data.voltage_v * data.current_a) / 1000.0
        if calculated_power_kw > 0:
            deviation = abs(data.power_kw - calculated_power_kw) / calculated_power_kw
            if deviation > 0.05:
                anomalies.append(f"POWER_PLAUSIBILITY_FAIL: Reported power ({data.power_kw} kW) deviates from calculated power ({calculated_power_kw:.2f} kW) by {deviation*100:.1f}%. Possible sensor calibration drift.")
                status = "WARNING"
                
        # 4. Temperature safety check
        if data.temperature_c is not None and data.temperature_c > self.max_temp_c:
            anomalies.append(f"OVER_TEMPERATURE: Connector temperature {data.temperature_c} C exceeds safety threshold of {self.max_temp_c} C.")
            status = "CRITICAL"
            
        return {
            "transactionId": data.transaction_id,
            "status": status,
            "anomalies": anomalies,
            "data": asdict(data)
        }
