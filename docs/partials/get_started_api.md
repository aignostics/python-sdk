# Get started with the API

The Aignostics Platform API is a REST API over HTTPS, rooted at `https://platform.aignostics.com/api/v1`. Call it directly when you integrate the platform into another language or into an existing pipeline.

This guide covers one full workflow with plain HTTP calls — authenticate, analyze slides with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product), follow progress, download results. Examples use `curl` and `jq`. The complete contract is in the [API Explorer](https://aignostics.readthedocs.io/en/latest/api_explorer_v1.html).

```{include} ../partials/_get_started_signup.md
```

## Upload your slides

### 1. Authenticate

Authentication is tied to a person, not to a machine: every call acts as a user in an organization, and each analysis records a `submitted_by`. There is no anonymous access and no organization-wide API key. You need two things:

- **A platform account**, created by invitation from your organization's administrator (the section above). If your organization is not on the platform yet, talk to `support@aignostics.com`.
- **A client ID**, the public identifier of your integration. Ask `support@aignostics.com`; you cannot mint one yourself. There is no matching client *secret*, because a program running on a user's machine cannot keep one safe.

#### How it works

The API never sees your password. It accepts a short-lived **access token** — issued by Auth0, the identity service behind the platform — which every call carries in an `Authorization: Bearer …` header. You log in once in a browser; from then on your program renews tokens itself with the long-lived **refresh token** it got alongside the first one. When a call returns `401`, renew and retry.

This is the standard OAuth 2.0 Device Authorization Grant ([RFC 8628](https://datatracker.ietf.org/doc/html/rfc8628)), so most languages have a library for the three steps below — you supply the endpoints and client ID.

#### Start the login

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

#### Approve it, and collect the tokens

Open `verification_uri_complete` in a browser, log in, and check the code shown matches the `user_code` your program printed — that comparison is what stops someone else's program from being approved with your account. Meanwhile, poll for the tokens every `interval` seconds while the response says `error: authorization_pending` (or `slow_down`, meaning you are asking too often):

```shell
curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=urn:ietf:params:oauth:grant-type:device_code \
  -d device_code="$DEVICE_CODE" \
  -d client_id="$CLIENT_ID" | jq .
```

Once you approve, the same call returns `access_token` and `refresh_token`. Store the refresh token as a secret — it is what makes the next step possible — and never log or commit either token.

#### Renew without a browser

This is what CI and long-running services do whenever a call returns `401`:

```shell
export TOKEN=$(curl -s -X POST https://aignostics-platform.eu.auth0.com/oauth/token \
  -d grant_type=refresh_token \
  -d client_id="$CLIENT_ID" \
  -d refresh_token="$REFRESH_TOKEN" | jq -r .access_token)
```

An access token lasts about an hour. When it expires, calls return `401` with the plain-text body `Jwt is expired` — so a command that pipes into `jq` fails with `parse error: Invalid numeric literal` instead. Either way, run the renewal above and retry.

Because the refresh token belongs to the person who logged in, an unattended service acts as that user — and stops working if that account does. If you need a true machine identity, ask support; these flows are what the API supports today.

#### Check that it worked

```shell
export API=https://platform.aignostics.com/api/v1

curl -s "$API/me" -H "Authorization: Bearer $TOKEN" | jq .
```

`GET /v1/me` returns your user and your organization — including `aignostics_bucket_name`, the bucket used below.

#### Hello world, end to end

All of the above in one script, with your client ID as the only input. It needs `curl` and `jq`. Save it as `hello_aignostics.sh`, then run it:

```shell
chmod +x hello_aignostics.sh
./hello_aignostics.sh your-client-id
```

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

if jq -e .error <<<"$device" >/dev/null; then             # e.g. a mistyped client ID
  jq -r '"login failed: " + (.error_description // .error)' <<<"$device" >&2; exit 1
fi

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

# 3. Keep the refresh token, readable only by you, for the renewal call above.
(umask 077; printf '%s' "$REFRESH_TOKEN" > "$HOME/.aignostics_refresh_token")
echo "Saved it to ~/.aignostics_refresh_token."

# 4. Confirm the API answers as you.
curl -sS "$API/me" -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '{user: .user.email, organization: .organization.display_name, bucket: .organization.aignostics_bucket_name}'
```

```text
Open this link:        https://aignostics-platform.eu.auth0.com/activate?user_code=ABCD-EFGH
Confirm it shows code: ABCD-EFGH
Got an access token, and a refresh token to store as a secret (64 chars).
Saved it to ~/.aignostics_refresh_token.
{
  "user": "you@your-organization.example",
  "organization": "Your Organization",
  "bucket": "your-aignostics-bucket"
}
```

Later sessions skip the browser entirely — load the saved token and run the renewal call above:

```shell
export CLIENT_ID=your-client-id
export API=https://platform.aignostics.com/api/v1
REFRESH_TOKEN=$(cat ~/.aignostics_refresh_token)
```

On a shared machine or in CI, keep the refresh token in your secret manager instead of a file.

### 2. Find out what the application expects

Two calls: one to see which applications your organization can run, one to read the contract of the version you intend to use.

```shell
curl -s "$API/applications" -H "Authorization: Bearer $TOKEN" | jq .
curl -s "$API/applications/he-tme/versions/2.0.1" -H "Authorization: Bearer $TOKEN" | jq .
```

The first call shows each application's `latest_version`; use that number in the second.

The version response tells you exactly what to send in step 4:

- `input_artifacts[].name` — the name to give the file you submit for each slide (`whole_slide_image` for Atlas H&E-TME).
- `input_artifacts[].metadata_schema` — a JSON Schema for the per-slide `metadata`. Validate against it locally instead of guessing; it is versioned with the application, so it is the source of truth for required fields.
- `output_artifacts[]` — the result files a successful slide produces, with their MIME types.

For Atlas H&E-TME, only three metadata fields are required — the rest (`width_px`, `height_px`, `resolution_mpp`, `media_type`) are optional:

| Field | Value |
| --- | --- |
| `checksum_base64_crc32c` | the slide file's CRC32C checksum, base64-encoded — step 3 shows how to get it |
| `staining_method` | `H&E` |
| `specimen` | a tissue and disease pair, for example `{"tissue": "BLADDER", "disease": "BLADDER_CANCER"}`. The schema's `$defs` list the valid pairs. |

### 3. Give the platform access to your slides

The platform fetches each slide from a URL you provide, so that URL has to work without your credentials and keep working while the analysis is queued.

**The preferred method is to store the slide in S3-compliant object storage** — AWS S3, Google Cloud Storage, anything speaking the S3 API — **and mint a signed URL for it**: a link with a temporary key in it, granting read access to that one object for a limited time. **Give it at least seven days**, so it outlives any queueing. Seven days is also the longest a SigV4 signature can live, so that is the number to use.

**If your slides are already in your own S3 or Google Cloud Storage bucket**, mint the signed URLs there with your own credentials and skip the upload below.

**If your slides are on your own disk, upload them to the bucket we provide.** Every organization gets a bucket, plus credentials to upload objects into it and sign download URLs from it. `GET /v1/me` returns all four under `organization`:

| Field | What it is |
| --- | --- |
| `aignostics_bucket_name` | your organization's bucket |
| `aignostics_bucket_protocol` | the storage backend — `gs`, Google Cloud Storage |
| `aignostics_bucket_hmac_access_key_id` | access key ID |
| `aignostics_bucket_hmac_secret_access_key` | secret access key |

The key pair is an ordinary S3 credential: point any S3 client at the provider's S3-compatible endpoint — `https://storage.googleapis.com` for `gs` — and sign with SigV4. The examples use the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Load the credentials straight from `GET /v1/me`:

```shell
ME=$(curl -s "$API/me" -H "Authorization: Bearer $TOKEN")
export BUCKET=$(jq -r .organization.aignostics_bucket_name <<<"$ME")
export AWS_ACCESS_KEY_ID=$(jq -r .organization.aignostics_bucket_hmac_access_key_id <<<"$ME")
export AWS_SECRET_ACCESS_KEY=$(jq -r .organization.aignostics_bucket_hmac_secret_access_key <<<"$ME")
unset ME
export AWS_DEFAULT_REGION=auto
export GCS=https://storage.googleapis.com

# AWS CLI 2.23 and later add checksums that Google Cloud Storage rejects on large uploads
# ("SignatureDoesNotMatch"); send them only where required.
export AWS_REQUEST_CHECKSUM_CALCULATION=when_required
export AWS_RESPONSE_CHECKSUM_VALIDATION=when_required
```

Then, for each slide:

```shell
# upload the slide
aws s3 --endpoint-url "$GCS" cp slide1.tiff "s3://$BUCKET/slide1.tiff"

# mint the signed URL to hand to the platform (7 days)
URL=$(aws s3 --endpoint-url "$GCS" presign "s3://$BUCKET/slide1.tiff" --expires-in 604800)

# read the checksum Google Cloud Storage computed on upload; this also proves the URL works
CHECKSUM=$(curl -sI -r 0-0 "$URL" | tr -d '\r' | grep -i '^x-goog-hash: crc32c=' | cut -d= -f2-)
echo "$CHECKSUM"
```

`CHECKSUM` is the `checksum_base64_crc32c` for step 4, for example `O5m1XA==`. If it comes back empty, the URL does not work — check the bucket path.

If your own storage does not report a CRC32C checksum, compute it locally (`pip install google-crc32c`):

```shell
python3 -c 'import sys, base64, google_crc32c
c = google_crc32c.Checksum()
with open(sys.argv[1], "rb") as f:
    for block in iter(lambda: f.read(8 << 20), b""): c.update(block)
print(base64.b64encode(c.digest()).decode())' slide1.tiff
```

Treat the secret like any other credential: it grants access to your organization's slides.

## Analyze your slides with Atlas H&E-TME

### 4. Start the analysis

> ⚠️ **This example is specific to Atlas H&E-TME `2.0.1`.** Artifact names, metadata, and outputs differ per application and change between versions, so read the version's own contract — *Find out what the application expects*, above — instead of copying this payload.

One `POST` describes the whole analysis: which application, which version, and one entry per slide. The API calls those entries **items**, and the files attached to them **artifacts** — here a single input artifact, your slide. Give each item your own `external_id` so you can match results back to your records. Omit `version_number` for the latest version, or pin it as below so a repeat analysis behaves identically.

`jq` builds the request from the `URL` and `CHECKSUM` of step 3, so the signed URL's special characters need no escaping:

```shell
BODY=$(jq -n --arg url "$URL" --arg checksum "$CHECKSUM" '{
  application_id: "he-tme",
  version_number: "2.0.1",
  items: [{
    external_id: "slide_1",
    input_artifacts: [{
      name: "whole_slide_image",
      download_url: $url,
      metadata: {
        checksum_base64_crc32c: $checksum,
        staining_method: "H&E",
        specimen: {tissue: "LUNG", disease: "LUNG_CANCER"}
      }
    }]
  }]
}')

curl -s -X POST "$API/runs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq .
```

**One analysis can hold all your slides:** add one entry to `items` per slide, each with its own `external_id`, `download_url`, and checksum.

A `201` returns `{"run_id": "..."}` — the handle you follow the analysis with, so keep it. `custom_metadata` and `scheduling` are optional; the [API Explorer](https://aignostics.readthedocs.io/en/latest/api_explorer_v1.html) lists what your API version accepts.

A `422` means nothing ran and `detail` names the offending field — usually metadata that fails `metadata_schema`, a download URL the platform cannot fetch, or two slides sharing an `external_id`.

### 5. Follow the analysis

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

### 6. Download results

Every succeeded slide lists its result files under `output_artifacts`. Fetch each one through `GET /v1/runs/{run_id}/artifacts/{output_artifact_id}/file`: it answers with a redirect to a short-lived signed link, so let `curl` follow it with `-L`.

Artifact names look like `readout_generation:cell_readouts` — a processing step and a file name, with no file extension. This loop downloads every result of every succeeded slide into `results/<external_id>/<step>/<file>`:

```shell
curl -s "$API/runs/$RUN_ID/items?state=TERMINATED" -H "Authorization: Bearer $TOKEN" \
  | jq -r '.[] | select(.termination_reason == "SUCCEEDED") | .external_id as $slide
           | .output_artifacts[] | [$slide, .output_artifact_id, .name] | @tsv' \
  | while IFS=$'\t' read -r slide id name; do
      curl -sSL --create-dirs -o "results/$slide/${name//://}" \
        "$API/runs/$RUN_ID/artifacts/$id/file" -H "Authorization: Bearer $TOKEN" \
        && echo "downloaded $slide/${name//://}"
    done
```

The version's `output_artifacts[]` from step 2 gives each name's `mime_type` — CSV, GeoJSON, Parquet, or TIFF for Atlas H&E-TME — so you know which extension to add.

Since slides finish one by one, the efficient pattern is a loop: poll `/items`, download whatever is newly `SUCCEEDED`, and track what you already have.

> ⚠️ **Results are kept for 30 days** from the day you started the analysis. After that, re-analyzing the slides is the only way to get them back.

### 7. List, cancel, or clean up

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

## Where to go next

- {doc}`Invite your team <invite_your_team>` — add colleagues so they can run analyses too.
- {doc}`API Explorer <api_explorer_v1>` — all operations and parameters.
