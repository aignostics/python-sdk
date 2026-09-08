## Troubleshooting

**I can't find my invitation email.** Check your spam folder. If it isn't there either, ask your organization's administrator to invite you, or email `support@aignostics.com`.

**The install command failed.** Make sure you copied the whole line, then paste it again. If `uvx aignostics --help` fails right after installing, close the terminal and try again in a new one — the install is only active in a fresh window, and the first run takes a minute to get ready. If it still fails, email the error message to `support@aignostics.com`.

**What is a bucket, and who can see my slides?** Your bucket is your organization's private storage area on the Aignostics Platform. Only members of your organization can see what is in it. Uploading a slide does not start an analysis; it just puts the slide where Console can find it.

**Which folder are my slides in?** The folder is named after the user account on your computer — run `whoami` in the terminal if you are unsure. `uvx aignostics bucket find` lists everything in your bucket. Subfolders inside your upload folder are preserved.

**I don't see a progress bar during the upload.** The progress bar only fits in a wide terminal window; otherwise you see the per-file messages alone. The upload is running normally.

**My upload was interrupted.** Run the same `uvx aignostics bucket upload` command again. Files already uploaded are replaced, so nothing is duplicated or lost. If it keeps happening, make sure your computer does not go to sleep and your network connection is stable.

**My slides don't show up when I start an analysis.** Run `uvx aignostics bucket find --detail` to confirm they arrived, and check you are browsing the right folder in Console. Only `.svs`, `.tif`, `.tiff`, and `.dcm` files appear as slides; other files are uploaded but not shown. For DICOM, the complete set of `.dcm` files belonging to a slide must be uploaded together, so upload the whole folder. If your slides are there, in the right format, and still not selectable, email `support@aignostics.com`.

**The bucket keys are empty.** If `uvx aignostics user whoami` shows no keys under organization, your organization is not set up for direct bucket access yet. Email support@aignostics.com.

**A slide failed, or the whole analysis failed.** The **Status** column on **Run Details** shows the outcome per slide; results for slides that succeeded are unaffected. A single failed slide usually points at the file itself — unsupported or incomplete, or metadata that does not match the tissue. Check the file opens on your computer, then analyze it on its own. If the whole analysis failed, or a slide fails twice, email `support@aignostics.com` with the name or ID shown on **Run Details**.

**I can't log in, or my six-digit code is rejected.** The code changes every 30 seconds — wait for a new one and enter it promptly. Make sure your phone's clock is set automatically; if it is off by a minute, the codes will not match. Use "Forgot password" on the login page if needed, and email `support@aignostics.com` if you still can't get in.

**I want to analyze hundreds of slides.** For larger cohorts you may prefer to script the whole workflow instead of clicking through Console for every batch. If you copy slides from your own cloud with rclone, run it on a virtual machine in that cloud rather than on your laptop — the data passes through the machine running rclone. See [Get started with the Python Library](https://aignostics.readthedocs.io/en/latest/get_started_library.html) or [Get started with the API](https://aignostics.readthedocs.io/en/latest/get_started_api.html), or email `support@aignostics.com` and we will help you choose.

Still stuck? Email `support@aignostics.com` and describe what you were doing and what you saw.
