from openapi_core import OpenAPI
from pprint import pp

# Load from a file
petstore_spec = OpenAPI.from_file_path("petstore.json")
# Access components"
print(petstore_spec.check_spec)


# Load from a URL
#openapi_spec = OpenAPI.from_url("https://example.com/openapi.json")

# Access components
#print(f"Paths from URL: {openapi_spec.paths}")

