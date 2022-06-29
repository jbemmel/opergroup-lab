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
options { object debug { value true } }

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
