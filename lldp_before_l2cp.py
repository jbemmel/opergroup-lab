import sys
import json

# main entry function for event handler
def event_handler_main(in_json_str):
    # parse input json string passed by event handler
    in_json = json.loads(in_json_str)
    paths = in_json["paths"]
    options = in_json["options"]

    lldp = "persistent-data" in in_json

    if options.get("debug") == "true":
       print( in_json_str )

    response_actions = []

    for p in paths:
      if p['path']['value'] == "up":
        uplink = p['path'].split(' ')[1]
        response_actions.append( [
            {
                "set-ephemeral-path": {
                    "path": f"interface {uplink} ethernet l2cp-transparency tunnel-all-l2cp",
                    "value": lldp,
                }
            },
            {
                "set-ephemeral-path": {
                    "path": f"system lldp interface {uplink} admin-state",
                    "value": "disable" if lldp else "enable",
                }
            },
            ]
        )
        if not lldp:
            response_actions.append( [
              {
                "persistent-data": {
                 "lldp" : "enabled"
                },
              },
              {
                "reinvoke-with-delay": 60000 # Could make configurable in config
              }
             ]
            )

    response = {"actions": response_actions}
    return json.dumps(response)


#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path":"interface ethernet-1/49 oper-status",
            "value":"down"
        },
        {
            "path":"interface ethernet-1/50 oper-status",
            "value":"down"
        }
    ],
    "options": {
        "required-up-uplinks":1,
        "down-links": [
            "Ethernet-1/1",
            "Ethernet-1/2"
        ],
        "debug": "true"
    },
    "persistent-data": {"last-state":"up"}
}
"""
    json_response = event_handler_main(example_in_json_str)
    print(f"Response JSON:\n{json_response}")


if __name__ == "__main__":
    sys.exit(main())
