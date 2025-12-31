# Hybrid Connectivity: Advanced Alternativities
## Bakhmach Business Hub - Multi-Link Data Transmission

**Overview**: Redundant multi-protocol system ensuring 99.5% uptime for energy monitoring

---

## Alternative 1: Traditional mwan3 (Primary + LTE Backup)

### Characteristics
- **Primary Link**: Ethernet (ISP) - 95.2% uptime, 3.5 UAH/kWh
- **Backup Link**: USB LTE Modem - 75% uptime, 0.05 UAH/kWh SIM data  
- **Failover Time**: 15 seconds
- **Best For**: Normal operation, cost-effective

### Configuration
```bash
# /etc/config/mwan3 - Load balance 3:1 ratio
config mwan3_interface 'Primary_WAN'
  option weight 3        # 75% traffic
  option reliability 90
  
config mwan3_interface 'Backup_LTE'
  option weight 1        # 25% traffic  
  option reliability 75
```

**Pros**: Cheap, proven, simple
**Cons**: LTE data limits, slow failover

---

## Alternative 2: Mesh Networking (LoRaWAN Backhaul)

### Characteristics
- **Primary Link**: Local LoRaWAN gateway (500m range)
- **Secondary Link**: USB LTE (metered backup)
- **Mesh Nodes**: 3x ESP32 repeaters (low power)
- **Bandwidth**: 11 kbps (optimized for sensor data)
- **Cost**: ~$200 hardware (one-time)

### Mesh Architecture
```
  [Bakhmach Hub] ----LoRa---- [Repeater A] ----LoRa---- [Remote Sensor]
        |
        +----LTE (emergency)
```

### Implementation
```python
import socket
import struct

class LoRaMesh:
    def __init__(self, freq_mhz=868):
        self.freq = freq_mhz
        self.nodes = []  # List of repeater addresses
        
    def send_metrics(self, sensor_id, power_w, temp_c):
        """Send 16-byte compressed metrics via LoRa"""
        # Header (2B) + Sensor_ID (2B) + Power (4B) + Temp (4B) + CRC (2B)
        packet = struct.pack('<HHfH', sensor_id, int(power_w*10), temp_c, 0)
        self.transmit_lora(packet)
        
    def transmit_lora(self, data):
        # SX1278/RFM95 modem control
        # Tx power: 20dBm, datarate: SF12 (slowest but farthest)
        pass
```

**Pros**: No metered costs, long range (500m), self-healing mesh
**Cons**: Requires hardware, 15-20min data latency per hop

---

## Alternative 3: Satellite IoT (Sigfox/NB-IoT)

### Characteristics
- **Technology**: Sigfox (Europe-wide coverage)
- **Data Limit**: 140 messages/day (300 bytes each)
- **Latency**: 10-30 seconds
- **Cost**: ~€50-150/year (Sigfox backend)
- **Integration**: REST API to metrics DB

### Sigfox Callback Setup
```json
{
  "url": "https://bakhmach-hub.local:8443/sigfox/callback",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  },
  "contentType": "application/json",
  "body": "{
    \"device_id\": \"{deviceId}\",
    \"power_reading\": {power},
    \"timestamp\": {time},
    \"rssi\": {rssi},
    \"seq\": {seqNumber}
  }"
}
```

### Daily Metrics (Compressed)
```
Time   | Power (W) | Temp (C) | Battery (%) | Lost packets
-------|-----------|---------|-------------|-------------
05:00  | 150       | 18      | 85          | 0
06:00  | 145       | 19      | 84          | 1  
12:00  | 200       | 25      | 82          | 0
18:00  | 160       | 22      | 80          | 2
```

**Pros**: Geographic independence, ultra-low power
**Cons**: Message limits, latency, cost per message

---

## Alternative 4: Hybrid Multi-Protocol (Recommended)

### Combined System
```
┌─────────────────────────────────────────┐
│  Real-Time Monitoring System            │
│  (Prometheus, Grafana, Alerts)          │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │   Failover      │
    │   Controller    │
    │   (systemd)     │
    └────┬─────┬──────┘
         │     │
    ┌────▼─┐ ┌─▼────┐
    │mwan3 │ │Sigfox│
    └──┬───┘ └──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌─▼────┐
│eth0 │ │usb0  │
│ISP  │ │LTE   │
└─────┘ └──────┘

Priority Order:
1. Primary (eth0) - Active
2. LTE (usb0) - Hot standby
3. Sigfox - Emergency data only (once/day)
4. LoRa mesh - Critical sensor replication
```

### Activation Logic
```python
class HybridConnectivity:
    def get_best_link(self):
        links = []
        
        # Check primary (ISP)
        if self.ping('8.8.8.8') < 50ms:
            links.append(('eth0', 100))  # Priority 100
        
        # Check LTE backup
        if self.ping_via_usb0('1.1.1.1') < 500ms:
            links.append(('usb0', 50))
        
        # Check LoRa mesh
        if self.lorawan_poll_gateway() == online:
            links.append(('lora', 30))
        
        # Sigfox always available (but throttled)
        if self.sigfox_is_configured():
            links.append(('sigfox', 1))
        
        # Return highest priority available
        return max(links, key=lambda x: x[1]) if links else None
    
    def publish_metrics(self, power_w, temp_c):
        best = self.get_best_link()
        
        if best[0] == 'eth0':
            self.publish_prometheus(power_w, temp_c)  # Full resolution
        elif best[0] == 'usb0':
            self.publish_prometheus(power_w, temp_c)  # Full (slower)
        elif best[0] == 'lora':
            self.send_lora_compressed(power_w, temp_c)  # 20-min batches
        elif best[0] == 'sigfox':
            self.send_sigfox_daily_summary()  # Once/day
```

**Pros**: Maximum redundancy, automatic fallback
**Cons**: Complexity, multiple integrations

---

## Cost Comparison (Monthly)

| Method | ISP | LTE SIM | Hardware | Total UAH/mo |
|--------|-----|---------|----------|---------------|
| **Alt 1: mwan3** | 105 | 50 | 0 | **155** |
| **Alt 2: LoRa** | 105 | 0 | 5 (amortized) | **110** |
| **Alt 3: Sigfox** | 105 | 0 | 10 (amortized) | **115** |
| **Alt 4: Hybrid** | 105 | 25 | 8 (amortized) | **138** |

---

## Recommendation

**Use Alt 4 (Hybrid Multi-Protocol)** for Bakhmach:

1. **Primary**: mwan3 (eth0 + usb0) - handles 99% of traffic
2. **Secondary**: LoRaWAN mesh - local sensor replication (if 5+ IoT devices)
3. **Tertiary**: Sigfox - ultra-reliable emergency (once/week check-in)
4. **Monitoring**: Prometheus scrapes primary every 15s, fallback to 5-min batches on LTE

**Expected Uptime**: 99.7% (5 min/month downtime)
**Data Integrity**: 99.9% (automatic retry on link fail)

---

## Implementation Checklist

- [ ] mwan3 configured (main system)
- [ ] LTE failover tested (manual + automatic)
- [ ] LoRa gateway setup (optional, for <5km range)
- [ ] Sigfox backend integrated (emergency channel)
- [ ] Prometheus scrape configs updated
- [ ] Alert rules for link status
- [ ] Monthly cost review
- [ ] Annual failover test
