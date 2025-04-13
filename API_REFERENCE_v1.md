# API v1 Reference
## PAPI API Reference v1.0.0

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

Base URLs:

* 

## Externals

### list_applications_v1_applications_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/applications', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### list_versions_by_application_id_v1_applications__application_id__versions_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/applications/{application_id}/versions', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### read_application_by_slug_v1_applications__application_slug__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/applications/{application_slug}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### list_versions_by_application_slug_v1_applications__application_slug__versions_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/applications/{application_slug}/versions', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### list_application_runs_v1_runs_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/runs', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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
|status|canceled_system|
|status|canceled_user|
|status|completed|
|status|completed_with_error|
|status|received|
|status|rejected|
|status|running|
|status|scheduled|


This operation does not require authentication


### create_application_run_v1_runs_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
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
  'Accept':'application/json'
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


This operation does not require authentication


### get_run_v1_runs__application_run_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/runs/{application_run_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### cancel_run_v1_runs__application_run_id__cancel_post



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/v1/runs/{application_run_id}/cancel', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### delete_run_results_v1_runs__application_run_id__results_delete



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.delete('/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### list_run_results_v1_runs__application_run_id__results_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/runs/{application_run_id}/results', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


### register_version_v1_versions_post



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
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
  'Accept':'application/json'
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


This operation does not require authentication


### get_version_v1_versions__application_version_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/v1/versions/{application_version_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json'
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


This operation does not require authentication


## Schemas

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
