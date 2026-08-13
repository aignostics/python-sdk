# Get started with the API

The Aignostics Platform API is a REST API over HTTPS, rooted at `https://platform.aignostics.com/api/v1`. Call it directly when you integrate the platform into another language or into an existing pipeline.

This guide covers one full workflow with plain HTTP calls — authenticate, analyze slides with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product), follow progress, download results. Examples use `curl` and `jq`. The complete contract is in the [API reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html).

```{include} ../partials/_get_started_signup.md
```

## Authenticate

Authentication is tied to a person, not to a machine. Every call acts as a user in an organization — each analysis records a `submitted_by` — so there is no anonymous access and no organization-wide API key. You need two things before your first call:

- **A platform account**, created by invitation from your organization's administrator (the section above). There is no self-service signup; if your organization is not on the platform yet, talk to `support@aignostics.com`.
- **A client ID**, the public identifier of your integration, registered for you in the platform's identity service. Ask `support@aignostics.com`; you cannot mint one yourself. There is no matching client *secret*, because a program running on a user's machine cannot keep one safe.

### How it works

The API never sees your password. It accepts a short-lived **access token**: a signed string saying who you are, which organization you belong to, and when it expires. Tokens are issued by Auth0, the identity service behind the platform — not by the API itself. You log in once in a browser, and from then on your program renews tokens on its own.

Six steps, of which the first four happen only once:

1. Your program asks Auth0 to start a login. Auth0 returns a link, a short **user code**, a secret **device code**, and how often to poll.
2. You open the link, log in as usual, and check that the code shown matches the one your program printed. That comparison is what stops someone else's program from being approved with your account.
3. Your program polls Auth0 with the device code. Until you finish, the answer is `authorization_pending`.
4. Auth0 hands over two tokens: an **access token** (the pass, short-lived) and a **refresh token** (a long-lived voucher that buys new access tokens without a browser).
5. Every API call carries the access token in an `Authorization: Bearer …` header.
6. When a call comes back `401`, the token expired: exchange the refresh token for a new one and retry.

This is the standard OAuth 2.0 Device Authorization Grant ([RFC 8628](https://datatracker.ietf.org/doc/html/rfc8628)), so most languages have a library that implements steps 1–4 for you — you supply the endpoints and client ID below.

### Step 1: start the login

```shell
CLIENT_ID=your-client-id

curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/device/code \
  -d client_id="$CLIENT_ID" \
  -d scope=offline_access \
  -d audience=https://aignostics-platform-samia | jq .
```

- `client_id` — your integration's public identifier.
- `audience` — which API the token should be valid for. `https://aignostics-platform-samia` is the Aignostics Platform.
- `scope=offline_access` — "also give me a refresh token". Leave it out and you get an access token that you cannot renew.

The response carries `verification_uri_complete` (the link for you), `user_code` (the code to compare), `device_code` (your program's secret handle), and `interval` (seconds between polls).

### Step 2: approve it, and collect the tokens

Open `verification_uri_complete` in a browser, log in, and confirm the code matches. Meanwhile, poll for the tokens — repeating every `interval` seconds while the response says `error: authorization_pending` (or `slow_down`, meaning you are asking too often):

```shell
curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=urn:ietf:params:oauth:grant-type:device_code \
  -d device_code="$DEVICE_CODE" \
  -d client_id="$CLIENT_ID" | jq .
```

Once you approve, the same call returns `access_token` and `refresh_token`. Store the refresh token as a secret — it is what makes the next step possible — and never log or commit either token.

### Step 3: renew without a browser

This is what CI and long-running services do whenever a call returns `401`:

```shell
curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=refresh_token \
  -d client_id="$CLIENT_ID" \
  -d refresh_token="$REFRESH_TOKEN" | jq -r .access_token
```

Because the refresh token belongs to the person who logged in, an unattended service acts as that user — and stops working if that account does. If you need a true machine identity, ask support; the two flows above are what the API supports today.

### Check that it worked

```shell
export TOKEN=your-access-token
export API=https://platform.aignostics.com/api/v1

curl -s "$API/me" -H "Authorization: Bearer $TOKEN" | jq .
```

`GET /v1/me` returns your user and your organization — including `aignostics_bucket_name`, the bucket used below.

### Hello world, end to end

Steps 1 to 3 and the check above, in one script. The only input is your client ID: it prints the link to open, waits while you approve it in the browser, and then confirms the API answers as you. It needs `curl` and `jq`.

```shell
#!/usr/bin/env bash
# hello_aignostics.sh — log in, then confirm the API answers as you.
# Usage: ./hello_aignostics.sh <client-id>
set -euo pipefail

CLIENT_ID="${1:?usage: $0 <client-id>}"
AUTH0="https://aignostics-platform.eu.auth0.com"
AUDIENCE="https://aignostics-platform-samia"
API="https://platform.aignostics.com/api/v1"

# 1. Ask Auth0 to start a login.
device=$(curl -sS -X POST "$AUTH0/oauth/device/code" \
  -d client_id="$CLIENT_ID" \
  -d scope=offline_access \
  -d audience="$AUDIENCE")

device_code=$(jq -r .device_code <<<"$device")
interval=$(jq -r .interval <<<"$device")

echo "Open this link:        $(jq -r .verification_uri_complete <<<"$device")"
echo "Confirm it shows code: $(jq -r .user_code <<<"$device")"

# 2. Poll until you approve it in the browser.
while :; do
  sleep "$interval"
  tokens=$(curl -sS -X POST "$AUTH0/oauth/token" \
    -d grant_type=urn:ietf:params:oauth:grant-type:device_code \
    -d device_code="$device_code" \
    -d client_id="$CLIENT_ID")
  case "$(jq -r '.error // "ok"' <<<"$tokens")" in
    ok) break ;;
    authorization_pending) ;;                        # not approved yet — keep waiting
    slow_down) interval=$((interval + 5)) ;;         # polling too fast — back off
    *) jq -r '"login failed: " + (.error_description // .error)' <<<"$tokens" >&2; exit 1 ;;
  esac
done

ACCESS_TOKEN=$(jq -r .access_token <<<"$tokens")
REFRESH_TOKEN=$(jq -r .refresh_token <<<"$tokens")
echo "Got an access token, and a refresh token to store as a secret (${#REFRESH_TOKEN} chars)."

# 3. Confirm the API answers as you.
curl -sS "$API/me" -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '{user: .user.email, organization: .organization.display_name, bucket: .organization.aignostics_bucket_name}'
```

```text
Open this link:        https://aignostics-platform.eu.auth0.com/activate?user_code=ABCD-EFGH
Confirm it shows code: ABCD-EFGH
Got an access token, and a refresh token to store as a secret (64 chars).
{
  "user": "you@your-organization.example",
  "organization": "Your Organization",
  "bucket": "your-aignostics-bucket"
}
```

That is a working integration. Keep the refresh token in your secret manager and every later run skips the browser entirely — Step 3 above is the whole renewal.

## Find out what the application expects

Two calls: one to see which applications your organization can run, one to read the contract of the version you intend to use.

```shell
curl -s "$API/applications" -H "Authorization: Bearer $TOKEN" | jq .
curl -s "$API/applications/he-tme/versions/1.3.0" -H "Authorization: Bearer $TOKEN" | jq .
```

The version response tells you exactly what to send in the next step:

- `input_artifacts[].name` — the name to give the file you submit for each slide (`input_slide` for Atlas H&E-TME).
- `input_artifacts[].metadata_schema` — a JSON Schema for the per-slide `metadata`. Validate against it locally instead of guessing; it is versioned with the application, so it is the one source of truth for required fields.
- `output_artifacts[]` — the result files a successful slide produces, with their MIME types.

## Give the platform access to your slides

The platform fetches each slide from a URL you provide, so that URL has to work without your credentials and keep working while the analysis is queued.

**The preferred method is to store the whole slide image in S3-compliant object storage** — AWS S3, Google Cloud Storage, or anything else speaking the S3 API — **and mint a signed URL for it**: a link with a temporary key in it, granting read access to that one object for a limited time. **Give it an expiry of at least seven days**, so the link outlives any queueing before your slide is picked up. Seven days is also the longest a SigV4 signature can live, so in practice that is the number to use.

**For convenience, we provide such storage.** Every organization gets a bucket on the platform, plus the credentials to upload objects into it and to sign download URLs from it. `GET /v1/me` returns all four values under `organization`:

| Field | What it is |
| --- | --- |
| `aignostics_bucket_name` | your organization's bucket |
| `aignostics_bucket_protocol` | the storage backend behind it — `gs`, Google Cloud Storage |
| `aignostics_bucket_hmac_access_key_id` | access key ID |
| `aignostics_bucket_hmac_secret_access_key` | secret access key |

The key pair is an ordinary S3 credential. Point any S3 client at the provider's S3-compatible endpoint — `https://storage.googleapis.com` for `gs` — sign with SigV4, and upload and sign as you would against AWS:

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

`boto3` and every other S3 client work the same way, given the endpoint and `s3v4` signing. Treat the secret like any other credential: it grants access to your organization's slides.

## Analyze your slides with Atlas H&E-TME

> ⚠️ **This example is specific to Atlas H&E-TME `1.3.0`.** Artifact names, required metadata, and outputs differ from one application to the next, and can change when a new version of the same application is released. Read the version's own contract first — the *Find out what the application expects* section above — rather than copying this payload verbatim.

One `POST` describes the whole analysis: which application, which version, and one entry per slide. The API calls those entries **items**, and the files attached to them **artifacts** — here a single input artifact, your slide. Give each item your own `external_id` so you can match results back to your records. Omit `version_number` to get the latest version, or pin it as below so a repeat analysis behaves identically.

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

A `201` returns `{"run_id": "..."}` — the API's handle for this analysis, and how you follow it below. Keep it. `custom_metadata` and `scheduling` are optional; check the [API reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) for the fields your API version accepts, since the request model grows over time.

A `422` means the request was rejected before anything ran, and the `detail` array names the offending field. The usual causes are metadata that does not satisfy `metadata_schema`, a download URL the platform cannot fetch, and two slides sharing an `external_id`.

## Follow the analysis

Ask about the analysis as a whole:

```shell
RUN_ID=your-run-id
curl -s "$API/runs/$RUN_ID" -H "Authorization: Bearer $TOKEN" | jq '{state, termination_reason, statistics}'
```

`state` moves `PENDING` → `PROCESSING` → `TERMINATED`. Read the two fields together, because **`TERMINATED` does not mean "succeeded"** — it only means the analysis is over:

- `termination_reason` says why it ended: `ALL_ITEMS_PROCESSED`, `CANCELED_BY_USER`, or `CANCELED_BY_SYSTEM`.
- `statistics` counts slides per outcome (`item_succeeded_count`, `item_user_error_count`, `item_system_error_count`, `item_skipped_count`, …). An analysis can reach `ALL_ITEMS_PROCESSED` with failed slides in it, so this is where you check.

Or ask about individual slides — `items`, in the API's words — which finish independently of each other:

```shell
curl -s "$API/runs/$RUN_ID/items?state=TERMINATED" -H "Authorization: Bearer $TOKEN" \
  | jq '.[] | {external_id, termination_reason, output_artifacts}'
```

Per slide, `termination_reason` is `SUCCEEDED`, `USER_ERROR` (something about your input — bad file, wrong metadata), `SYSTEM_ERROR` (ours; `error_code` and `error_message` say more), or `SKIPPED`. Poll at a sane interval; every 30 seconds is plenty for analyses that take minutes to hours.

## Download results

Every succeeded slide lists its result files under `output_artifacts`, each with a `download_url` you can fetch directly. Those URLs expire, so if one has gone stale, ask for a fresh one:

```shell
curl -s "$API/runs/$RUN_ID/artifacts/$ARTIFACT_ID/file" -H "Authorization: Bearer $TOKEN"
```

Since slides finish one by one, the efficient pattern is a loop: poll `/items`, download whatever is newly `SUCCEEDED`, and remember which files you already have.

> ⚠️ **Results are kept for 30 days**, counting from the day you started the analysis. After that they can no longer be fetched, and analyzing the slides again is the only way to get them back.

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

- **Retries.** Retry `5xx`, timeouts, and connection errors with exponential backoff and jitter; do not retry `4xx`, which will fail again. Four attempts backing off from 0.1 s to a 60 s cap is a sane default.
- **Idempotency.** `POST /v1/runs` is not idempotent — calling it twice analyzes your slides twice. Record the returned `run_id` before retrying, and use your `external_id` values with `GET /v1/runs` to detect an analysis you already submitted.
- **Caching.** Application and version metadata barely changes; the state of a running analysis changes constantly. Caching the former for a few minutes and the latter for seconds at most is a reasonable starting point.
- **Status.** Live platform status is at [status.platform.aignostics.com](https://status.platform.aignostics.com).

Questions about the API, or something behaving differently from this guide? Email `support@aignostics.com`.
