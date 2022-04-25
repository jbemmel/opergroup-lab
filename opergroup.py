import sys
import json

# list of downstream links to manage based on the current state of monitored uplinks
downlinks = ["interface ethernet-1/1"]

# count_up_uplinks returns the number of monitored uplinks that have oper-state=up
def count_up_uplinks(paths):
    up_cnt = 0
    for path in paths:
        if path.get("value", "down") == "up":
            up_cnt = up_cnt + 1
    return up_cnt


# required_up_uplinks returns the value of the `required-up-uplinks` option
def required_up_uplinks(options):
    return options.get("required-up-uplinks", 1)


# main entry function for event handler
def event_handler_main(in_json_str):
    # parse input json string passed by event handler
    in_json = json.loads(in_json_str)
    paths = in_json["paths"]
    options = in_json["options"]
    persist = in_json["persistent-data"]

    num_up_uplinks = count_up_uplinks(paths)
    downlinks_new_state = (
        "up" if required_up_uplinks(options) <= num_up_uplinks else "down"
    )
    last_state = persist.get("last-state", "down")

    if options.get("debug"):
        print(
            f"num of required up uplinks = {required_up_uplinks(options)}\n\
detected num of up uplinks = {num_up_uplinks}\n\
last state = {last_state}\n\
downlinks new state = {downlinks_new_state}\n"
        )

    response_persist = {"last-state": last_state}
    response_actions = {"actions": []}
    # return empty result if no state change is required
    if downlinks_new_state == last_state:
        return json.dumps(
            {"persistent-data": response_persist, "actions": response_actions}
        )

    for downlink in downlinks:
        response_actions["actions"].append(
            {"set-ephemeral-path": downlink, "value": downlinks_new_state}
        )

    response_persist = {"last-state": downlinks_new_state}
    response = {"persistent-data": response_persist, "actions": response_actions}
    if options.get("debug"):
        json_response = json.dumps(response, indent=4)
    else:
        json_response = json.dumps(response)
    return json_response


#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path":"interface ethernet-1/49 oper-status",
            "value":"up"
        },
        {
            "path":"interface ethernet-1/50 oper-status",
            "value":"up"
        }
    ],
    "options": {"required-up-uplinks":1, "debug":true},
    "persistent-data": {"last-state":"up"}
}
"""
    json_response = event_handler_main(example_in_json_str)
    print(json_response)


if __name__ == "__main__":
    sys.exit(main())
