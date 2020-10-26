[Prototype Readme.md]

STUN TOOL:
- place your captures in a folder where `stundump.exe` is
- double click `stundump.exe` or run from shell
- known issues: you may see `invalid TCP dump header` this is `dpkt` library bug, so sorry :) 

[TODO]:
- add User,Pass,Host,Port as a `json` fields
- Add options to select other fields rather `participants`

[example json file]:
```
{
  "session1": {
    "session": {
      "login": null, 
      "queries": []
    }
  }, 
  "session2": {
    "session": {
      "login": "10.164.76.246:8888:hive", 
      "queries": [
        "select * from kafka_events_12 where product_type = 'VOIP' and topic = 'mcapi.avro.pri.decoded' order by start_time desc limit 50", 
        "select * from kafka_events_12 where product_type = 'VIBER' and topic = 'mcapi.avro.pri.decoded' order by start_time desc limit 50"
      ]
    }
  }
}
```



List all `participants` field as a `json` . 

[Example output]

```
------------

CallID:	"d808616f_976c0cc0"

Name on storage:	"0x50000f9c35da8000.PRI.xml"

Participants:	[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "IP_ADDRESS", 
        "value": "10.0.20.20"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "UNKNOWN", 
    "id": 1
  }
]

{
  "gtp_dest_ip": null, 
  "network_id": null, 
  "access_protocol": "RADIUS", 
  "gtp_dest_fteid": null, 
  "gtp_tunnel_id": null, 
  "id": 0
}

{
  "target_side": null, 
  "destination_ip": "10.0.20.20", 
  "ip_protocol": "UDP", 
  "source_ip": "212.72.213.160", 
  "direction": "SERVER_TO_CLIENT", 
  "destination_port": 50850, 
  "source_mac": "00-50-56-9c-53-0b", 
  "app_protocol": "UNDEF", 
  "time": "2020-03-17T13:57:59.090Z", 
  "source_port": 35416, 
  "end_reason": null, 
  "connection_key": "0_10.0.20.20_50850_212.72.213.160_35416_U", 
  "id": 0, 
  "destination_mac": "44-00-10-40-fb-84"
}



------------
```