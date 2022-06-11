# Temporarily enable LLDP before enabling l2cp transparency on uplinks

```
enter candidate
/system event-handler instance brief_lldp_on_uplinks
admin-state enable
upython-script lldp_before_l2cp.py
paths [
 "interface ethernet-1/{49..50} oper-state"
]
options {
 object debug {
  value true
 }
}
commit stay
```
