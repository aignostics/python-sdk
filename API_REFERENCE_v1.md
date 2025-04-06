# API v1 Reference
## Aignostics Platform API v0.1.0

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

Pagination is done via `page` and `page_size`. Sorting via `sort` query parameter. sort is a comma-separated list of field names. The sorting direction can be indicated via `+` (ascending) or `-` (descending) (e.g. `/applications?sort=+name)`.

## Authentication

- oAuth2 authentication. 

    - Flow: authorizationCode
    - Authorization URL = [https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize](https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize)
    - Token URL = [https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token](https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token)

|Scope|Scope Description|
|---|---|

## Default

### get_documentation_docs_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/docs', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/docs',
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

`GET /docs`

*Get Documentation*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|access_token|cookie|any|false|none|

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema


This operation does not require authentication


## Externals

Called by externals to interact with our API

### list_applications_v1_applications_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/applications', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications',
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
    "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
    "description": "Aignostics H&E TME application",
    "name": "HETA",
    "regulatory_classes": [
      "RuO"
    ],
    "slug": "heta"
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
|»» application_id|string(uuid)|true|none|none|
|»» description|string|true|none|none|
|»» name|string|true|none|none|
|»» regulatory_classes|[string]|true|none|none|
|»» slug|string|true|none|none|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### read_application_by_id_v1_applications__application_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/applications/{application_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications/{application_id}',
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

`GET /v1/applications/{application_id}`

*Read Application By Id*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|path|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "description": "Aignostics H&E TME application",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ],
  "slug": "heta"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ApplicationReadResponse](#schemaapplicationreadresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


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

r = requests.get('/v1/applications/{application_id}/versions', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications/{application_id}/versions',
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

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|path|string(uuid)|true|none|
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
    "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
    "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
    "application_version_slug": "tissue-segmentation-qc:v0.0.1",
    "changelog": "string",
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
        "scope": "item"
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
|»» application_id|string(uuid)|true|none|none|
|»» application_version_id|string(uuid)|true|none|none|
|»» application_version_slug|string|true|none|none|
|»» changelog|string|true|none|none|
|»» flow_id|any|false|none|none|

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
|»» input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|none|
|»»» InputArtifactReadResponse|[InputArtifactReadResponse](#schemainputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»» output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|none|
|»»» OutputArtifactReadResponse|[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»»»» scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|»» version|string|true|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|scope|item|
|scope|global|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### read_application_by_slug_v1_applications__application_slug__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/applications/{application_slug}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications/{application_slug}',
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

`GET /v1/applications/{application_slug}`

*Read Application By Slug*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_slug|path|string|true|none|

> Example responses

> 200 Response

```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "description": "Aignostics H&E TME application",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ],
  "slug": "heta"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ApplicationReadResponse](#schemaapplicationreadresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_versions_by_application_slug_v1_applications__application_slug__versions_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/applications/{application_slug}/versions', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications/{application_slug}/versions',
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

`GET /v1/applications/{application_slug}/versions`

*List Versions By Application Slug*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_slug|path|string|true|none|
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
    "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
    "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
    "application_version_slug": "tissue-segmentation-qc:v0.0.1",
    "changelog": "string",
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
        "scope": "item"
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

*Response List Versions By Application Slug V1 Applications  Application Slug  Versions Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response List Versions By Application Slug V1 Applications  Application Slug  Versions Get|[[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)]|false|none|none|
|» ApplicationVersionReadResponse|[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)|false|none|none|
|»» application_id|string(uuid)|true|none|none|
|»» application_version_id|string(uuid)|true|none|none|
|»» application_version_slug|string|true|none|none|
|»» changelog|string|true|none|none|
|»» flow_id|any|false|none|none|

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
|»» input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|none|
|»»» InputArtifactReadResponse|[InputArtifactReadResponse](#schemainputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»» output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|none|
|»»» OutputArtifactReadResponse|[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»»»» scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|»» version|string|true|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|scope|item|
|scope|global|


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

r = requests.get('/v1/runs', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/runs',
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

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|query|any|false|none|
|application_version_id|query|any|false|none|
|include|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|none|

> Example responses

> 200 Response

```json
[
  {
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
    "organization_id": "string",
    "status": "canceled_system",
    "triggered_at": "2019-08-24T14:15:22Z",
    "triggered_by": "string",
    "user_payload": {
      "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
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
|»» application_run_id|string(uuid)|true|none|none|
|»» application_version_id|string(uuid)|true|none|none|
|»» organization_id|string|true|none|none|
|»» status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|none|
|»» triggered_at|string(date-time)|true|none|none|
|»» triggered_by|string|true|none|none|
|»» user_payload|any|false|none|none|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[UserPayload](#schemauserpayload)|false|none|none|
|»»»» application_id|string(uuid)|true|none|none|
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
|»»»»»»»» input_artifact_id|string(uuid)|true|none|none|
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
|status|canceled_system|
|status|canceled_user|
|status|completed|
|status|completed_with_error|
|status|received|
|status|rejected|
|status|running|
|status|scheduled|


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

r = requests.post('/v1/runs', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "application_version": "efbf9822-a1e5-4045-a283-dbf26e8064a9",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_crc32c": "752f9554",
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

fetch('/v1/runs',
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

> Body parameter

```json
{
  "application_version": "efbf9822-a1e5-4045-a283-dbf26e8064a9",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_crc32c": "752f9554",
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
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe"
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

r = requests.get('/v1/runs/{application_run_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/runs/{application_run_id}',
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

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|none|
|include|query|any|false|none|

> Example responses

> 200 Response

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
  "organization_id": "string",
  "status": "canceled_system",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "string",
  "user_payload": {
    "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
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


### cancel_run_v1_runs__application_run_id__cancel_post



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/runs/{application_run_id}/cancel', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/runs/{application_run_id}/cancel',
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

*Cancel Run*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|none|

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


### delete_run_results_v1_runs__application_run_id__results_delete



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.delete('/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/runs/{application_run_id}/results',
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

*Delete Run Results*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|none|

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

r = requests.get('/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/runs/{application_run_id}/results',
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

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_run_id|path|string(uuid)|true|none|
|item_id__in|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|reference__in|query|any|false|none|
|status__in|query|any|false|none|
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
        "mime_type": "application/vnd.apache.parquet",
        "name": "string",
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      }
    ],
    "reference": "string",
    "status": "pending"
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
|»» application_run_id|string(uuid)|true|none|none|
|»» error|any|true|none|none|

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
|»» item_id|string(uuid)|true|none|none|
|»» output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|none|
|»»» OutputArtifactResultReadResponse|[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)|false|none|none|
|»»»» download_url|any|true|none|none|

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
|»»»» metadata|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»»»» output_artifact_id|string(uuid)|true|none|none|
|»» reference|string|true|none|none|
|»» status|[ItemStatus](#schemaitemstatus)|true|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|canceled_user|
|status|canceled_system|
|status|error_user|
|status|error_system|
|status|succeeded|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### create_user_v1_users__post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/users/', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "email": "string",
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "user_id": "string"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/users/',
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

`POST /v1/users/`

*Create User*

> Body parameter

```json
{
  "email": "string",
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "user_id": "string"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[UserCreationRequest](#schemausercreationrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "slide_quota": {
    "total": 0,
    "used": 0
  },
  "user_id": "string"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserResponse](#schemauserresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_user_v1_users__user_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/users/{user_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/users/{user_id}',
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

`GET /v1/users/{user_id}`

*Get User*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "slide_quota": {
    "total": 0,
    "used": 0
  },
  "user_id": "string"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserResponse](#schemauserresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### update_user_v1_users__user_id__patch



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.patch('/v1/users/{user_id}', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "slide_quota": 0,
  "user_id": "string"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/users/{user_id}',
{
  method: 'PATCH',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`PATCH /v1/users/{user_id}`

*Update User*

> Body parameter

```json
{
  "slide_quota": 0,
  "user_id": "string"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|string(uuid)|true|none|
|body|body|[UserUpdateRequest](#schemauserupdaterequest)|true|none|

> Example responses

> 200 Response

```json
{
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "slide_quota": {
    "total": 0,
    "used": 0
  },
  "user_id": "string"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserResponse](#schemauserresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### register_version_v1_versions_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/versions', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "changelog": "string",
  "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
  "input_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string"
    }
  ],
  "output_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string",
      "scope": "item",
      "visibility": "internal"
    }
  ],
  "version": "string"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/versions',
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

`POST /v1/versions`

*Register Version*

> Body parameter

```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "changelog": "string",
  "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
  "input_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string"
    }
  ],
  "output_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string",
      "scope": "item",
      "visibility": "internal"
    }
  ],
  "version": "string"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[VersionCreationRequest](#schemaversioncreationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[VersionCreationResponse](#schemaversioncreationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_version_v1_versions__application_version_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/versions/{application_version_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/versions/{application_version_id}',
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

`GET /v1/versions/{application_version_id}`

*Get Version*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_version_id|path|string(uuid)|true|none|
|include|query|any|false|none|

> Example responses

> 200 Response

```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
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
      "scope": "item",
      "visibility": "internal"
    }
  ],
  "version": "string"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[VersionReadResponse](#schemaversionreadresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Algorithms/Apps

Called by the Algorithms and applications to update statuses

### trigger_artifact_event_v1_artifacts__output_artifact_id__event_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/v1/artifacts/{output_artifact_id}/event', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "error": "string",
  "event": "succeeded",
  "metadata": {}
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json'
};

fetch('/v1/artifacts/{output_artifact_id}/event',
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

`POST /v1/artifacts/{output_artifact_id}/event`

*Trigger Artifact Event*

> Body parameter

```json
{
  "error": "string",
  "event": "succeeded",
  "metadata": {}
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|output_artifact_id|path|string(uuid)|true|none|
|body|body|[OutputArtifactEventTriggerRequest](#schemaoutputartifacteventtriggerrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
  "status": "pending"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[OutputArtifactEventTriggerResponse](#schemaoutputartifacteventtriggerresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


This operation does not require authentication


## Scheduler

Called by the Scheduler

### get_item_v1_items__item_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/items/{item_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/items/{item_id}',
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

`GET /v1/items/{item_id}`

*Get Item*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|item_id|path|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "error": "string",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "reference": "string",
  "status": "pending"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ItemReadResponse](#schemaitemreadresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### register_item_event_v1_items__item_id__event_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/items/{item_id}/event', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "error": "string",
  "event": "failed_with_system_error"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/items/{item_id}/event',
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

`POST /v1/items/{item_id}/event`

*Register Item Event*

> Body parameter

```json
{
  "error": "string",
  "event": "failed_with_system_error"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|item_id|path|string(uuid)|true|none|
|body|body|[ItemEventCreationRequest](#schemaitemeventcreationrequest)|true|none|

> Example responses

> 202 Response

```json
{
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "status": "pending"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Successful Response|[ItemEventCreationResponse](#schemaitemeventcreationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Admins

Called by Admins to manage and register entities

### register_application_v1_applications_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/applications', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "description": "H&E Tumor Micro Environment Analysis: Performing tissue QC, segmentation, cell detection and cell classfication",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/applications',
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

`POST /v1/applications`

*Register Application*

> Body parameter

```json
{
  "description": "H&E Tumor Micro Environment Analysis: Performing tissue QC, segmentation, cell detection and cell classfication",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ]
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ApplicationCreationRequest](#schemaapplicationcreationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[ApplicationCreationResponse](#schemaapplicationcreationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_quotas_v1_quotas_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/quotas', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/quotas',
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

`GET /v1/quotas`

*List Quotas*

> Example responses

> 200 Response

```json
{
  "quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[QuotasReadResponse](#schemaquotasreadresponse)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### update_quotas_v1_quotas_patch



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.patch('/v1/quotas', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/quotas',
{
  method: 'PATCH',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`PATCH /v1/quotas`

*Update Quotas*

> Body parameter

```json
{
  "quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[QuotasUpdateRequest](#schemaquotasupdaterequest)|true|none|

> Example responses

> 200 Response

```json
{
  "updated_quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[QuotasUpdateResponse](#schemaquotasupdateresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Infrastructure

Called by other Infra

### health_health_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/health', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/health',
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

`GET /health`

*Health*

Check that the API application is alive and responsive.

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

#### Response Schema


This operation does not require authentication


### liveness_liveness_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/liveness', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/liveness',
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

`GET /liveness`

*Liveness*

Check that the API application is alive and responsive.

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

#### Response Schema


This operation does not require authentication


### readiness_readiness_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/readiness', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/readiness',
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

`GET /readiness`

*Readiness*

Check that the API application is ready to serve.

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

#### Response Schema


This operation does not require authentication


## Organizations

### create_organization_v1_organizations_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/v1/organizations', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "batch_size": 0,
  "organization_id": "string",
  "owner_email": "string",
  "slide_quota": 0
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/organizations',
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

`POST /v1/organizations`

*Create Organization*

> Body parameter

```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_email": "string",
  "slide_quota": 0
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[OrganizationCreationRequest](#schemaorganizationcreationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_id": "8826ee2e-7933-4665-aef2-2393f84a0d05",
  "slide_quota": {
    "total": 0,
    "used": 0
  }
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[OrganizationResponse](#schemaorganizationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_organization_v1_organizations__organization_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/v1/organizations/{organization_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/organizations/{organization_id}',
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

`GET /v1/organizations/{organization_id}`

*Get Organization*

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|organization_id|path|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_id": "8826ee2e-7933-4665-aef2-2393f84a0d05",
  "slide_quota": {
    "total": 0,
    "used": 0
  }
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[OrganizationResponse](#schemaorganizationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### update_organization_v1_organizations__organization_id__patch



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.patch('/v1/organizations/{organization_id}', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "batch_size": 0,
  "slide_quota": 0
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/v1/organizations/{organization_id}',
{
  method: 'PATCH',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`PATCH /v1/organizations/{organization_id}`

*Update Organization*

> Body parameter

```json
{
  "batch_size": 0,
  "slide_quota": 0
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|organization_id|path|string|true|none|
|body|body|[OrganizationUpdateRequest](#schemaorganizationupdaterequest)|true|none|

> Example responses

> 200 Response

```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_id": "8826ee2e-7933-4665-aef2-2393f84a0d05",
  "slide_quota": {
    "total": 0,
    "used": 0
  }
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[OrganizationResponse](#schemaorganizationresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Schemas

### ApplicationCreationRequest






```json
{
  "description": "H&E Tumor Micro Environment Analysis: Performing tissue QC, segmentation, cell detection and cell classfication",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ]
}

```

ApplicationCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|description|string|true|none|none|
|name|string|true|none|none|
|regulatory_classes|[string]|true|none|none|

### ApplicationCreationResponse






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c"
}

```

ApplicationCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string(uuid)|true|none|none|

### ApplicationReadResponse






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "description": "Aignostics H&E TME application",
  "name": "HETA",
  "regulatory_classes": [
    "RuO"
  ],
  "slug": "heta"
}

```

ApplicationReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string(uuid)|true|none|none|
|description|string|true|none|none|
|name|string|true|none|none|
|regulatory_classes|[string]|true|none|none|
|slug|string|true|none|none|

### ApplicationRunStatus






```json
"canceled_system"

```

ApplicationRunStatus

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ApplicationRunStatus|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ApplicationRunStatus|canceled_system|
|ApplicationRunStatus|canceled_user|
|ApplicationRunStatus|completed|
|ApplicationRunStatus|completed_with_error|
|ApplicationRunStatus|received|
|ApplicationRunStatus|rejected|
|ApplicationRunStatus|running|
|ApplicationRunStatus|scheduled|

### ApplicationVersionReadResponse






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
  "application_version_slug": "tissue-segmentation-qc:v0.0.1",
  "changelog": "string",
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
      "scope": "item"
    }
  ],
  "version": "string"
}

```

ApplicationVersionReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string(uuid)|true|none|none|
|application_version_id|string(uuid)|true|none|none|
|application_version_slug|string|true|none|none|
|changelog|string|true|none|none|
|flow_id|any|false|none|none|

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
|input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|none|
|output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|none|
|version|string|true|none|none|

### ArtifactEvent






```json
"succeeded"

```

ArtifactEvent

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ArtifactEvent|string|false|none|This is a subset of the OutputArtifactEvent used by the state machine.Only the variants defined below are allowed to be submitted from the Algorithms/Applications.|

##### Enumerated Values

|Property|Value|
|---|---|
|ArtifactEvent|succeeded|
|ArtifactEvent|failed_with_user_error|
|ArtifactEvent|failed_with_system_error|

### ArtifactStatus






```json
"pending"

```

ArtifactStatus

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ArtifactStatus|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ArtifactStatus|pending|
|ArtifactStatus|canceled_user|
|ArtifactStatus|canceled_system|
|ArtifactStatus|error_user|
|ArtifactStatus|error_system_fatal|
|ArtifactStatus|error_system_recoverable|
|ArtifactStatus|skipped|
|ArtifactStatus|succeeded|

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

### InputArtifact






```json
{
  "metadata_schema": {},
  "mime_type": "image/tiff",
  "name": "string"
}

```

InputArtifact

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|

### InputArtifactCreationRequest






```json
{
  "download_url": "https://example.com/case-no-1-slide.tiff",
  "metadata": {
    "checksum_crc32c": "752f9554",
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
|download_url|string(uri)|true|none|none|
|metadata|object|true|none|none|
|name|string|true|none|none|

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

### InputArtifactSchemaCreationRequest






```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string"
}

```

InputArtifactSchemaCreationRequest

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
        "checksum_crc32c": "752f9554",
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
|input_artifacts|[[InputArtifactCreationRequest](#schemainputartifactcreationrequest)]|true|none|none|
|reference|string|true|none|none|

### ItemEvent






```json
"failed_with_system_error"

```

ItemEvent

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemEvent|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemEvent|failed_with_system_error|
|ItemEvent|failed_recoverable|

### ItemEventCreationRequest






```json
{
  "error": "string",
  "event": "failed_with_system_error"
}

```

ItemEventCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|error|string|true|none|none|
|event|[ItemEvent](#schemaitemevent)|true|none|none|

### ItemEventCreationResponse






```json
{
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "status": "pending"
}

```

ItemEventCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|item_id|string(uuid)|true|none|none|
|status|[ItemStatus](#schemaitemstatus)|true|none|none|

### ItemReadResponse






```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "error": "string",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "reference": "string",
  "status": "pending"
}

```

ItemReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|any|false|none|none|

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
|error|any|true|none|none|

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
|item_id|string(uuid)|true|none|none|
|reference|string|true|none|none|
|status|[ItemStatus](#schemaitemstatus)|true|none|none|

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
      "mime_type": "application/vnd.apache.parquet",
      "name": "string",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  ],
  "reference": "string",
  "status": "pending"
}

```

ItemResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|string(uuid)|true|none|none|
|error|any|true|none|none|

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
|item_id|string(uuid)|true|none|none|
|output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|none|
|reference|string|true|none|none|
|status|[ItemStatus](#schemaitemstatus)|true|none|none|

### ItemStatus






```json
"pending"

```

ItemStatus

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemStatus|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemStatus|pending|
|ItemStatus|canceled_user|
|ItemStatus|canceled_system|
|ItemStatus|error_user|
|ItemStatus|error_system|
|ItemStatus|succeeded|

### OrganizationCreationRequest






```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_email": "string",
  "slide_quota": 0
}

```

OrganizationCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|batch_size|integer|true|none|none|
|organization_id|string|true|none|none|
|owner_email|string|true|none|none|
|slide_quota|integer|true|none|none|

### OrganizationQuota






```json
{
  "total": 0,
  "used": 0
}

```

OrganizationQuota

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|total|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|used|integer|true|none|none|

### OrganizationResponse






```json
{
  "batch_size": 0,
  "organization_id": "string",
  "owner_id": "8826ee2e-7933-4665-aef2-2393f84a0d05",
  "slide_quota": {
    "total": 0,
    "used": 0
  }
}

```

OrganizationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|batch_size|integer|true|none|none|
|organization_id|string|true|none|none|
|owner_id|string(uuid)|true|none|none|
|slide_quota|[OrganizationQuota](#schemaorganizationquota)|true|none|none|

### OrganizationUpdateRequest






```json
{
  "batch_size": 0,
  "slide_quota": 0
}

```

OrganizationUpdateRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|batch_size|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|slide_quota|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### OutputArtifact






```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "scope": "item",
  "visibility": "internal"
}

```

OutputArtifact

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|visibility|[OutputArtifactVisibility](#schemaoutputartifactvisibility)|true|none|none|

### OutputArtifactEventTriggerRequest






```json
{
  "error": "string",
  "event": "succeeded",
  "metadata": {}
}

```

OutputArtifactEventTriggerRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|error|any|false|none|none|

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
|event|[ArtifactEvent](#schemaartifactevent)|true|none|This is a subset of the OutputArtifactEvent used by the state machine.Only the variants defined below are allowed to be submitted from the Algorithms/Applications.|
|metadata|object|true|none|none|

### OutputArtifactEventTriggerResponse






```json
{
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
  "status": "pending"
}

```

OutputArtifactEventTriggerResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|output_artifact_id|string(uuid)|true|none|none|
|status|[ArtifactStatus](#schemaartifactstatus)|true|none|none|

### OutputArtifactReadResponse






```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "scope": "item"
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
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
}

```

OutputArtifactResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|any|true|none|none|

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
|metadata|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|output_artifact_id|string(uuid)|true|none|none|

### OutputArtifactSchemaCreationRequest






```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "scope": "item",
  "visibility": "internal"
}

```

OutputArtifactSchemaCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|visibility|[OutputArtifactVisibility](#schemaoutputartifactvisibility)|true|none|none|

### OutputArtifactScope






```json
"item"

```

OutputArtifactScope

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|OutputArtifactScope|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|OutputArtifactScope|item|
|OutputArtifactScope|global|

### OutputArtifactVisibility






```json
"internal"

```

OutputArtifactVisibility

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|OutputArtifactVisibility|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|OutputArtifactVisibility|internal|
|OutputArtifactVisibility|external|

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
|input_artifact_id|string(uuid)|true|none|none|
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

### QuotaName






```json
"max_users"

```

QuotaName

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|QuotaName|string|false|none|Global, API-level, and slide-level quotas for Samia API.|

##### Enumerated Values

|Property|Value|
|---|---|
|QuotaName|max_users|
|QuotaName|max_organizations|
|QuotaName|max_users_per_organization|
|QuotaName|max_applications|
|QuotaName|max_application_versions|
|QuotaName|max_slides_per_run|
|QuotaName|max_parallel_runs|
|QuotaName|max_parallel_runs_per_organization|
|QuotaName|max_parallel_runs_per_user|

### QuotaReadResponse






```json
{
  "name": "max_users",
  "quota": 0
}

```

QuotaReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|[QuotaName](#schemaquotaname)|true|none|Global, API-level, and slide-level quotas for Samia API.|
|quota|integer|true|none|none|

### QuotaUpdateRequest






```json
{
  "name": "max_users",
  "quota": 0
}

```

QuotaUpdateRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|[QuotaName](#schemaquotaname)|true|none|Global, API-level, and slide-level quotas for Samia API.|
|quota|integer|true|none|none|

### QuotaUpdateResponse






```json
{
  "name": "max_users",
  "quota": 0
}

```

QuotaUpdateResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|[QuotaName](#schemaquotaname)|true|none|Global, API-level, and slide-level quotas for Samia API.|
|quota|integer|true|none|none|

### QuotasReadResponse






```json
{
  "quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}

```

QuotasReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|quotas|[[QuotaReadResponse](#schemaquotareadresponse)]|true|none|[GET response payload for quota read.]|

### QuotasUpdateRequest






```json
{
  "quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}

```

QuotasUpdateRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|quotas|[[QuotaUpdateRequest](#schemaquotaupdaterequest)]|true|none|[PATCH request payload for quota update.]|

### QuotasUpdateResponse






```json
{
  "updated_quotas": [
    {
      "name": "max_users",
      "quota": 0
    }
  ]
}

```

QuotasUpdateResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|updated_quotas|[[QuotaUpdateResponse](#schemaquotaupdateresponse)]|true|none|[PATCH response payload for quota update.]|

### RunCreationRequest






```json
{
  "application_version": "efbf9822-a1e5-4045-a283-dbf26e8064a9",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example.com/case-no-1-slide.tiff",
          "metadata": {
            "checksum_crc32c": "752f9554",
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
|application_version|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SlugVersionRequest](#schemaslugversionrequest)|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ItemCreationRequest](#schemaitemcreationrequest)]|true|none|none|

### RunCreationResponse






```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe"
}

```

RunCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_run_id|string(uuid)|true|none|none|

### RunReadResponse






```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
  "organization_id": "string",
  "status": "canceled_system",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "string",
  "user_payload": {
    "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
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
|application_run_id|string(uuid)|true|none|none|
|application_version_id|string(uuid)|true|none|none|
|organization_id|string|true|none|none|
|status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|none|
|triggered_at|string(date-time)|true|none|none|
|triggered_by|string|true|none|none|
|user_payload|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[UserPayload](#schemauserpayload)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### SlugVersionRequest






```json
{
  "application_slug": "string",
  "version": "string"
}

```

SlugVersionRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_slug|string|true|none|none|
|version|string|true|none|none|

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

### UserCreationRequest






```json
{
  "email": "string",
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "user_id": "string"
}

```

UserCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|email|any|true|none|none|

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
|organization_id|string(uuid)|true|none|none|
|user_id|string|true|none|none|

### UserPayload






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
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
|application_id|string(uuid)|true|none|none|
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

### UserQuota






```json
{
  "total": 0,
  "used": 0
}

```

UserQuota

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|total|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|used|integer|true|none|none|

### UserResponse






```json
{
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "slide_quota": {
    "total": 0,
    "used": 0
  },
  "user_id": "string"
}

```

UserResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|organization_id|any|true|none|none|

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
|slide_quota|[UserQuota](#schemauserquota)|true|none|none|
|user_id|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### UserUpdateRequest






```json
{
  "slide_quota": 0,
  "user_id": "string"
}

```

UserUpdateRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|slide_quota|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|user_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

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

### VersionCreationRequest






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "changelog": "string",
  "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
  "input_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string"
    }
  ],
  "output_artifacts": [
    {
      "metadata_schema": {},
      "mime_type": "application/vnd.apache.parquet",
      "name": "string",
      "scope": "item",
      "visibility": "internal"
    }
  ],
  "version": "string"
}

```

VersionCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string(uuid)|true|none|none|
|changelog|string|true|none|none|
|flow_id|string(uuid)|true|none|none|
|input_artifacts|[[InputArtifactSchemaCreationRequest](#schemainputartifactschemacreationrequest)]|true|none|none|
|output_artifacts|[[OutputArtifactSchemaCreationRequest](#schemaoutputartifactschemacreationrequest)]|true|none|none|
|version|string|true|none|none|

### VersionCreationResponse






```json
{
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c"
}

```

VersionCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_version_id|string(uuid)|true|none|none|

### VersionReadResponse






```json
{
  "application_id": "48ac72d0-a829-4896-a067-dcb1c2b0f30c",
  "application_version_id": "4108b546-90d4-4689-8b58-78cd9ef4691c",
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
      "scope": "item",
      "visibility": "internal"
    }
  ],
  "version": "string"
}

```

VersionReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string(uuid)|true|none|none|
|application_version_id|string(uuid)|true|none|none|
|changelog|string|true|none|none|
|created_at|string(date-time)|true|none|none|
|flow_id|any|false|none|none|

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
|input_artifacts|[[InputArtifact](#schemainputartifact)]|true|none|none|
|output_artifacts|[[OutputArtifact](#schemaoutputartifact)]|true|none|none|
|version|string|true|none|none|
