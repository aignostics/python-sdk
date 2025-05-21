# Runbook for Python SDK / CLI Spike:

1. Install the Python SDK by copy&pasting the script shown on
   https://platform.aignostics.com to your terminal. You should see
   "Installation complete"
2. Download the `aignx-gcp-credentials.json` into your Downloads folder. Then
   execute
   `mv ~/Downloads/aignx-gcp-credentials.json ~/.aignostics/aignx-gcp-credentials.json`
3. Execute

```shell
mkdir ~/heta
curl https://raw.githubusercontent.com/aignostics/python-sdk/.../user_slide.csv ...
```

4. Check the metadata by opening `~/heta/user_slide.csv` in Excel or another
   program

5. Run the following commands in your terminal, step by step:

```shell
# Goto folder we created in step 4
cd ~/heta

# Should print installation complete
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics system install 

# List all available applications, abbreviated form
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application list 

# List all available applications, more details
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application list --verbose

# Describe the details of the HETA application
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application describe --application-id h-e-tme

# Submit a run given the meta in user_slide.csv
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run submit --application-version-id h-e-tme:v0.36.0 --source user_slide.csv

# List all runs you triggered, abbreviated form - should be one entry now
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run list 

# List all runs you triggered, more details - should still be one entry only
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run list --verbose

# Show details of the run. You will have to replace <output of previous command> with the application run id output when submitting the run or listing runs submitted.
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run describe --run-id <output of previous command> 

# Let's cancel the run - replace the <output of previous command> with the application run id output when submitting the run before.
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally application run cancel --run-id <output of previous command>

# List all runs you triggered again. The run should be marked as canceled now.
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run list 

# Submit a run given the meta in user_slide.csv again
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run submit --application-version-id h-e-tme:v0.36.0 --source user_slide.csv

# Download the results. This waits for the processing to complete, which takes half an hour or so. Replace the <output of previous command> with the application run id output when submitting the run before.
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run result download --run-id <output of previous command> --destination .

# List all runs you triggered, abbreviated form - one rone should be marked as canceled, the other as completed
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics application run list

# Show System Info
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics aignostics system info 

# Show syste info in GUI
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally aignostics gui
```

# HMAC

```
uv run aignostics application upload --source-file data/in/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff
```

### Bugs detected

- Pagination of runs fails when there is 40 runs
- There is a large number of runs running but not progressing, and not
  cancelable (exception NotCancelleable when trying to cancel.)
- Regulatory class missing in H&E App
- Input artifact mime type should be a list, e.g. to indicate image/tiff and
  application/dicom support
- Invalid, was Test / Dummy App: Results are zeroes (csv), and empty (heatmaps)

### Requests to improve

- Message of ValueError "X is greater then Y supported" does not indicate the
  attribute this refers to - in this case mpp
- Sort runs by triggered date, descending -> self
- Allow to retrieve progress
- Get info about completion date of a run
- Get incremental progress info
- Get info in list of runs, so i don't have to blast to fetch details just to
  get triggered date -> self
- Get info about organisation name, not only this interesting organisation id.

## Feature requests

- whoami call, indicating user id, organisation id, user full name, organisation
  full name
- possiblity to delete runs

# Tests
- ANN Slide

# Edit .env

notepad .aignostics/.env

# Strangeness, gone away suddenly.

                                                                         │
                             │ C:\Users\helmut\AppData\Roaming\uv\python\cpython-3.13.3-windows-x86_64- │
                             │ none\Lib\urllib\request.py:1322 in do_open                               │
                             │                                                                          │
                             │   1319 │   │   │   │   h.request(req.get_method(), req.selector, req.dat │
                             │   1320 │   │   │   │   │   │     encode_chunked=req.has_header('Transfer │
                             │   1321 │   │   │   except OSError as err: # timeout error                │
                             │ ❱ 1322 │   │   │   │   raise URLError(err)                               │
                             │   1323 │   │   │   r = h.getresponse()                                   │
                             │   1324 │   │   except:                                                   │
                             │   1325 │   │   │   h.close()                                             │
                             ╰──────────────────────────────────────────────────────────────────────────╯
                             URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify
                             failed: unable to get local issuer certificate (_ssl.c:1028)>

                             The above exception was the direct cause of the following exception:

                             ╭─────────────────── Traceback (most recent call last) ────────────────────╮
                             │ C:\Users\helmut\AppData\Local\uv\cache\archive-v0\McrATamrJ1LIUCorgomc_\ │
                             │ Lib\site-packages\aignostics\platform\_authentication.py:114 in          │
                             │ verify_and_decode_token                                                  │
                             │                                                                          │
                             │   111 │   jwk_client = jwt.PyJWKClient(settings().jws_json_url)          │
                             │   112 │   try:                                                           │
                             │   113 │   │   # Get the public key from the JWK client                   │
                             │ ❱ 114 │   │   key = jwk_client.get_signing_key_from_jwt(token).key       │
                             │   115 │   │   # Verify and decode the token using the public key         │
                             │   116 │   │   return t.cast(                                             │
                             │   117 │   │   │   "dict[str, str]",                                      │
                             │                                                                          │
                             │ C:\Users\helmut\AppData\Local\uv\cache\archive-v0\McrATamrJ1LIUCorgomc_\ │
                             │ Lib\site-packages\jwt\jwks_client.py:115 in get_signing_key_from_jwt     │
                             │                                                                          │
                             │   112 │   def get_signing_key_from_jwt(self, token: str) -> PyJWK:       │
                             │   113 │   │   unverified = decode_token(token, options={"verify_signatur │
                             │   114 │   │   header = unverified["header"]                              │
                             │ ❱ 115 │   │   return self.get_signing_key(header.get("kid"))             │
                             │   116 │                                                                  │
                             │   117 │   @staticmethod                                                  │
                             │   118 │   def match_kid(signing_keys: List[PyJWK], kid: str) -> Optional │
                             │                                                                          │
                             │ C:\Users\helmut\AppData\Local\uv\cache\archive-v0\McrATamrJ1LIUCorgomc_\ │
                             │ Lib\site-packages\jwt\jwks_client.py:97 in get_signing_key               │
                             │                                                                          │
                             │    94 │   │   return signing_keys                                        │
                             │    95 │                                                                  │
                             │    96 │   def get_signing_key(self, kid: str) -> PyJWK:                  │

# setup the `.env` file with your client credentials

'''shell

```
# install the Aignostics Python SDK

uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally
--with marimo aignostics system install uvx --from
git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally --with marimo
aignostics --help ``
```

# TODOs (Helmut)

## General
- Ruff, Mypy
- GPG

## Bugs or Issues

- Behavior if no run
- Reset in submission to back, then forward
- lung / other validate
- Pin Versions, see 0.10.0
- Proxy for Windows
- File Selection on Linux
- Detection of Staining
- Support large images for preview (Image size (3217677886 pixels) exceeds limit of 178956970 pixels, could be decompression bomb DOS attack)
# Features
- QuPath Integration
- Single File Selection
- Offline Mode
- Runs / Filter by application, status, date


# Proxy with HTTP Toolkit (https://httptoolkit.com/) on MacOS
export HTTP_PROXY=http://localhost:8000
export HTTPS_PROXY=http://localhost:8000
export NO_PROXY=localhost,127.0.0.1,.charite.de,charite.de
export REQUESTS_CA_BUNDLE=~/Library/Preferences/httptoolkit/ca.pem
export SSL_CERT_FILE=~/Library/Preferences/httptoolkit/ca.pem
git config --global http.sslCAInfo ~/Library/Preferences/httptoolkit/ca.pem

unset HTTP_PROXY
unset HTTPS_PROXY
unset REQUESTS_CA_BUNDLE
unset SSL_CERT_FILE
git config --global --unset http.sslCAInfo 
