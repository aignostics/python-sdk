# API v1 Reference
<<<<<<< HEAD
<<<<<<< HEAD
## Aignostics Platform API v1.0.0-beta.3
=======
## Aignostics Platform API v1.0.0-beta6
>>>>>>> 99401ec (Refactor tests)
=======
## Aignostics Platform API v1.0.0.beta7
>>>>>>> b165166 (chore: rebase)

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

The Aignostics Platform is a cloud-based service that enables organizations to access advanced computational pathology applications through a secure API.  The platform provides standardized access to Aignostics' portfolio of computational pathology solutions, with Atlas H&E-TME serving as an example of the available API endpoints. 

To begin using the platform, your organization must first be registered by our business support team. If you don't have an account yet, please contact your account manager or email support@aignostics.com to get started. 

More information about our applications can be found on (https://platform.aignostics.com).

**How to authorize and test API endpoints:**

1. Click the "Authorize" button in the right corner below
3. Click "Authorize" button in the dialog to log in with your Aignostics Platform credentials
4. After successful login, you'll be redirected back and can use "Try it out" on any endpoint

**Note**: You only need to authorize once per session. The lock icons next to endpoints will show green when authorized.

Base URLs:

* [/api](/api)

## Authentication

- oAuth2 authentication. 

    - Flow: authorizationCode
    - Authorization URL = [https://aignostics-platform-staging.eu.auth0.com/authorize](https://aignostics-platform-staging.eu.auth0.com/authorize)
    - Token URL = [https://aignostics-platform-staging.eu.auth0.com/oauth/token](https://aignostics-platform-staging.eu.auth0.com/oauth/token)

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

*List available applications*

Returns the list of the applications, available to the caller.

The application is available if any of the versions of the application is assigned to the caller’s organization.
The response is paginated and sorted according to the provided parameters.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|page|query|integer|false|none|
<<<<<<< HEAD
<<<<<<< HEAD
|page-size|query|integer|false|none|
=======
|page_size|query|integer|false|none|
>>>>>>> 99401ec (Refactor tests)
=======
|page-size|query|integer|false|none|
>>>>>>> b165166 (chore: rebase)
|sort|query|any|false|Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.|

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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
    "latest_version": {
      "number": "1.0.0",
      "released_at": "2025-09-01T19:01:05.401Z"
    },
<<<<<<< HEAD
=======
>>>>>>> 99401ec (Refactor tests)
=======
>>>>>>> b165166 (chore: rebase)
    "name": "Atlas H&E-TME",
    "regulatory_classes": [
      "RUO"
    ]
  },
  {
    "application_id": "test-app",
    "description": "This is the test application with two algorithms: TissueQc and Tissue Segmentation",
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
    "latest_version": {
      "number": "2.0.0",
      "released_at": "2025-09-02T19:01:05.401Z"
    },
<<<<<<< HEAD
=======
>>>>>>> 99401ec (Refactor tests)
=======
>>>>>>> b165166 (chore: rebase)
    "name": "Test Application",
    "regulatory_classes": [
      "RUO"
    ]
  }
]
```

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
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|A list of applications available to the caller|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized - Invalid or missing authentication|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Applications V1 Applications Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|Response List Applications V1 Applications Get|[[ApplicationReadShortResponse](#schemaapplicationreadshortresponse)]|false|none|[Response schema for `List available applications` and `Read Application by Id` endpoints]|
|» ApplicationReadShortResponse|[ApplicationReadShortResponse](#schemaapplicationreadshortresponse)|false|none|Response schema for `List available applications` and `Read Application by Id` endpoints|
|»» application_id|string|true|none|Application ID|
|»» description|string|true|none|Describing what the application can do|
|»» latest_version|any|false|none|The version with highest version number available to the user|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[ApplicationVersion](#schemaapplicationversion)|false|none|none|
|»»»» number|string|true|none|The number of the latest version|
|»»»» released_at|string(date-time)|true|none|The timestamp for when the application version was made available in the Platform|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» name|string|true|none|Application display name|
|»» regulatory_classes|[string]|true|none|Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA.|
=======
|Response List Applications V1 Applications Get|[[ApplicationReadResponse](#schemaapplicationreadresponse)]|false|none|[Response schema for `List available applications` and `Read Application by Id` endpoints]|
|» ApplicationReadResponse|[ApplicationReadResponse](#schemaapplicationreadresponse)|false|none|Response schema for `List available applications` and `Read Application by Id` endpoints|
=======
|Response List Applications V1 Applications Get|[[ApplicationReadShortResponse](#schemaapplicationreadshortresponse)]|false|none|[Response schema for `List available applications` and `Read Application by Id` endpoints]|
|» ApplicationReadShortResponse|[ApplicationReadShortResponse](#schemaapplicationreadshortresponse)|false|none|Response schema for `List available applications` and `Read Application by Id` endpoints|
>>>>>>> b165166 (chore: rebase)
|»» application_id|string|true|none|Application ID|
|»» description|string|true|none|Describing what the application can do|
|»» latest_version|any|false|none|The version with highest version number available to the user|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[ApplicationVersion](#schemaapplicationversion)|false|none|none|
|»»»» number|string|true|none|The number of the latest version|
|»»»» released_at|string(date-time)|true|none|The timestamp for when the application version was made available in the Platform|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» name|string|true|none|Application display name|
|»» regulatory_classes|[string]|true|none|Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA.|


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

r = requests.get('/api/v1/applications/{application_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/applications/{application_id}',
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

Retrieve details of a specific application by its ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|path|string|true|none|

> Example responses

> 200 Response

```json
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "name": "Atlas H&E-TME",
  "regulatory_classes": [
    "RUO"
  ],
  "versions": [
    {
      "number": "1.0.0",
      "released_at": "2025-09-15T10:30:45.123Z"
    }
  ]
}
```

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
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ApplicationReadResponse](#schemaapplicationreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this application|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Application with the given ID does not exist|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|
>>>>>>> 99401ec (Refactor tests)


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### application_version_details_v1_applications__application_id__versions__version__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/applications/{application_id}/versions/{version}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/applications/{application_id}/versions/{version}',
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

`GET /v1/applications/{application_id}/versions/{version}`

<<<<<<< HEAD
<<<<<<< HEAD
*Read Application By Id*

Retrieve details of a specific application by its ID.
=======
*List Available Application Versions*
=======
*Application Version Details*
>>>>>>> b165166 (chore: rebase)

Get the application version details

<<<<<<< HEAD
A version is considered available when it has been assigned to your organization. Within a major version,
all minor and patch updates are automatically accessible unless a specific version has been deprecated.
Major version upgrades, however, require explicit assignment and may be subject to contract modifications
before becoming available to your organization.
>>>>>>> 99401ec (Refactor tests)
=======
Allows caller to  retrieve information about application version based on provided application version ID.
>>>>>>> b165166 (chore: rebase)

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|path|string|true|none|
<<<<<<< HEAD
<<<<<<< HEAD
=======
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|version|query|any|false|Semantic version of the application, example: `1.0.13`|
|sort|query|any|false|Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.|

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
>>>>>>> 99401ec (Refactor tests)
=======
|version|path|string|true|none|
>>>>>>> b165166 (chore: rebase)

> Example responses

> 200 Response

```json
<<<<<<< HEAD
<<<<<<< HEAD
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "name": "Atlas H&E-TME",
  "regulatory_classes": [
    "RUO"
  ],
  "versions": [
    {
      "number": "1.0.0",
      "released_at": "2025-09-15T10:30:45.123Z"
    }
  ]
}
=======
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
                  "enum": [
                    "LUNG_CANCER"
                  ],
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
=======
{
  "changelog": "New deployment",
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
>>>>>>> b165166 (chore: rebase)
              },
              "type": {
                "const": "lung",
                "enum": [
                  "lung"
                ],
                "title": "Type",
                "type": "string"
              }
            },
            "required": [
              "type",
              "tissue"
            ],
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
            "anyOf": [
              false
            ],
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
            "enum": [
              "application/dicom",
              "image/tiff"
            ],
            "title": "Mime Type",
            "type": "string"
          },
          "stain": {
            "const": "H&E",
            "default": "H&E",
            "enum": [
              "H&E"
            ],
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
<<<<<<< HEAD
        "mime_type": "image/tiff",
        "name": "tissue_qc:geojson_polygons",
        "scope": "ITEM"
      }
    ],
    "version": "0.5.0"
  }
]
>>>>>>> 99401ec (Refactor tests)
=======
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
      "name": "whole_slide_image"
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
            "enum": [
              "image/tiff"
            ],
            "title": "Mime Type",
            "type": "string"
          },
          "width": {
            "title": "Width",
            "type": "integer"
          }
        },
        "required": [
          "checksum_crc32c",
          "width",
          "height",
          "class_colors"
        ],
        "title": "HeatmapMetadata",
        "type": "object"
      },
      "mime_type": "image/tiff",
      "name": "tissue_qc:tiff_heatmap",
      "scope": "ITEM",
      "visibility": "EXTERNAL"
    }
  ],
  "released_at": "2025-04-16T08:45:20.655972Z",
  "version_number": "0.4.4"
}
>>>>>>> b165166 (chore: rebase)
```

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
<<<<<<< HEAD
<<<<<<< HEAD
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ApplicationReadResponse](#schemaapplicationreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this application|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Application with the given ID does not exist|None|
=======
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|A list of application versions for a given application ID available to the caller|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized - Invalid or missing authentication|None|
>>>>>>> 99401ec (Refactor tests)
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### application_version_details_v1_applications__application_id__versions__version__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/applications/{application_id}/versions/{version}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/applications/{application_id}/versions/{version}',
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

`GET /v1/applications/{application_id}/versions/{version}`

*Application Version Details*

Get the application version details

Allows caller to  retrieve information about application version based on provided application version ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|application_id|path|string|true|none|
|version|path|string|true|none|
=======
|Response List Versions By Application Id V1 Applications  Application Id  Versions Get|[[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)]|false|none|[Response schema for `List Available Application Versions` endpoint]|
|» ApplicationVersionReadResponse|[ApplicationVersionReadResponse](#schemaapplicationversionreadresponse)|false|none|Response schema for `List Available Application Versions` endpoint|
|»» application_id|string|true|none|Application ID|
|»» application_version_id|string|true|none|Application version ID|
|»» changelog|string|true|none|Description of the changes relative to the previous version|
|»» created_at|string(date-time)|true|none|The timestamp when the application version was registered|
|»» flow_id|any|false|none|Flow ID, used internally by the platform|
>>>>>>> 99401ec (Refactor tests)

> Example responses

> 200 Response

```json
{
  "changelog": "New deployment",
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
                "enum": [
                  "lung"
                ],
                "title": "Type",
                "type": "string"
              }
            },
            "required": [
              "type",
              "tissue"
            ],
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
            "anyOf": [
              false
            ],
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
            "enum": [
              "application/dicom",
              "image/tiff"
            ],
            "title": "Mime Type",
            "type": "string"
          },
          "stain": {
            "const": "H&E",
            "default": "H&E",
            "enum": [
              "H&E"
            ],
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
      "name": "whole_slide_image"
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
            "enum": [
              "image/tiff"
            ],
            "title": "Mime Type",
            "type": "string"
          },
          "width": {
            "title": "Width",
            "type": "integer"
          }
        },
        "required": [
          "checksum_crc32c",
          "width",
          "height",
          "class_colors"
        ],
        "title": "HeatmapMetadata",
        "type": "object"
      },
      "mime_type": "image/tiff",
      "name": "tissue_qc:tiff_heatmap",
      "scope": "ITEM",
      "visibility": "EXTERNAL"
    }
  ],
  "released_at": "2025-04-16T08:45:20.655972Z",
  "version_number": "0.4.4"
}
```

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
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[VersionReadResponse](#schemaversionreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this version|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Application version with given ID is not available to you or does not exist|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_item_v1_items__item_id__get



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
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/items/{item_id}',
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

Retrieve details of a specific item (slide) by its ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|item_id|path|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "external_id": "sample-123",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "message": "Processing started",
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}
```

<<<<<<< HEAD
#### Responses
=======
|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|Lists required input fields, that should be provided by the caller|
|»»» InputArtifactReadResponse|[InputArtifactReadResponse](#schemainputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»» output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|Lists the structure of the output artifacts generated by the application|
|»»» OutputArtifactReadResponse|[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)|false|none|none|
|»»»» metadata_schema|object|true|none|none|
|»»»» mime_type|string|true|none|none|
|»»»» name|string|true|none|none|
|»»»» scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|»» version|string|true|none|Semantic version of the application|
>>>>>>> 99401ec (Refactor tests)

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ItemReadResponse](#schemaitemreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this item|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Item with given ID does not exist|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_item_v1_items__item_id__get



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
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/items/{item_id}',
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

Retrieve details of a specific item (slide) by its ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|item_id|path|string(uuid)|true|none|

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

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ItemReadResponse](#schemaitemreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this item|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Item with given ID does not exist|None|
=======
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[VersionReadResponse](#schemaversionreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this version|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Application version with given ID is not available to you or does not exist|None|
>>>>>>> b165166 (chore: rebase)
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_item_v1_items__item_id__get



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
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/items/{item_id}',
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

Retrieve details of a specific item (slide) by its ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|item_id|path|string(uuid)|true|none|

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

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ItemReadResponse](#schemaitemreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this item|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Item with given ID does not exist|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


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
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/me',
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

`GET /v1/me`

*Get current user*

Retrieves your identity details, including name, email, and organization.
This is useful for verifying that the request is being made under the correct user profile
and organization context, as well as confirming that the expected environment variables are correctly set
(in case you are using Python SDK)

> Example responses

> 200 Response

```json
{
  "organization": {
<<<<<<< HEAD
<<<<<<< HEAD
    "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
    "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
=======
    "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
>>>>>>> 99401ec (Refactor tests)
=======
    "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
    "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
>>>>>>> b165166 (chore: rebase)
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

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[MeReadResponse](#schemamereadresponse)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_runs_v1_runs_get



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

*List Runs*

<<<<<<< HEAD
<<<<<<< HEAD
List runs with filtering, sorting, and pagination capabilities.

Returns paginated runs that were submitted by the user.
=======
List application runs with filtering, sorting, and pagination capabilities.

Returns paginated application runs that were triggered by the user.
>>>>>>> 99401ec (Refactor tests)
=======
List runs with filtering, sorting, and pagination capabilities.

Returns paginated runs that were submitted by the user.
>>>>>>> b165166 (chore: rebase)

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|application_id|query|any|false|Optional application ID filter|
<<<<<<< HEAD
<<<<<<< HEAD
|application_version|query|any|false|Optional Version Name|
|external_id|query|any|false|Optionally filter runs by items with this external ID|
|custom_metadata|query|any|false|Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata.|
=======
|application_version|query|any|false|Optional application version filter|
|metadata|query|any|false|Use PostgreSQL JSONPath expressions to filter runs by their metadata.|
>>>>>>> 99401ec (Refactor tests)
=======
|application_version|query|any|false|Optional Version Name|
|external_id|query|any|false|Optionally filter runs by items with this external ID|
|custom_metadata|query|any|false|Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata.|
>>>>>>> b165166 (chore: rebase)
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.|

##### Detailed descriptions

<<<<<<< HEAD
<<<<<<< HEAD
**custom_metadata**: Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata.
=======
**metadata**: Use PostgreSQL JSONPath expressions to filter runs by their metadata.
>>>>>>> 99401ec (Refactor tests)
=======
**custom_metadata**: Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata.
>>>>>>> b165166 (chore: rebase)
##### URL Encoding Required
**Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.

##### Examples (Clear Format):
- **Field existence**: `$.study` - Runs that have a study field defined
- **Exact value match**: `$.study ? (@ == "high")` - Runs with specific study value
- **Numeric comparison**: `$.confidence_score ? (@ > 0.75)` - Runs with confidence score greater than 0.75
- **Array operations**: `$.tags[*] ? (@ == "draft")` - Runs with tags array containing "draft"
- **Complex conditions**: `$.resources ? (@.gpu_count > 2 && @.memory_gb >= 16)` - Runs with high resource requirements

##### Examples (URL-Encoded Format):
- **Field existence**: `%24.study`
- **Exact value match**: `%24.study%20%3F%20(%40%20%3D%3D%20%22high%22)`
- **Numeric comparison**: `%24.confidence_score%20%3F%20(%40%20%3E%200.75)`
- **Array operations**: `%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22draft%22)`
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
<<<<<<< HEAD
<<<<<<< HEAD
- `run_id`
- `application_version_id`
- `organization_id`
- `status`
- `submitted_at`
- `submitted_by`

**Examples:**
- `?sort=submitted_at` - Sort by creation time (ascending)
- `?sort=-submitted_at` - Sort by creation time (descending)
- `?sort=status&sort=-submitted_at` - Sort by status, then by time (descending)
=======
- `application_run_id`
=======
- `run_id`
>>>>>>> b165166 (chore: rebase)
- `application_version_id`
- `organization_id`
- `status`
- `submitted_at`
- `submitted_by`

**Examples:**
<<<<<<< HEAD
- `?sort=triggered_at` - Sort by creation time (ascending)
- `?sort=-triggered_at` - Sort by creation time (descending)
- `?sort=status&sort=-triggered_at` - Sort by status, then by time (descending)
>>>>>>> 99401ec (Refactor tests)
=======
- `?sort=submitted_at` - Sort by creation time (ascending)
- `?sort=-submitted_at` - Sort by creation time (descending)
- `?sort=status&sort=-submitted_at` - Sort by status, then by time (descending)
>>>>>>> b165166 (chore: rebase)

> Example responses

> 200 Response

```json
[
  {
<<<<<<< HEAD
<<<<<<< HEAD
    "application_id": "he-tme",
    "custom_metadata": {
      "department": "D1",
      "study": "abc-1"
    },
    "custom_metadata_checksum": "f54fe109",
    "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
    "error_message": "Run canceled given errors on more than 10 items.",
    "output": "NONE",
    "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
    "state": "PENDING",
    "statistics": {
      "item_count": 0,
      "item_pending_count": 0,
      "item_processing_count": 0,
      "item_skipped_count": 0,
      "item_succeeded_count": 0,
      "item_system_error_count": 0,
      "item_user_error_count": 0
    },
    "submitted_at": "2019-08-24T14:15:22Z",
    "submitted_by": "auth0|123456",
    "terminated_at": "2024-01-15T10:30:45.123Z",
    "termination_reason": "ALL_ITEMS_PROCESSED",
    "version_number": "0.4.4"
=======
    "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
    "application_version_id": "he-tme:v0.4.4",
    "message": "The run was cancelled because the threshold of 3 items finishing in error state was reached. Query /runs/{run_id}/results to get the error message per item.",
    "metadata": {
=======
    "application_id": "he-tme",
    "custom_metadata": {
>>>>>>> b165166 (chore: rebase)
      "department": "D1",
      "study": "abc-1"
    },
    "custom_metadata_checksum": "f54fe109",
    "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
    "error_message": "Run canceled given errors on more than 10 items.",
    "output": "NONE",
    "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
    "state": "PENDING",
    "statistics": {
      "item_count": 0,
      "item_pending_count": 0,
      "item_processing_count": 0,
      "item_skipped_count": 0,
      "item_succeeded_count": 0,
      "item_system_error_count": 0,
      "item_user_error_count": 0
    },
    "submitted_at": "2019-08-24T14:15:22Z",
    "submitted_by": "auth0|123456",
    "terminated_at": "2024-01-15T10:30:45.123Z",
<<<<<<< HEAD
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
>>>>>>> 99401ec (Refactor tests)
=======
    "termination_reason": "ALL_ITEMS_PROCESSED",
    "version_number": "0.4.4"
>>>>>>> b165166 (chore: rebase)
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Runs V1 Runs Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|Response List Runs V1 Runs Get|[[RunReadResponse](#schemarunreadresponse)]|false|none|[Response schema for `Get run details` endpoint]|
|» RunReadResponse|[RunReadResponse](#schemarunreadresponse)|false|none|Response schema for `Get run details` endpoint|
|»» application_id|string|true|none|Application id|
|»» custom_metadata|any|false|none|Optional JSON metadata that was stored in alongside the run by the user|
=======
|Response List Application Runs V1 Runs Get|[[RunReadResponse](#schemarunreadresponse)]|false|none|[Response schema for `Get run details` endpoint]|
=======
|Response List Runs V1 Runs Get|[[RunReadResponse](#schemarunreadresponse)]|false|none|[Response schema for `Get run details` endpoint]|
>>>>>>> b165166 (chore: rebase)
|» RunReadResponse|[RunReadResponse](#schemarunreadresponse)|false|none|Response schema for `Get run details` endpoint|
|»» application_id|string|true|none|Application id|
|»» custom_metadata|any|false|none|Optional JSON metadata that was stored in alongside the run by the user|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|object|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|»» organization_id|string|true|none|Organization of the owner of the application run|
|»» status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|none|
|»» terminated_at|any|false|none|Timestamp showing when the application run reached a terminal state.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|string(date-time)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» triggered_at|string(date-time)|true|none|Timestamp showing when the application run was triggered|
|»» triggered_by|string|true|none|Id of the user who triggered the application run|
|»» user_payload|any|false|none|Field used internally by the Platform|
>>>>>>> 99401ec (Refactor tests)

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|object|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field. Can be used ine the `PUT /runs/{run-id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|
=======
|»» custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field. Can be used in the `PUT /runs/{run-id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|
>>>>>>> b165166 (chore: rebase)

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
|»» error_code|any|true|none|When the termination_reason is set to CANCELED_BY_SYSTEM, the error_code is set to define the        structured description of the error.|

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
|»» error_message|any|true|none|When the termination_reason is set to CANCELED_BY_SYSTEM, the error_message is set to provide        more insights to the error cause.|

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
|»» output|[RunOutput](#schemarunoutput)|true|none|none|
|»» run_id|string(uuid)|true|none|UUID of the application|
|»» state|[RunState](#schemarunstate)|true|none|none|
|»» statistics|[RunItemStatistics](#schemarunitemstatistics)|true|none|none|
|»»» item_count|integer|true|none|Total number of the items in the run|
|»»» item_pending_count|integer|true|none|The number of items in `PENDING` state|
|»»» item_processing_count|integer|true|none|The number of items in `PROCESSING` state|
|»»» item_skipped_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SKIPPED`|
|»»» item_succeeded_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SUCCEEDED`|
|»»» item_system_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SYSTEM_ERROR`|
|»»» item_user_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `USER_ERROR`|
|»» submitted_at|string(date-time)|true|none|Timestamp showing when the run was triggered|
|»» submitted_by|string|true|none|Id of the user who triggered the run|
|»» terminated_at|any|false|none|Timestamp showing when the run reached a terminal state.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|string(date-time)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» termination_reason|any|true|none|The termination reason of the run. When the run is not in `TERMINATED` state, the        termination_reason is `null`. If all items of of the run are processed (successfully or with an error), then        termination_reason is set to `ALL_ITEMS_PROCESSED`. If the run is cancelled by the user, the value is set to        `CANCELED_BY_USER`. If the run reaches the threshold of number of failed items, the Platform cancels the run        and sets the termination_reason to `CANCELED_BY_SYSTEM`.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[RunTerminationReason](#schemarunterminationreason)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» version_number|string|true|none|Application version number|

##### Enumerated Values

|Property|Value|
|---|---|
|output|NONE|
|output|PARTIAL|
|output|FULL|
|state|PENDING|
|state|PROCESSING|
|state|TERMINATED|
|*anonymous*|ALL_ITEMS_PROCESSED|
|*anonymous*|CANCELED_BY_SYSTEM|
|*anonymous*|CANCELED_BY_USER|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### create_run_v1_runs_post



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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
<<<<<<< HEAD
=======
  "application_version_id": "he-tme:v1.0.0-beta",
>>>>>>> 99401ec (Refactor tests)
=======
>>>>>>> b165166 (chore: rebase)
  "items": [
    {
      "external_id": "slide_1",
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
<<<<<<< HEAD
<<<<<<< HEAD
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
=======
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
>>>>>>> 99401ec (Refactor tests)
=======
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
>>>>>>> b165166 (chore: rebase)
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

<<<<<<< HEAD
<<<<<<< HEAD
*Initiate Run*

This endpoint initiates a processing run for a selected application and version, and returns a `run_id` for tracking purposes.
=======
*Initiate Application Run*

This endpoint initiates a processing run for a selected application version and returns an `application_run_id` for tracking purposes.
>>>>>>> 99401ec (Refactor tests)
=======
*Initiate Run*

This endpoint initiates a processing run for a selected application and version, and returns a `run_id` for tracking purposes.
>>>>>>> b165166 (chore: rebase)

Slide processing occurs asynchronously, allowing you to retrieve results for individual slides as soon as they
complete processing. The system typically processes slides in batches of four, though this number may be reduced
during periods of high demand.
Below is an example of the required payload for initiating an Atlas H&E TME processing run.

#### Payload

The payload includes `application_id`, optional `version_number`, and `items` base fields.

`application_id` is the unique identifier for the application.
`version_number` is the semantic version to use. If not provided, the latest available version will be used.

`items` includes the list of the items to process (slides, in case of HETA application).
Every item has a set of standard fields defined by the API, plus the custom_metadata, specific to the
chosen application.

Example payload structure with the comments:
```
{
<<<<<<< HEAD
<<<<<<< HEAD
    application_id: "he-tme",
    version_number: "1.0.0-beta",
    items: [{
        "external_id": "slide_1",
        "input_artifacts": [{
            "name": "user_slide",
            "download_url": "https://...",
            "custom_metadata": {
=======
    application_version_id: "he-tme:v1.0.0-beta",
=======
    application_id: "he-tme",
    version_number: "1.0.0-beta",
>>>>>>> b165166 (chore: rebase)
    items: [{
        "external_id": "slide_1",
        "input_artifacts": [{
            "name": "user_slide",
            "download_url": "https://...",
<<<<<<< HEAD
            "metadata": {
>>>>>>> 99401ec (Refactor tests)
=======
            "custom_metadata": {
>>>>>>> b165166 (chore: rebase)
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

| Parameter  | Description |
| :---- | :---- |
<<<<<<< HEAD
<<<<<<< HEAD
| `application_id` required | Unique ID for the application |
| `version_number` optional | Semantic version of the application. If not provided, the latest available version will be used |
| `items` required | List of submitted items (WSIs) with parameters described below. |
| `external_id` required | Unique WSI name or ID for easy reference to items, provided by the caller. The external_id should be unique across all items of the run.  |
=======
| `application_version_id` required | Unique ID for the application (must include version) |
| `items` required | List of submitted items (WSIs) with parameters described below. |
| `reference` required | Unique WSI name or ID for easy reference to results, provided by the caller. The reference should be unique across all items of the application run.  |
>>>>>>> 99401ec (Refactor tests)
=======
| `application_id` required | Unique ID for the application |
| `version_number` optional | Semantic version of the application. If not provided, the latest available version will be used |
| `items` required | List of submitted items (WSIs) with parameters described below. |
| `external_id` required | Unique WSI name or ID for easy reference to items, provided by the caller. The external_id should be unique across all items of the run.  |
>>>>>>> b165166 (chore: rebase)
| `input_artifacts` required | List of provided artifacts for a WSI; at the moment Atlas H&E-TME receives only 1 artifact per slide (the slide itself), but for some other applications this can be a slide and an segmentation map  |
| `name` required | Type of artifact; Atlas H&E-TME supports only `"input_slide"` |
| `download_url` required | Signed URL to the input file in the S3 or GCS; Should be valid for at least 6 days |
| `specimen: disease` required | Supported cancer types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) |
| `specimen: tissue` required | Supported tissue types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) |
| `staining_method` required | WSI stain /bio-marker; Atlas H&E-TME supports only `"H&E"` |
| `width_px` required | Integer value. Number of pixels of the WSI in the X dimension. |
| `height_px` required | Integer value. Number of pixels of the WSI in the Y dimension. |
| `resolution_mpp` required | Resolution of WSI in micrometers per pixel; check allowed range in Atlas H&E-TME manual |
| `media-type` required | Supported media formats; available values are: image/tiff  (for .tiff or .tif WSI) application/dicom (for DICOM ) application/zip (for zipped DICOM) application/octet-stream  (for .svs WSI) |
| `checksum_base64_crc32c` required | Base64 encoded big-endian CRC32C checksum of the WSI image |

#### Response

<<<<<<< HEAD
<<<<<<< HEAD
The endpoint returns the run UUID. After that the job is scheduled for the
execution in the background.

To check the status of the run call `v1/runs/{run_id}`.
=======
The endpoint returns the application run UUID. After that the job is scheduled for the
execution in the background.

To check the status of the run call `v1/runs/{application_run_id}`.
>>>>>>> 99401ec (Refactor tests)
=======
The endpoint returns the run UUID. After that the job is scheduled for the
execution in the background.

To check the status of the run call `v1/runs/{run_id}`.
>>>>>>> b165166 (chore: rebase)

#### Rejection

Apart from the authentication, authorization and malformed input error, the request can be
rejected when the quota limit is exceeded. More details on quotas is described in the
documentation

> Body parameter

```json
{
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
<<<<<<< HEAD
=======
  "application_version_id": "he-tme:v1.0.0-beta",
>>>>>>> 99401ec (Refactor tests)
=======
>>>>>>> b165166 (chore: rebase)
  "items": [
    {
      "external_id": "slide_1",
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
<<<<<<< HEAD
<<<<<<< HEAD
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
=======
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
>>>>>>> 99401ec (Refactor tests)
=======
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
>>>>>>> b165166 (chore: rebase)
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
<<<<<<< HEAD
<<<<<<< HEAD
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
=======
  "application_run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
>>>>>>> 99401ec (Refactor tests)
=======
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
>>>>>>> b165166 (chore: rebase)
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[RunCreationResponse](#schemaruncreationresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request - Input validation failed|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to create this run|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application version not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_run_v1_runs__run_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs/{run_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}',
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

`GET /v1/runs/{run_id}`

*Get run details*

<<<<<<< HEAD
<<<<<<< HEAD
This endpoint allows the caller to retrieve the current status of a run along with other relevant run details.
 A run becomes available immediately after it is created through the POST `/runs/` endpoint.

 To download the output results, use GET `/runs/{run_id}/` items to get outputs for all slides.
=======
This endpoint allows the caller to retrieve the current status of an application run along with other relevant run details.
 A run becomes available immediately after it is created through the POST `/runs/` endpoint.

 To download the output results, use GET `/runs/{application_run_id}/` results to get outputs for all slides.
>>>>>>> 99401ec (Refactor tests)
=======
This endpoint allows the caller to retrieve the current status of a run along with other relevant run details.
 A run becomes available immediately after it is created through the POST `/runs/` endpoint.

 To download the output results, use GET `/runs/{run_id}/` items to get outputs for all slides.
>>>>>>> b165166 (chore: rebase)
Access to a run is restricted to the user who created it.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|
=======
|application_run_id|path|string(uuid)|true|Application run id, returned by `POST /runs/` endpoint|
>>>>>>> 99401ec (Refactor tests)
=======
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|
>>>>>>> b165166 (chore: rebase)

> Example responses

> 200 Response

```json
{
<<<<<<< HEAD
<<<<<<< HEAD
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109",
  "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
  "error_message": "Run canceled given errors on more than 10 items.",
  "output": "NONE",
  "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
  "state": "PENDING",
  "statistics": {
    "item_count": 0,
    "item_pending_count": 0,
    "item_processing_count": 0,
    "item_skipped_count": 0,
    "item_succeeded_count": 0,
    "item_system_error_count": 0,
    "item_user_error_count": 0
  },
  "submitted_at": "2019-08-24T14:15:22Z",
  "submitted_by": "auth0|123456",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "termination_reason": "ALL_ITEMS_PROCESSED",
  "version_number": "0.4.4"
=======
  "application_run_id": "53c0c6ed-e767-49c4-ad7c-b1a749bf7dfe",
  "application_version_id": "he-tme:v0.4.4",
  "message": "The run was cancelled because the threshold of 3 items finishing in error state was reached. Query /runs/{run_id}/results to get the error message per item.",
  "metadata": {
=======
  "application_id": "he-tme",
  "custom_metadata": {
>>>>>>> b165166 (chore: rebase)
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109",
  "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
  "error_message": "Run canceled given errors on more than 10 items.",
  "output": "NONE",
  "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
  "state": "PENDING",
  "statistics": {
    "item_count": 0,
    "item_pending_count": 0,
    "item_processing_count": 0,
    "item_skipped_count": 0,
    "item_succeeded_count": 0,
    "item_system_error_count": 0,
    "item_user_error_count": 0
  },
  "submitted_at": "2019-08-24T14:15:22Z",
  "submitted_by": "auth0|123456",
  "terminated_at": "2024-01-15T10:30:45.123Z",
<<<<<<< HEAD
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
>>>>>>> 99401ec (Refactor tests)
=======
  "termination_reason": "ALL_ITEMS_PROCESSED",
  "version_number": "0.4.4"
>>>>>>> b165166 (chore: rebase)
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[RunReadResponse](#schemarunreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this run|None|
<<<<<<< HEAD
<<<<<<< HEAD
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found because it was deleted.|None|
=======
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Application run not found because it was deleted.|None|
>>>>>>> 99401ec (Refactor tests)
=======
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found because it was deleted.|None|
>>>>>>> b165166 (chore: rebase)
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### delete_run_items_v1_runs__run_id__artifacts_delete



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.delete('/api/v1/runs/{run_id}/artifacts', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}/artifacts',
<<<<<<< HEAD
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

`DELETE /v1/runs/{run_id}/artifacts`

*Delete Run Items*

This endpoint allows the caller to explicitly delete artifacts generated by a run.
It can only be invoked when the run has reached a final state
(PROCESSED, CANCELED_SYSTEM, CANCELED_USER).
Note that by default, all artifacts are automatically deleted 30 days after the run finishes,
 regardless of whether the caller explicitly requests deletion.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Run artifacts deleted|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### cancel_run_v1_runs__run_id__cancel_post



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('/api/v1/runs/{run_id}/cancel', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}/cancel',
=======
>>>>>>> b112cc6 (chore: Rebase)
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

<<<<<<< HEAD
`POST /v1/runs/{run_id}/cancel`

*Cancel Run*

The run can be canceled by the user who created the run.

The execution can be canceled any time while the application is not in a final state. The
pending items will not be processed and will not add to the cost.

When the application is canceled, the already completed items stay available for download.
=======
`DELETE /v1/runs/{run_id}/artifacts`

*Delete Run Items*

This endpoint allows the caller to explicitly delete artifacts generated by a run.
It can only be invoked when the run has reached a final state
(PROCESSED, CANCELED_SYSTEM, CANCELED_USER).
Note that by default, all artifacts are automatically deleted 30 days after the run finishes,
 regardless of whether the caller explicitly requests deletion.
>>>>>>> b112cc6 (chore: Rebase)

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|

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
<<<<<<< HEAD
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Successful Response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to cancel this run|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Conflict - The Run is already cancelled|None|
=======
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Run cancelled successfully|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to cancel this run|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
>>>>>>> 99401ec (Refactor tests)
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


<<<<<<< HEAD
### list_run_items_v1_runs__run_id__items_get
=======
### cancel_run_v1_runs__run_id__cancel_post
>>>>>>> b112cc6 (chore: Rebase)



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

<<<<<<< HEAD
r = requests.get('/api/v1/runs/{run_id}/items', headers = headers)
=======
r = requests.post('/api/v1/runs/{run_id}/cancel', headers = headers)
>>>>>>> b112cc6 (chore: Rebase)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

<<<<<<< HEAD
<<<<<<< HEAD
fetch('/api/v1/runs/{run_id}/items',
=======
fetch('/api/v1/runs/{application_run_id}/results',
=======
fetch('/api/v1/runs/{run_id}/cancel',
>>>>>>> b112cc6 (chore: Rebase)
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

`POST /v1/runs/{run_id}/cancel`

*Cancel Run*

The run can be canceled by the user who created the run.

The execution can be canceled any time while the application is not in a final state. The
pending items will not be processed and will not add to the cost.

When the application is canceled, the already completed items stay available for download.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|

> Example responses

> 202 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Successful Response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to cancel this run|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Conflict - The Run is already cancelled|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### put_run_custom_metadata_v1_runs__run_id__custom_metadata_put



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.put('/api/v1/runs/{run_id}/custom-metadata', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}/custom-metadata',
{
  method: 'PUT',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`PUT /v1/runs/{run_id}/custom-metadata`

*Put Run Custom Metadata*

> Body parameter

```json
{
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|
|body|body|[CustomMetadataUpdateRequest](#schemacustommetadataupdaterequest)|true|none|

> Example responses

> 200 Response

```json
null
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### list_run_items_v1_runs__run_id__items_get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs/{run_id}/items', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

<<<<<<< HEAD
fetch('/api/v1/runs/{application_run_id}/results',
>>>>>>> 99401ec (Refactor tests)
=======
fetch('/api/v1/runs/{run_id}/items',
>>>>>>> b112cc6 (chore: Rebase)
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

`GET /v1/runs/{run_id}/items`

*List Run Items*

<<<<<<< HEAD
<<<<<<< HEAD
List items in a run with filtering, sorting, and pagination capabilities.

Returns paginated items within a specific run. Results can be filtered
by item IDs, external_ids, status, and custom_metadata using JSONPath expressions.

### JSONPath Metadata Filtering
Use PostgreSQL JSONPath expressions to filter items using their custom_metadata.
=======
List results for items in an application run with filtering, sorting, and pagination capabilities.
=======
List items in a run with filtering, sorting, and pagination capabilities.
>>>>>>> b165166 (chore: rebase)

Returns paginated items within a specific run. Results can be filtered
by item IDs, external_ids, status, and custom_metadata using JSONPath expressions.

### JSONPath Metadata Filtering
<<<<<<< HEAD
Use PostgreSQL JSONPath expressions to filter results by their metadata.
>>>>>>> 99401ec (Refactor tests)
=======
Use PostgreSQL JSONPath expressions to filter items using their custom_metadata.
>>>>>>> b165166 (chore: rebase)

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

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|Run id, returned by `POST /runs/` endpoint|
|item_id__in|query|any|false|Filter for item ids|
|external_id__in|query|any|false|Filter for items by their external_id from the input payload|
<<<<<<< HEAD
|status__in|query|any|false|Filter for items in certain statuses|
<<<<<<< HEAD
|custom_metadata|query|any|false|JSONPath expression to filter items by their custom_metadata|
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|Sort the items by one or more fields. Use `+` for ascending and `-` for descending order.|

##### Detailed descriptions

**sort**: Sort the items by one or more fields. Use `+` for ascending and `-` for descending order.
                **Available fields:**
- `item_id`
- `run_id`
- `external_id`
- `status`
- `custom_metadata`

**Examples:**
- `?sort=item_id` - Sort by id of the item (ascending)
- `?sort=-external_id` - Sort by external ID (descending)
- `?sort=status&sort=-external_id` - Sort by status, then by external ID (descending)
=======
|metadata|query|any|false|JSONPath expression to filter results by their metadata|
=======
|state|query|any|false|Filter items by their state|
|termination_reason|query|any|false|Filter items by their termination reason. Only applies to TERMINATED items.|
|custom_metadata|query|any|false|JSONPath expression to filter items by their custom_metadata|
>>>>>>> b165166 (chore: rebase)
|page|query|integer|false|none|
|page_size|query|integer|false|none|
|sort|query|any|false|Sort the items by one or more fields. Use `+` for ascending and `-` for descending order.|

##### Detailed descriptions

**sort**: Sort the items by one or more fields. Use `+` for ascending and `-` for descending order.
                **Available fields:**
- `item_id`
- `run_id`
- `external_id`
- `custom_metadata`

**Examples:**
- `?sort=item_id` - Sort by id of the item (ascending)
<<<<<<< HEAD
- `?sort=-application_run_id` - Sort by id of the run (descending)
- `?sort=status&sort=-item_idt` - Sort by status, then by id of the item (descending)
>>>>>>> 99401ec (Refactor tests)
=======
- `?sort=-external_id` - Sort by external ID (descending)
- `?sort=custom_metadata&sort=-external_id` - Sort by metadata, then by external ID (descending)
>>>>>>> b165166 (chore: rebase)

> Example responses

> 200 Response

```json
[
  {
    "custom_metadata": {},
    "custom_metadata_checksum": "f54fe109",
    "error_message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
    "external_id": "slide_1",
    "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
<<<<<<< HEAD
    "message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
<<<<<<< HEAD
=======
    "metadata": {},
>>>>>>> 99401ec (Refactor tests)
=======
    "output": "NONE",
>>>>>>> b165166 (chore: rebase)
    "output_artifacts": [
      {
        "download_url": "http://example.com",
        "error_message": "string",
        "metadata": {},
        "name": "tissue_qc:tiff_heatmap",
        "output": "NONE",
        "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
        "state": "PENDING",
        "termination_reason": "SUCCEEDED"
      }
    ],
<<<<<<< HEAD
<<<<<<< HEAD
    "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
=======
    "reference": "slide_1",
>>>>>>> 99401ec (Refactor tests)
    "status": "PENDING",
    "terminated_at": "2024-01-15T10:30:45.123Z"
=======
    "state": "PENDING",
    "terminated_at": "2024-01-15T10:30:45.123Z",
    "termination_reason": "SUCCEEDED"
>>>>>>> b165166 (chore: rebase)
  }
]
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Run not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

#### Response Schema

Status Code **200**

*Response List Run Items V1 Runs  Run Id  Items Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
|Response List Run Items V1 Runs  Run Id  Items Get|[[ItemResultReadResponse](#schemaitemresultreadresponse)]|false|none|[Response schema for items in `List Run Items` endpoint]|
|» ItemResultReadResponse|[ItemResultReadResponse](#schemaitemresultreadresponse)|false|none|Response schema for items in `List Run Items` endpoint|
|»» custom_metadata|any|true|none|The custom_metadata of the item that has been provided by the user on run creation.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|object|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|»» error_message|any|false|none|The error message in case the item is in `error_system` or `error_user` state|
=======
|Response List Run Results V1 Runs  Application Run Id  Results Get|[[ItemResultReadResponse](#schemaitemresultreadresponse)]|false|none|[Response schema for items in `List Run Results` endpoint]|
|» ItemResultReadResponse|[ItemResultReadResponse](#schemaitemresultreadresponse)|false|none|Response schema for items in `List Run Results` endpoint|
|»» application_run_id|string(uuid)|true|none|Application run UUID to which the item belongs|
|»» error|any|false|none|The error message in case the item is in `error_system` or `error_user` state|
>>>>>>> 99401ec (Refactor tests)
=======
|»» custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field.Can be used in the `PUT /runs/{run-id}/items/{external_id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|

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
|»» error_message|any|false|none|The error message in case the `termination_reason` is in `USER_ERROR` or `SYSTEM_ERROR`|
>>>>>>> b165166 (chore: rebase)

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
|»» external_id|string|true|none|The external_id of the item from the user payload|
|»» item_id|string(uuid)|true|none|Item UUID generated by the Platform|
<<<<<<< HEAD
|»» message|any|true|none|The error message in case the item is in `error_system` or `error_user` state|

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
<<<<<<< HEAD
=======
|»» metadata|any|true|none|The metadata of the item that has been provided by the user on application run creation.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|object|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
>>>>>>> 99401ec (Refactor tests)
=======
|»» output|[ItemOutput](#schemaitemoutput)|true|none|none|
>>>>>>> b165166 (chore: rebase)
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
|»»»» error_message|any|false|none|Error message when artifact is in error state|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|string|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»» metadata|object|true|none|The metadata of the output artifact, provided by the application|
|»»»» name|string|true|none|Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint.|
|»»»» output|[ArtifactOutput](#schemaartifactoutput)|true|none|none|
|»»»» output_artifact_id|string(uuid)|true|none|The Id of the artifact. Used internally|
|»»»» state|[ArtifactState](#schemaartifactstate)|true|none|none|
|»»»» termination_reason|any|false|none|The reason for termination when state is TERMINATED|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|[ArtifactTerminationReason](#schemaartifactterminationreason)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» state|[ItemState](#schemaitemstate)|true|none|none|
|»» terminated_at|any|false|none|Timestamp showing when the item reached a terminal state.|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|string(date-time)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

*continued*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» termination_reason|any|false|none|When the `state` is `TERMINATED` this will explain why`SUCCEEDED` -> Successful processing.`USER_ERROR` -> Failed because the provided input was invalid.`SYSTEM_ERROR` -> There was an error in the model or platform.`SKIPPED` -> Was cancelled|

*anyOf*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|[ItemTerminationReason](#schemaitemterminationreason)|false|none|none|

*or*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»»» *anonymous*|null|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|output|NONE|
|output|FULL|
|output|NONE|
|output|AVAILABLE|
|output|DELETED_BY_USER|
|output|DELETED_BY_SYSTEM|
|state|PENDING|
|state|PROCESSING|
|state|TERMINATED|
|*anonymous*|SUCCEEDED|
|*anonymous*|USER_ERROR|
|*anonymous*|SYSTEM_ERROR|
|*anonymous*|SKIPPED|
|state|PENDING|
|state|PROCESSING|
|state|TERMINATED|
|*anonymous*|SUCCEEDED|
|*anonymous*|USER_ERROR|
|*anonymous*|SYSTEM_ERROR|
|*anonymous*|SKIPPED|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### get_item_by_run_v1_runs__run_id__items__external_id__get



> Code samples

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('/api/v1/runs/{run_id}/items/{external_id}', headers = headers)

print(r.json())

```

```javascript

const headers = {
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}/items/{external_id}',
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

`GET /v1/runs/{run_id}/items/{external_id}`

*Get Item By Run*

Retrieve details of a specific item (slide) by its external ID and the run ID.

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|The run id, returned by `POST /runs/` endpoint|
|external_id|path|string|true|The `external_id` that was defined for the item by the customer that triggered the run.|

> Example responses

> 200 Response

```json
{
  "custom_metadata": {},
  "custom_metadata_checksum": "f54fe109",
  "error_message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
  "external_id": "slide_1",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "output": "NONE",
  "output_artifacts": [
    {
      "download_url": "http://example.com",
      "error_message": "string",
      "metadata": {},
      "name": "tissue_qc:tiff_heatmap",
      "output": "NONE",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
      "state": "PENDING",
      "termination_reason": "SUCCEEDED"
    }
  ],
  "state": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "termination_reason": "SUCCEEDED"
}
```

#### Responses

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ItemResultReadResponse](#schemaitemresultreadresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Forbidden - You don't have permission to see this item|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found - Item with given ID does not exist|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


### put_item_custom_metadata_by_run_v1_runs__run_id__items__external_id__custom_metadata_put



> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.put('/api/v1/runs/{run_id}/items/{external_id}/custom-metadata', headers = headers)

print(r.json())

```

```javascript
const inputBody = '{
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109"
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('/api/v1/runs/{run_id}/items/{external_id}/custom-metadata',
{
  method: 'PUT',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

`PUT /v1/runs/{run_id}/items/{external_id}/custom-metadata`

*Put Item Custom Metadata By Run*

> Body parameter

```json
{
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109"
}
```

#### Parameters

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|run_id|path|string(uuid)|true|The run id, returned by `POST /runs/` endpoint|
|external_id|path|string|true|The `external_id` that was defined for the item by the customer that triggered the run.|
|body|body|[CustomMetadataUpdateRequest](#schemacustommetadataupdaterequest)|true|none|

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


To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2AuthorizationCodeBearer


## Schemas

### ApplicationReadResponse






```json
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "name": "Atlas H&E-TME",
  "regulatory_classes": [
    "RUO"
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b165166 (chore: rebase)
  ],
  "versions": [
    {
      "number": "1.0.0",
      "released_at": "2025-09-15T10:30:45.123Z"
    }
<<<<<<< HEAD
=======
>>>>>>> 99401ec (Refactor tests)
=======
>>>>>>> b165166 (chore: rebase)
  ]
}

```

ApplicationReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application ID|
|description|string|true|none|Describing what the application can do|
|name|string|true|none|Application display name|
|regulatory_classes|[string]|true|none|Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA.|
<<<<<<< HEAD
<<<<<<< HEAD
|versions|[[ApplicationVersion](#schemaapplicationversion)]|true|none|All version numbers available to the user|
=======
>>>>>>> 99401ec (Refactor tests)
=======
|versions|[[ApplicationVersion](#schemaapplicationversion)]|true|none|All version numbers available to the user|
>>>>>>> b165166 (chore: rebase)

### ApplicationReadShortResponse
<<<<<<< HEAD
=======






```json
{
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "latest_version": {
    "number": "1.0.0",
    "released_at": "2025-09-15T10:30:45.123Z"
  },
  "name": "Atlas H&E-TME",
  "regulatory_classes": [
    "RUO"
  ]
}

```

ApplicationReadShortResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application ID|
|description|string|true|none|Describing what the application can do|
|latest_version|any|false|none|The version with highest version number available to the user|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ApplicationVersion](#schemaapplicationversion)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|Application display name|
|regulatory_classes|[string]|true|none|Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA.|

### ApplicationVersion
>>>>>>> b112cc6 (chore: Rebase)






```json
{
<<<<<<< HEAD
<<<<<<< HEAD
  "application_id": "he-tme",
  "description": "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the tumor microenvironment.",
  "latest_version": {
    "number": "1.0.0",
    "released_at": "2025-09-15T10:30:45.123Z"
  },
  "name": "Atlas H&E-TME",
  "regulatory_classes": [
    "RUO"
  ]
=======
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
>>>>>>> 99401ec (Refactor tests)
=======
  "number": "1.0.0",
  "released_at": "2025-09-15T10:30:45.123Z"
>>>>>>> b165166 (chore: rebase)
}

```

<<<<<<< HEAD
ApplicationReadShortResponse
=======
ApplicationVersion
>>>>>>> b112cc6 (chore: Rebase)

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|application_id|string|true|none|Application ID|
|description|string|true|none|Describing what the application can do|
|latest_version|any|false|none|The version with highest version number available to the user|
=======
|number|string|true|none|The number of the latest version|
|released_at|string(date-time)|true|none|The timestamp for when the application version was made available in the Platform|

### ArtifactOutput






```json
"NONE"

```

ArtifactOutput

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ArtifactOutput|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ArtifactOutput|NONE|
|ArtifactOutput|AVAILABLE|
|ArtifactOutput|DELETED_BY_USER|
|ArtifactOutput|DELETED_BY_SYSTEM|

### ArtifactState






```json
"PENDING"

```

ArtifactState

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ArtifactState|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ArtifactState|PENDING|
|ArtifactState|PROCESSING|
|ArtifactState|TERMINATED|

### ArtifactTerminationReason






```json
"SUCCEEDED"

```

ArtifactTerminationReason

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ArtifactTerminationReason|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ArtifactTerminationReason|SUCCEEDED|
|ArtifactTerminationReason|USER_ERROR|
|ArtifactTerminationReason|SYSTEM_ERROR|
|ArtifactTerminationReason|SKIPPED|

### Auth0Organization






```json
{
  "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
  "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
  "aignostics_bucket_name": "aignostics-platform-bucket",
  "aignostics_bucket_protocol": "gs",
  "aignostics_logfire_token": "your-logfire-token",
  "aignostics_sentry_dsn": "https://2354s3#ewsha@o44.ingest.us.sentry.io/34345123432",
  "display_name": "Aignostics GmbH",
  "id": "org_123456",
  "name": "aignx"
}

```

Auth0Organization

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|aignostics_bucket_hmac_access_key_id|string|true|none|HMAC access key ID for the Aignostics-provided storage bucket. Used to authenticate requests for uploading files and generating signed URLs|
|aignostics_bucket_hmac_secret_access_key|string|true|none|HMAC secret access key paired with the access key ID. Keep this credential secure.|
|aignostics_bucket_name|string|true|none|Name of the bucket provided by Aignostics for storing input artifacts (slide images)|
|aignostics_bucket_protocol|string|true|none|Protocol to use for bucket access. Defines the URL scheme for connecting to the storage service|
|aignostics_logfire_token|string|true|none|Authentication token for Logfire observability service. Enables sending application logs and performance metrics to Aignostics for monitoring and support|
|aignostics_sentry_dsn|string|true|none|Data Source Name (DSN) for Sentry error tracking service. Allows automatic reporting of errors and exceptions to Aignostics support team|
|display_name|any|false|none|Public organization name (E.g. “Aignostics GmbH”)|
>>>>>>> b165166 (chore: rebase)

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|» *anonymous*|[ApplicationVersion](#schemaapplicationversion)|false|none|none|
=======
|» *anonymous*|string|false|none|none|
>>>>>>> b165166 (chore: rebase)

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|name|string|true|none|Application display name|
|regulatory_classes|[string]|true|none|Regulatory classes, to which the applications comply with. Possible values include: RUO, IVDR, FDA.|

### ApplicationVersion
=======
|id|string|true|none|Unique organization identifier|
|name|any|false|none|Organization name (E.g. “aignx”)|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### Auth0User
>>>>>>> b165166 (chore: rebase)






```json
{
<<<<<<< HEAD
  "number": "1.0.0",
  "released_at": "2025-09-15T10:30:45.123Z"
=======
  "email": "user@domain.com",
  "email_verified": true,
  "family_name": "Doe",
  "given_name": "Jane",
  "id": "auth0|123456",
  "name": "Jane Doe",
  "nickname": "jdoe",
  "picture": "https://example.com/jdoe.jpg",
  "updated_at": "2023-10-05T14:48:00.000Z"
>>>>>>> b165166 (chore: rebase)
}

```

<<<<<<< HEAD
ApplicationVersion
=======
Auth0User
>>>>>>> b165166 (chore: rebase)

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|number|string|true|none|The number of the latest version|
|released_at|string(date-time)|true|none|The timestamp for when the application version was made available in the Platform|
=======
|input_artifacts|[[InputArtifactReadResponse](#schemainputartifactreadresponse)]|true|none|Lists required input fields, that should be provided by the caller|
|output_artifacts|[[OutputArtifactReadResponse](#schemaoutputartifactreadresponse)]|true|none|Lists the structure of the output artifacts generated by the application|
|version|string|true|none|Semantic version of the application|
>>>>>>> 99401ec (Refactor tests)
=======
|email|any|false|none|User email|

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
|email_verified|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|family_name|any|false|none|none|

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
|given_name|any|false|none|none|

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
|id|string|true|none|Unique user identifier|
|name|any|false|none|First and last name of the user|

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
|nickname|any|false|none|none|

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
|picture|any|false|none|none|

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
|updated_at|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### CustomMetadataUpdateRequest






```json
{
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109"
}

```

CustomMetadataUpdateRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|custom_metadata|any|false|none|JSON metadata that should be set for the run|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|custom_metadata_checksum|any|false|none|Optional field to verify that the latest custom metadata was known. If set to the checksum retrieved via the /runs endpoint, it must match the checksum of the current value in the database.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|
>>>>>>> b165166 (chore: rebase)

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

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|download_url|string(uri)|true|none|[Signed URL](https://cloud.google.com/cdn/docs/using-signed-urls) to the input artifact file. The URL should be valid for at least 6 days from the payload submission time.|
|metadata|object|true|none|The metadata of the artifact, required by the application version. The JSON schema of the metadata can be requested by `/v1/versions/{application_version_id}`. The schema is located in `input_artifacts.[].metadata_schema`|
|name|string|true|none|Type of artifact. For Atlas H&E-TME, use "input_slide"|
<<<<<<< HEAD
=======

### ItemCreationRequest






```json
{
  "custom_metadata": {
    "case": "abc"
  },
  "external_id": "slide_1",
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
  ]
}

```

ItemCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
>>>>>>> 99401ec (Refactor tests)
=======
|custom_metadata|any|false|none|Optional JSON custom_metadata to store additional information alongside an item.|
>>>>>>> b112cc6 (chore: Rebase)

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|external_id|string|true|none|Unique identifier for this item within the run. Used for referencing items. Must be unique across all items in the same run|
|input_artifacts|[[InputArtifactCreationRequest](#schemainputartifactcreationrequest)]|true|none|List of input artifacts for this item. For Atlas H&E-TME, typically contains one artifact (the slide image)|

### ItemOutput






```json
"NONE"

```

ItemOutput

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemOutput|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemOutput|NONE|
|ItemOutput|FULL|

### ItemResultReadResponse






```json
{
<<<<<<< HEAD
  "custom_metadata": {
    "case": "abc"
  },
  "external_id": "slide_1",
  "input_artifacts": [
=======
  "custom_metadata": {},
  "custom_metadata_checksum": "f54fe109",
  "error_message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
  "external_id": "slide_1",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "output": "NONE",
  "output_artifacts": [
>>>>>>> b165166 (chore: rebase)
    {
      "download_url": "http://example.com",
      "error_message": "string",
      "metadata": {},
      "name": "tissue_qc:tiff_heatmap",
      "output": "NONE",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
      "state": "PENDING",
      "termination_reason": "SUCCEEDED"
    }
<<<<<<< HEAD
  ]
=======
  ],
<<<<<<< HEAD
  "metadata": {
    "case": "abc"
  },
  "reference": "slide_1"
>>>>>>> 99401ec (Refactor tests)
=======
  "state": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "termination_reason": "SUCCEEDED"
>>>>>>> b165166 (chore: rebase)
}

```

ItemResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|custom_metadata|any|false|none|Optional JSON custom_metadata to store additional information alongside an item.|
=======
|input_artifacts|[[InputArtifactCreationRequest](#schemainputartifactcreationrequest)]|true|none|List of input artifacts for this item. For Atlas H&E-TME, typically contains one artifact (the slide image)|
|metadata|any|false|none|Optional JSON metadata to store additional information alongside an item.|
=======
|custom_metadata|any|true|none|The custom_metadata of the item that has been provided by the user on run creation.|
>>>>>>> b165166 (chore: rebase)

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field.Can be used in the `PUT /runs/{run-id}/items/{external_id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|

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
<<<<<<< HEAD
|reference|string|true|none|none|
|status|[ItemStatus](#schemaitemstatus)|true|none|none|
|terminated_at|any|false|none|Timestamp showing when the item reached a terminal state.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|
>>>>>>> 99401ec (Refactor tests)

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|external_id|string|true|none|Unique identifier for this item within the run. Used for referencing items. Must be unique across all items in the same run|
|input_artifacts|[[InputArtifactCreationRequest](#schemainputartifactcreationrequest)]|true|none|List of input artifacts for this item. For Atlas H&E-TME, typically contains one artifact (the slide image)|

### ItemReadResponse






```json
{
<<<<<<< HEAD
  "external_id": "sample-123",
=======
  "custom_metadata": {},
  "error_message": "string",
  "external_id": "slide_1",
>>>>>>> b112cc6 (chore: Rebase)
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
<<<<<<< HEAD
  "message": "Processing started",
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
=======
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
>>>>>>> 99401ec (Refactor tests)
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}

```

ItemReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|external_id|string|true|none|none|
|item_id|string(uuid)|true|none|none|
|message|any|false|none|none|
=======
|application_run_id|string(uuid)|true|none|Application run UUID to which the item belongs|
|error|any|false|none|The error message in case the item is in `error_system` or `error_user` state|
>>>>>>> 99401ec (Refactor tests)
=======
|error_message|any|false|none|The error message in case the `termination_reason` is in `USER_ERROR` or `SYSTEM_ERROR`|
>>>>>>> b165166 (chore: rebase)

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
<<<<<<< HEAD
|run_id|any|false|none|none|

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
|status|[ItemStatus](#schemaitemstatus)|true|none|none|
|terminated_at|any|false|none|Timestamp showing when the item reached a terminal state.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### ItemResultReadResponse






```json
{
  "custom_metadata": {},
  "error_message": "string",
  "external_id": "slide_1",
  "item_id": "4d8cd62e-a579-4dae-af8c-3172f96f8f7c",
  "message": "This item was not processed because the threshold of 3 items finishing in error state (user or system error) was reached before the item was processed.",
  "output_artifacts": [
    {
      "download_url": "http://example.com",
      "metadata": {},
      "name": "tissue_qc:tiff_heatmap",
      "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b"
    }
  ],
  "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
  "status": "PENDING",
  "terminated_at": "2024-01-15T10:30:45.123Z"
}

```

ItemResultReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|custom_metadata|any|true|none|The custom_metadata of the item that has been provided by the user on run creation.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|error_message|any|false|none|The error message in case the item is in `error_system` or `error_user` state|

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
=======
>>>>>>> b112cc6 (chore: Rebase)
|external_id|string|true|none|The external_id of the item from the user payload|
|item_id|string(uuid)|true|none|Item UUID generated by the Platform|
<<<<<<< HEAD
|message|any|true|none|The error message in case the item is in `error_system` or `error_user` state|

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
<<<<<<< HEAD
|output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.|
|run_id|string(uuid)|true|none|Run UUID to which the item belongs|
|status|[ItemStatus](#schemaitemstatus)|true|none|When the item is not processed yet, the status is set to `pending`.When the item is successfully finished, status is set to `succeeded`, and the processing resultsbecome available for download in `output_artifacts` field.When the item processing is failed because the provided item is invalid, the status is set to`error_user`. When the item processing failed because of the error in the model or platform,the status is set to `error_system`. When the run is canceled, the status of allpending items is set to either `cancelled_user` or `cancelled_system`.|
=======
|metadata|any|true|none|The metadata of the item that has been provided by the user on application run creation.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.|
|reference|string|true|none|The reference of the item from the user payload|
|status|[ItemStatus](#schemaitemstatus)|true|none|When the item is not processed yet, the status is set to `pending`.When the item is successfully finished, status is set to `succeeded`, and the processing resultsbecome available for download in `output_artifacts` field.When the item processing is failed because the provided item is invalid, the status is set to`error_user`. When the item processing failed because of the error in the model or platform,the status is set to `error_system`. When the application_run is canceled, the status of allpending items is set to either `cancelled_user` or `cancelled_system`.|
>>>>>>> 99401ec (Refactor tests)
=======
|output|[ItemOutput](#schemaitemoutput)|true|none|The output status of the item (NONE, FULL)|
|output_artifacts|[[OutputArtifactResultReadResponse](#schemaoutputartifactresultreadresponse)]|true|none|The list of the results generated by the application algorithm. The number of files and theirtypes depend on the particular application version, call `/v1/versions/{version_id}` to getthe details.|
|state|[ItemState](#schemaitemstate)|true|none|The item moves from `PENDING` to `PROCESSING` to `TERMINATED` state.When terminated, consult the `termination_reason` property to see whether it was successful.|
>>>>>>> b165166 (chore: rebase)
|terminated_at|any|false|none|Timestamp showing when the item reached a terminal state.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|termination_reason|any|false|none|When the `state` is `TERMINATED` this will explain why`SUCCEEDED` -> Successful processing.`USER_ERROR` -> Failed because the provided input was invalid.`SYSTEM_ERROR` -> There was an error in the model or platform.`SKIPPED` -> Was cancelled|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ItemTerminationReason](#schemaitemterminationreason)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### ItemState






```json
"PENDING"

```

ItemState

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemState|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemState|PENDING|
|ItemState|PROCESSING|
|ItemState|TERMINATED|

### ItemTerminationReason






```json
"SUCCEEDED"

```

ItemTerminationReason

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ItemTerminationReason|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|ItemTerminationReason|SUCCEEDED|
|ItemTerminationReason|USER_ERROR|
|ItemTerminationReason|SYSTEM_ERROR|
|ItemTerminationReason|SKIPPED|

### MeReadResponse






```json
{
  "organization": {
<<<<<<< HEAD
<<<<<<< HEAD
    "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
    "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
=======
    "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
>>>>>>> 99401ec (Refactor tests)
=======
    "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
    "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
>>>>>>> b165166 (chore: rebase)
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

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|organization|[OrganizationReadResponse](#schemaorganizationreadresponse)|true|none|Part of response schema for Organization object in `Get current user` endpoint.This model corresponds to the response schema returned fromAuth0 GET /v2/organizations/{id} endpoint, flattens out the metadata outand doesn't return branding or token_quota objects.For details, see:https://auth0.com/docs/api/management/v2/organizations/get-organizations-by-id#### Configuration for integrating with Aignostics Platform services.The Aignostics Platform API requires signed URLs for input artifacts (slide images). To simplify this process,Aignostics provides a dedicated storage bucket. The HMAC credentials below grant read and writeaccess to this bucket, allowing you to upload files and generate the signed URLs needed for API calls.Additionally, logging and error reporting tokens enable Aignostics to provide better support and monitorsystem performance for your integration.|
|user|[UserReadResponse](#schemauserreadresponse)|true|none|Part of response schema for User object in `Get current user` endpoint.This model corresponds to the response schema returned fromAuth0 GET /v2/users/{id} endpoint.For details, see:https://auth0.com/docs/api/management/v2/users/get-users-by-id|

### OrganizationReadResponse






```json
{
<<<<<<< HEAD
  "aignostics_bucket_hmac_access_key_id": "YOUR_HMAC_ACCESS_KEY_ID",
  "aignostics_bucket_hmac_secret_access_key": "YOUR/HMAC/SECRET_ACCESS_KEY",
=======
  "aignostics_bucket_hmac_access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "aignostics_bucket_hmac_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
>>>>>>> 99401ec (Refactor tests)
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

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|aignostics_bucket_hmac_access_key_id|string|true|none|HMAC access key ID for the Aignostics-provided storage bucket. Used to authenticate requests for uploading files and generating signed URLs|
|aignostics_bucket_hmac_secret_access_key|string|true|none|HMAC secret access key paired with the access key ID. Keep this credential secure.|
|aignostics_bucket_name|string|true|none|Name of the bucket provided by Aignostics for storing input artifacts (slide images)|
|aignostics_bucket_protocol|string|true|none|Protocol to use for bucket access. Defines the URL scheme for connecting to the storage service|
|aignostics_logfire_token|string|true|none|Authentication token for Logfire observability service. Enables sending application logs and performance metrics to Aignostics for monitoring and support|
|aignostics_sentry_dsn|string|true|none|Data Source Name (DSN) for Sentry error tracking service. Allows automatic reporting of errors and exceptions to Aignostics support team|
|display_name|any|false|none|Public organization name (E.g. “Aignostics GmbH”)|

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
|id|string|true|none|Unique organization identifier|
|name|any|false|none|Organization name (E.g. “aignx”)|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|
=======
|organization|[Auth0Organization](#schemaauth0organization)|true|none|Model for Auth0 Organization object returned from Auth0 API.For details, see:https://auth0.com/docs/api/management/v2#!/Organizations/get_organizations_by_idAignostics-specific metadata fields are extracted from the `metadata` field.|
|user|[Auth0User](#schemaauth0user)|true|none|Model for Auth0 User object returned from Auth0 API.For details, see:https://auth0.com/docs/api/management/v2/users/get-users-by-id|
>>>>>>> b165166 (chore: rebase)

### OutputArtifact
<<<<<<< HEAD
=======






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

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|visibility|[OutputArtifactVisibility](#schemaoutputartifactvisibility)|true|none|none|

<<<<<<< HEAD
<<<<<<< HEAD
### OutputArtifactReadResponse
>>>>>>> 99401ec (Refactor tests)
=======
### OutputArtifact
>>>>>>> b112cc6 (chore: Rebase)






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

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|metadata_schema|object|true|none|none|
|mime_type|string|true|none|none|
|name|string|true|none|none|
|scope|[OutputArtifactScope](#schemaoutputartifactscope)|true|none|none|
|visibility|[OutputArtifactVisibility](#schemaoutputartifactvisibility)|true|none|none|

=======
>>>>>>> b165166 (chore: rebase)
### OutputArtifactResultReadResponse






```json
{
  "download_url": "http://example.com",
  "error_message": "string",
  "metadata": {},
  "name": "tissue_qc:tiff_heatmap",
  "output": "NONE",
  "output_artifact_id": "3f78e99c-5d35-4282-9e82-63c422f3af1b",
  "state": "PENDING",
  "termination_reason": "SUCCEEDED"
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
|error_message|any|false|none|Error message when artifact is in error state|

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
|metadata|object|true|none|The metadata of the output artifact, provided by the application|
|name|string|true|none|Name of the output from the output schema from the `/v1/versions/{version_id}` endpoint.|
|output|[ArtifactOutput](#schemaartifactoutput)|true|none|The output status of the artifact (NONE, FULL)|
|output_artifact_id|string(uuid)|true|none|The Id of the artifact. Used internally|
|state|[ArtifactState](#schemaartifactstate)|true|none|The current state of the artifact (PENDING, PROCESSING, TERMINATED)|
|termination_reason|any|false|none|The reason for termination when state is TERMINATED|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ArtifactTerminationReason](#schemaartifactterminationreason)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

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

### OutputArtifactVisibility
<<<<<<< HEAD
=======






```json
"INTERNAL"

```

OutputArtifactVisibility

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|OutputArtifactVisibility|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|OutputArtifactVisibility|INTERNAL|
|OutputArtifactVisibility|EXTERNAL|

<<<<<<< HEAD
<<<<<<< HEAD
### PayloadInputArtifact
>>>>>>> 99401ec (Refactor tests)
=======
### OutputArtifactVisibility
>>>>>>> b112cc6 (chore: Rebase)






```json
"INTERNAL"

```

OutputArtifactVisibility

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|OutputArtifactVisibility|string|false|none|none|

##### Enumerated Values
=======
### RunCreationRequest
>>>>>>> b165166 (chore: rebase)

<<<<<<< HEAD
|Property|Value|
|---|---|
|OutputArtifactVisibility|INTERNAL|
|OutputArtifactVisibility|EXTERNAL|
=======





```json
{
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "items": [
    {
      "external_id": "slide_1",
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
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
}

```

RunCreationRequest

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Unique ID for the application to use for processing|
|custom_metadata|any|false|none|Optional JSON metadata to store additional information alongside the run|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ItemCreationRequest](#schemaitemcreationrequest)]|true|none|List of items (slides) to process. Each item represents a whole slide image (WSI) with its associated metadata and artifacts|
|version_number|any|false|none|Semantic version of the application to use for processing. If not provided, the latest available version will be used|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### RunCreationResponse






```json
{
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}

```

RunCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|run_id|string(uuid)|false|none|none|
>>>>>>> b112cc6 (chore: Rebase)

### RunItemStatistics






```json
{
<<<<<<< HEAD
<<<<<<< HEAD
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
=======
  "application_version_id": "he-tme:v1.0.0-beta",
>>>>>>> 99401ec (Refactor tests)
  "items": [
    {
      "external_id": "slide_1",
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
<<<<<<< HEAD
      ]
    }
  ],
  "version_number": "1.0.0-beta1"
=======
      ],
      "reference": "slide_1"
    }
  ],
  "metadata": {
    "department": "D1",
    "study": "abc-1"
  }
>>>>>>> 99401ec (Refactor tests)
=======
  "item_count": 0,
  "item_pending_count": 0,
  "item_processing_count": 0,
  "item_skipped_count": 0,
  "item_succeeded_count": 0,
  "item_system_error_count": 0,
  "item_user_error_count": 0
>>>>>>> b165166 (chore: rebase)
}

```

RunItemStatistics

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
<<<<<<< HEAD
|application_id|string|true|none|Unique ID for the application to use for processing|
|custom_metadata|any|false|none|Optional JSON metadata to store additional information alongside the run|
=======
|application_version_id|string|true|none|Unique ID for the application version to use for processing. Must include version suffix (e.g., 'he-tme:v1.0.0-beta')|
|items|[[ItemCreationRequest](#schemaitemcreationrequest)]|true|none|List of items (slides) to process. Each item represents a whole slide image (WSI) with its associated metadata and artifacts|
|metadata|any|false|none|Optional JSON metadata to store additional information alongside the application run|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|
=======
|item_count|integer|true|none|Total number of the items in the run|
|item_pending_count|integer|true|none|The number of items in `PENDING` state|
|item_processing_count|integer|true|none|The number of items in `PROCESSING` state|
|item_skipped_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SKIPPED`|
|item_succeeded_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SUCCEEDED`|
|item_system_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SYSTEM_ERROR`|
|item_user_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `USER_ERROR`|
>>>>>>> b165166 (chore: rebase)

### RunOutput






```json
"NONE"

```

RunOutput

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RunOutput|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|RunOutput|NONE|
|RunOutput|PARTIAL|
|RunOutput|FULL|

### RunReadResponse






```json
{
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109",
  "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
  "error_message": "Run canceled given errors on more than 10 items.",
  "output": "NONE",
  "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
  "state": "PENDING",
  "statistics": {
    "item_count": 0,
    "item_pending_count": 0,
    "item_processing_count": 0,
    "item_skipped_count": 0,
    "item_succeeded_count": 0,
    "item_system_error_count": 0,
    "item_user_error_count": 0
  },
  "submitted_at": "2019-08-24T14:15:22Z",
  "submitted_by": "auth0|123456",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "termination_reason": "ALL_ITEMS_PROCESSED",
  "version_number": "0.4.4"
}

```

RunReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application id|
|custom_metadata|any|false|none|Optional JSON metadata that was stored in alongside the run by the user|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|organization_id|string|true|none|Organization of the owner of the application run|
|status|[ApplicationRunStatus](#schemaapplicationrunstatus)|true|none|When the application run request is received by the Platform, the `status` of it is set to`running`. When the application run is scheduled, the input items will be processed and the result willbe generated incrementally. The results can be downloaded via `/v1/runs/{run_id}/results` endpoint.When all items are processed and all results are generated, the application status is set to`completed`. If the processing is done, but some items fail, the status is set to`completed_with_error`.When the application run reaches the threshold of number of failed items, the wholeapplication run is set to `canceled_system` and the remaining pending items are not processed.When the application run fails, the finished item results are available for download.If the application run is canceled by calling `POST /v1/runs/{run_id}/cancel` endpoint, theprocessing of the items is stopped, and the application status is set to `cancelled_user`|
|terminated_at|any|false|none|Timestamp showing when the application run reached a terminal state.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|triggered_at|string(date-time)|true|none|Timestamp showing when the application run was triggered|
|triggered_by|string|true|none|Id of the user who triggered the application run|
|user_payload|any|false|none|Field used internally by the Platform|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
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
>>>>>>> 99401ec (Refactor tests)

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
=======
>>>>>>> b112cc6 (chore: Rebase)
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
<<<<<<< HEAD
|items|[[ItemCreationRequest](#schemaitemcreationrequest)]|true|none|List of items (slides) to process. Each item represents a whole slide image (WSI) with its associated metadata and artifacts|
|version_number|any|false|none|Semantic version of the application to use for processing. If not provided, the latest available version will be used|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

### RunCreationResponse






```json
{
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}

```

RunCreationResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|run_id|string(uuid)|false|none|none|

### RunItemStatistics






```json
{
  "item_count": 0,
  "item_pending_count": 0,
  "item_processing_count": 0,
  "item_skipped_count": 0,
  "item_succeeded_count": 0,
  "item_system_error_count": 0,
  "item_user_error_count": 0
}

```

RunItemStatistics

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|item_count|integer|true|none|Total number of the items in the run|
|item_pending_count|integer|true|none|The number of items in `PENDING` state|
|item_processing_count|integer|true|none|The number of items in `PROCESSING` state|
|item_skipped_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SKIPPED`|
|item_succeeded_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SUCCEEDED`|
|item_system_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `SYSTEM_ERROR`|
|item_user_error_count|integer|true|none|The number of items in `TERMINATED` state, and the item termination reason is `USER_ERROR`|

### RunOutput






```json
"NONE"

```

RunOutput

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RunOutput|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|RunOutput|NONE|
|RunOutput|PARTIAL|
|RunOutput|FULL|

### RunReadResponse






```json
{
  "application_id": "he-tme",
  "custom_metadata": {
    "department": "D1",
    "study": "abc-1"
  },
  "custom_metadata_checksum": "f54fe109",
  "error_code": "SCHEDULER.ITEMS_WITH_ERROR_THRESHOLD_REACHED",
  "error_message": "Run canceled given errors on more than 10 items.",
  "output": "NONE",
  "run_id": "dded282c-8ebd-44cf-8ba5-9a234973d1ec",
  "state": "PENDING",
  "statistics": {
    "item_count": 0,
    "item_pending_count": 0,
    "item_processing_count": 0,
    "item_skipped_count": 0,
    "item_succeeded_count": 0,
    "item_system_error_count": 0,
    "item_user_error_count": 0
  },
  "submitted_at": "2019-08-24T14:15:22Z",
  "submitted_by": "auth0|123456",
  "terminated_at": "2024-01-15T10:30:45.123Z",
  "termination_reason": "ALL_ITEMS_PROCESSED",
  "version_number": "0.4.4"
}

```

RunReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|application_id|string|true|none|Application id|
|custom_metadata|any|false|none|Optional JSON metadata that was stored in alongside the run by the user|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
=======
>>>>>>> b112cc6 (chore: Rebase)
|custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field. Can be used ine the `PUT /runs/{run-id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|
=======
|custom_metadata_checksum|any|false|none|The checksum of the `custom_metadata` field. Can be used in the `PUT /runs/{run-id}/custom_metadata`request to avoid unwanted override of the values in concurrent requests.|
>>>>>>> b165166 (chore: rebase)

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
|error_code|any|true|none|When the termination_reason is set to CANCELED_BY_SYSTEM, the error_code is set to define the        structured description of the error.|

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
|error_message|any|true|none|When the termination_reason is set to CANCELED_BY_SYSTEM, the error_message is set to provide        more insights to the error cause.|

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
|output|[RunOutput](#schemarunoutput)|true|none|The status of the output of the run. When 0 items are successfully processed the output is`NONE`, after one item is successfully processed, the value is set to `PARTIAL`. When all items of the run aresuccessfully processed, the output is set to `FULL`.|
|run_id|string(uuid)|true|none|UUID of the application|
|state|[RunState](#schemarunstate)|true|none|When the run request is received by the Platform, the `state` of it is set to`PENDING`. The state changes to `PROCESSING` when at least one item is being processed. After `PROCESSING`, thestate of the run can switch back to `PENDING` if there are no processing items, or to `TERMINATED` when the runfinished processing.|
|statistics|[RunItemStatistics](#schemarunitemstatistics)|true|none|Aggregated statistics of the run execution|
|submitted_at|string(date-time)|true|none|Timestamp showing when the run was triggered|
|submitted_by|string|true|none|Id of the user who triggered the run|
|terminated_at|any|false|none|Timestamp showing when the run reached a terminal state.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(date-time)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|termination_reason|any|true|none|The termination reason of the run. When the run is not in `TERMINATED` state, the        termination_reason is `null`. If all items of of the run are processed (successfully or with an error), then        termination_reason is set to `ALL_ITEMS_PROCESSED`. If the run is cancelled by the user, the value is set to        `CANCELED_BY_USER`. If the run reaches the threshold of number of failed items, the Platform cancels the run        and sets the termination_reason to `CANCELED_BY_SYSTEM`.|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[RunTerminationReason](#schemarunterminationreason)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|version_number|string|true|none|Application version number|

### RunState






```json
"PENDING"

```

RunState

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RunState|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|RunState|PENDING|
|RunState|PROCESSING|
|RunState|TERMINATED|

### RunTerminationReason






```json
"ALL_ITEMS_PROCESSED"

```

RunTerminationReason

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RunTerminationReason|string|false|none|none|

##### Enumerated Values

|Property|Value|
|---|---|
|RunTerminationReason|ALL_ITEMS_PROCESSED|
|RunTerminationReason|CANCELED_BY_SYSTEM|
|RunTerminationReason|CANCELED_BY_USER|

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

### VersionReadResponse






```json
{
  "changelog": "string",
<<<<<<< HEAD
<<<<<<< HEAD
=======
  "created_at": "2019-08-24T14:15:22Z",
>>>>>>> 99401ec (Refactor tests)
  "flow_id": "0746f03b-16cc-49fb-9833-df3713d407d2",
=======
>>>>>>> b165166 (chore: rebase)
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
<<<<<<< HEAD
<<<<<<< HEAD
  "released_at": "2019-08-24T14:15:22Z",
  "version_number": "string"
=======
  "version": "string"
>>>>>>> 99401ec (Refactor tests)
=======
  "released_at": "2019-08-24T14:15:22Z",
  "version_number": "string"
>>>>>>> b165166 (chore: rebase)
}

```

VersionReadResponse

#### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|changelog|string|true|none|Description of the changes relative to the previous version|
<<<<<<< HEAD
<<<<<<< HEAD
=======
|created_at|string(date-time)|true|none|The timestamp when the application version was registered|
>>>>>>> 99401ec (Refactor tests)
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
|input_artifacts|[[InputArtifact](#schemainputartifact)]|true|none|List of the input fields, provided by the User|
|output_artifacts|[[OutputArtifact](#schemaoutputartifact)]|true|none|List of the output fields, generated by the application|
<<<<<<< HEAD
|released_at|string(date-time)|true|none|The timestamp when the application version was registered|
|version_number|string|true|none|Semantic version of the application|
=======
|version|string|true|none|Semantic version of the application|
>>>>>>> 99401ec (Refactor tests)
=======
|input_artifacts|[[InputArtifact](#schemainputartifact)]|true|none|List of the input fields, provided by the User|
|output_artifacts|[[OutputArtifact](#schemaoutputartifact)]|true|none|List of the output fields, generated by the application|
|released_at|string(date-time)|true|none|The timestamp when the application version was registered|
|version_number|string|true|none|Semantic version of the application|
>>>>>>> b165166 (chore: rebase)
