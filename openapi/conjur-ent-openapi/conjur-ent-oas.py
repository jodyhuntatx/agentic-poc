from openapi_core import OpenAPI

import yaml, json, jsonref

with open("conjur-ent-spec/openapi.yml", "r") as file:
    yaml_object = yaml.safe_load(file)
json_out = json.dumps(yaml_object, indent=2)
print(json_out)

# Load from a file
openapi_spec = OpenAPI.from_file_path("conjur-ent-spec/openapi.yml")
# Access components
print(f"Spec from file: {openapi_spec}")

# Load from a URL
#openapi_spec = OpenAPI.from_url("https://example.com/openapi.json")

# Access components
#print(f"Paths from URL: {openapi_spec.paths}")

