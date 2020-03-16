[Prototype Readme.md]

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

```
[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "IP_ADDRESS", 
        "value": "10.242.50.240"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "CALLER", 
    "id": 1
  }
]
[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "PUBLIC_IP_ADDRESS", 
        "value": "109.161.146.32"
      }, 
      {
        "type": "IP_ADDRESS", 
        "value": "10.242.50.240"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "CALLER", 
    "id": 1
  }
]
[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "PUBLIC_IP_ADDRESS", 
        "value": "109.161.146.32"
      }, 
      {
        "type": "IP_ADDRESS", 
        "value": "10.242.50.240"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "CALLER", 
    "id": 1
  }
]
[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "IP_ADDRESS", 
        "value": "10.242.50.240"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "CALLER", 
    "id": 1
  }
]
[
  {
    "roaming_status": null, 
    "is_target": null, 
    "is_owner": false, 
    "additional_types": null, 
    "identifiers": [
      {
        "type": "IP_ADDRESS", 
        "value": "10.242.50.240"
      }
    ], 
    "serving_network": null, 
    "line_type": null, 
    "ip_access_network_index": 0, 
    "device": null, 
    "subscription_network": null, 
    "type": "CALLER", 
    "id": 1
  }
]
```