# Temporarily enable LLDP before enabling l2cp transparency on uplinks, 22.6 syntax

```
enter candidate
/system event-handler instance brief_lldp_on_uplink_49
admin-state enable
upython-script lldp_before_l2cp.py
paths [
 "interface ethernet-1/49 oper-state"
 "system lldp interface ethernet-1/49 neighbor * system-name"
 "system lldp interface ethernet-1/49 neighbor * port-id"
]
options { 
 object debug { value true } 
 object peer-regex { value "spine.*" } 
}

/system event-handler instance brief_lldp_on_uplink_50
admin-state enable
upython-script lldp_before_l2cp.py
paths [
 "interface ethernet-1/50 oper-state"
 "system lldp interface ethernet-1/50 neighbor * system-name"
 "system lldp interface ethernet-1/50 neighbor * port-id"
]
options { object debug { value true } }
commit stay
```

# Toggle Forward Error Correction state
```
enter candidate
/system event-handler instance toggle_fec
admin-state enable
upython-script toggle_fec.py
path [
 "interface ethernet-1/{49..50} oper-state"
 "interface ethernet-1/{49..50} transceiver forward-error-correction"
]
options { object debug { value true } }

commit stay
```

Note that there is a limit of 100 paths to monitor, and {1..50} keeps hanging in 'starting'
