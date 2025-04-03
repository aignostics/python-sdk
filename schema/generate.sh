#!/bin/sh
# run from platform root
docker run --rm -u "$(id -u):$(id -g)" -v "${PWD}:/local" openapitools/openapi-generator-cli:v7.10.0 generate \
    -i "/local/schema/api.json" \
    -g python \
    -o /local/codegen \
    -c /local/schema/config.json \
# Hotfix for https://github.com/OpenAPITools/openapi-generator/issues/18932
# create __init__.py files
ls codegen/aignx/codegen/models/ | awk -F . '/[a-z].py/ {print "from ."$1" import *"}' > codegen/aignx/codegen/models/__init__.py



##!/bin/sh
## obtain token
#TOKEN=$(poetry run python src/aignx/platform/_authentication.py)
## run from platform root
#docker run --rm -u "$(id -u):$(id -g)" -v "${PWD}:/local" openapitools/openapi-generator-cli:v7.10.0 generate \
#    -i "https://platform-dev.aignostics.com/openapi.json" \
#    -g python \
#    -o /local/codegen \
#    -c /local/schema/config.json \
#    -a "Authorization:Bearer $TOKEN"
## Hotfix for https://github.com/OpenAPITools/openapi-generator/issues/18932
#ls codegen/aignostics/codegen/models/ | awk -F . '/[a-z].py/ {print "from ."$1" import *"}' > codegen/aignostics/codegen/models/__init__.py
