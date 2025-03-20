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

## Polishing GitHub repository

1. Goto https://github.com/aignostics/python-sdk
2. Click on the cogs icon in the top right corner next to about
4. Copy aignostics.readthedocs.io into the website field
3. Copy the description from the pyproject.toml file into the description field
5. Copy up to 20 tags from the pyproject.toml file into the topics field
6. Goto https://github.com/aignostics/python-sdk/settings and upload a soclial media image (e.g. logo.png) into the "Social preview" field
