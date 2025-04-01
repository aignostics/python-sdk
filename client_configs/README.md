# Generate client
Run the `schema/generate.sh` shell script from the library root to generate
a new version of the client based on the `schema/api.json` schema.

# Run tests
```sh
# build docker image if necessary
docker build -t aignx-client .

# run tests in docker container (requires SA that has permissions to generate signed urls for sample slides)
docker run \
-v <local-path-to-sa-file>:/.config/google-sa.json \
-e GOOGLE_APPLICATION_CREDENTIALS=/.config/google-sa.json \
-e AIGNX_REFRESH_TOKEN="<your refresh token>" aignx-client
```
