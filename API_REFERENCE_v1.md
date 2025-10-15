# API v1 Reference

## Aignostics Platform API v1.0.0-beta6

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

The Aignostics Platform is a cloud-based service that enables organizations to access advanced computational pathology applications through a secure API. The platform provides standardized access to Aignostics' portfolio of computational pathology solutions, with Atlas H&E-TME serving as an example of the available API endpoints.

To begin using the platform, your organization must first be registered by our business support team. If you don't have an account yet, please contact your account manager or email support@aignostics.com to get started.

More information about our applications can be found on (https://platform.aignostics.com).

**How to authorize and test API endpoints:**

1. Click the "Authorize" button in the right corner below
2. Click "Authorize" button in the dialog to log in with your Aignostics Platform credentials
3. After successful login, you'll be redirected back and can use "Try it out" on any endpoint

**Note**: You only need to authorize once per session. The lock icons next to endpoints will show green when authorized.

Base URLs:

- [/api](/api)

## Authentication

- oAuth2 authentication.

  - Flow: authorizationCode
  - Authorization URL = [https://aignostics-platform.eu.auth0.com/authorize](https://aignostics-platform.eu.auth0.com/authorize)
  - Token URL = [https://aignostics-platform.eu.auth0.com/oauth/token](https://aignostics-platform.eu.auth0.com/oauth/token)

| Scope | Scope Description |
| ----- | ----------------- |

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/applications", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/applications`

_List available applications_

Returns the list of the applications, available to the caller.

The application is available if any of the versions of the application is assigned to the caller’s organization.
The response is paginated and sorted according to the provided parameters.

#### Parameters

| Name      | In    | Type    | Required | Description                                                                                 |
| --------- | ----- | ------- | -------- | ------------------------------------------------------------------------------------------- |
| page      | query | integer | false    | none                                                                                        |
| page_size | query | integer | false    | none                                                                                        |
| sort      | query | any     | false    | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order. |

##### Detailed descriptions

**sort**: Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.

**Available fields:**

- `application_id`
- `name`
- `description`
- `regulatory_classes`

**Examples:**

- `?sort=application_id` - Sort by application_id ascending
- `?sort=-name` - Sort by name descending
- `?sort=+description&sort=name` - Sort by description ascending, then name descending

> Example responses

> 200 Response

```json
[
  {
    "application_id": "he-tme",
    "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
    "name": "Atlas H&E-TME",
    "regulatory_classes": ["RUO"]
  },
  {
    "application_id": "test-app",
    "description": "This is the test application with two algorithms: TissueQc and Tissue Segmentation",
    "name": "Test Application",
    "regulatory_classes": ["RUO"]
  }
]
```

> 422 Response

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                      | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | A list of applications available to the caller   | Inline                                            |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)          | Unauthorized - Invalid or missing authentication | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                 | [HTTPValidationError](#schemahttpvalidationerror) |

#### Response Schema

Status Code **200**

_Response List Applications V1 Applications Get_

| Name                                           | Type                                                        | Required | Restrictions | Description                                                                                         |
| ---------------------------------------------- | ----------------------------------------------------------- | -------- | ------------ | --------------------------------------------------------------------------------------------------- |
| Response List Applications V1 Applications Get | [[ApplicationReadResponse](#schemaapplicationreadresponse)] | false    | none         | [Response schema for `List available applications` and `Read Application by Id` endpoints]          |
| » ApplicationReadResponse                      | [ApplicationReadResponse](#schemaapplicationreadresponse)   | false    | none         | Response schema for `List available applications` and `Read Application by Id` endpoints            |
| »» application_id                              | string                                                      | true     | none         | Application ID                                                                                      |
| »» description                                 | string                                                      | true     | none         | Describing what the application can do                                                              |
| »» name                                        | string                                                      | true     | none         | Application display name                                                                            |
| »» regulatory_classes                          | [string]                                                    | true     | none         | Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA. |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### read_application_by_id_v1_applications**application_id**get

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/applications/{application_id}', headers = headers)

print(r.json())

```

```javascript
const headers = {
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/applications/{application_id}", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/applications/{application_id}`

_Read Application By Id_

Retrieve details of a specific application by its ID.

#### Parameters

| Name           | In   | Type   | Required | Description |
| -------------- | ---- | ------ | -------- | ----------- |
| application_id | path | string | true     | none        |

> Example responses

> 200 Response

```json
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "name": "Atlas H&E-TME",
  "regulatory_classes": ["RUO"]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                                   | Schema                                                    |
| ------ | ------------------------------------------------------------------------ | ------------------------------------------------------------- | --------------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response                                           | [ApplicationReadResponse](#schemaapplicationreadresponse) |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to see this application | None                                                      |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Not Found - Application with the given ID does not exist      | None                                                      |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                              | [HTTPValidationError](#schemahttpvalidationerror)         |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### list_versions_by_application_id_v1_applications**application_id**versions_get

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/applications/{application_id}/versions", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/applications/{application_id}/versions`

_List Available Application Versions_

Returns a list of available application versions for a specific application.

A version is considered available when it has been assigned to your organization. Within a major version,
all minor and patch updates are automatically accessible unless a specific version has been deprecated.
Major version upgrades, however, require explicit assignment and may be subject to contract modifications
before becoming available to your organization.

#### Parameters

| Name           | In    | Type    | Required | Description                                                                                 |
| -------------- | ----- | ------- | -------- | ------------------------------------------------------------------------------------------- |
| application_id | path  | string  | true     | none                                                                                        |
| page           | query | integer | false    | none                                                                                        |
| page_size      | query | integer | false    | none                                                                                        |
| version        | query | any     | false    | Semantic version of the application, example: `1.0.13`                                      |
| sort           | query | any     | false    | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order. |

##### Detailed descriptions

**sort**: Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.

**Available fields:**

- `application_version_id`
- `version`
- `application_id`
- `changelog`
- `created_at`

**Examples:**

- `?sort=application_id` - Sort by application_id ascending
- `?sort=-version` - Sort by version descending
- `?sort=+application_id&sort=-created_at` - Sort by application_id ascending, then created_at descending

> Example responses

> 200 Response

```json
[
  {
    "application_id": "he-tme",
    "application_version_id": "he-tme:v0.5.0",
    "changelog": "Redeployed after metadata name changes. ",
    "created_at": "2025-06-03T11:45:55.646211Z",
    "input_artifacts": [
      {
        "metadata_schema": {
          "$defs": {
            "LungCancerSpecimen": {
              "additionalProperties": false,
              "properties": {
                "disease": {
                  "const": "LUNG_CANCER",
                  "enum": ["LUNG_CANCER"],
                  "title": "Disease",
                  "type": "string"
                },
                "tissue": {
                  "enum": [
                    "LUNG",
                    "LYMPH_NODE",
                    "LIVER",
                    "ADRENAL_GLAND",
                    "BONE",
                    "BRAIN"
                  ],
                  "title": "Tissue",
                  "type": "string"
                }
              },
              "required": ["disease", "tissue"],
              "title": "LungCancerSpecimen",
              "type": "object"
            }
          },
          "$schema": "http://json-schema.org/draft-07/schema#",
          "additionalProperties": false,
          "description": "Schema of a slide.",
          "properties": {
            "checksum_base64_crc32c": {
              "title": "Base64 encoded big-endian CRC32C checksum",
              "type": "string"
            },
            "height_px": {
              "minimum": 1,
              "title": "Height (px)",
              "type": "integer"
            },
            "media_type": {
              "enum": [
                "application/dicom",
                "image/tiff",
                "application/octet-stream",
                "application/zip"
              ],
              "title": "Media Type",
              "type": "string"
            },
            "resolution_mpp": {
              "maximum": 0.5,
              "minimum": 0.125,
              "title": "Resolution (mpp)",
              "type": "number"
            },
            "specimen": {
              "anyOf": [false],
              "title": "Specimen"
            },
            "staining_method": {
              "const": "H&E",
              "enum": ["H&E"],
              "title": "Staining Method",
              "type": "string"
            },
            "width_px": {
              "minimum": 1,
              "title": "Width (px)",
              "type": "integer"
            }
          },
          "required": [
            "media_type",
            "checksum_base64_crc32c",
            "specimen",
            "resolution_mpp",
            "width_px",
            "height_px",
            "staining_method"
          ],
          "title": "Slide Schema",
          "type": "object"
        },
        "mime_type": "image/tiff",
        "name": "user_slide"
      }
    ],
    "output_artifacts": [
      {
        "metadata_schema": {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "additionalProperties": false,
          "description": "Metadata corresponding to GeoJSON polygons.",
          "properties": {
            "checksum_base64_crc32c": {
              "title": "Base64 encoded big-endian CRC32C checksum",
              "type": "string"
            },
            "media_type": {
              "const": "application/geo+json",
              "default": "application/geo+json",
              "enum": ["application/geo+json"],
              "title": "Media Type",
              "type": "string"
            },
            "polygon_mpp": {
              "title": "Polygon Mpp",
              "type": "number"
            }
          },
          "required": ["checksum_base64_crc32c", "polygon_mpp"],
          "title": "GeoJsonPolygonsMetadata",
          "type": "object"
        },
        "mime_type": "image/tiff",
        "name": "tissue_qc:geojson_polygons",
        "scope": "ITEM"
      }
    ],
    "version": "0.5.0"
  }
]
```

> 422 Response

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                                                       | Schema                                            |
| ------ | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | A list of application versions for a given application ID available to the caller | Inline                                            |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)          | Unauthorized - Invalid or missing authentication                                  | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                                                  | [HTTPValidationError](#schemahttpvalidationerror) |

#### Response Schema

Status Code **200**

_Response List Versions By Application Id V1 Applications Application Id Versions Get_

| Name                                                                                 | Type                                                                      | Required | Restrictions | Description                                                          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | -------- | ------------ | -------------------------------------------------------------------- |
| Response List Versions By Application Id V1 Applications Application Id Versions Get | [[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)] | false    | none         | [Response schema for `List Available Application Versions` endpoint] |
| » ApplicationVersionReadResponse                                                     | [ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)   | false    | none         | Response schema for `List Available Application Versions` endpoint   |
| »» application_id                                                                    | string                                                                    | true     | none         | Application ID                                                       |
| »» application_version_id                                                            | string                                                                    | true     | none         | Application version ID                                               |
| »» changelog                                                                         | string                                                                    | true     | none         | Description of the changes relative to the previous version          |
| »» created_at                                                                        | string(date-time)                                                         | true     | none         | The timestamp when the application version was registered            |
| »» flow_id                                                                           | any                                                                       | false    | none         | Flow ID, used internally by the platform                             |

_anyOf_

| Name            | Type         | Required | Restrictions | Description |
| --------------- | ------------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | string(uuid) | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name                           | Type                                                              | Required | Restrictions | Description                                                              |
| ------------------------------ | ----------------------------------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------ |
| »» input_artifacts             | [[InputArtifactReadResponse](#schemainputartifactreadresponse)]   | true     | none         | Lists required input fields, that should be provided by the caller       |
| »»» InputArtifactReadResponse  | [InputArtifactReadResponse](#schemainputartifactreadresponse)     | false    | none         | none                                                                     |
| »»»» metadata_schema           | object                                                            | true     | none         | none                                                                     |
| »»»» mime_type                 | string                                                            | true     | none         | none                                                                     |
| »»»» name                      | string                                                            | true     | none         | none                                                                     |
| »» output_artifacts            | [[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)] | true     | none         | Lists the structure of the output artifacts generated by the application |
| »»» OutputArtifactReadResponse | [OutputArtifactReadResponse](#schemaoutputartifactreadresponse)   | false    | none         | none                                                                     |
| »»»» metadata_schema           | object                                                            | true     | none         | none                                                                     |
| »»»» mime_type                 | string                                                            | true     | none         | none                                                                     |
| »»»» name                      | string                                                            | true     | none         | none                                                                     |
| »»»» scope                     | [OutputArtifactScope](#schemaoutputartifactscope)                 | true     | none         | none                                                                     |
| »» version                     | string                                                            | true     | none         | Semantic version of the application                                      |

##### Enumerated Values

| Property | Value  |
| -------- | ------ |
| scope    | ITEM   |
| scope    | GLOBAL |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### get_item_v1_items**item_id**get

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/items/{item_id}', headers = headers)

print(r.json())

```

```javascript
const headers = {
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/items/{item_id}", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/items/{item_id}`

_Get Item_

Retrieve details of a specific item (slide) by its ID.

#### Parameters

| Name    | In   | Type         | Required | Description |
| ------- | ---- | ------------ | -------- | ----------- |
| item_id | path | string(uuid) | true     | none        |

> Example responses

> 200 Response

```json
{
  "application_run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "message": "Processing started",
  "reference": "sample-123",
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}
```

#### Responses

| Status | Meaning                                                                  | Description                                            | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response                                    | [ItemReadResponse](#schemaitemreadresponse)       |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to see this item | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Not Found - Item with given ID does not exist          | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                       | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### get_me_v1_me_get

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/me', headers = headers)

print(r.json())

```

```javascript
const headers = {
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/me", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/me`

_Get current user_

Retrieves your identity details, including name, email, and organization.
This is useful for verifying that the request is being made under the correct user profile
and organization context, as well as confirming that the expected environment variables are correctly set
(in case you are using Python SDK)

> Example responses

> 200 Response

```json
{
  "organization": {
    "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aignostics_bucket_name": "aignostics-platform-bucket",
    "aignostics_bucket_protocol": "gs",
    "aignostics_logfire_token": "your-logfire-token",
    "aignostics_sentry_dsn": "https://2354s3#ewsha@o44.ingest.us.sentry.io/34345123432",
    "display_name": "Aignostics GmbH",
    "id": "org_123456",
    "name": "aignx"
  },
  "user": {
    "email": "user@domain.com",
    "email_verified": true,
    "family_name": "Doe",
    "given_name": "Jane",
    "id": "auth0|123456",
    "name": "Jane Doe",
    "nickname": "jdoe",
    "picture": "https://example.com/jdoe.jpg",
    "updated_at": "2023-10-05T14:48:00.000Z"
  }
}
```

#### Responses

| Status | Meaning                                                 | Description         | Schema                                  |
| ------ | ------------------------------------------------------- | ------------------- | --------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1) | Successful Response | [MeReadResponse](#schemamereadresponse) |

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/runs", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/runs`

_List Application Runs_

List application runs with filtering, sorting, and pagination capabilities.

Returns paginated application runs that were triggered by the user.

#### Parameters

| Name                | In    | Type    | Required | Description                                                                                 |
| ------------------- | ----- | ------- | -------- | ------------------------------------------------------------------------------------------- |
| application_id      | query | any     | false    | Optional application ID filter                                                              |
| application_version | query | any     | false    | Optional application version filter                                                         |
| metadata            | query | any     | false    | Use PostgreSQL JSONPath expressions to filter runs by their metadata.                       |
| page                | query | integer | false    | none                                                                                        |
| page_size           | query | integer | false    | none                                                                                        |
| sort                | query | any     | false    | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order. |

##### Detailed descriptions

**metadata**: Use PostgreSQL JSONPath expressions to filter runs by their metadata.

##### URL Encoding Required

**Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.

##### Examples (Clear Format):

- **Field existence**: `$.project` - Runs that have a project field defined
- **Exact value match**: `$.project ? (@ == "cancer-research")` - Runs with specific project value
- **Numeric comparison**: `$.duration_hours ? (@  2 && @.memory_gb >= 16)` - Runs with high resource requirements

##### Examples (URL-Encoded Format):

- **Field existence**: `%24.project`
- **Exact value match**: `%24.project%20%3F%20(%40%20%3D%3D%20%22cancer-research%22)`
- **Numeric comparison**: `%24.duration_hours%20%3F%20(%40%20%3C%202)`
- **Array operations**: `%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22production%22)`
- **Complex conditions**: `%24.resources%20%3F%20(%40.gpu_count%20%3E%202%20%26%26%20%40.memory_gb%20%3E%3D%2016)`

##### Notes

- JSONPath expressions are evaluated using PostgreSQL's `@?` operator
- The `$.` prefix is automatically added to root-level field references if missing
- String values in conditions must be enclosed in double quotes
- Use `&&` for AND operations and `||` for OR operations
- Regular expressions use `like_regex` with standard regex syntax
- **Remember to URL-encode the entire JSONPath expression when making HTTP requests**

**sort**: Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.

**Available fields:**

- `application_run_id`
- `application_version_id`
- `organization_id`
- `status`
- `triggered_at`
- `triggered_by`

**Examples:**

- `?sort=triggered_at` - Sort by creation time (ascending)
- `?sort=-triggered_at` - Sort by creation time (descending)
- `?sort=status&sort=-triggered_at` - Sort by status, then by time (descending)

> Example responses

> 200 Response

```json
[
  {
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "application_version_id": "he-tme:v0.4.4",
    "message": "The run was cancelled because the threshold of 3 items finishing in error state was reached. Query /runs/{run_id}/results to get the error message per item.",
    "metadata": {
      "department": "D1",
      "study": "abc-1"
    },
    "organization_id": "org-123",
    "status": "CANCELED_SYSTEM",
    "terminated_at": "2024-01-15T10:30:45.123Z",
    "triggered_at": "2019-08-24T14:15:22Z",
    "triggered_by": "auth0|123456",
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

| Status | Meaning                                                                  | Description               | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ------------------------- | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response       | Inline                                            |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Application run not found | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error          | [HTTPValidationError](#schemahttpvalidationerror) |

#### Response Schema

Status Code **200**

_Response List Application Runs V1 Runs Get_

| Name                                       | Type                                        | Required | Restrictions | Description                                      |
| ------------------------------------------ | ------------------------------------------- | -------- | ------------ | ------------------------------------------------ |
| Response List Application Runs V1 Runs Get | [[RunReadResponse](#schemarunreadresponse)] | false    | none         | [Response schema for `Get run details` endpoint] |
| » RunReadResponse                          | [RunReadResponse](#schemarunreadresponse)   | false    | none         | Response schema for `Get run details` endpoint   |
| »» application_run_id                      | string(uuid)                                | true     | none         | UUID of the application                          |
| »» application_version_id                  | string                                      | true     | none         | ID of the application version                    |
| »» message                                 | any                                         | true     | none         | The description of the run error                 |

_anyOf_

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | string | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name        | Type | Required | Restrictions | Description                                                                         |
| ----------- | ---- | -------- | ------------ | ----------------------------------------------------------------------------------- |
| »» metadata | any  | false    | none         | Optional JSON metadata that was stored in alongside the application run by the user |

_anyOf_

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | object | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name               | Type                                                | Required | Restrictions | Description                                                          |
| ------------------ | --------------------------------------------------- | -------- | ------------ | -------------------------------------------------------------------- |
| »» organization_id | string                                              | true     | none         | Organization of the owner of the application run                     |
| »» status          | [ApplicationRunStatus](#schemaapplicationrunstatus) | true     | none         | none                                                                 |
| »» terminated_at   | any                                                 | false    | none         | Timestamp showing when the application run reached a terminal state. |

_anyOf_

| Name            | Type              | Required | Restrictions | Description |
| --------------- | ----------------- | -------- | ------------ | ----------- |
| »»» _anonymous_ | string(date-time) | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name            | Type              | Required | Restrictions | Description                                              |
| --------------- | ----------------- | -------- | ------------ | -------------------------------------------------------- |
| »» triggered_at | string(date-time) | true     | none         | Timestamp showing when the application run was triggered |
| »» triggered_by | string            | true     | none         | Id of the user who triggered the application run         |
| »» user_payload | any               | false    | none         | Field used internally by the Platform                    |

_anyOf_

| Name                         | Type                              | Required | Restrictions | Description |
| ---------------------------- | --------------------------------- | -------- | ------------ | ----------- |
| »»» _anonymous_              | [UserPayload](#schemauserpayload) | false    | none         | none        |
| »»»» application_id          | string                            | true     | none         | none        |
| »»»» application_run_id      | string(uuid)                      | true     | none         | none        |
| »»»» global_output_artifacts | any                               | true     | none         | none        |

_anyOf_

| Name                         | Type                                                  | Required | Restrictions | Description |
| ---------------------------- | ----------------------------------------------------- | -------- | ------------ | ----------- |
| »»»»» _anonymous_            | object                                                | false    | none         | none        |
| »»»»»» PayloadOutputArtifact | [PayloadOutputArtifact](#schemapayloadoutputartifact) | false    | none         | none        |
| »»»»»»» data                 | [TransferUrls](#schematransferurls)                   | true     | none         | none        |
| »»»»»»»» download_url        | string(uri)                                           | true     | none         | none        |
| »»»»»»»» upload_url          | string(uri)                                           | true     | none         | none        |
| »»»»»»» metadata             | [TransferUrls](#schematransferurls)                   | true     | none         | none        |
| »»»»»»» output_artifact_id   | string(uuid)                                          | true     | none         | none        |

_or_

| Name              | Type | Required | Restrictions | Description |
| ----------------- | ---- | -------- | ------------ | ----------- |
| »»»»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name                          | Type                                                  | Required | Restrictions | Description |
| ----------------------------- | ----------------------------------------------------- | -------- | ------------ | ----------- |
| »»»» items                    | [[PayloadItem](#schemapayloaditem)]                   | true     | none         | none        |
| »»»»» PayloadItem             | [PayloadItem](#schemapayloaditem)                     | false    | none         | none        |
| »»»»»» input_artifacts        | object                                                | true     | none         | none        |
| »»»»»»» PayloadInputArtifact  | [PayloadInputArtifact](#schemapayloadinputartifact)   | false    | none         | none        |
| »»»»»»»» download_url         | string(uri)                                           | true     | none         | none        |
| »»»»»»»» input_artifact_id    | string(uuid)                                          | false    | none         | none        |
| »»»»»»»» metadata             | object                                                | true     | none         | none        |
| »»»»»» item_id                | string(uuid)                                          | true     | none         | none        |
| »»»»»» output_artifacts       | object                                                | true     | none         | none        |
| »»»»»»» PayloadOutputArtifact | [PayloadOutputArtifact](#schemapayloadoutputartifact) | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

##### Enumerated Values

| Property | Value                |
| -------- | -------------------- |
| status   | CANCELED_SYSTEM      |
| status   | CANCELED_USER        |
| status   | COMPLETED            |
| status   | COMPLETED_WITH_ERROR |
| status   | RECEIVED             |
| status   | REJECTED             |
| status   | RUNNING              |
| status   | SCHEDULED            |

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
  "application_version_id": "he-tme:v1.0.0-beta",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example-bucket.s3.amazonaws.com/slide1.tiff?signature=...",
          "metadata": {
            "checksum_base64_crc32c": "64RKKA==",
            "height_px": 87761,
            "media-type": "image/tiff",
            "resolution_mpp": 0.2628238,
            "specimen": {
              "disease": "LUNG_CANCER",
              "tissue": "LUNG"
            },
            "staining_method": "H&E",
            "width_px": 136223
          },
          "name": "input_slide"
        }
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
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

_Initiate Application Run_

This endpoint initiates a processing run for a selected application version and returns an `application_run_id` for tracking purposes.

Slide processing occurs asynchronously, allowing you to retrieve results for individual slides as soon as they
complete processing. The system typically processes slides in batches of four, though this number may be reduced
during periods of high demand.
Below is an example of the required payload for initiating an Atlas H&E TME processing run.

#### Payload

The payload includes `application_version_id` and `items` base fields.

`application_version_id` is the id used for `/v1/versions/{application_id}` endpoint.

`items` includes the list of the items to process (slides, in case of HETA application).
Every item has a set of standard fields defined by the API, plus the metadata, specific to the
chosen application.

Example payload structure with the comments:

```
{
    application_version_id: "he-tme:v1.0.0-beta",
    items: [{
        "reference": "slide_1",
        "input_artifacts": [{
            "name": "user_slide",
            "download_url": "https://...",
            "metadata": {
                "specimen": {
                  "disease": "LUNG_CANCER",
                  "tissue": "LUNG"
                },
                "staining_method": "H&E",
                "width_px": 136223,
                "height_px": 87761,
                "resolution_mpp": 0.2628238,
                "media-type":"image/tiff",
                "checksum_base64_crc32c": "64RKKA=="
            }
        }]
    }]
}
```

| Parameter                         | Description                                                                                                                                                                                          |
| :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `application_version_id` required | Unique ID for the application (must include version)                                                                                                                                                 |
| `items` required                  | List of submitted items (WSIs) with parameters described below.                                                                                                                                      |
| `reference` required              | Unique WSI name or ID for easy reference to results, provided by the caller. The reference should be unique across all items of the application run.                                                 |
| `input_artifacts` required        | List of provided artifacts for a WSI; at the moment Atlas H&E-TME receives only 1 artifact per slide (the slide itself), but for some other applications this can be a slide and an segmentation map |
| `name` required                   | Type of artifact; Atlas H&E-TME supports only `"input_slide"`                                                                                                                                        |
| `download_url` required           | Signed URL to the input file in the S3 or GCS; Should be valid for at least 6 days                                                                                                                   |
| `specimen: disease` required      | Supported cancer types for Atlas H&E-TME (see full list in Atlas H&E-TME manual)                                                                                                                     |
| `specimen: tissue` required       | Supported tissue types for Atlas H&E-TME (see full list in Atlas H&E-TME manual)                                                                                                                     |
| `staining_method` required        | WSI stain /bio-marker; Atlas H&E-TME supports only `"H&E"`                                                                                                                                           |
| `width_px` required               | Integer value. Number of pixels of the WSI in the X dimension.                                                                                                                                       |
| `height_px` required              | Integer value. Number of pixels of the WSI in the Y dimension.                                                                                                                                       |
| `resolution_mpp` required         | Resolution of WSI in micrometers per pixel; check allowed range in Atlas H&E-TME manual                                                                                                              |
| `media-type` required             | Supported media formats; available values are: image/tiff (for .tiff or .tif WSI) application/dicom (for DICOM ) application/zip (for zipped DICOM) application/octet-stream (for .svs WSI)          |
| `checksum_base64_crc32c` required | Base64 encoded big-endian CRC32C checksum of the WSI image                                                                                                                                           |

#### Response

The endpoint returns the application run UUID. After that the job is scheduled for the
execution in the background.

To check the status of the run call `v1/runs/{application_run_id}`.

#### Rejection

Apart from the authentication, authorization and malformed input error, the request can be
rejected when the quota limit is exceeded. More details on quotas is described in the
documentation

> Body parameter

```json
{
  "application_version_id": "he-tme:v1.0.0-beta",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example-bucket.s3.amazonaws.com/slide1.tiff?signature=...",
          "metadata": {
            "checksum_base64_crc32c": "64RKKA==",
            "height_px": 87761,
            "media-type": "image/tiff",
            "resolution_mpp": 0.2628238,
            "specimen": {
              "disease": "LUNG_CANCER",
              "tissue": "LUNG"
            },
            "staining_method": "H&E",
            "width_px": 136223
          },
          "name": "input_slide"
        }
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
}
```

#### Parameters

| Name | In   | Type                                            | Required | Description |
| ---- | ---- | ----------------------------------------------- | -------- | ----------- |
| body | body | [RunCreationRequest](#schemaruncreationrequest) | true     | none        |

> Example responses

> 201 Response

```json
{
  "application_run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

#### Responses

| Status | Meaning                                                                  | Description                                              | Schema                                            |
| ------ | ------------------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------- |
| 201    | [Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)             | Successful Response                                      | [RunCreationResponse](#schemaruncreationresponse) |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)         | Bad Request - Input validation failed                    | None                                              |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to create this run | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Application version not found                            | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                         | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### get_run_v1_runs**application_run_id**get

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/runs/{application_run_id}", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/runs/{application_run_id}`

_Get run details_

This endpoint allows the caller to retrieve the current status of an application run along with other relevant run details.
A run becomes available immediately after it is created through the POST `/runs/` endpoint.

To download the output results, use GET `/runs/{application_run_id}/` results to get outputs for all slides.
Access to a run is restricted to the user who created it.

#### Parameters

| Name               | In   | Type         | Required | Description                                            |
| ------------------ | ---- | ------------ | -------- | ------------------------------------------------------ |
| application_run_id | path | string(uuid) | true     | Application run id, returned by `POST /runs/` endpoint |

> Example responses

> 200 Response

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "he-tme:v0.4.4",
  "message": "The run was cancelled because the threshold of 3 items finishing in error state was reached. Query /runs/{run_id}/results to get the error message per item.",
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "organization_id": "org-123",
  "status": "CANCELED_SYSTEM",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "auth0|123456",
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

| Status | Meaning                                                                  | Description                                           | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response                                   | [RunReadResponse](#schemarunreadresponse)         |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to see this run | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Application run not found because it was deleted.     | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                      | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### cancel_application_run_v1_runs**application_run_id**cancel_post

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/runs/{application_run_id}/cancel", {
  method: "POST",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`POST /v1/runs/{application_run_id}/cancel`

_Cancel Application Run_

The application run can be canceled by the user who created the application run.

The execution can be canceled any time while the application is not in a final state. The
pending items will not be processed and will not add to the cost.

When the application is canceled, the already completed items stay available for download.

#### Parameters

| Name               | In   | Type         | Required | Description                                            |
| ------------------ | ---- | ------------ | -------- | ------------------------------------------------------ |
| application_run_id | path | string(uuid) | true     | Application run id, returned by `POST /runs/` endpoint |

> Example responses

> 422 Response

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                              | Schema                                            |
| ------ | ------------------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------- |
| 202    | [Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)            | Run cancelled successfully                               | None                                              |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to cancel this run | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Run not found                                            | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                         | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### delete_application_run_results_v1_runs**application_run_id**results_delete

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/runs/{application_run_id}/results", {
  method: "DELETE",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`DELETE /v1/runs/{application_run_id}/results`

_Delete Application Run Results_

This endpoint allows the caller to explicitly delete outputs generated by an application.
It can only be invoked when the application run has reached a final state
(COMPLETED, COMPLETED_WITH_ERROR, CANCELED_USER, or CANCELED_SYSTEM).
Note that by default, all outputs are automatically deleted 30 days after the application run finishes,
regardless of whether the caller explicitly requests deletion.

#### Parameters

| Name               | In   | Type         | Required | Description                                            |
| ------------------ | ---- | ------------ | -------- | ------------------------------------------------------ |
| application_run_id | path | string(uuid) | true     | Application run id, returned by `POST /runs/` endpoint |

> Example responses

> 422 Response

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                  | Schema                                            |
| ------ | ------------------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------- |
| 204    | [No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)          | All application outputs successfully deleted | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Application run not found                    | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                             | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### list_run_results_v1_runs**application_run_id**results_get

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
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/runs/{application_run_id}/results", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/runs/{application_run_id}/results`

_List Run Results_

List results for items in an application run with filtering, sorting, and pagination capabilities.

Returns paginated results for items within a specific application run. Results can be filtered
by item IDs, references, status, and custom metadata using JSONPath expressions.

### JSONPath Metadata Filtering

Use PostgreSQL JSONPath expressions to filter results by their metadata.

#### Examples:

- **Field existence**: `$.case_id` - Results that have a case_id field defined
- **Exact value match**: `$.priority ? (@ == "high")` - Results with high priority
- **Numeric comparison**: `$.confidence_score ? (@ > 0.95)` - Results with high confidence
- **Array operations**: `$.flags[*] ? (@ == "reviewed")` - Results flagged as reviewed
- **Complex conditions**: `$.metrics ? (@.accuracy > 0.9 && @.recall > 0.8)` - Results meeting performance thresholds

### Notes

- JSONPath expressions are evaluated using PostgreSQL's `@?` operator
- The `$.` prefix is automatically added to root-level field references if missing
- String values in conditions must be enclosed in double quotes
- Use `&&` for AND operations and `||` for OR operations

#### Parameters

| Name               | In    | Type         | Required | Description                                                                                 |
| ------------------ | ----- | ------------ | -------- | ------------------------------------------------------------------------------------------- |
| application_run_id | path  | string(uuid) | true     | Application run id, returned by `POST /runs/` endpoint                                      |
| item_id\_\_in      | query | any          | false    | Filter for items ids                                                                        |
| reference\_\_in    | query | any          | false    | Filter for items by their reference from the input payload                                  |
| status\_\_in       | query | any          | false    | Filter for items in certain statuses                                                        |
| metadata           | query | any          | false    | JSONPath expression to filter results by their metadata                                     |
| page               | query | integer      | false    | none                                                                                        |
| page_size          | query | integer      | false    | none                                                                                        |
| sort               | query | any          | false    | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order. |

##### Detailed descriptions

**sort**: Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.
**Available fields:**

- `item_id`
- `application_run_id`
- `reference`
- `status`
- `metadata`

**Examples:**

- `?sort=item_id` - Sort by id of the item (ascending)
- `?sort=-application_run_id` - Sort by id of the run (descending)
- `?sort=status&sort=-item_idt` - Sort by status, then by id of the item (descending)

> Example responses

> 200 Response

```json
[
  {
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "error": "string",
    "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
    "message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
    "metadata": {},
    "output_artifacts": [
      {
        "download_url": "http://example.com",
        "metadata": {},
        "name": "tissue_qc:tiff_heatmap",
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
      }
    ],
    "reference": "slide_1",
    "status": "PENDING",
    "terminated_at": "2024-01-15T10:30:45.123Z"
  }
]
```

#### Responses

| Status | Meaning                                                                  | Description               | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ------------------------- | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response       | Inline                                            |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Application run not found | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error          | [HTTPValidationError](#schemahttpvalidationerror) |

#### Response Schema

Status Code **200**

_Response List Run Results V1 Runs Application Run Id Results Get_

| Name                                                             | Type                                                      | Required | Restrictions | Description                                                                   |
| ---------------------------------------------------------------- | --------------------------------------------------------- | -------- | ------------ | ----------------------------------------------------------------------------- |
| Response List Run Results V1 Runs Application Run Id Results Get | [[ItemResultReadResponse](#schemaitemresultreadresponse)] | false    | none         | [Response schema for items in `List Run Results` endpoint]                    |
| » ItemResultReadResponse                                         | [ItemResultReadResponse](#schemaitemresultreadresponse)   | false    | none         | Response schema for items in `List Run Results` endpoint                      |
| »» application_run_id                                            | string(uuid)                                              | true     | none         | Application run UUID to which the item belongs                                |
| »» error                                                         | any                                                       | false    | none         | The error message in case the item is in `error_system` or `error_user` state |

_anyOf_

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | string | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name       | Type         | Required | Restrictions | Description                                                                   |
| ---------- | ------------ | -------- | ------------ | ----------------------------------------------------------------------------- |
| »» item_id | string(uuid) | true     | none         | Item UUID generated by the Platform                                           |
| »» message | any          | true     | none         | The error message in case the item is in `error_system` or `error_user` state |

_anyOf_

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | string | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name        | Type | Required | Restrictions | Description                                                                              |
| ----------- | ---- | -------- | ------------ | ---------------------------------------------------------------------------------------- |
| »» metadata | any  | true     | none         | The metadata of the item that has been provided by the user on application run creation. |

_anyOf_

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| »»» _anonymous_ | object | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name                                 | Type                                                                          | Required | Restrictions | Description                                                                                                                                                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| »» output_artifacts                  | [[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)] | true     | none         | The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details. |
| »»» OutputArtifactResultReadResponse | [OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)   | false    | none         | none                                                                                                                                                                                                 |
| »»»» download_url                    | any                                                                           | true     | none         | The download URL to the output file. The URL is valid for 1 hour after the endpoint is called.A new URL is generated every time the endpoint is called.                                              |

_anyOf_

| Name              | Type        | Required | Restrictions | Description |
| ----------------- | ----------- | -------- | ------------ | ----------- |
| »»»»» _anonymous_ | string(uri) | false    | none         | none        |

_or_

| Name              | Type | Required | Restrictions | Description |
| ----------------- | ---- | -------- | ------------ | ----------- |
| »»»»» _anonymous_ | null | false    | none         | none        |

_continued_

| Name                    | Type                            | Required | Restrictions | Description                                                                              |
| ----------------------- | ------------------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------- |
| »»»» metadata           | object                          | true     | none         | The metadata of the output artifact, provided by the application                         |
| »»»» name               | string                          | true     | none         | Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint. |
| »»»» output_artifact_id | string(uuid)                    | true     | none         | The Id of the artifact. Used internally                                                  |
| »» reference            | string                          | true     | none         | The reference of the item from the user payload                                          |
| »» status               | [ItemStatus](#schemaitemstatus) | true     | none         | none                                                                                     |
| »» terminated_at        | any                             | false    | none         | Timestamp showing when the item reached a terminal state.                                |

_anyOf_

| Name            | Type              | Required | Restrictions | Description |
| --------------- | ----------------- | -------- | ------------ | ----------- |
| »»» _anonymous_ | string(date-time) | false    | none         | none        |

_or_

| Name            | Type | Required | Restrictions | Description |
| --------------- | ---- | -------- | ------------ | ----------- |
| »»» _anonymous_ | null | false    | none         | none        |

##### Enumerated Values

| Property | Value           |
| -------- | --------------- |
| status   | PENDING         |
| status   | CANCELED_USER   |
| status   | CANCELED_SYSTEM |
| status   | ERROR_USER      |
| status   | ERROR_SYSTEM    |
| status   | SUCCEEDED       |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

### application_version_details_v1_versions**application_version_id**get

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/versions/{application_version_id}', headers = headers)

print(r.json())

```

```javascript
const headers = {
  Accept: "application/json",
  Authorization: "Bearer {access-token}",
};

fetch("/api/v1/versions/{application_version_id}", {
  method: "GET",

  headers: headers,
})
  .then(function (res) {
    return res.json();
  })
  .then(function (body) {
    console.log(body);
  });
```

`GET /v1/versions/{application_version_id}`

_Application Version Details_

Get the application version details

Allows caller to retrieve information about application version based on provided application version ID.

#### Parameters

| Name                   | In   | Type   | Required | Description |
| ---------------------- | ---- | ------ | -------- | ----------- |
| application_version_id | path | string | true     | none        |

> Example responses

> 200 Response

```json
{
  "application_id": "he-tme",
  "application_version_id": "he-tme:v0.4.4",
  "changelog": "New deployment",
  "created_at": "2025-04-16T08:45:20.655972Z",
  "input_artifacts": [
    {
      "metadata_schema": {
        "$defs": {
          "LungCancerMetadata": {
            "additionalProperties": false,
            "properties": {
              "tissue": {
                "enum": [
                  "lung",
                  "lymph node",
                  "liver",
                  "adrenal gland",
                  "bone",
                  "brain"
                ],
                "title": "Tissue",
                "type": "string"
              },
              "type": {
                "const": "lung",
                "enum": ["lung"],
                "title": "Type",
                "type": "string"
              }
            },
            "required": ["type", "tissue"],
            "title": "LungCancerMetadata",
            "type": "object"
          }
        },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": false,
        "description": "Metadata corresponding to an external image.",
        "properties": {
          "base_mpp": {
            "maximum": 0.5,
            "minimum": 0.125,
            "title": "Base Mpp",
            "type": "number"
          },
          "cancer": {
            "anyOf": [false],
            "title": "Cancer"
          },
          "checksum_crc32c": {
            "title": "Checksum Crc32C",
            "type": "string"
          },
          "height": {
            "maximum": 150000,
            "minimum": 1,
            "title": "Height",
            "type": "integer"
          },
          "mime_type": {
            "default": "image/tiff",
            "enum": ["application/dicom", "image/tiff"],
            "title": "Mime Type",
            "type": "string"
          },
          "stain": {
            "const": "H&E",
            "default": "H&E",
            "enum": ["H&E"],
            "title": "Stain",
            "type": "string"
          },
          "width": {
            "maximum": 150000,
            "minimum": 1,
            "title": "Width",
            "type": "integer"
          }
        },
        "required": [
          "checksum_crc32c",
          "base_mpp",
          "width",
          "height",
          "cancer"
        ],
        "title": "ExternalImageMetadata",
        "type": "object"
      },
      "mime_type": "image/tiff",
      "name": "user_slide"
    }
  ],
  "output_artifacts": [
    {
      "metadata_schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": false,
        "description": "Metadata corresponding to a segmentation heatmap file.",
        "properties": {
          "base_mpp": {
            "maximum": 0.5,
            "minimum": 0.125,
            "title": "Base Mpp",
            "type": "number"
          },
          "checksum_crc32c": {
            "title": "Checksum Crc32C",
            "type": "string"
          },
          "class_colors": {
            "additionalProperties": {
              "maxItems": 3,
              "minItems": 3,
              "prefixItems": [
                {
                  "maximum": 255,
                  "minimum": 0,
                  "type": "integer"
                },
                {
                  "maximum": 255,
                  "minimum": 0,
                  "type": "integer"
                },
                {
                  "maximum": 255,
                  "minimum": 0,
                  "type": "integer"
                }
              ],
              "type": "array"
            },
            "title": "Class Colors",
            "type": "object"
          },
          "height": {
            "title": "Height",
            "type": "integer"
          },
          "mime_type": {
            "const": "image/tiff",
            "default": "image/tiff",
            "enum": ["image/tiff"],
            "title": "Mime Type",
            "type": "string"
          },
          "width": {
            "title": "Width",
            "type": "integer"
          }
        },
        "required": ["checksum_crc32c", "width", "height", "class_colors"],
        "title": "HeatmapMetadata",
        "type": "object"
      },
      "mime_type": "image/tiff",
      "name": "tissue_qc:tiff_heatmap",
      "scope": "ITEM",
      "visibility": "EXTERNAL"
    }
  ],
  "version": "0.4.4"
}
```

> 422 Response

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Responses

| Status | Meaning                                                                  | Description                                                  | Schema                                            |
| ------ | ------------------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                  | Successful Response                                          | [VersionReadResponse](#schemaversionreadresponse) |
| 403    | [Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)           | Forbidden - You don't have permission to see this version    | None                                              |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)           | Not Found - Application version with given ID does not exist | None                                              |
| 422    | [Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3) | Validation Error                                             | [HTTPValidationError](#schemahttpvalidationerror) |

To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer

## Schemas

### ApplicationReadResponse

```json
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "name": "Atlas H&E-TME",
  "regulatory_classes": ["RUO"]
}
```

ApplicationReadResponse

#### Properties

| Name               | Type     | Required | Restrictions | Description                                                                                         |
| ------------------ | -------- | -------- | ------------ | --------------------------------------------------------------------------------------------------- |
| application_id     | string   | true     | none         | Application ID                                                                                      |
| description        | string   | true     | none         | Describing what the application can do                                                              |
| name               | string   | true     | none         | Application display name                                                                            |
| regulatory_classes | [string] | true     | none         | Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA. |

### ApplicationRunStatus

```json
"CANCELED_SYSTEM"
```

ApplicationRunStatus

#### Properties

| Name                 | Type   | Required | Restrictions | Description |
| -------------------- | ------ | -------- | ------------ | ----------- |
| ApplicationRunStatus | string | false    | none         | none        |

##### Enumerated Values

| Property             | Value                |
| -------------------- | -------------------- |
| ApplicationRunStatus | CANCELED_SYSTEM      |
| ApplicationRunStatus | CANCELED_USER        |
| ApplicationRunStatus | COMPLETED            |
| ApplicationRunStatus | COMPLETED_WITH_ERROR |
| ApplicationRunStatus | RECEIVED             |
| ApplicationRunStatus | REJECTED             |
| ApplicationRunStatus | RUNNING              |
| ApplicationRunStatus | SCHEDULED            |

### ApplicationVersionReadResponse

```json
{
  "application_id": "string",
  "application_version_id": "he-tme:v0.0.1",
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
  "version": "0.0.1"
}
```

ApplicationVersionReadResponse

#### Properties

| Name                   | Type              | Required | Restrictions | Description                                                 |
| ---------------------- | ----------------- | -------- | ------------ | ----------------------------------------------------------- |
| application_id         | string            | true     | none         | Application ID                                              |
| application_version_id | string            | true     | none         | Application version ID                                      |
| changelog              | string            | true     | none         | Description of the changes relative to the previous version |
| created_at             | string(date-time) | true     | none         | The timestamp when the application version was registered   |
| flow_id                | any               | false    | none         | Flow ID, used internally by the platform                    |

anyOf

| Name          | Type         | Required | Restrictions | Description |
| ------------- | ------------ | -------- | ------------ | ----------- |
| » _anonymous_ | string(uuid) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name             | Type                                                              | Required | Restrictions | Description                                                              |
| ---------------- | ----------------------------------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------ |
| input_artifacts  | [[InputArtifactReadResponse](#schemainputartifactreadresponse)]   | true     | none         | Lists required input fields, that should be provided by the caller       |
| output_artifacts | [[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)] | true     | none         | Lists the structure of the output artifacts generated by the application |
| version          | string                                                            | true     | none         | Semantic version of the application                                      |

### HTTPValidationError

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

HTTPValidationError

#### Properties

| Name   | Type                                        | Required | Restrictions | Description |
| ------ | ------------------------------------------- | -------- | ------------ | ----------- |
| detail | [[ValidationError](#schemavalidationerror)] | false    | none         | none        |

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

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| metadata_schema | object | true     | none         | none        |
| mime_type       | string | true     | none         | none        |
| name            | string | true     | none         | none        |

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
  "name": "input_slide"
}
```

InputArtifactCreationRequest

#### Properties

| Name         | Type        | Required | Restrictions | Description                                                                                                                                                                                                                   |
| ------------ | ----------- | -------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| download_url | string(uri) | true     | none         | [Signed URL](https://cloud.google.com/cdn/docs/using-signed-urls) to the input artifact file. The URL should be valid for at least 6 days from the payload submission time.                                                   |
| metadata     | object      | true     | none         | The metadata of the artifact, required by the application version. The JSON schema of the metadata can be requested by `/v1/versions/{application_version_id}`. The schema is located in `input_artifacts.[].metadata_schema` |
| name         | string      | true     | none         | Type of artifact. For Atlas H&E-TME, use "input_slide"                                                                                                                                                                        |

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

| Name            | Type   | Required | Restrictions | Description |
| --------------- | ------ | -------- | ------------ | ----------- |
| metadata_schema | object | true     | none         | none        |
| mime_type       | string | true     | none         | none        |
| name            | string | true     | none         | none        |

### ItemCreationRequest

```json
{
  "input_artifacts": [
    {
      "download_url": "https://example-bucket.s3.amazonaws.com/slide1.tiff",
      "metadata": {
        "checksum_base64_crc32c": "64RKKA==",
        "height_px": 87761,
        "media-type": "image/tiff",
        "resolution_mpp": 0.2628238,
        "specimen": {
          "disease": "LUNG_CANCER",
          "tissue": "LUNG"
        },
        "staining_method": "H&E",
        "width_px": 136223
      },
      "name": "input_slide"
    }
  ],
  "metadata": {
    "case": "abc"
  },
  "reference": "slide_1"
}
```

ItemCreationRequest

#### Properties

| Name            | Type                                                                  | Required | Restrictions | Description                                                                                                 |
| --------------- | --------------------------------------------------------------------- | -------- | ------------ | ----------------------------------------------------------------------------------------------------------- |
| input_artifacts | [[InputArtifactCreationRequest](#schemainputartifactcreationrequest)] | true     | none         | List of input artifacts for this item. For Atlas H&E-TME, typically contains one artifact (the slide image) |
| metadata        | any                                                                   | false    | none         | Optional JSON metadata to store additional information alongside an item.                                   |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | object | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name      | Type   | Required | Restrictions | Description                                                                                                                               |
| --------- | ------ | -------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| reference | string | true     | none         | Unique identifier for this item within the run. Used for referencing results. Must be unique across all items in the same application run |

### ItemReadResponse

```json
{
  "application_run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "message": "Processing started",
  "reference": "sample-123",
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}
```

ItemReadResponse

#### Properties

| Name               | Type | Required | Restrictions | Description |
| ------------------ | ---- | -------- | ------------ | ----------- |
| application_run_id | any  | false    | none         | none        |

anyOf

| Name          | Type         | Required | Restrictions | Description |
| ------------- | ------------ | -------- | ------------ | ----------- |
| » _anonymous_ | string(uuid) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name    | Type         | Required | Restrictions | Description |
| ------- | ------------ | -------- | ------------ | ----------- |
| item_id | string(uuid) | true     | none         | none        |
| message | any          | false    | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name          | Type                            | Required | Restrictions | Description                                               |
| ------------- | ------------------------------- | -------- | ------------ | --------------------------------------------------------- |
| reference     | string                          | true     | none         | none                                                      |
| status        | [ItemStatus](#schemaitemstatus) | true     | none         | none                                                      |
| terminated_at | any                             | false    | none         | Timestamp showing when the item reached a terminal state. |

anyOf

| Name          | Type              | Required | Restrictions | Description |
| ------------- | ----------------- | -------- | ------------ | ----------- |
| » _anonymous_ | string(date-time) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### ItemResultReadResponse

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "error": "string",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
  "metadata": {},
  "output_artifacts": [
    {
      "download_url": "http://example.com",
      "metadata": {},
      "name": "tissue_qc:tiff_heatmap",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  ],
  "reference": "slide_1",
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}
```

ItemResultReadResponse

#### Properties

| Name               | Type         | Required | Restrictions | Description                                                                   |
| ------------------ | ------------ | -------- | ------------ | ----------------------------------------------------------------------------- |
| application_run_id | string(uuid) | true     | none         | Application run UUID to which the item belongs                                |
| error              | any          | false    | none         | The error message in case the item is in `error_system` or `error_user` state |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name    | Type         | Required | Restrictions | Description                                                                   |
| ------- | ------------ | -------- | ------------ | ----------------------------------------------------------------------------- |
| item_id | string(uuid) | true     | none         | Item UUID generated by the Platform                                           |
| message | any          | true     | none         | The error message in case the item is in `error_system` or `error_user` state |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name     | Type | Required | Restrictions | Description                                                                              |
| -------- | ---- | -------- | ------------ | ---------------------------------------------------------------------------------------- |
| metadata | any  | true     | none         | The metadata of the item that has been provided by the user on application run creation. |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | object | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name             | Type                                                                          | Required | Restrictions | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| output_artifacts | [[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)] | true     | none         | The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.                                                                                                                                                                                                                                                                                                                                                                                     |
| reference        | string                                                                        | true     | none         | The reference of the item from the user payload                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| status           | [ItemStatus](#schemaitemstatus)                                               | true     | none         | When the item is not processed yet, the status is set to `pending`.When the item is successfully finished, status is set to `succeeded`, and the processing resultsbecome available for download in `output_artifacts` field.When the item processing is failed because the provided item is invalid, the status is set to`error_user`. When the item processing failed because of the error in the model or platform,the status is set to `error_system`. When the application_run is canceled, the status of allpending items is set to either `cancelled_user` or `cancelled_system`. |
| terminated_at    | any                                                                           | false    | none         | Timestamp showing when the item reached a terminal state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

anyOf

| Name          | Type              | Required | Restrictions | Description |
| ------------- | ----------------- | -------- | ------------ | ----------- |
| » _anonymous_ | string(date-time) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### ItemStatus

```json
"PENDING"
```

ItemStatus

#### Properties

| Name       | Type   | Required | Restrictions | Description |
| ---------- | ------ | -------- | ------------ | ----------- |
| ItemStatus | string | false    | none         | none        |

##### Enumerated Values

| Property   | Value           |
| ---------- | --------------- |
| ItemStatus | PENDING         |
| ItemStatus | CANCELED_USER   |
| ItemStatus | CANCELED_SYSTEM |
| ItemStatus | ERROR_USER      |
| ItemStatus | ERROR_SYSTEM    |
| ItemStatus | SUCCEEDED       |

### MeReadResponse

```json
{
  "organization": {
    "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aignostics_bucket_name": "aignostics-platform-bucket",
    "aignostics_bucket_protocol": "gs",
    "aignostics_logfire_token": "your-logfire-token",
    "aignostics_sentry_dsn": "https://2354s3#ewsha@o44.ingest.us.sentry.io/34345123432",
    "display_name": "Aignostics GmbH",
    "id": "org_123456",
    "name": "aignx"
  },
  "user": {
    "email": "user@domain.com",
    "email_verified": true,
    "family_name": "Doe",
    "given_name": "Jane",
    "id": "auth0|123456",
    "name": "Jane Doe",
    "nickname": "jdoe",
    "picture": "https://example.com/jdoe.jpg",
    "updated_at": "2023-10-05T14:48:00.000Z"
  }
}
```

MeReadResponse

#### Properties

| Name         | Type                                                        | Required | Restrictions | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------ | ----------------------------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| organization | [OrganizationReadResponse](#schemaorganizationreadresponse) | true     | none         | Part of response schema for Organization object in `Get current user` endpoint.This model corresponds to the response schema returned fromAuth0 GET /v2/organizations/{id} endpoint, flattens out the metadata outand doesn't return branding or token_quota objects.For details, see:https://auth0.com/docs/api/management/v2/organizations/get-organizations-by-id#### Configuration for integrating with Aignostics Platform services.The Aignostics Platform API requires signed URLs for input artifacts (slide images). To simplify this process,Aignostics provides a dedicated storage bucket. The HMAC credentials below grant read and writeaccess to this bucket, allowing you to upload files and generate the signed URLs needed for API calls.Additionally, logging and error reporting tokens enable Aignostics to provide better support and monitorsystem performance for your integration. |
| user         | [UserReadResponse](#schemauserreadresponse)                 | true     | none         | Part of response schema for User object in `Get current user` endpoint.This model corresponds to the response schema returned fromAuth0 GET /v2/users/{id} endpoint.For details, see:https://auth0.com/docs/api/management/v2/users/get-users-by-id                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

### OrganizationReadResponse

```json
{
  "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "aignostics_bucket_name": "aignostics-platform-bucket",
  "aignostics_bucket_protocol": "gs",
  "aignostics_logfire_token": "your-logfire-token",
  "aignostics_sentry_dsn": "https://2354s3#ewsha@o44.ingest.us.sentry.io/34345123432",
  "display_name": "Aignostics GmbH",
  "id": "org_123456",
  "name": "aignx"
}
```

OrganizationReadResponse

#### Properties

| Name                                     | Type   | Required | Restrictions | Description                                                                                                                                               |
| ---------------------------------------- | ------ | -------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| aignostics_bucket_hmac_access_key_id     | string | true     | none         | HMAC access key ID for the Aignostics-provided storage bucket. Used to authenticate requests for uploading files and generating signed URLs               |
| aignostics_bucket_hmac_secret_access_key | string | true     | none         | HMAC secret access key paired with the access key ID. Keep this credential secure.                                                                        |
| aignostics_bucket_name                   | string | true     | none         | Name of the bucket provided by Aignostics for storing input artifacts (slide images)                                                                      |
| aignostics_bucket_protocol               | string | true     | none         | Protocol to use for bucket access. Defines the URL scheme for connecting to the storage service                                                           |
| aignostics_logfire_token                 | string | true     | none         | Authentication token for Logfire observability service. Enables sending application logs and performance metrics to Aignostics for monitoring and support |
| aignostics_sentry_dsn                    | string | true     | none         | Data Source Name (DSN) for Sentry error tracking service. Allows automatic reporting of errors and exceptions to Aignostics support team                  |
| display_name                             | any    | false    | none         | Public organization name (E.g. “Aignostics GmbH”)                                                                                                         |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name | Type   | Required | Restrictions | Description                      |
| ---- | ------ | -------- | ------------ | -------------------------------- |
| id   | string | true     | none         | Unique organization identifier   |
| name | any    | false    | none         | Organization name (E.g. “aignx”) |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### OutputArtifact

```json
{
  "metadata_schema": {},
  "mime_type": "application/vnd.apache.parquet",
  "name": "string",
  "scope": "ITEM",
  "visibility": "INTERNAL"
}
```

OutputArtifact

#### Properties

| Name            | Type                                                        | Required | Restrictions | Description |
| --------------- | ----------------------------------------------------------- | -------- | ------------ | ----------- |
| metadata_schema | object                                                      | true     | none         | none        |
| mime_type       | string                                                      | true     | none         | none        |
| name            | string                                                      | true     | none         | none        |
| scope           | [OutputArtifactScope](#schemaoutputartifactscope)           | true     | none         | none        |
| visibility      | [OutputArtifactVisibility](#schemaoutputartifactvisibility) | true     | none         | none        |

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

| Name            | Type                                              | Required | Restrictions | Description |
| --------------- | ------------------------------------------------- | -------- | ------------ | ----------- |
| metadata_schema | object                                            | true     | none         | none        |
| mime_type       | string                                            | true     | none         | none        |
| name            | string                                            | true     | none         | none        |
| scope           | [OutputArtifactScope](#schemaoutputartifactscope) | true     | none         | none        |

### OutputArtifactResultReadResponse

```json
{
  "download_url": "http://example.com",
  "metadata": {},
  "name": "tissue_qc:tiff_heatmap",
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
}
```

OutputArtifactResultReadResponse

#### Properties

| Name         | Type | Required | Restrictions | Description                                                                                                                                             |
| ------------ | ---- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| download_url | any  | true     | none         | The download URL to the output file. The URL is valid for 1 hour after the endpoint is called.A new URL is generated every time the endpoint is called. |

anyOf

| Name          | Type        | Required | Restrictions | Description |
| ------------- | ----------- | -------- | ------------ | ----------- |
| » _anonymous_ | string(uri) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name               | Type         | Required | Restrictions | Description                                                                              |
| ------------------ | ------------ | -------- | ------------ | ---------------------------------------------------------------------------------------- |
| metadata           | object       | true     | none         | The metadata of the output artifact, provided by the application                         |
| name               | string       | true     | none         | Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint. |
| output_artifact_id | string(uuid) | true     | none         | The Id of the artifact. Used internally                                                  |

### OutputArtifactScope

```json
"ITEM"
```

OutputArtifactScope

#### Properties

| Name                | Type   | Required | Restrictions | Description |
| ------------------- | ------ | -------- | ------------ | ----------- |
| OutputArtifactScope | string | false    | none         | none        |

##### Enumerated Values

| Property            | Value  |
| ------------------- | ------ |
| OutputArtifactScope | ITEM   |
| OutputArtifactScope | GLOBAL |

### OutputArtifactVisibility

```json
"INTERNAL"
```

OutputArtifactVisibility

#### Properties

| Name                     | Type   | Required | Restrictions | Description |
| ------------------------ | ------ | -------- | ------------ | ----------- |
| OutputArtifactVisibility | string | false    | none         | none        |

##### Enumerated Values

| Property                 | Value    |
| ------------------------ | -------- |
| OutputArtifactVisibility | INTERNAL |
| OutputArtifactVisibility | EXTERNAL |

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

| Name              | Type         | Required | Restrictions | Description |
| ----------------- | ------------ | -------- | ------------ | ----------- |
| download_url      | string(uri)  | true     | none         | none        |
| input_artifact_id | string(uuid) | false    | none         | none        |
| metadata          | object       | true     | none         | none        |

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

| Name                       | Type                                                  | Required | Restrictions | Description |
| -------------------------- | ----------------------------------------------------- | -------- | ------------ | ----------- |
| input_artifacts            | object                                                | true     | none         | none        |
| » **additionalProperties** | [PayloadInputArtifact](#schemapayloadinputartifact)   | false    | none         | none        |
| item_id                    | string(uuid)                                          | true     | none         | none        |
| output_artifacts           | object                                                | true     | none         | none        |
| » **additionalProperties** | [PayloadOutputArtifact](#schemapayloadoutputartifact) | false    | none         | none        |

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

| Name               | Type                                | Required | Restrictions | Description |
| ------------------ | ----------------------------------- | -------- | ------------ | ----------- |
| data               | [TransferUrls](#schematransferurls) | true     | none         | none        |
| metadata           | [TransferUrls](#schematransferurls) | true     | none         | none        |
| output_artifact_id | string(uuid)                        | true     | none         | none        |

### RunCreationRequest

```json
{
  "application_version_id": "he-tme:v1.0.0-beta",
  "items": [
    {
      "input_artifacts": [
        {
          "download_url": "https://example-bucket.s3.amazonaws.com/slide1.tiff?signature=...",
          "metadata": {
            "checksum_base64_crc32c": "64RKKA==",
            "height_px": 87761,
            "media-type": "image/tiff",
            "resolution_mpp": 0.2628238,
            "specimen": {
              "disease": "LUNG_CANCER",
              "tissue": "LUNG"
            },
            "staining_method": "H&E",
            "width_px": 136223
          },
          "name": "input_slide"
        }
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
}
```

RunCreationRequest

#### Properties

| Name                   | Type                                                | Required | Restrictions | Description                                                                                                                  |
| ---------------------- | --------------------------------------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| application_version_id | string                                              | true     | none         | Unique ID for the application version to use for processing. Must include version suffix (e.g., 'he-tme:v1.0.0-beta')        |
| items                  | [[ItemCreationRequest](#schemaitemcreationrequest)] | true     | none         | List of items (slides) to process. Each item represents a whole slide image (WSI) with its associated metadata and artifacts |
| metadata               | any                                                 | false    | none         | Optional JSON metadata to store additional information alongside the application run                                         |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | object | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### RunCreationResponse

```json
{
  "application_run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

RunCreationResponse

#### Properties

| Name               | Type         | Required | Restrictions | Description |
| ------------------ | ------------ | -------- | ------------ | ----------- |
| application_run_id | string(uuid) | false    | none         | none        |

### RunReadResponse

```json
{
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "he-tme:v0.4.4",
  "message": "The run was cancelled because the threshold of 3 items finishing in error state was reached. Query /runs/{run_id}/results to get the error message per item.",
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "organization_id": "org-123",
  "status": "CANCELED_SYSTEM",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "triggered_at": "2019-08-24T14:15:22Z",
  "triggered_by": "auth0|123456",
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

| Name                   | Type         | Required | Restrictions | Description                      |
| ---------------------- | ------------ | -------- | ------------ | -------------------------------- |
| application_run_id     | string(uuid) | true     | none         | UUID of the application          |
| application_version_id | string       | true     | none         | ID of the application version    |
| message                | any          | true     | none         | The description of the run error |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name     | Type | Required | Restrictions | Description                                                                         |
| -------- | ---- | -------- | ------------ | ----------------------------------------------------------------------------------- |
| metadata | any  | false    | none         | Optional JSON metadata that was stored in alongside the application run by the user |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | object | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name            | Type                                                | Required | Restrictions | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------- | --------------------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| organization_id | string                                              | true     | none         | Organization of the owner of the application run                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| status          | [ApplicationRunStatus](#schemaapplicationrunstatus) | true     | none         | When the application run request is received by the Platform, the `status` of it is set to`running`. When the application run is scheduled, the input items will be processed and the result willbe generated incrementally. The results can be downloaded via `/v1/runs/{run_id}/results` endpoint.When all items are processed and all results are generated, the application status is set to`completed`. If the processing is done, but some items fail, the status is set to`completed_with_error`.When the application run reaches the threshold of number of failed items, the wholeapplication run is set to `canceled_system` and the remaining pending items are not processed.When the application run fails, the finished item results are available for download.If the application run is canceled by calling `POST /v1/runs/{run_id}/cancel` endpoint, theprocessing of the items is stopped, and the application status is set to `cancelled_user` |
| terminated_at   | any                                                 | false    | none         | Timestamp showing when the application run reached a terminal state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

anyOf

| Name          | Type              | Required | Restrictions | Description |
| ------------- | ----------------- | -------- | ------------ | ----------- |
| » _anonymous_ | string(date-time) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name         | Type              | Required | Restrictions | Description                                              |
| ------------ | ----------------- | -------- | ------------ | -------------------------------------------------------- |
| triggered_at | string(date-time) | true     | none         | Timestamp showing when the application run was triggered |
| triggered_by | string            | true     | none         | Id of the user who triggered the application run         |
| user_payload | any               | false    | none         | Field used internally by the Platform                    |

anyOf

| Name          | Type                              | Required | Restrictions | Description |
| ------------- | --------------------------------- | -------- | ------------ | ----------- |
| » _anonymous_ | [UserPayload](#schemauserpayload) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### TransferUrls

```json
{
  "download_url": "http://example.com",
  "upload_url": "http://example.com"
}
```

TransferUrls

#### Properties

| Name         | Type        | Required | Restrictions | Description |
| ------------ | ----------- | -------- | ------------ | ----------- |
| download_url | string(uri) | true     | none         | none        |
| upload_url   | string(uri) | true     | none         | none        |

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

| Name                    | Type         | Required | Restrictions | Description |
| ----------------------- | ------------ | -------- | ------------ | ----------- |
| application_id          | string       | true     | none         | none        |
| application_run_id      | string(uuid) | true     | none         | none        |
| global_output_artifacts | any          | true     | none         | none        |

anyOf

| Name                        | Type                                                  | Required | Restrictions | Description |
| --------------------------- | ----------------------------------------------------- | -------- | ------------ | ----------- |
| » _anonymous_               | object                                                | false    | none         | none        |
| »» **additionalProperties** | [PayloadOutputArtifact](#schemapayloadoutputartifact) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name  | Type                                | Required | Restrictions | Description |
| ----- | ----------------------------------- | -------- | ------------ | ----------- |
| items | [[PayloadItem](#schemapayloaditem)] | true     | none         | none        |

### UserReadResponse

```json
{
  "email": "user@domain.com",
  "email_verified": true,
  "family_name": "Doe",
  "given_name": "Jane",
  "id": "auth0|123456",
  "name": "Jane Doe",
  "nickname": "jdoe",
  "picture": "https://example.com/jdoe.jpg",
  "updated_at": "2023-10-05T14:48:00.000Z"
}
```

UserReadResponse

#### Properties

| Name  | Type | Required | Restrictions | Description |
| ----- | ---- | -------- | ------------ | ----------- |
| email | any  | false    | none         | User email  |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name           | Type | Required | Restrictions | Description |
| -------------- | ---- | -------- | ------------ | ----------- |
| email_verified | any  | false    | none         | none        |

anyOf

| Name          | Type    | Required | Restrictions | Description |
| ------------- | ------- | -------- | ------------ | ----------- |
| » _anonymous_ | boolean | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name        | Type | Required | Restrictions | Description |
| ----------- | ---- | -------- | ------------ | ----------- |
| family_name | any  | false    | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name       | Type | Required | Restrictions | Description |
| ---------- | ---- | -------- | ------------ | ----------- |
| given_name | any  | false    | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name | Type   | Required | Restrictions | Description                     |
| ---- | ------ | -------- | ------------ | ------------------------------- |
| id   | string | true     | none         | Unique user identifier          |
| name | any    | false    | none         | First and last name of the user |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name     | Type | Required | Restrictions | Description |
| -------- | ---- | -------- | ------------ | ----------- |
| nickname | any  | false    | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name    | Type | Required | Restrictions | Description |
| ------- | ---- | -------- | ------------ | ----------- |
| picture | any  | false    | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name       | Type | Required | Restrictions | Description |
| ---------- | ---- | -------- | ------------ | ----------- |
| updated_at | any  | false    | none         | none        |

anyOf

| Name          | Type              | Required | Restrictions | Description |
| ------------- | ----------------- | -------- | ------------ | ----------- |
| » _anonymous_ | string(date-time) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

### ValidationError

```json
{
  "loc": ["string"],
  "msg": "string",
  "type": "string"
}
```

ValidationError

#### Properties

| Name | Type    | Required | Restrictions | Description |
| ---- | ------- | -------- | ------------ | ----------- |
| loc  | [anyOf] | true     | none         | none        |

anyOf

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| » _anonymous_ | string | false    | none         | none        |

or

| Name          | Type    | Required | Restrictions | Description |
| ------------- | ------- | -------- | ------------ | ----------- |
| » _anonymous_ | integer | false    | none         | none        |

continued

| Name | Type   | Required | Restrictions | Description |
| ---- | ------ | -------- | ------------ | ----------- |
| msg  | string | true     | none         | none        |
| type | string | true     | none         | none        |

### VersionReadResponse

```json
{
  "application_id": "string",
  "application_version_id": "string",
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
      "scope": "ITEM",
      "visibility": "INTERNAL"
    }
  ],
  "version": "string"
}
```

VersionReadResponse

#### Properties

| Name                   | Type              | Required | Restrictions | Description                                                 |
| ---------------------- | ----------------- | -------- | ------------ | ----------------------------------------------------------- |
| application_id         | string            | true     | none         | Application ID                                              |
| application_version_id | string            | true     | none         | Application version ID                                      |
| changelog              | string            | true     | none         | Description of the changes relative to the previous version |
| created_at             | string(date-time) | true     | none         | The timestamp when the application version was registered   |
| flow_id                | any               | false    | none         | Flow ID, used internally by the platform                    |

anyOf

| Name          | Type         | Required | Restrictions | Description |
| ------------- | ------------ | -------- | ------------ | ----------- |
| » _anonymous_ | string(uuid) | false    | none         | none        |

or

| Name          | Type | Required | Restrictions | Description |
| ------------- | ---- | -------- | ------------ | ----------- |
| » _anonymous_ | null | false    | none         | none        |

continued

| Name             | Type                                      | Required | Restrictions | Description                                             |
| ---------------- | ----------------------------------------- | -------- | ------------ | ------------------------------------------------------- |
| input_artifacts  | [[InputArtifact](#schemainputartifact)]   | true     | none         | List of the input fields, provided by the User          |
| output_artifacts | [[OutputArtifact](#schemaoutputartifact)] | true     | none         | List of the output fields, generated by the application |
| version          | string                                    | true     | none         | Semantic version of the application                     |
