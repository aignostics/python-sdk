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
