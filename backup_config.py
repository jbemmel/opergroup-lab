#!/usr/libexec/platform-python
#
# Example implementation of a script that sends a backup of the config via scp
# upon changes. Assumes ssh keys are setup such that no passwords are required.
# Filename will include a timestamp reflecting the moment of last change
#
# Paths:
#   trigger - e.g. "system configuration last-change". Could include name(s) of users logged in at the time
# Options:
#   target: user, server and path where to scp config files to - e.g. backups@server.net:/backups
#   debug: (optional) flag to get debug output if set to 'true'
#
# Example config:
#    system {
#        event-handler {
#            instance backup-config-on-changes {
#                admin-state enable
#                upython-script backup_config.py
#                paths [
#                    "system configuration last-change",
#                    "system aaa authentication session * username"
#                ]
#                options {
#                    object target {
#                        value "backups@server.net:/backups"
#                    }
#                }
#            }
#        }
#    }
import json, time

# main entry function for event handler
def event_handler_main(in_json_str):
    # parse input json string passed by event handler
    in_json = json.loads(in_json_str)
    paths = in_json["paths"]
    options = in_json["options"]
    debug = options.get("debug") == "true"

    if debug:
       print( in_json_str )

    target = options.get("target", None)
    if target:
      timestamp = None
      for p in paths:
        if p['path']=="system configuration last-change":
          timestamp = p['value']
          break
        # elif p['path'] starts with "system aaa authentication session" ...

      if not timestamp:
        t = time.gmtime() # in UTC
        timestamp = '{:04d}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}_UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5])
      response = { "actions": [
        { "run-script": {
           "cmdline": f"ip netns exec srbase-mgmt /usr/bin/scp /etc/opt/srlinux/config.json {target}/config-{timestamp}.json"
          }
        }
      ] }
      return json.dumps(response)

    print( "Error: no 'target' defined" )
    return { "actions": [] }
