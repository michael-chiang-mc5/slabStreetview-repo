from django.shortcuts import render
import json
from bson import json_util

def serialize_json(json_dict):
    return json.dumps(json_dict, default=json_util.default)

def deserialize_json_string(str):
    return json.loads(str, object_hook=json_util.object_hook)
