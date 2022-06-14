import json

# main entry function for event handler
def event_handler_main(in_json_str):
    # parse input json string passed by event handler
    in_json = json.loads(in_json_str)
    paths = in_json["paths"]
    options = in_json["options"]

    reinvoked = "persistent-data" in in_json and in_json["persistent-data"]["reinvoked"]

    if options.get("debug") == "true":
       print( in_json_str )

    response_actions = []

    for p in paths:
      if p['value'] == "up":
        uplink = p['path'].split(' ')[1]
        response_actions += [
            {
             "set-cfg-path": {
                 "path": f"system lldp interface {uplink} admin-state",
                 "value": "disable" if reinvoked else "enable",
             }
            },
            {
             "set-cfg-path": {
                 "path": f"interface {uplink} ethernet l2cp-transparency tunnel-all-l2cp",
                 "value": reinvoked,
             }
            },
            {
             "set-cfg-path": { # Disable OSPF while waiting for LLDP to complete discovery
                 "path": f"network-instance default protocols ospf instance main area 0.0.0.0 interface {uplink} admin-state",
                 "value": "enable" if reinvoked else "disable",
             }
            },
        ]
        if not reinvoked:
            response_actions += [
              {
                "reinvoke-with-delay": 60000 # Could make configurable in config
              }
            ]
            reinvoked = True
      elif p['value'] == "down":
        reinvoked = False # reset state
      else: # LLDP system name, TODO add port name
        response_actions += [
            {
             "set-cfg-path": {
                 "path": f"interface {uplink} description",
                 "value": p['value'],
             }
            },
        ]

    response = {"actions": response_actions, "persistent-data": { "reinvoked": reinvoked } }
    return json.dumps(response)
