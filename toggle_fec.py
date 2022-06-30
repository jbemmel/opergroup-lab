#
# Copyright(C) 2022 Nokia
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#
# For links that have FEC enabled, this script toggles the FEC state upon link failures
#

import json, time

# main entry function for event handler
def event_handler_main(in_json_str):
    # parse input json string passed by event handler
    in_json = json.loads(in_json_str)
    paths = in_json["paths"]
    options = in_json["options"]
    data = in_json["persistent-data"] if "persistent-data" in in_json else {}

    if options.get("debug") == "true":
       print( in_json_str )

    response_actions = []
    uplinks_seen = {}
    reinvoked = False
    save_fec = False
    for p in paths:
      path_parts = p['path'].split(' ')
      uplink = path_parts[1]

      if p['value'] == "up":
        uplinks_seen[ uplink ] = True
      elif p['value'] == "down":
        uplinks_seen[ uplink ] = False
      else:
        fec_state = p['value']
        prev_fec = data[ uplink ] if uplink in data else None

        # XXX assumes oper-state entries appear before FEC states
        if fec_state == "disabled":
          if prev_fec and uplink in uplinks_seen and uplinks_seen[uplink]:
            response_actions += [
             {
              "set-cfg-path": {
                 "path": f"interface {uplink} transceiver forward-error-correction",
                 "value": prev_fec,
              }
             },
            ]
            del data[ uplink ]
        else if uplink in uplinks_seen and uplinks_seen[uplink]:
          response_actions += [
             {
              "set-cfg-path": {
                 "path": f"interface {uplink} transceiver forward-error-correction",
                 "value": "disabled",
              }
             },
             {
              "reinvoke-with-delay": 1000 # After 1 second
             }
          ]
          data[ uplink ] = fec_state

    response = {"actions": response_actions, "persistent-data": data }
    return json.dumps(response)
