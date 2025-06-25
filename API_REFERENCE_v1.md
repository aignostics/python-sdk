# API v1 Reference
## Aignostics Platform API reference v1.0.0

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

Pagination is done via `page` and `page_size`. Sorting via `sort` query parameter.
The `sort` query parameter can be provided multiple times. The sorting direction can be indicated via
`+` (ascending) or `-` (descending) (e.g. `/v1/applications?sort=+name)`.

Base URLs:

* [/api](/api)

## Authentication

- oAuth2 authentication. 

    - Flow: authorizationCode
    - Authorization URL = [https://aignostics-platform.eu.auth0.com/authorize](https://aignostics-platform.eu.auth0.com/authorize)
    - Token URL = [https://aignostics-platform.eu.auth0.com/oauth/token](https://aignostics-platform.eu.auth0.com/oauth/token)

|Scope|Scope Description|
|---|---|

## Public

### list_applications_v1_applications_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/applications', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/applications',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`GET /v1/applications`

*List Applications*

Returns the list of the applications, available to the caller.

The application is available if any of the version of the application is assigned to the
user organization. To switch between organizations, the user should re-login and choose the
needed organization.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|none|

> Example responses

> 200 Response

```json
[
  {
    "application_id": "h-e-tme",
    "description": "string",
    "name": "HETA",
    "regulatory_classes": [
      "RuO"
    ]
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Applications V1 Applications Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response List Applications V1 Applications Get|[[ApplicationReadResponse](#schemaapplicationreadresponse)]|false|none|none|
|» ApplicationReadResponse|[ApplicationReadResponse](#schemaapplicationreadresponse)|false|none|none|
|»» application_id|string|true|none|Application ID|
|»» description|string|true|none|Application documentations|
|»» name|string|true|none|Application display name|
|»» regulatory_classes|[string]|true|none|Regulatory class, to which the applications compliance|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_versions_by_application_id_v1_applications__application_id__versions_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/applications/{application_id}/versions', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/applications/{application_id}/versions',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`GET /v1/applications/{application_id}/versions`

*List Versions By Application Id*

Returns the list of the application versions for this application, available to the caller.

The application version is available if it is assigned to the user's organization.

The application versions are assigned to the organization by the Aignostics admin. To
assign or unassign a version from your organization, please contact Aignostics support team.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|path|string|true|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|version|query|any|false|none|
|include|query|any|false|none|
|sort|query|any|false|none|

> Example responses

> 200 Response

```json
[
  {
    "application_id": "string",
    "application_version_id": "h-e-tme:v0.0.1",
    "changelog": "string",
    "created_at": "2019-08-24T14:15:22Z",
    "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
    "input_artifacts": [
      {
        "metadata_schema": {},
        "mime_type": "image/tiff",
        "name": "string"
      }
    ],
    "output_artifacts": [
      {
        "metadata_schema": {},
        "mime_type": "application/vnd.apache.parquet",
        "name": "string",
        "scope": "ITEM"
      }
    ],
    "version": "string"
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Versions By Application Id V1 Applications  Application Id  Versions Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response List Versions By Application Id V1 Applications  Application Id  Versions Get|[[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)]|false|none|none|
|» ApplicationVersionReadResponse|[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)|false|none|none|
|»» application_id|string|true|none|Application ID|
|»» application_version_id|string|true|none|Application version ID|
|»» changelog|string|true|none|Description of the changes relative to the previous version|
|»» created_at|string(date-time)|true|none|The timestamp when the application version was registered|
|»» flow_id|any|false|none|Flow ID, used internally by the platform|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|string(uuid)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|List of the input fields, provided by the User|
|»»» InputArtifactReadResponse|[InputArtifactReadResponse](#schemainputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»» output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|List of the output fields, generated by the application|
|»»» OutputArtifactReadResponse|[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»»»» scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|»» version|string|true|none|Semantic version of the application|

##### Enumerated Values

|Property|Value|
|---|---|
|scope|ITEM|
|scope|GLOBAL|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_application_runs_v1_runs_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`GET /v1/runs`

*List Application Runs*

The endpoint returns the application runs triggered by the caller. After the application run
is created by POST /v1/runs, it becomes available for the current endpoint

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|query|any|false|Optional application ID filter|
|application_version|query|any|false|Optional application version filter|
|include|query|any|false|Request optional output values. Used internally by the platform|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|none|

> Example responses

> 200 Response

```json
[
  {
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "application_version_id": "string",
    "organization_id": "string",
    "status": "CANCELED_SYSTEM",
    "triggered_at": "2019-08-24T14:15:22Z",
    "triggered_by": "string",
    "user_payload": {
      "application_id": "string",
      "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
      "global_output_artifacts": {
        "property1": {
          "data": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "metadata": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
        },
        "property2": {
          "data": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "metadata": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
        }
      },
      "items": [
        {
          "input_artifacts": {
            "property1": {
              "download_url": "http://example.com",
              "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
              "metadata": {}
            },
            "property2": {
              "download_url": "http://example.com",
              "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
              "metadata": {}
            }
          },
          "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
          "output_artifacts": {
            "property1": {
              "data": {
                "download_url": "http://example.com",
                "upload_url": "http://example.com"
              },
              "metadata": {
                "download_url": "http://example.com",
                "upload_url": "http://example.com"
              },
              "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
            },
            "property2": {
              "data": {
                "download_url": "http://example.com",
                "upload_url": "http://example.com"
              },
              "metadata": {
                "download_url": "http://example.com",
                "upload_url": "http://example.com"
              },
              "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
            }
          }
        }
      ]
    }
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Application Runs V1 Runs Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response List Application Runs V1 Runs Get|[[RunReadResponse](#schemarunreadresponse)]|false|none|none|
|» RunReadResponse|[RunReadResponse](#schemarunreadresponse)|false|none|none|
|»» application_run_id|string(uuid)|true|none|UUID of the application|
|»» application_version_id|string|true|none|ID of the application version|
|»» organization_id|string|true|none|Organization of the owner of the application run|
|»» status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|none|
|»» triggered_at|string(date-time)|true|none|Timestamp showing when the application run was triggered|
|»» triggered_by|string|true|none|Id of the user who triggered the application run|
|»» user_payload|any|false|none|Field used internally by the Platform|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[UserPayload](#schemauserpayload)|false|none|none|
|»»»» application_id|string|true|none|none|
|»»»» application_run_id|string(uuid)|true|none|none|
|»»»» global_output_artifacts|any|true|none|none|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|object|false|none|none|
|»»»»»» PayloadOutputArtifact|[PayloadOutputArtifact](#schemapayloadoutputartifact)|false|none|none|
|»»»»»»» data|[TransferUrls](#schematransferurls)|true|none|none|
|»»»»»»»» download_url|string(uri)|true|none|none|
|»»»»»»»» upload_url|string(uri)|true|none|none|
|»»»»»»» metadata|[TransferUrls](#schematransferurls)|true|none|none|
|»»»»»»» output_artifact_id|string(uuid)|true|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»» items|[[PayloadItem](#schemapayloaditem)]|true|none|none|
|»»»»» PayloadItem|[PayloadItem](#schemapayloaditem)|false|none|none|
|»»»»»» input_artifacts|object|true|none|none|
|»»»»»»» PayloadInputArtifact|[PayloadInputArtifact](#schemapayloadinputartifact)|false|none|none|
|»»»»»»»» download_url|string(uri)|true|none|none|
|»»»»»»»» input_artifact_id|string(uuid)|false|none|none|
|»»»»»»»» metadata|object|true|none|none|
|»»»»»» item_id|string(uuid)|true|none|none|
|»»»»»» output_artifacts|object|true|none|none|
|»»»»»»» PayloadOutputArtifact|[PayloadOutputArtifact](#schemapayloadoutputartifact)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|status|CANCELED_SYSTEM|
|status|CANCELED_USER|
|status|COMPLETED|
|status|COMPLETED_WITH_ERROR|
|status|RECEIVED|
|status|REJECTED|
|status|RUNNING|
|status|SCHEDULED|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### create_application_run_v1_runs_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/api/v1/runs', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "application_version_id": "h-e-tme:v1.2.3",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_base64_crc32c": "752f9554",
            "height": 2000,
            "height_mpp": 0.5,
            "width": 10000,
            "width_mpp": 0.5
          },
          "name": "slide"
        }
      ],
      "reference": "case-no-1"
    }
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`POST /v1/runs`

*Create Application Run*

The endpoint is used to process the input items by the chosen application version. The endpoint
returns the `application_run_id`. The processing fo the items is done asynchronously.

To check the status or cancel the execution, use the /v1/runs/{application_run_id} endpoint.

#### Payload

The payload includes `application_version_id` and `items` base fields.

`application_version_id` is the id used for `/v1/versions/{application_id}` endpoint.

`items` includes the list of the items to process (slides, in case of HETA application).
Every item has a set of standard fields defined by the API, plus the metadata, specific to the
chosen application.

Example payload structure with the comments:
```
{
    application_version_id: "test-app:v0.0.2",
    items: [{
        "reference": "slide_1",   Body parameter

```json
{
  "application_version_id": "h-e-tme:v1.2.3",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_base64_crc32c": "752f9554",
            "height": 2000,
            "height_mpp": 0.5,
            "width": 10000,
            "width_mpp": 0.5
          },
          "name": "slide"
        }
      ],
      "reference": "case-no-1"
    }
  ]
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[RunCreationRequest](#schemaruncreationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "application_run_id": "Application run id"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[RunCreationResponse](#schemaruncreationresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_run_v1_runs__application_run_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs/{application_run_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{application_run_id}',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`GET /v1/runs/{application_run_id}`

*Get Run*

Returns the details of the application run. The application run is available as soon as it is
created via `POST /runs/` endpoint. To download the items results, call
`/runs/{application_run_id}/results`.

The application is only available to the user who triggered it, regardless of the role.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|Application run id, returned by `POST /runs/` endpoint|
|include|query|any|false|none|

> Example responses

> 200 Response

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "string",
  "organization_id": "string",
  "status": "CANCELED_SYSTEM",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "string",
  "user_payload": {
    "application_id": "string",
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "global_output_artifacts": {
      "property1": {
        "data": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "metadata": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      },
      "property2": {
        "data": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "metadata": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      }
    },
    "items": [
      {
        "input_artifacts": {
          "property1": {
            "download_url": "http://example.com",
            "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
            "metadata": {}
          },
          "property2": {
            "download_url": "http://example.com",
            "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
            "metadata": {}
          }
        },
        "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
        "output_artifacts": {
          "property1": {
            "data": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "metadata": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
          },
          "property2": {
            "data": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "metadata": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
          }
        }
      }
    ]
  }
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[RunReadResponse](#schemarunreadresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### cancel_application_run_v1_runs__application_run_id__cancel_post



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/api/v1/runs/{application_run_id}/cancel', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{application_run_id}/cancel',
{
  method: 'POST',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`POST /v1/runs/{application_run_id}/cancel`

*Cancel Application Run*

The application run can be canceled by the user who created the application run.

The execution can be canceled any time while the application is not in a final state. The
pending items will not be processed and will not add to the cost.

When the application is canceled, the already completed items stay available for download.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|Application run id, returned by `POST /runs/` endpoint|

> Example responses

> 202 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### delete_application_run_results_v1_runs__application_run_id__results_delete



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.delete('/api/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{application_run_id}/results',
{
  method: 'DELETE',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`DELETE /v1/runs/{application_run_id}/results`

*Delete Application Run Results*

Delete the application run results. It can only be called when the application is in a final
state (meaning it's not in `received` or `pending` states). To delete the results of the running
artifacts, first call `POST /v1/runs/{application_run_id}/cancel` to cancel the application run.

The output results are deleted automatically 30 days after the application run is finished.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|Application run id, returned by `POST /runs/` endpoint|

> Example responses

> 422 Response

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|204|[No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)|Successful Response|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_run_results_v1_runs__application_run_id__results_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{application_run_id}/results',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`GET /v1/runs/{application_run_id}/results`

*List Run Results*

Get the list of the results for the run items

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|Application run id, returned by `POST /runs/` endpoint|
|item_id__in|query|any|false|Filter for items ids|
|reference__in|query|any|false|Filter for items by their reference from the input payload|
|status__in|query|any|false|Filter for items in certain statuses|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|none|

> Example responses

> 200 Response

```json
[
  {
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "error": "string",
    "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
    "output_artifacts": [
      {
        "download_url": "http://example.com",
        "metadata": {},
        "name": "string",
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      }
    ],
    "reference": "string",
    "status": "PENDING"
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Run Results V1 Runs  Application Run Id  Results Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response List Run Results V1 Runs  Application Run Id  Results Get|[[ItemResultReadResponse](#schemaitemresultreadresponse)]|false|none|none|
|» ItemResultReadResponse|[ItemResultReadResponse](#schemaitemresultreadresponse)|false|none|none|
|»» application_run_id|string(uuid)|true|none|Application run UUID to which the item belongs|
|»» error|any|true|none|The error message in case the item is in `error_system` or `error_user` state|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|string|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» item_id|string(uuid)|true|none|Item UUID generated by the Platform|
|»» output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.|
|»»» OutputArtifactResultReadResponse|[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)|false|none|none|
|»»»» download_url|any|true|none|The download URL to the output file. The URL is valid for 1 hour after the endpoint is called.A new URL is generated every time the endpoint is called.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|string(uri)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»» metadata|object|true|none|The metadata of the output artifact, provided by the application|
|»»»» name|string|true|none|Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint.|
|»»»» output_artifact_id|string(uuid)|true|none|The Id of the artifact. Used internally|
|»» reference|string|true|none|The reference of the item from the user payload|
|»» status|[ItemStatus](#schemaitemstatus)|true|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|status|PENDING|
|status|CANCELED_USER|
|status|CANCELED_SYSTEM|
|status|ERROR_USER|
|status|ERROR_SYSTEM|
|status|SUCCEEDED|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Schemas

### ApplicationReadResponse






```json
{
  "application_id": "h-e-tme",
  "description": "string",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ]
}

```

ApplicationReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application ID|
|description|string|true|none|Application documentations|
|name|string|true|none|Application display name|
|regulatory_classes|[string]|true|none|Regulatory class, to which the applications compliance|

### ApplicationRunStatus






```json
"CANCELED_SYSTEM"

```

ApplicationRunStatus

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ApplicationRunStatus|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ApplicationRunStatus|CANCELED_SYSTEM|
|ApplicationRunStatus|CANCELED_USER|
|ApplicationRunStatus|COMPLETED|
|ApplicationRunStatus|COMPLETED_WITH_ERROR|
|ApplicationRunStatus|RECEIVED|
|ApplicationRunStatus|REJECTED|
|ApplicationRunStatus|RUNNING|
|ApplicationRunStatus|SCHEDULED|

### ApplicationVersionReadResponse






```json
{
  "application_id": "string",
  "application_version_id": "h-e-tme:v0.0.1",
  "changelog": "string",
  "created_at": "2019-08-24T14:15:22Z",
  "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
  "input_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "image/tiff",
      "name": "string"
    }
  ],
  "output_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string",
      "scope": "ITEM"
    }
  ],
  "version": "string"
}

```

ApplicationVersionReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application ID|
|application_version_id|string|true|none|Application version ID|
|changelog|string|true|none|Description of the changes relative to the previous version|
|created_at|string(date-time)|true|none|The timestamp when the application version was registered|
|flow_id|any|false|none|Flow ID, used internally by the platform|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|List of the input fields, provided by the User|
|output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|List of the output fields, generated by the application|
|version|string|true|none|Semantic version of the application|

### HTTPValidationError






```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

### InputArtifactCreationRequest






```json
{
  "download_url": "https://example.com/case-no-1-slide.tiff",
  "metadata": {
    "checksum_base64_crc32c": "752f9554",
    "height": 2000,
    "height_mpp": 0.5,
    "width": 10000,
    "width_mpp": 0.5
  },
  "name": "slide"
}

```

InputArtifactCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|string(uri)|true|none|[Signed URL](https://cloud.google.com/cdn/docs/using-signed-urls) to the input artifact file. The URL should be valid for at least 6 days from the payload submission time.|
|metadata|object|true|none|The metadata of the artifact, required by the application version. The JSON schema of the metadata can be requested by `/v1/versions/{application_version_id}`. The schema is located in `input_artifacts.[].metadata_schema`|
|name|string|true|none|The artifact name according to the application version. List of required artifacts is returned by `/v1/versions/{application_version_id}`. The artifact names are located in the `input_artifacts.[].name` value|

### InputArtifactReadResponse






```json
{
  "metadata_schema": {},
  "mime_type": "image/tiff",
  "name": "string"
}

```

InputArtifactReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|

### ItemCreationRequest






```json
{
  "input_artifacts": [
    {
      "download_url": "https://example.com/case-no-1-slide.tiff",
      "metadata": {
        "checksum_base64_crc32c": "752f9554",
        "height": 2000,
        "height_mpp": 0.5,
        "width": 10000,
        "width_mpp": 0.5
      },
      "name": "slide"
    }
  ],
  "reference": "case-no-1"
}

```

ItemCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|input_artifacts|[[InputArtifactCreationRequest](#schemainputartifactcreationrequest)]|true|none|All the input files of the item, required by the application version|
|reference|string|true|none|The ID of the slide provided by the caller. The reference should be unique across all items of the application run|

### ItemResultReadResponse






```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "error": "string",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "output_artifacts": [
    {
      "download_url": "http://example.com",
      "metadata": {},
      "name": "string",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  ],
  "reference": "string",
  "status": "PENDING"
}

```

ItemResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|string(uuid)|true|none|Application run UUID to which the item belongs|
|error|any|true|none|The error message in case the item is in `error_system` or `error_user` state|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|item_id|string(uuid)|true|none|Item UUID generated by the Platform|
|output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.|
|reference|string|true|none|The reference of the item from the user payload|
|status|[ItemStatus](#schemaitemstatus)|true|none|When the item is not processed yet, the status is set to `pending`.When the item is successfully finished, status is set to `succeeded`, and the processing resultsbecome available for download in `output_artifacts` field.When the item processing is failed because the provided item is invalid, the status is set to`error_user`. When the item processing failed because of the error in the model or platform,the status is set to `error_system`. When the application_run is canceled, the status of allpending items is set to either `cancelled_user` or `cancelled_system`.|

### ItemStatus






```json
"PENDING"

```

ItemStatus

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemStatus|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemStatus|PENDING|
|ItemStatus|CANCELED_USER|
|ItemStatus|CANCELED_SYSTEM|
|ItemStatus|ERROR_USER|
|ItemStatus|ERROR_SYSTEM|
|ItemStatus|SUCCEEDED|

### OutputArtifactReadResponse






```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "scope": "ITEM"
}

```

OutputArtifactReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|

### OutputArtifactResultReadResponse






```json
{
  "download_url": "http://example.com",
  "metadata": {},
  "name": "string",
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
}

```

OutputArtifactResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|any|true|none|The download URL to the output file. The URL is valid for 1 hour after the endpoint is called.A new URL is generated every time the endpoint is called.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uri)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata|object|true|none|The metadata of the output artifact, provided by the application|
|name|string|true|none|Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint.|
|output_artifact_id|string(uuid)|true|none|The Id of the artifact. Used internally|

### OutputArtifactScope






```json
"ITEM"

```

OutputArtifactScope

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|OutputArtifactScope|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|OutputArtifactScope|ITEM|
|OutputArtifactScope|GLOBAL|

### PayloadInputArtifact






```json
{
  "download_url": "http://example.com",
  "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
  "metadata": {}
}

```

PayloadInputArtifact

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|string(uri)|true|none|none|
|input_artifact_id|string(uuid)|false|none|none|
|metadata|object|true|none|none|

### PayloadItem






```json
{
  "input_artifacts": {
    "property1": {
      "download_url": "http://example.com",
      "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
      "metadata": {}
    },
    "property2": {
      "download_url": "http://example.com",
      "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
      "metadata": {}
    }
  },
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "output_artifacts": {
    "property1": {
      "data": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "metadata": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    },
    "property2": {
      "data": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "metadata": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  }
}

```

PayloadItem

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|input_artifacts|object|true|none|none|
|» **additionalProperties**|[PayloadInputArtifact](#schemapayloadinputartifact)|false|none|none|
|item_id|string(uuid)|true|none|none|
|output_artifacts|object|true|none|none|
|» **additionalProperties**|[PayloadOutputArtifact](#schemapayloadoutputartifact)|false|none|none|

### PayloadOutputArtifact






```json
{
  "data": {
    "download_url": "http://example.com",
    "upload_url": "http://example.com"
  },
  "metadata": {
    "download_url": "http://example.com",
    "upload_url": "http://example.com"
  },
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
}

```

PayloadOutputArtifact

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|data|[TransferUrls](#schematransferurls)|true|none|none|
|metadata|[TransferUrls](#schematransferurls)|true|none|none|
|output_artifact_id|string(uuid)|true|none|none|

### RunCreationRequest






```json
{
  "application_version_id": "h-e-tme:v1.2.3",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_base64_crc32c": "752f9554",
            "height": 2000,
            "height_mpp": 0.5,
            "width": 10000,
            "width_mpp": 0.5
          },
          "name": "slide"
        }
      ],
      "reference": "case-no-1"
    }
  ]
}

```

RunCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_version_id|string|true|none|Application version ID|
|items|[[ItemCreationRequest](#schemaitemcreationrequest)]|true|none|List of the items to process by the application|

### RunCreationResponse






```json
{
  "application_run_id": "Application run id"
}

```

RunCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|string(uuid)|false|none|none|

### RunReadResponse






```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "string",
  "organization_id": "string",
  "status": "CANCELED_SYSTEM",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "string",
  "user_payload": {
    "application_id": "string",
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "global_output_artifacts": {
      "property1": {
        "data": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "metadata": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      },
      "property2": {
        "data": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "metadata": {
          "download_url": "http://example.com",
          "upload_url": "http://example.com"
        },
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      }
    },
    "items": [
      {
        "input_artifacts": {
          "property1": {
            "download_url": "http://example.com",
            "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
            "metadata": {}
          },
          "property2": {
            "download_url": "http://example.com",
            "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
            "metadata": {}
          }
        },
        "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
        "output_artifacts": {
          "property1": {
            "data": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "metadata": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
          },
          "property2": {
            "data": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "metadata": {
              "download_url": "http://example.com",
              "upload_url": "http://example.com"
            },
            "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
          }
        }
      }
    ]
  }
}

```

RunReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|string(uuid)|true|none|UUID of the application|
|application_version_id|string|true|none|ID of the application version|
|organization_id|string|true|none|Organization of the owner of the application run|
|status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|When the application run request is received by the Platform, the `status` of it is set to`received`. Then it is transitioned to `scheduled`, when it is scheduled for the processing.When the application run is scheduled, it will process the input items and generate the resultincrementally. As soon as the first result is generated, the state is changed to `running`.The results can be downloaded via `/v1/runs/{run_id}/results` endpoint.When all items are processed and all results are generated, the application status is set to`completed`. If the processing is done, but some items fail, the status is set to`completed_with_error`.When the application run request is rejected by the Platform before scheduling, it is transferredto `rejected`. When the application run reaches the threshold of number of failed items, the wholeapplication run is set to `canceled_system` and the remaining pending items are not processed.When the application run fails, the finished item results are available for download.If the application run is canceled by calling `POST /v1/runs/{run_id}/cancel` endpoint, theprocessing of the items is stopped, and the application status is set to `cancelled_user`|
|triggered_at|string(date-time)|true|none|Timestamp showing when the application run was triggered|
|triggered_by|string|true|none|Id of the user who triggered the application run|
|user_payload|any|false|none|Field used internally by the Platform|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[UserPayload](#schemauserpayload)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### TransferUrls






```json
{
  "download_url": "http://example.com",
  "upload_url": "http://example.com"
}

```

TransferUrls

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|string(uri)|true|none|none|
|upload_url|string(uri)|true|none|none|

### UserPayload






```json
{
  "application_id": "string",
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "global_output_artifacts": {
    "property1": {
      "data": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "metadata": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    },
    "property2": {
      "data": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "metadata": {
        "download_url": "http://example.com",
        "upload_url": "http://example.com"
      },
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  },
  "items": [
    {
      "input_artifacts": {
        "property1": {
          "download_url": "http://example.com",
          "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
          "metadata": {}
        },
        "property2": {
          "download_url": "http://example.com",
          "input_artifact_id": "a4134709-460b-44b6-99b2-2d637f889159",
          "metadata": {}
        }
      },
      "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
      "output_artifacts": {
        "property1": {
          "data": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "metadata": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
        },
        "property2": {
          "data": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "metadata": {
            "download_url": "http://example.com",
            "upload_url": "http://example.com"
          },
          "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
        }
      }
    }
  ]
}

```

UserPayload

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|none|
|application_run_id|string(uuid)|true|none|none|
|global_output_artifacts|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|
|»» **additionalProperties**|[PayloadOutputArtifact](#schemapayloadoutputartifact)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[PayloadItem](#schemapayloaditem)]|true|none|none|

### ValidationError






```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|
