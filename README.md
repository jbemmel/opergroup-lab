# Temporarily enable LLDP before enabling l2cp transparency on uplinks

```
enter candidate
/system event-handler instance brief_lldp_on_uplink_49
admin-state enable
upython-script lldp_before_l2cp.py
path [
 "interface ethernet-1/49 oper-state",
 "system lldp interface ethernet-1/49"
]
options { object debug { value true } }

/system event-handler instance brief_lldp_on_uplink_50
admin-state enable
upython-script lldp_before_l2cp.py
path [
 "interface ethernet-1/50 oper-state",
 "system lldp interface ethernet-1/50"
]
options { object debug { value true } }
commit stay
```
