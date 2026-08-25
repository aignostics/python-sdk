# Get started with the API

The Aignostics Platform API is a REST API over HTTPS, rooted at `https://platform.aignostics.com/api/v1`. Call it directly when you integrate the platform into another language or into an existing pipeline.

This guide covers one full workflow with plain HTTP calls — authenticate, analyze slides with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product), follow progress, download results. Examples use `curl`, `jq`, and `openssl`. The complete contract is in the [API reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html).

```{include} ../partials/_get_started_signup.md
```

## Authenticate

Authentication is tied to a person, not to a machine: every call acts as a user in an organization, and each analysis records a `submitted_by`. There is no anonymous access and no organization-wide API key. You need two things:

- **A platform account**, created by invitation from your organization's administrator (the section above). If your organization is not on the platform yet, talk to `support@aignostics.com`.
- **A client ID**, the public identifier of your integration, together with a **redirect URI** registered against it. Ask `support@aignostics.com`; you cannot mint one yourself. There is no matching client *secret*, because a program running on a user's machine cannot keep one safe.

### How it works

The API never sees your password. It accepts a short-lived **access token** — issued by Auth0, the identity service behind the platform — which every call carries in an `Authorization: Bearer …` header. You log in once in a browser; from then on your program renews tokens itself with the long-lived **refresh token** it got alongside the first one. When a call returns `401`, renew and retry.

This is the standard OAuth 2.0 Authorization Code flow with PKCE ([RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)), so most languages have a library for the steps below — you supply the endpoints, client ID, and redirect URI.

PKCE — Proof Key for Code Exchange — is what makes this safe without a client secret. You invent a random secret, send only its fingerprint when you start the login, and reveal the secret when you redeem the result. Anyone who intercepts the authorization code cannot use it, because they do not have the secret.

### Step 1: create the PKCE pair

The `code_verifier` is your random secret and never leaves your machine. The `code_challenge` is its SHA-256 fingerprint, sent to Auth0 in the next step.

```shell
CLIENT_ID=your-client-id
REDIRECT_URI=http://localhost:8989/

CODE_VERIFIER=$(openssl rand -base64 60 | tr -d '\n=' | tr '+/' '-_')

CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" \
  | openssl dgst -binary -sha256 | openssl base64 | tr -d '\n=' | tr '+/' '-_')
```

Keep this shell open. Losing `CODE_VERIFIER` means starting again.

### Step 2: start the login

Print the authorization URL and open it in a browser.

```shell
echo "https://aignostics-platform.eu.auth0.com/authorize\
?response_type=code\
&client_id=$CLIENT_ID\
&redirect_uri=http%3A%2F%2Flocalhost%3A8989%2F\
&audience=https%3A%2F%2Faignostics-platform-samia\
&scope=offline_access\
&code_challenge=$CODE_CHALLENGE\
&code_challenge_method=S256"
```

- `client_id` — your integration's public identifier.
- `redirect_uri` — where Auth0 sends the browser afterwards. It must match a value registered against your client exactly, trailing slash included.
- `audience` — which API the token should be valid for. `https://aignostics-platform-samia` is the Aignostics Platform.
- `scope=offline_access` — "also give me a refresh token". Leave it out and you get an access token that you cannot renew.
- `code_challenge_method=S256` — the fingerprint is a SHA-256 hash, not the raw secret.

### Step 3: log in, and collect the tokens

Log in in the browser. Auth0 then redirects to your redirect URI with `?code=…` appended. If nothing is listening on that address the browser shows a connection error, which is expected — the code you need is in the address bar.

```shell
CODE=the-code-from-the-address-bar

curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=authorization_code \
  -d client_id="$CLIENT_ID" \
  -d code="$CODE" \
  -d code_verifier="$CODE_VERIFIER" \
  -d redirect_uri="$REDIRECT_URI" | jq .
```

The response carries `access_token` and `refresh_token`. Store the refresh token as a secret — it is what makes the next step possible — and never log or commit either token. The authorization code is single-use and short-lived, so redeem it promptly.

A real integration listens on the redirect URI instead of asking a person to copy the code. That is the only part of this flow that needs more than `curl`, and it is why the flow cannot run on a machine with no browser.

### Step 4: renew without a browser

This is what CI and long-running services do whenever a call returns `401`:

```shell
curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=refresh_token \
  -d client_id="$CLIENT_ID" \
  -d refresh_token="$REFRESH_TOKEN" | jq -r .access_token
```

Because the refresh token belongs to the person who logged in, an unattended service acts as that user — and stops working if that account does. If you need a true machine identity, ask support; these flows are what the API supports today.

### Check that it worked

```shell
export TOKEN=your-access-token
export API=https://platform.aignostics.com/api/v1

curl -s "$API/me" -H "Authorization: Bearer $TOKEN" | jq .
```

`GET /v1/me` returns your user and your organization — including `aignostics_bucket_name`, the bucket used below.

### Hello world, end to end

All of the above in one script, with your client ID as the only input. It needs `curl`, `jq`, and `openssl`.

```shell
#!/usr/bin/env bash
# hello_aignostics.sh — log in, then confirm the API answers as you.
# Usage: ./hello_aignostics.sh <client-id>
set -euo pipefail

CLIENT_ID="${1:?usage: $0 <client-id>}"
AUTH0="https://aignostics-platform.eu.auth0.com"
AUDIENCE="https://aignostics-platform-samia"
REDIRECT_URI="http://localhost:8989/"
API="https://platform.aignostics.com/api/v1"

# 1. Invent a secret, and derive the fingerprint Auth0 will see.
CODE_VERIFIER=$(openssl rand -base64 60 | tr -d '\n=' | tr '+/' '-_')
CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" \
  | openssl dgst -binary -sha256 | openssl base64 | tr -d '\n=' | tr '+/' '-_')

# 2. Send the user to Auth0, carrying the fingerprint.
authorize_url="$AUTH0/authorize?$(jq -rn \
  --arg client_id "$CLIENT_ID" \
  --arg redirect_uri "$REDIRECT_URI" \
  --arg audience "$AUDIENCE" \
  --arg challenge "$CODE_CHALLENGE" \
  '{response_type:"code", client_id:$client_id, redirect_uri:$redirect_uri,
    audience:$audience, scope:"offline_access",
    code_challenge:$challenge, code_challenge_method:"S256"}
   | to_entries | map("\(.key)=\(.value|@uri)") | join("&")')"

echo "Open this link:  $authorize_url"
echo "Your browser will fail to reach $REDIRECT_URI. That is expected."
read -r -p "Paste the 'code' from the address bar: " CODE

# 3. Redeem the code, revealing the secret.
tokens=$(curl -sS -X POST "$AUTH0/oauth/token" \
  -d grant_type=authorization_code \
  -d client_id="$CLIENT_ID" \
  -d code="$CODE" \
  -d code_verifier="$CODE_VERIFIER" \
  -d redirect_uri="$REDIRECT_URI")

if [ "$(jq -r '.error // "ok"' <<<"$tokens")" != "ok" ]; then
  jq -r '"login failed: " + (.error_description // .error)' <<<"$tokens" >&2
  exit 1
fi

ACCESS_TOKEN=$(jq -r .access_token <<<"$tokens")
REFRESH_TOKEN=$(jq -r .refresh_token <<<"$tokens")
echo "Got an access token, and a refresh token to store as a secret (${#REFRESH_TOKEN} chars)."

# 4. Confirm the API answers as you.
curl -sS "$API/me" -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '{user: .user.email, organization: .organization.display_name, bucket: .organization.aignostics_bucket_name}'
```

```text
Open this link:  https://aignostics-platform.eu.auth0.com/authorize?response_type=code&client_id=...
Your browser will fail to reach http://localhost:8989/. That is expected.
Paste the 'code' from the address bar: nB2f...
Got an access token, and a refresh token to store as a secret (64 chars).
{
  "user": "you@your-organization.example",
  "organization": "Your Organization",
  "bucket": "your-aignostics-bucket"
}
```

Keep the refresh token in your secret manager and later runs skip the browser entirely — Step 4 is the whole renewal.

## Find out what the application expects

Two calls: one to see which applications your organization can run, one to read the contract of the version you intend to use.

```shell
curl -s "$API/applications" -H "Authorization: Bearer $TOKEN" | jq .
curl -s "$API/applications/he-tme/versions/1.3.0" -H "Authorization: Bearer $TOKEN" | jq .
```

The version response tells you exactly what to send in the next step:

- `input_artifacts[].name` — the name to give the file you submit for each slide (`input_slide` for Atlas H&E-TME).
- `input_artifacts[].metadata_schema` — a JSON Schema for the per-slide `metadata`. Validate against it locally instead of guessing; it is versioned with the application, so it is the source of truth for required fields.
- `output_artifacts[]` — the result files a successful slide produces, with their MIME types.

## Give the platform access to your slides

The platform fetches each slide from a URL you provide, so that URL has to work without your credentials and keep working while the analysis is queued.

**The preferred method is to store the slide in S3-compliant object storage** — AWS S3, Google Cloud Storage, anything speaking the S3 API — **and mint a signed URL for it**: a link with a temporary key in it, granting read access to that one object for a limited time. **Give it at least seven days**, so it outlives any queueing. Seven days is also the longest a SigV4 signature can live, so that is the number to use.

**For convenience we provide that storage.** Every organization gets a bucket, plus credentials to upload objects into it and sign download URLs from it. `GET /v1/me` returns all four under `organization`:

| Field | What it is |
| --- | --- |
| `aignostics_bucket_name` | your organization's bucket |
| `aignostics_bucket_protocol` | the storage backend — `gs`, Google Cloud Storage |
| `aignostics_bucket_hmac_access_key_id` | access key ID |
| `aignostics_bucket_hmac_secret_access_key` | secret access key |

The key pair is an ordinary S3 credential: point any S3 client at the provider's S3-compatible endpoint — `https://storage.googleapis.com` for `gs` — and sign with SigV4.

```shell
export AWS_ACCESS_KEY_ID=your-aignostics-bucket-hmac-access-key-id
export AWS_SECRET_ACCESS_KEY=your-aignostics-bucket-hmac-secret-access-key
export BUCKET=your-aignostics-bucket-name
export GCS=https://storage.googleapis.com

# upload the slide
aws s3 --endpoint-url "$GCS" cp slide1.tiff "s3://$BUCKET/slide1.tiff"

# mint the signed URL to hand to the platform (7 days)
aws s3 --endpoint-url "$GCS" presign "s3://$BUCKET/slide1.tiff" --expires-in 604800
```

Treat the secret like any other credential: it grants access to your organization's slides.

## Analyze your slides with Atlas H&E-TME

> ⚠️ **This example is specific to Atlas H&E-TME `1.3.0`.** Artifact names, metadata, and outputs differ per application and change between versions, so read the version's own contract — *Find out what the application expects*, above — instead of copying this payload.

One `POST` describes the whole analysis: which application, which version, and one entry per slide. The API calls those entries **items**, and the files attached to them **artifacts** — here a single input artifact, your slide. Give each item your own `external_id` so you can match results back to your records. Omit `version_number` for the latest version, or pin it as below so a repeat analysis behaves identically.

```shell
curl -s -X POST "$API/runs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "he-tme",
    "version_number": "1.3.0",
    "items": [
      {
        "external_id": "slide_1",
        "input_artifacts": [
          {
            "name": "input_slide",
            "download_url": "https://example-bucket.storage.example.com/slide1.tiff?signature=...",
            "metadata": {
              "checksum_base64_crc32c": "64RKKA==",
              "media-type": "image/tiff",
              "width_px": 136223,
              "height_px": 87761,
              "resolution_mpp": 0.2628238,
              "staining_method": "H&E",
              "specimen": {"tissue": "LUNG", "disease": "LUNG_CANCER"}
            }
          }
        ]
      }
    ]
  }' | jq .
```

A `201` returns `{"run_id": "..."}` — the handle you follow the analysis with, so keep it. `custom_metadata` and `scheduling` are optional; the [API reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) lists what your API version accepts.

A `422` means nothing ran and `detail` names the offending field — usually metadata that fails `metadata_schema`, a download URL the platform cannot fetch, or two slides sharing an `external_id`.

## Follow the analysis

Ask about the analysis as a whole:

```shell
RUN_ID=your-run-id
curl -s "$API/runs/$RUN_ID" -H "Authorization: Bearer $TOKEN" | jq '{state, termination_reason, statistics}'
```

`state` moves `PENDING` → `PROCESSING` → `TERMINATED`. Read it together with the next field, because **`TERMINATED` does not mean "succeeded"** — only that the analysis is over:

- `termination_reason` says why it ended: `ALL_ITEMS_PROCESSED`, `CANCELED_BY_USER`, or `CANCELED_BY_SYSTEM`.
- `statistics` counts slides per outcome (`item_succeeded_count`, `item_user_error_count`, `item_system_error_count`, `item_skipped_count`, …). An analysis can reach `ALL_ITEMS_PROCESSED` with failed slides in it, so check here.

Or ask about individual slides — `items` — which finish independently:

```shell
curl -s "$API/runs/$RUN_ID/items?state=TERMINATED" -H "Authorization: Bearer $TOKEN" \
  | jq '.[] | {external_id, termination_reason, output_artifacts}'
```

Per slide, `termination_reason` is `SUCCEEDED`, `USER_ERROR` (your input — bad file, wrong metadata), `SYSTEM_ERROR` (ours; `error_code` and `error_message` say more), or `SKIPPED`. Every 30 seconds is a plenty frequent poll for analyses taking minutes to hours.

## Download results

Every succeeded slide lists its result files under `output_artifacts`, each with a `download_url` you can fetch directly. Those URLs expire; if one has gone stale, ask for a fresh one:

```shell
curl -s "$API/runs/$RUN_ID/artifacts/$ARTIFACT_ID/file" -H "Authorization: Bearer $TOKEN"
```

Since slides finish one by one, the efficient pattern is a loop: poll `/items`, download whatever is newly `SUCCEEDED`, and track what you already have.

> ⚠️ **Results are kept for 30 days** from the day you started the analysis. After that, re-analyzing the slides is the only way to get them back.

## List, cancel, or clean up

```shell
# list your analyses, filtered and paginated
curl -s "$API/runs?application_id=he-tme&page=1&page_size=20" -H "Authorization: Bearer $TOKEN" | jq .

# cancel an analysis that is still pending or processing
curl -s -X POST "$API/runs/$RUN_ID/cancel" -H "Authorization: Bearer $TOKEN"

# delete an analysis' results before the retention window ends
curl -s -X DELETE "$API/runs/$RUN_ID/artifacts" -H "Authorization: Bearer $TOKEN"
```

`GET /v1/runs` also filters by `application_version`, `external_id`, `custom_metadata`, and `for_organization`, and sorts via `sort`. To attach your own metadata after the fact, `PUT /v1/runs/{run_id}/custom-metadata` and `PUT /v1/runs/{run_id}/items/{external_id}/custom-metadata` expect the `custom_metadata_checksum` from your last read, so concurrent updates cannot silently overwrite each other.

## Conventions worth knowing

- **Retries.** Retry `5xx`, timeouts, and connection errors with exponential backoff and jitter; never `4xx`, which fails again. Four attempts backing off from 0.1 s to a 60 s cap is a sane default.
- **Idempotency.** `POST /v1/runs` is not idempotent — calling it twice analyzes your slides twice. Record the returned `run_id` before retrying, and match `external_id` values via `GET /v1/runs` to spot an analysis you already submitted.
- **Caching.** Application and version metadata barely changes; the state of a running analysis changes constantly. Caching the former for a few minutes and the latter for seconds at most is a reasonable starting point.
- **Status.** Live platform status is at [status.platform.aignostics.com](https://status.platform.aignostics.com).

Questions about the API, or something behaving differently from this guide? Email `support@aignostics.com`.
