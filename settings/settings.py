import json 

with open("./settings/config.json", "r") as fp:
    config: dict = json.loads(fp.read())