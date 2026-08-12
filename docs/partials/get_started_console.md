# Get started with Console

[Console](https://platform.aignostics.com) is the web interface of the Aignostics Platform. This guide walks you through running [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) — which analyzes the tumor microenvironment in H&E-stained tissue — on your own slides: you upload the slides with one command, then analyze them, review the results, and download them in your browser. You do not need any programming experience, and the setup takes about 15 minutes plus the time your slides take to upload. Results stay available in Console for 30 days.

**What you need:** a Mac, Windows (Windows 10 or later), or Linux (Ubuntu) computer, a web browser, a mobile phone for the login security step, and your whole slide images in a supported format — `.svs`, `.tif`, `.tiff`, or DICOM (`.dcm`). No slides at hand? [Step 4](#optional-get-an-example-slide) downloads a public example slide for you.

```{include} ../partials/_get_started_signup.md
```

## Upload your slides

### 1. Install the Aignostics Python SDK

The SDK runs in a terminal — a text window where you type commands. You only need it for the upload; everything after that happens in your browser. If a command does not work, see [Troubleshooting](#troubleshooting).

**On macOS or Linux:** open the **Terminal** app — on macOS, press `Cmd` + `Space`, type `Terminal`, and press `Enter`. Paste this command and press `Enter`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:** open **PowerShell** — click the Start menu, type `PowerShell`, and press `Enter`. Paste this command and press `Enter`:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

When it finishes, **close that window and open a new one.** Then check the install worked by pasting this command and pressing `Enter`:

```bash
uvx aignostics --help
```

The first run takes a minute to get ready. A list of command groups (`application`, `bucket`, `dataset`, and more) means the install worked. If you see an error instead, see [Troubleshooting](#troubleshooting).

### 2. Log in

In the same window, paste this command and press `Enter`:

```bash
uvx aignostics user login
```

A browser window opens at `platform.aignostics.com`. Enter your email and password, then the six-digit code from your authenticator app, and return to your terminal. You stay logged in for future sessions.

### 3. Prepare your slides for upload

Collect the slides you want to analyze in a single folder on your computer — for example a folder called `my-slides`. Subfolders are fine; they are preserved during upload.

Only files of the supported formats (`.svs`, `.tif`, `.tiff`, `.dcm`) can be analyzed. Other files in the folder are uploaded but will not appear as slides when you start the analysis.

### 4. (Optional) Get an example slide

To try the workflow before using your own data, download a public example slide — a TCGA lung adenocarcinoma case from the NCI Image Data Commons. Paste this command and press `Enter`:

```bash
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 data/
```

This takes a few minutes and creates the folder `data/tcga_luad`. Use it in place of your own folder in the next step.

### 5. Run the upload

Your organization has a private storage area on the Aignostics Platform — your **bucket**. Only you and the other members of your organization can see what is in it. Uploading a slide does not start an analysis; it just puts the slide where Console can find it.

Paste this command and press `Enter`, replacing `./my-slides` with the path to your folder:

```bash
uvx aignostics bucket upload ./my-slides
```

A progress bar appears, and the message `All files uploaded successfully!` tells you the upload is done.

**Keep the terminal open and your computer awake until then** — a single whole slide image is often 1–4 GB, so this can take a while. If the upload is interrupted, run the same command again.

Your slides are filed in a folder named after the user account you are logged in with on your computer, so they stay separate from your colleagues' slides. If that account is `jdoe`, then `my-slides/slide1.svs` becomes `jdoe/slide1.svs`. Run `whoami` if you are unsure what your account is called — you will need the folder name in the next step.

To list what arrived in your bucket:

```bash
uvx aignostics bucket find
```

## Analyze your slides with Atlas H&E-TME

### 6. Start the analysis

Open [platform.aignostics.com](https://platform.aignostics.com) and log in. Select **Analyze** → **My Application Runs** in the sidebar, then click **Create run** in the top right.

![The My Application Runs page with the Create run button in the top right](_static/console/01-analyze-create-run.png)

Fill in the **Create run** form:

- **Slides.** You see the contents of your organization's bucket. Use the breadcrumb (**Bucket » …**) to open the folder named after your computer account, then tick the slides you want to analyze. Your selection is listed under the table, so you can check it before you continue.

  ![The Create run form with the bucket contents listed and one slide ticked](_static/console/02-select-slides.png)

- **Version.** Pick the entry starting with `he-tme` — that is Atlas H&E-TME. Unless you need to reproduce an earlier analysis, use the highest version number.
- **Staining method.** Already fixed to `H&E` for Atlas H&E-TME, so there is nothing to choose.
- **Indication.** The disease your slides relate to — for the example slide, `Lung cancer`.
- **Tissue.** The tissue your slides were taken from — for the example slide, `Lung`.
- **Name.** A name of your choice, which makes the analysis easier to recognise later.

Your entries apply to every slide you selected, so all slides you analyze together must share the same staining method, indication, and tissue. Click **Run now** to start the analysis.

![The lower half of the Create run form with Version, Staining method, Indication, Tissue and Name filled in](_static/console/03-metadata.png)

Your analysis now appears at the top of **My Application Runs**.

### 7. Wait for results

The analysis runs on Aignostics servers, so you can close your browser and switch off your computer. How long it takes depends on the size and number of your slides — anywhere from a few minutes to several hours. Return to **My Application Runs** any time: the **Status** column shows how far the analysis has got, and **Completed** means it has finished.

### 8. Review your results in the viewer

Select your analysis in **My Application Runs** to open **Run Details**, then click a slide name to open it in the built-in viewer.

The **Overlays** panel on the right switches the results on and off on top of your slide: **Tissue Segmentation** colours the tissue regions that were found, **Cell Classification** colours the individual cells by type — with a legend of the cell types and a slider to make the colours more or less transparent — and **Tissue QC** shows areas flagged during quality control. Use the zoom buttons at the top right (`0.4×` to `40×`) to look at an area closely.

![A slide in the viewer with tissue and cell overlays switched on and the Overlays panel open](_static/console/04-viewer-overlays.png)

### 9. Download your results

On **Run Details**, click **Download Available Results** for all your slides, or use the download icon in the **Actions** column to get a single slide. For each slide you get the tissue regions that were found, the individual cells that were detected and classified by type, and a spreadsheet of measurements such as cell counts and densities.

![The Run Details page with the Download Available Results button and per-slide download icons](_static/console/05-download-results.png)

> ⚠️ **Results are kept for 30 days**, counting from the day you started the analysis. After that they can no longer be viewed or downloaded, and the only way to get them back is to analyze the slides again — so download whatever you want to keep in time.

**Congratulations** — you have run your first analysis, reviewed it in the viewer, and downloaded the results.

### (Optional) Clean up your bucket

Your slides stay in your bucket until you delete them, so analyzing the same slides again needs no new upload. Deletion works on patterns and is a dry run by default. Replace `jdoe` with your own folder name from step 5:

```bash
uvx aignostics bucket delete "jdoe/.*"              # shows how many objects would be deleted
uvx aignostics bucket delete "jdoe/.*" --no-dry-run # actually deletes them
```

> ⚠️ Deleting objects from your bucket cannot be undone. It does not affect results you have already downloaded.

```{include} ../partials/_invite_your_team.md
```

## Troubleshooting

<details>
<summary><strong>The install command failed</strong></summary>

First, make sure you copied the whole command, including everything from the start of the line to the end. Paste it again and press `Enter`.

If `uvx aignostics --help` did not work right after installing, close that terminal window, open a new one, and try again. The install command is only fully active in a freshly opened window.

If it still fails, copy the error message and email it to `support@aignostics.com`.

</details>

<details>
<summary><strong>My upload was interrupted</strong></summary>

Run the same `uvx aignostics bucket upload` command again. Files that were already uploaded are simply uploaded again and replace the earlier copy, so nothing is duplicated and nothing is lost.

If uploads are interrupted repeatedly, check that your computer does not go to sleep while the upload runs, and that your network connection is stable.

</details>

<details>
<summary><strong>My slides don't show up when I start an analysis</strong></summary>

1. Confirm the upload arrived by running `uvx aignostics bucket find --detail` and looking for your files.
2. Check that you are browsing the right folder in Console — the one named after your computer account, or the one you passed to `--destination-prefix`.
3. Check the file format. Only `.svs`, `.tif`, `.tiff`, and `.dcm` files can be analyzed. For DICOM slides, the complete set of `.dcm` files belonging to the slide must be uploaded together, so upload the whole folder rather than individual files.

If your slides are in the bucket, in the right format, and still not selectable, email `support@aignostics.com`.

</details>

<details>
<summary><strong>A slide failed, or the whole analysis failed</strong></summary>

Open the analysis on **My Application Runs** to see which slides failed — the **Status** column on **Run Details** shows the outcome per slide. Results for the slides that succeeded are unaffected — you can review and download them as usual.

A single failed slide usually points at the slide itself: an unsupported or incomplete file, or metadata that does not match the tissue on the slide. Check the file opens on your computer, then analyze that slide on its own.

If the whole analysis failed, or a slide fails again on a second attempt, email `support@aignostics.com` with the name or ID shown on **Run Details** and we will look into it.

</details>

<details>
<summary><strong>I can't log in, or my six-digit code is rejected</strong></summary>

The six-digit code from your authenticator app changes every 30 seconds. If yours was rejected, wait for the app to show a new code and enter that one promptly.

Make sure your phone's clock is set to update automatically — if it is wrong by even a minute, the codes will not match.

If you have forgotten your password, use the "Forgot password" link on the login page. If you still can't get in, email `support@aignostics.com`.

</details>

<details>
<summary><strong>I want to upload and analyze hundreds of slides</strong></summary>

The upload command handles large folders, but for larger cohorts you may prefer to script the whole workflow — including submission and result download — instead of clicking through Console for every batch. See [Get started with the CLI](https://aignostics.readthedocs.io/en/latest/get_started_cli.html) and [Get started with the Python Library](https://aignostics.readthedocs.io/en/latest/get_started_library.html), or email `support@aignostics.com` and we will help you choose an approach.

</details>

Still stuck? Email `support@aignostics.com` and describe what you were doing and what you saw.

<!-- Organizing uploads with --destination-prefix is deliberately left out of this guide: the default folder is enough
     for a first analysis, and the option is documented in the CLI reference. -->
