# Setup service connections

## Reporting code coverage via CodeCov (codecov.io)

1. Sign-Up at https://app.codecov.io/
2. Configure via https://app.codecov.io/gh/aignostics
3. Select (o) Repository token. Copy value of `CODECOV_TOKEN` into your clipboard
4. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and create a new repository secret called `CODECOV_TOKEN`, pasting the token from your clipboard as value
5. Re-run the `CI / test` GitHub job in case you tried before and it failed as Codecov was not yet wired up

## Analyzing code quality and security analysis via SonarQube cloud (sonarcloud.io)

1. Sign-Up at https://sonarcloud.io
2. Grant access to your new repo via https://github.com/settings/installations -> Configure
3. Goto https://sonarcloud.io/projects/create and select the repo
4. Select Previous Code when prompted
5. Configure by going to https://sonarcloud.io/project/configuration?id=aignostics_python-sdk and clicking on "With GitHub Actions". Copy the value of `SONAR_TOKEN` into your clipboard.
6. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and create a new repository secret called `SONAR_TOKEN`, pasting the token from your clipboard as the value
7. Goto https://sonarcloud.io/project/settings?id=aignostics_python-sdk and select "Quality Gate" in the left menu. Select "Sonar way" as default quality gate.
8. Re-run the `CI / test` GitHub job in case you tried before and it failed as SonarQube was not yet wired up

## Generating and publishing documentation via ReadTheDocs (readthedocs.org)

1. Sign-Up at https://readthedocs.org/
2. Goto https://app.readthedocs.org/dashboard/import/ and search for your repo by enterin python-sdk in the search bar
3. Select the repo and click Continue, then Next.
4. On https://app.readthedocs.org/projects/python-sdk/ wait for the build of the documentation to finish
5. Goto https://aignostics.readthedocs.io/en/latest/

## Automatic dependency updates via Rennovate (https://github.com/apps/renovate)

1. Goto https://github.com/apps/renovate and click the "Configure" button
2. Select the owner of your project's repository and configure "Repository access"
3. Rennovate creates a [Dependency Dashboard](https://github.com/aignostics/python-sdk/issues?q=is%3Aissue%20state%3Aopen%20Dependency%20Dashboard) as an issue in your repository

## Publishing package to Python Package Index (pypi.org)

1. Execute `uv build`. This will generate the build files (wheel and tar.gz) in the `dist` folder
2. Sign-Up at https://pypi.org/
3. Goto https://pypi.org/manage/account/ and create an API token of scope "Entire account", calling it python-sdk. Copy the value of the token into your clipboard.
4. Execute `uv publish`, entering __token__ as username and paste the token from your clipboard as password. This will register your package on PyPI and upload the build files
5. Goto https://pypi.org/manage/account/ again and delete the previously created token python-sdk of scope "Entire account".
6. Now create an new API token, again called python-sdk, but this time of scope "Project: python-sdk". Copy the token into your clipboard.
7. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and delete the previously created token.
8. Then create a new repository secret called `UV_PUBLISH_TOKEN`, pasting the token from your clipboard as value
9. In case your `CI / test` job passed, and you are ready to release and publish, bump the version of your project by executing `bump`. In case you tried before completing this setup script, you can as well go to https://github.com/aignostics/python-sdk/actions/workflows/package-build-publish-release.yml, click on the failed job, and re-run.

## Publishing Docker images to Docker Hub (docker.io)

1. Sign-Up at https://hub.docker.com/
2. Click on your avatar or profile pic and copy the username below that into your clipboard.
3. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and create a new repository secret called `DOCKER_USERNAME`, setting your username at Docker Hub as the value
4. Goto https://app.docker.com/settings/personal-access-tokens/create and create a new access token setting the description to python-sdk, permissions Read & Write & Delete. Copy the value of the token into your clipboard.
5. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and create a new repository secret called `DOCKER_PASSWORD`, pasting the token from your clipboard as the value
6. In case your `CI / test` job passed, and you are ready to release and publish, bump the version of your project by executing `bump`. In case you tried before completing this setup script, you can as well go to https://github.com/aignostics/python-sdk/actions/workflows/package-build-publish-release.yml, click on the failed job, and re-run.

## Publishing Docker images to GitHub Container Registry (ghcr.io)

1. This just works, no further setup required.
2. Just `bump` to release and publish.

## Streamlit app (streamlit.io)

1. Sign-up at https://streamlit.io
2. In settings connect your GitHub account
3. Goto https://share.streamlit.io/new and click "Deploy a public app from GitHub"
4. Select the python-sdk repo, for "Main file path" select `examples/streamlit.py`, for App URL enter `aignostics`.streamlit.app. Click "Deploy"
5. Goto https://aignostics.streamlit.app

## GitHub repository settings

1. Goto https://github.com/aignostics/python-sdk/settings/security_analysis
2. Enable Private vulnerability reporting
3. Enable Dependabot alerts
4. Enable Dependabot security updates
5. CodeQL analyis will be automatically set up via a GitHub action


## Error monitoring and profiling with Sentry

1. Goto https://sentry.io/ and sign-in - it's free for solo devs
2. Follow the instructions to create a new project and get the DSN. Copy the
   value of the token into your clipboard.
3. For your local environment: Open your local `.env` file and set the
   `AIGNOSTICS_SENTRY_DSN` variable to the value of the token from your
   clipboard. You can check `.env.example` for the correct format.
4. For the test, preview and production stage: Goto
   https://github.com/aignostics/python-sdk/settings/secrets/actions/new
   and create a new repository secret called `AIGNOSTICS_SENTRY_DSN`,
   pasting from your clipboard.

## Logging and metrics with Logfire

1. Goto https://pydantic.dev/logfire and sign-in - it's free for up to 10
   million spans/metrics per month.
2. Follow the instructions to create a new project and get the write token. Copy
   the value of the token into your clipboard.
3. For your local environment: Open your local `.env` file and set the
   `AIGNOSTICS_LOGFIRE_TOKEN` variable to the value of the token from
   your clipboard. You can check `.env.example` for the correct format.
4. For the test, preview and production stage: Goto
   https://github.com/aignostics/python-sdk/settings/secrets/actions/new
   and create a new repository secret called `AIGNOSTICS_SENTRY_DSN`,
   pasting from your clipboard.

## Uptime monitoring with betterstack

### Monitoring your API and display uptime on status page and in GitHub
1. Goto https://betterstack.com/ and sign-in - it's free for up to 10 monitors
   and one status page
2. Go to Uptime > Monitors and create a monitor, pointing to the `/api/v1/healthz` endpoint of your API on
   your production environment: (a) . Copy the URL into the "URL to monitor" field. (b) Set "Alert us when" to "URL returns HTTP status other then",
   (c) )select "200" from drop down "Expected HTTP status codes". (d) Click "Create monitor" at the bottom of the page.
3. Go to Uptime > Status pages and create a status page for your project. Add the monitor you created in step #2 to the page.
4. Go to Uptime > Monitors, select the monitor you created in step #2. (a) Click "Configure", and scroll down to "Advanced Settings" / "Github badge".
   Click "Copy to clipboard" for a badge of your liking, (b) `copier update --trust` and paste the snippet when asked for it

### Monitoring your scheduled tests
1. Go to https://betterstack.com/ and sign-in.
2. Goto Uptime > Heartbeat and hit "Create heartbeat".
3. Set "What service will this heartbeat track? to "Aignostics Python SDK / Scheduled tests"
4. Change "Expect a heartbeat every" in case you changed cron setting in your `.github/workflows/test-scheduled.yml`. If you did not change, the efault of 1 day is fine.
5. Click "Create heartbeat" at the bottom of the page.
6. Click "Copy to clipboard' next to "Make a HEAD, GET, or a POST request to the following URL".
7. Goto https://github.com/aignostics/python-sdk/settings/secrets/actions/new and create a new repository secret called `BETTERSTACK_HEARTBEAT_TEST_SCHEDULED_URL`, pasting the URL from your clipboard as value.

## Deploying webservice to Vercel as serverless function (optional)

1. Ensure you enabled Vercel deployment when creating or updating the project.
   If not, enable with `copier update`
2. Goto https://vercel.com/ and sign-in - it's free for solo devs and open
   source projects
3. Execute `pnpm i -g vercel@latest` to install or update the Vercel CLI, see
   https://vercel.com/docs/cli.
4. Execute `vercel login` to login to your Vercel account
5. In Vercel create a new project
6. Execute `vercel link` and link your repository to the newly created project
7. Execute `cat .vercel/project.json` to show the orgId and projectId
8. Goto
   https://github.com/aignostics/python-sdk/settings/secrets/actions/new
   and create a new repository secret called `VERCEL_ORG_ID`, copy and pasting
   from the output of step 6.
9. Goto
   https://github.com/aignostics/python-sdk/settings/secrets/actions/new
   and create a new repository secret called `VERCEL_PROJECT_ID`, copy and
   pasting from the output of step 6
10. Goto `https://vercel.com/account/tokens` and create a new token called
   `aignostics`. Copy the value of the token into your clipboard.
11. Goto
    https://github.com/aignostics/python-sdk/settings/secrets/actions/new
    and create a new repository secret called `VERCEL_TOKEN`, pasting from your
    clipboard.
12. In your Vercel project go to Settings > Deployment Protection, enable
    Protection Bypass for Automation, and copy the token it your clipboard.
13. Goto
    https://github.com/aignostics/python-sdk/settings/secrets/actions/new
    and create a new repository secret called `VERCEL_AUTOMATION_BYPASS_SECRET`, pasting from your
    clipboard. This is so the smoke test post deploy via GitHub Action can validate
    the deployment was successful.
14. Optional: In your Vercel project go to Settings > Environment Variables > Environments, and
      add environment variables with key 'AIGNOSTICS_LOGFIRE_TOKEN' 
      and 'AIGNOSTICS_SENTRY_DSN' - check your `.env` file for the values

## Polishing GitHub repository

1. Goto https://github.com/aignostics/python-sdk
2. Click on the cogs icon in the top right corner next to about
4. Copy aignostics.readthedocs.io into the website field
3. Copy the description from the pyproject.toml file into the description field
5. Copy up to 20 tags from the pyproject.toml file into the topics field
6. Goto https://github.com/aignostics/python-sdk/settings and upload a soclial media image (e.g. logo.png) into the "Social preview" field
