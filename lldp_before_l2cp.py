#
# Copyright(C) 2022 Nokia
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
    system_name = ""
    port_id = ""

    for p in paths:
      path_parts = p['path'].split(' ')
      if p['value'] == "up":
        uplink = path_parts[1]
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
                 "path": f"network-instance default protocols ospf instance main area 0.0.0.0 interface {uplink}.0 admin-state",
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
      elif path_parts[-1] == 'system-name': # LLDP system name or port-id
        uplink = path_parts[3] # 'system lldp interface XYZ'
        peer_mac = path_parts[5]
        system_name = p['value']
      elif path_parts[-1] == 'port-id': # LLDP system name or port-id
        uplink = path_parts[3] # 'system lldp interface XYZ'
        peer_mac = path_parts[5]
        port_id = p['value']

    if system_name or port_id:
     response_actions += [
        {
         "set-cfg-path": {
             "path": f"interface {uplink} description",
             "value": f"{system_name} {port_id} MAC={peer_mac}",
         }
        },
     ]

    response = {"actions": response_actions, "persistent-data": { "reinvoked": reinvoked } }
    return json.dumps(response)
