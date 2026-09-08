# Get started with Console

[Console](https://platform.aignostics.com) is the web interface of the Aignostics Platform. This guide takes you through your first analysis with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product), which profiles the tumor microenvironment on H&E slides: you upload your slides with one command, then start the analysis and download the results in your browser. It takes about 15 minutes plus upload time, and you don't need to know how to code.

You need a Mac, Windows, or Linux computer, a phone for the login code, and your slides as `.svs`, `.tif`, `.tiff`, or DICOM `.dcm` files.

```{include} ../partials/_get_started_signup.md
```

## Upload your slides

### 1. Install the Aignostics Python SDK

1. Open a terminal. On macOS, press `Cmd+Space`, type `Terminal`, and press `Enter`. On Windows, open the Start menu, type `PowerShell`, and press `Enter`.

2. Paste the install command for your system into the terminal and press Enter:

   ```bash
   # macOS or Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```powershell
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. Close the terminal and open a new one.

4. Check the install by running in your terminal:

   ```bash
   uvx aignostics --help
   ```

   You should see a list of commands.

### 2. Log in

1. Log in by running in your terminal:

   ```bash
   uvx aignostics user login
   ```

2. In the browser window that opens, log in with your email, password, and the six-digit code from your authenticator app.

You stay logged in for future sessions.

### 3. Upload your slides from your local disk

1. Put the slides you want to upload in one folder on your local disk.

2. Upload the folder by running the following, replacing `./my-slides` with its path:

   ```bash
   uvx aignostics bucket upload ./my-slides
   ```

3. Keep the terminal open until it prints `All files uploaded successfully!`. Slides are large, so this can take a while.

Your slides are now in your organization's private bucket, in a folder named after your computer's user account, for example `jdoe`.

### 4. (Optional) Copy slides from your own cloud bucket

If your slides are already stored in AWS S3, Azure Blob Storage, or Google Cloud Storage, you can copy them directly from there into your Aignostics bucket.

1. Install rclone, a tool for managing cloud storage, by following the [rclone installation guide](https://rclone.org/install/).

2. Log in to your own cloud provider account (`aws sso login`, `az login`, or `gcloud auth application-default login`).

3. Log in to your Aignostics account if you haven't already and get the access keys for your Aignostics bucket by running:

   ```bash
   uvx aignostics user whoami --no-mask-secrets
   ```

   Note `aignostics_bucket_name`, `aignostics_bucket_hmac_access_key_id`, and `aignostics_bucket_hmac_secret_access_key` — these are your access credentials. Treat them like a password.

4. Use the access credentials from the previous step to register both your own cloud bucket and your Aignostics bucket with rclone by running:

   ```bash
   rclone config create aignx s3 provider=GCS endpoint=https://storage.googleapis.com \
     access_key_id=<access key id> secret_access_key=<secret> no_check_bucket=true

   # and one of these, depending on your cloud:
   rclone config create mycloud s3 provider=AWS env_auth=true region=<your-region>
   rclone config create mycloud azureblob env_auth=true account=<your-storage-account>
   rclone config create mycloud "google cloud storage" env_auth=true
   ```

5. Copy your slides from your own bucket into a folder in your Aignostics bucket (for example, `jdoe`), by running:

   ```bash
   rclone copy mycloud:<your-bucket>/<slides-folder> aignx:<aignostics-bucket>/jdoe/ --progress
   ```

   Keep the process running and your machine awake until the copy finishes.

## Analyze your slides with Atlas H&E-TME

### 5. Start the analysis

1. Open [platform.aignostics.com](https://platform.aignostics.com) and select **Analyze** → **My Application Runs** in the sidebar.

2. Click **Create run** in the top right.

3. Under **Slides**, open your folder (**Bucket » jdoe**) and tick the slides to analyze.

   ```{figure} ../source/_static/console/02-select-slides.png
   :alt: The Create run form with the bucket contents listed and one slide ticked
   :figclass: guide-screenshot
   :target: ../source/_static/console/02-select-slides.png

   Pick your slides from the bucket. Click to view full size.
   ```

4. Under **Version**, pick the he-tme entry with the highest version number.

5. Under **Indication** and **Tissue**, pick what matches your slides, for example Lung cancer and Lung. They apply to all slides you selected.

6. Under **Name**, enter anything that helps you recognize the analysis later.

   ```{figure} ../source/_static/console/03-metadata.png
   :alt: The lower half of the Create run form with Version, Staining method, Indication, Tissue and Name filled in
   :figclass: guide-screenshot
   :target: ../source/_static/console/03-metadata.png

   The rest of the form, filled in for a lung slide. Click to view full size.
   ```

7. Click **Run now**.

Your analysis appears at the top of **My Application Runs**.

### 6. Wait for results

The analysis runs on Aignostics servers, so you can close your browser. It takes anywhere from minutes to hours depending on the number and size of your slides. The **Status** column on **My Application Runs** shows **Completed** when it is done.

### 7. Review your results in the viewer

1. Open your analysis and click a slide name to open it in the viewer.

2. Use the **Overlays** panel on the right to show the tissue regions, classified cells, and quality-control flags on top of your slide.

```{figure} ../source/_static/console/04-viewer-overlays.png
:alt: A slide in the viewer with tissue and cell overlays switched on and the Overlays panel open
:figclass: guide-screenshot
:target: ../source/_static/console/04-viewer-overlays.png

The viewer with tissue and cell overlays on. Click to view full size.
```

### 8. Download your results

On **Run Details**, click **Download Available Results**. For each slide you get the tissue regions, the classified cells, and a spreadsheet of measurements such as cell counts and densities. Results are kept for 30 days, so download what you want to keep.

```{figure} ../source/_static/console/05-download-results.png
:alt: The Run Details page with the Download Available Results button and per-slide download icons
:figclass: guide-screenshot
:target: ../source/_static/console/05-download-results.png

**Run Details** — download everything at once, or one slide at a time. Click to view full size.
```

That's it: you have analyzed your first slides with Atlas H&E-TME and have the results on your computer.

## Where to go next

- {doc}`Invite your team <invite_your_team>` — add colleagues so they can run analyses too.
- {doc}`Troubleshooting <troubleshooting>` — if something did not work as described.
- **Clean up your bucket** — your slides stay in your bucket until you delete them, so analyzing them again needs no new upload. Deletion cannot be undone but does not affect results you have downloaded. It is a dry run by default; replace `jdoe` with the folder your slides are in:

  ```bash
  uvx aignostics bucket delete "jdoe/.*"              # shows what would be deleted
  uvx aignostics bucket delete "jdoe/.*" --no-dry-run # deletes it
  ```

<!-- Organizing uploads with --destination-prefix is deliberately left out of this guide: the default folder is enough
     for a first analysis, and the option is documented in the CLI reference. -->
