# Get started with the Python Library

The **Aignostics Python Library** lets you use the Aignostics Platform from your own scripts, notebooks, and pipelines. This guide takes you through the same first analysis as the Console guide — upload your slides, run [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) on them, follow the analysis, and download the results — in Python.

```{include} ../partials/_get_started_signup.md
```

## Upload your slides

### 1. Install the library

Add the Aignostics Python SDK to your project with [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/):

```shell
uv add aignostics
# or
pip install aignostics
```

### 2. Log in

Create a client. The first time, your browser opens for you to log in with your email, password, and the six-digit code from your authenticator app. You stay logged in for future sessions.

```python
from aignostics import platform

client = platform.Client()
print(client.me().user.email)
```

### 3. Upload your slides

The platform reads each slide from the bucket Aignostics provides for your organization, together with its checksum, size, resolution, staining method, tissue, and disease. The library computes the technical values from the files; the medical ones you set per slide — here the same for all slides in the folder.

```python
from pathlib import Path

from aignostics.application import Service as ApplicationService

APPLICATION = "he-tme"
slides = Path("my-slides")

metadata = ApplicationService.generate_metadata_from_source_directory(
    slides,
    APPLICATION,
    mappings=[".*:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"],
)


def remember_bucket_url(_bytes_uploaded: int, source: Path, bucket_url: str) -> None:
    for row in metadata:
        if row["external_id"] == str(source):
            row["platform_bucket_url"] = bucket_url


ApplicationService.application_run_upload(APPLICATION, metadata, upload_progress_callable=remember_bucket_url)
```

`mappings` match slide paths by regular expression, so a folder with mixed cases takes one mapping per group, for example `"lung/.*:tissue=LUNG,disease=LUNG_CANCER"`. If your slides are already in a cloud bucket, you can skip the upload and hand the platform signed URLs instead — see {doc}`Give the platform access to your slides <get_started_api>` in the API guide.

## Analyze your slides with Atlas H&E-TME

### 4. Start the analysis

```python
run = ApplicationService().application_run_submit_from_metadata(APPLICATION, metadata, note="My first analysis")
print(run.run_id)
```

Keep the `run_id`: it is how you find the analysis again later, in Python and in Console.

### 5. Follow the analysis

The analysis runs on Aignostics servers, so your script can exit and pick it up later with `client.run(run_id)`. The run's state goes `PENDING` → `PROCESSING` → `TERMINATED`; each slide has its own state and outcome.

```python
details = run.details()
print(details.state, details.termination_reason)

s = details.statistics
failed = s.item_user_error_count + s.item_system_error_count
print(f"{s.item_succeeded_count} of {s.item_count} slides succeeded, {failed} failed")

for item in run.results():
    print(item.external_id, item.state, item.termination_reason)
```

The analysis also appears under **My Application Runs** in [Console](https://platform.aignostics.com), where you can review the results in the viewer.

### 6. Download results

```python
run.download_to_folder("results")
```

This waits for the analysis to finish and downloads each slide's results as soon as they are ready: the tissue regions, the classified cells, and a spreadsheet of measurements such as cell counts and densities. Results are kept for 30 days, so download what you want to keep.

### 7. List, cancel, or clean up

```python
for r in client.runs.list(application_id=APPLICATION):
    print(r.run_id, r.details().state)

run = client.run("<run_id>")
run.cancel()  # stop an analysis that is still running
run.delete()  # remove a finished analysis and its results
```

Your slides stay in your bucket until you delete them; see {doc}`Clean up your bucket <get_started_console>` in the Console guide.

## Where to go next

- {doc}`Invite your team <invite_your_team>` — add colleagues so they can run analyses too.
- {doc}`Library reference <lib_reference>` — all public classes and functions.
- [Example notebooks](https://github.com/aignostics/python-sdk/tree/main/examples) — ready-to-use [Marimo](https://marimo.io/) and Jupyter notebooks in the repository.
