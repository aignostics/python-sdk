# aignx.codegen.PublicApi

All URIs are relative to */api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**application_version_details_v1_applications_application_id_versions_version_get**](PublicApi.md#application_version_details_v1_applications_application_id_versions_version_get) | **GET** /v1/applications/{application_id}/versions/{version} | Application Version Details
[**cancel_run_v1_runs_run_id_cancel_post**](PublicApi.md#cancel_run_v1_runs_run_id_cancel_post) | **POST** /v1/runs/{run_id}/cancel | Cancel Run
[**create_run_v1_runs_post**](PublicApi.md#create_run_v1_runs_post) | **POST** /v1/runs | Initiate Run
[**delete_run_items_v1_runs_run_id_artifacts_delete**](PublicApi.md#delete_run_items_v1_runs_run_id_artifacts_delete) | **DELETE** /v1/runs/{run_id}/artifacts | Delete Run Items
[**get_item_by_run_v1_runs_run_id_items_external_id_get**](PublicApi.md#get_item_by_run_v1_runs_run_id_items_external_id_get) | **GET** /v1/runs/{run_id}/items/{external_id} | Get Item By Run
[**get_me_v1_me_get**](PublicApi.md#get_me_v1_me_get) | **GET** /v1/me | Get current user
[**get_run_v1_runs_run_id_get**](PublicApi.md#get_run_v1_runs_run_id_get) | **GET** /v1/runs/{run_id} | Get run details
[**list_applications_v1_applications_get**](PublicApi.md#list_applications_v1_applications_get) | **GET** /v1/applications | List available applications
[**list_run_items_v1_runs_run_id_items_get**](PublicApi.md#list_run_items_v1_runs_run_id_items_get) | **GET** /v1/runs/{run_id}/items | List Run Items
[**list_runs_v1_runs_get**](PublicApi.md#list_runs_v1_runs_get) | **GET** /v1/runs | List Runs
[**put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put**](PublicApi.md#put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put) | **PUT** /v1/runs/{run_id}/items/{external_id}/custom-metadata | Put Item Custom Metadata By Run
[**put_run_custom_metadata_v1_runs_run_id_custom_metadata_put**](PublicApi.md#put_run_custom_metadata_v1_runs_run_id_custom_metadata_put) | **PUT** /v1/runs/{run_id}/custom-metadata | Put Run Custom Metadata
[**read_application_by_id_v1_applications_application_id_get**](PublicApi.md#read_application_by_id_v1_applications_application_id_get) | **GET** /v1/applications/{application_id} | Read Application By Id


# **application_version_details_v1_applications_application_id_versions_version_get**
> VersionReadResponse application_version_details_v1_applications_application_id_versions_version_get(application_id, version)

Application Version Details

Get the application version details  Allows caller to  retrieve information about application version based on provided application version ID.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.version_read_response import VersionReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    application_id = 'application_id_example' # str | 
    version = 'version_example' # str | 

    try:
        # Application Version Details
        api_response = api_instance.application_version_details_v1_applications_application_id_versions_version_get(application_id, version)
        print("The response of PublicApi->application_version_details_v1_applications_application_id_versions_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->application_version_details_v1_applications_application_id_versions_version_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | 
 **version** | **str**|  | 

### Return type

[**VersionReadResponse**](VersionReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**403** | Forbidden - You don&#39;t have permission to see this version |  -  |
**404** | Not Found - Application version with given ID is not available to you or does not exist |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_run_v1_runs_run_id_cancel_post**
> object cancel_run_v1_runs_run_id_cancel_post(run_id)

Cancel Run

The run can be canceled by the user who created the run.  The execution can be canceled any time while the application is not in a final state. The pending items will not be processed and will not add to the cost.  When the application is canceled, the already completed items stay available for download.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | Run id, returned by `POST /runs/` endpoint

    try:
        # Cancel Run
        api_response = api_instance.cancel_run_v1_runs_run_id_cancel_post(run_id)
        print("The response of PublicApi->cancel_run_v1_runs_run_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->cancel_run_v1_runs_run_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| Run id, returned by &#x60;POST /runs/&#x60; endpoint | 

### Return type

**object**

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**404** | Run not found |  -  |
**403** | Forbidden - You don&#39;t have permission to cancel this run |  -  |
**409** | Conflict - The Run is already cancelled |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_run_v1_runs_post**
> RunCreationResponse create_run_v1_runs_post(run_creation_request)

Initiate Run

This endpoint initiates a processing run for a selected application and version, and returns a `run_id` for tracking purposes.  Slide processing occurs asynchronously, allowing you to retrieve results for individual slides as soon as they complete processing. The system typically processes slides in batches of four, though this number may be reduced during periods of high demand. Below is an example of the required payload for initiating an Atlas H&E TME processing run.   ### Payload  The payload includes `application_id`, optional `version_number`, and `items` base fields.  `application_id` is the unique identifier for the application. `version_number` is the semantic version to use. If not provided, the latest available version will be used.  `items` includes the list of the items to process (slides, in case of HETA application). Every item has a set of standard fields defined by the API, plus the custom_metadata, specific to the chosen application.  Example payload structure with the comments: ``` {     application_id: \"he-tme\",     version_number: \"1.0.0-beta\",     items: [{         \"external_id\": \"slide_1\",         \"input_artifacts\": [{             \"name\": \"user_slide\",             \"download_url\": \"https://...\",             \"custom_metadata\": {                 \"specimen\": {                   \"disease\": \"LUNG_CANCER\",                   \"tissue\": \"LUNG\"                 },                 \"staining_method\": \"H&E\",                 \"width_px\": 136223,                 \"height_px\": 87761,                 \"resolution_mpp\": 0.2628238,                 \"media-type\":\"image/tiff\",                 \"checksum_base64_crc32c\": \"64RKKA==\"             }         }]     }] } ```  | Parameter  | Description | | :---- | :---- | | `application_id` required | Unique ID for the application | | `version_number` optional | Semantic version of the application. If not provided, the latest available version will be used | | `items` required | List of submitted items (WSIs) with parameters described below. | | `external_id` required | Unique WSI name or ID for easy reference to items, provided by the caller. The external_id should be unique across all items of the run.  | | `input_artifacts` required | List of provided artifacts for a WSI; at the moment Atlas H&E-TME receives only 1 artifact per slide (the slide itself), but for some other applications this can be a slide and an segmentation map  | | `name` required | Type of artifact; Atlas H&E-TME supports only `\"input_slide\"` | | `download_url` required | Signed URL to the input file in the S3 or GCS; Should be valid for at least 6 days | | `specimen: disease` required | Supported cancer types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) | | `specimen: tissue` required | Supported tissue types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) | | `staining_method` required | WSI stain /bio-marker; Atlas H&E-TME supports only `\"H&E\"` | | `width_px` required | Integer value. Number of pixels of the WSI in the X dimension. | | `height_px` required | Integer value. Number of pixels of the WSI in the Y dimension. | | `resolution_mpp` required | Resolution of WSI in micrometers per pixel; check allowed range in Atlas H&E-TME manual | | `media-type` required | Supported media formats; available values are: image/tiff  (for .tiff or .tif WSI) application/dicom (for DICOM ) application/zip (for zipped DICOM) application/octet-stream  (for .svs WSI) | | `checksum_base64_crc32c` required | Base64 encoded big-endian CRC32C checksum of the WSI image |    ### Response  The endpoint returns the run UUID. After that the job is scheduled for the execution in the background.  To check the status of the run call `v1/runs/{run_id}`.  ### Rejection  Apart from the authentication, authorization and malformed input error, the request can be rejected when the quota limit is exceeded. More details on quotas is described in the documentation

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.run_creation_request import RunCreationRequest
from aignx.codegen.models.run_creation_response import RunCreationResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_creation_request = aignx.codegen.RunCreationRequest() # RunCreationRequest | 

    try:
        # Initiate Run
        api_response = api_instance.create_run_v1_runs_post(run_creation_request)
        print("The response of PublicApi->create_run_v1_runs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->create_run_v1_runs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_creation_request** | [**RunCreationRequest**](RunCreationRequest.md)|  | 

### Return type

[**RunCreationResponse**](RunCreationResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**404** | Application version not found |  -  |
**403** | Forbidden - You don&#39;t have permission to create this run |  -  |
**400** | Bad Request - Input validation failed |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_run_items_v1_runs_run_id_artifacts_delete**
> object delete_run_items_v1_runs_run_id_artifacts_delete(run_id)

Delete Run Items

This endpoint allows the caller to explicitly delete artifacts generated by a run. It can only be invoked when the run has reached a final state (PROCESSED, CANCELED_SYSTEM, CANCELED_USER). Note that by default, all artifacts are automatically deleted 30 days after the run finishes,  regardless of whether the caller explicitly requests deletion.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | Run id, returned by `POST /runs/` endpoint

    try:
        # Delete Run Items
        api_response = api_instance.delete_run_items_v1_runs_run_id_artifacts_delete(run_id)
        print("The response of PublicApi->delete_run_items_v1_runs_run_id_artifacts_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->delete_run_items_v1_runs_run_id_artifacts_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| Run id, returned by &#x60;POST /runs/&#x60; endpoint | 

### Return type

**object**

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Run artifacts deleted |  -  |
**404** | Run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_item_by_run_v1_runs_run_id_items_external_id_get**
> ItemResultReadResponse get_item_by_run_v1_runs_run_id_items_external_id_get(run_id, external_id)

Get Item By Run

Retrieve details of a specific item (slide) by its external ID and the run ID.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.item_result_read_response import ItemResultReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | The run id, returned by `POST /runs/` endpoint
    external_id = 'external_id_example' # str | The `external_id` that was defined for the item by the customer that triggered the run.

    try:
        # Get Item By Run
        api_response = api_instance.get_item_by_run_v1_runs_run_id_items_external_id_get(run_id, external_id)
        print("The response of PublicApi->get_item_by_run_v1_runs_run_id_items_external_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_item_by_run_v1_runs_run_id_items_external_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| The run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **external_id** | **str**| The &#x60;external_id&#x60; that was defined for the item by the customer that triggered the run. | 

### Return type

[**ItemResultReadResponse**](ItemResultReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found - Item with given ID does not exist |  -  |
**403** | Forbidden - You don&#39;t have permission to see this item |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_me_v1_me_get**
> MeReadResponse get_me_v1_me_get()

Get current user

Retrieves your identity details, including name, email, and organization. This is useful for verifying that the request is being made under the correct user profile and organization context, as well as confirming that the expected environment variables are correctly set (in case you are using Python SDK)

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.me_read_response import MeReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)

    try:
        # Get current user
        api_response = api_instance.get_me_v1_me_get()
        print("The response of PublicApi->get_me_v1_me_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_me_v1_me_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**MeReadResponse**](MeReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_run_v1_runs_run_id_get**
> RunReadResponse get_run_v1_runs_run_id_get(run_id)

Get run details

This endpoint allows the caller to retrieve the current status of a run along with other relevant run details.  A run becomes available immediately after it is created through the POST `/runs/` endpoint.   To download the output results, use GET `/runs/{run_id}/` items to get outputs for all slides. Access to a run is restricted to the user who created it.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.run_read_response import RunReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | Run id, returned by `POST /runs/` endpoint

    try:
        # Get run details
        api_response = api_instance.get_run_v1_runs_run_id_get(run_id)
        print("The response of PublicApi->get_run_v1_runs_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_run_v1_runs_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| Run id, returned by &#x60;POST /runs/&#x60; endpoint | 

### Return type

[**RunReadResponse**](RunReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Run not found because it was deleted. |  -  |
**403** | Forbidden - You don&#39;t have permission to see this run |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_applications_v1_applications_get**
> List[ApplicationReadShortResponse] list_applications_v1_applications_get(page=page, page_size=page_size, sort=sort)

List available applications

Returns the list of the applications, available to the caller.  The application is available if any of the versions of the application is assigned to the caller’s organization. The response is paginated and sorted according to the provided parameters.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.application_read_short_response import ApplicationReadShortResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.  **Available fields:** - `application_id` - `name` - `description` - `regulatory_classes`  **Examples:** - `?sort=application_id` - Sort by application_id ascending - `?sort=-name` - Sort by name descending - `?sort=+description&sort=name` - Sort by description ascending, then name descending (optional)

    try:
        # List available applications
        api_response = api_instance.list_applications_v1_applications_get(page=page, page_size=page_size, sort=sort)
        print("The response of PublicApi->list_applications_v1_applications_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_applications_v1_applications_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)| Sort the results by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.  **Available fields:** - &#x60;application_id&#x60; - &#x60;name&#x60; - &#x60;description&#x60; - &#x60;regulatory_classes&#x60;  **Examples:** - &#x60;?sort&#x3D;application_id&#x60; - Sort by application_id ascending - &#x60;?sort&#x3D;-name&#x60; - Sort by name descending - &#x60;?sort&#x3D;+description&amp;sort&#x3D;name&#x60; - Sort by description ascending, then name descending | [optional] 

### Return type

[**List[ApplicationReadShortResponse]**](ApplicationReadShortResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of applications available to the caller |  -  |
**401** | Unauthorized - Invalid or missing authentication |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_run_items_v1_runs_run_id_items_get**
> List[ItemResultReadResponse] list_run_items_v1_runs_run_id_items_get(run_id, item_id__in=item_id__in, external_id__in=external_id__in, state=state, termination_reason=termination_reason, custom_metadata=custom_metadata, page=page, page_size=page_size, sort=sort)

List Run Items

List items in a run with filtering, sorting, and pagination capabilities.  Returns paginated items within a specific run. Results can be filtered by item IDs, external_ids, status, and custom_metadata using JSONPath expressions.  ## JSONPath Metadata Filtering Use PostgreSQL JSONPath expressions to filter items using their custom_metadata.  ### Examples: - **Field existence**: `$.case_id` - Results that have a case_id field defined - **Exact value match**: `$.priority ? (@ == \"high\")` - Results with high priority - **Numeric comparison**: `$.confidence_score ? (@ > 0.95)` - Results with high confidence - **Array operations**: `$.flags[*] ? (@ == \"reviewed\")` - Results flagged as reviewed - **Complex conditions**: `$.metrics ? (@.accuracy > 0.9 && @.recall > 0.8)` - Results meeting performance thresholds  ## Notes - JSONPath expressions are evaluated using PostgreSQL's `@?` operator - The `$.` prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use `&&` for AND operations and `||` for OR operations

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.item_result_read_response import ItemResultReadResponse
from aignx.codegen.models.item_state import ItemState
from aignx.codegen.models.item_termination_reason import ItemTerminationReason
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | Run id, returned by `POST /runs/` endpoint
    item_id__in = ['item_id__in_example'] # List[str] | Filter for item ids (optional)
    external_id__in = ['external_id__in_example'] # List[str] | Filter for items by their external_id from the input payload (optional)
    state = aignx.codegen.ItemState() # ItemState | Filter items by their state (optional)
    termination_reason = aignx.codegen.ItemTerminationReason() # ItemTerminationReason | Filter items by their termination reason. Only applies to TERMINATED items. (optional)
    custom_metadata = '$' # str | JSONPath expression to filter items by their custom_metadata (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] | Sort the items by one or more fields. Use `+` for ascending and `-` for descending order.                 **Available fields:** - `item_id` - `run_id` - `external_id` - `custom_metadata`  **Examples:** - `?sort=item_id` - Sort by id of the item (ascending) - `?sort=-external_id` - Sort by external ID (descending) - `?sort=custom_metadata&sort=-external_id` - Sort by metadata, then by external ID (descending) (optional)

    try:
        # List Run Items
        api_response = api_instance.list_run_items_v1_runs_run_id_items_get(run_id, item_id__in=item_id__in, external_id__in=external_id__in, state=state, termination_reason=termination_reason, custom_metadata=custom_metadata, page=page, page_size=page_size, sort=sort)
        print("The response of PublicApi->list_run_items_v1_runs_run_id_items_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_run_items_v1_runs_run_id_items_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| Run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **item_id__in** | [**List[str]**](str.md)| Filter for item ids | [optional] 
 **external_id__in** | [**List[str]**](str.md)| Filter for items by their external_id from the input payload | [optional] 
 **state** | [**ItemState**](.md)| Filter items by their state | [optional] 
 **termination_reason** | [**ItemTerminationReason**](.md)| Filter items by their termination reason. Only applies to TERMINATED items. | [optional] 
 **custom_metadata** | **str**| JSONPath expression to filter items by their custom_metadata | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)| Sort the items by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.                 **Available fields:** - &#x60;item_id&#x60; - &#x60;run_id&#x60; - &#x60;external_id&#x60; - &#x60;custom_metadata&#x60;  **Examples:** - &#x60;?sort&#x3D;item_id&#x60; - Sort by id of the item (ascending) - &#x60;?sort&#x3D;-external_id&#x60; - Sort by external ID (descending) - &#x60;?sort&#x3D;custom_metadata&amp;sort&#x3D;-external_id&#x60; - Sort by metadata, then by external ID (descending) | [optional] 

### Return type

[**List[ItemResultReadResponse]**](ItemResultReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_runs_v1_runs_get**
> List[RunReadResponse] list_runs_v1_runs_get(application_id=application_id, application_version=application_version, external_id=external_id, custom_metadata=custom_metadata, page=page, page_size=page_size, sort=sort)

List Runs

List runs with filtering, sorting, and pagination capabilities.  Returns paginated runs that were submitted by the user.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.run_read_response import RunReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    application_id = 'application_id_example' # str | Optional application ID filter (optional)
    application_version = 'application_version_example' # str | Optional Version Name (optional)
    external_id = 'external_id_example' # str | Optionally filter runs by items with this external ID (optional)
    custom_metadata = '$' # str | Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata. #### URL Encoding Required **Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.  #### Examples (Clear Format): - **Field existence**: `$.study` - Runs that have a study field defined - **Exact value match**: `$.study ? (@ == \"high\")` - Runs with specific study value - **Numeric comparison**: `$.confidence_score ? (@ > 0.75)` - Runs with confidence score greater than 0.75 - **Array operations**: `$.tags[*] ? (@ == \"draft\")` - Runs with tags array containing \"draft\" - **Complex conditions**: `$.resources ? (@.gpu_count > 2 && @.memory_gb >= 16)` - Runs with high resource requirements  #### Examples (URL-Encoded Format): - **Field existence**: `%24.study` - **Exact value match**: `%24.study%20%3F%20(%40%20%3D%3D%20%22high%22)` - **Numeric comparison**: `%24.confidence_score%20%3F%20(%40%20%3E%200.75)` - **Array operations**: `%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22draft%22)` - **Complex conditions**: `%24.resources%20%3F%20(%40.gpu_count%20%3E%202%20%26%26%20%40.memory_gb%20%3E%3D%2016)`  #### Notes - JSONPath expressions are evaluated using PostgreSQL's `@?` operator - The `$.` prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use `&&` for AND operations and `||` for OR operations - Regular expressions use `like_regex` with standard regex syntax - **Remember to URL-encode the entire JSONPath expression when making HTTP requests**               (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.  **Available fields:** - `run_id` - `application_version_id` - `organization_id` - `status` - `submitted_at` - `submitted_by`  **Examples:** - `?sort=submitted_at` - Sort by creation time (ascending) - `?sort=-submitted_at` - Sort by creation time (descending) - `?sort=status&sort=-submitted_at` - Sort by status, then by time (descending)  (optional)

    try:
        # List Runs
        api_response = api_instance.list_runs_v1_runs_get(application_id=application_id, application_version=application_version, external_id=external_id, custom_metadata=custom_metadata, page=page, page_size=page_size, sort=sort)
        print("The response of PublicApi->list_runs_v1_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_runs_v1_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**| Optional application ID filter | [optional] 
 **application_version** | **str**| Optional Version Name | [optional] 
 **external_id** | **str**| Optionally filter runs by items with this external ID | [optional] 
 **custom_metadata** | **str**| Use PostgreSQL JSONPath expressions to filter runs by their custom_metadata. #### URL Encoding Required **Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.  #### Examples (Clear Format): - **Field existence**: &#x60;$.study&#x60; - Runs that have a study field defined - **Exact value match**: &#x60;$.study ? (@ &#x3D;&#x3D; \&quot;high\&quot;)&#x60; - Runs with specific study value - **Numeric comparison**: &#x60;$.confidence_score ? (@ &gt; 0.75)&#x60; - Runs with confidence score greater than 0.75 - **Array operations**: &#x60;$.tags[*] ? (@ &#x3D;&#x3D; \&quot;draft\&quot;)&#x60; - Runs with tags array containing \&quot;draft\&quot; - **Complex conditions**: &#x60;$.resources ? (@.gpu_count &gt; 2 &amp;&amp; @.memory_gb &gt;&#x3D; 16)&#x60; - Runs with high resource requirements  #### Examples (URL-Encoded Format): - **Field existence**: &#x60;%24.study&#x60; - **Exact value match**: &#x60;%24.study%20%3F%20(%40%20%3D%3D%20%22high%22)&#x60; - **Numeric comparison**: &#x60;%24.confidence_score%20%3F%20(%40%20%3E%200.75)&#x60; - **Array operations**: &#x60;%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22draft%22)&#x60; - **Complex conditions**: &#x60;%24.resources%20%3F%20(%40.gpu_count%20%3E%202%20%26%26%20%40.memory_gb%20%3E%3D%2016)&#x60;  #### Notes - JSONPath expressions are evaluated using PostgreSQL&#39;s &#x60;@?&#x60; operator - The &#x60;$.&#x60; prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use &#x60;&amp;&amp;&#x60; for AND operations and &#x60;||&#x60; for OR operations - Regular expressions use &#x60;like_regex&#x60; with standard regex syntax - **Remember to URL-encode the entire JSONPath expression when making HTTP requests**               | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)| Sort the results by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.  **Available fields:** - &#x60;run_id&#x60; - &#x60;application_version_id&#x60; - &#x60;organization_id&#x60; - &#x60;status&#x60; - &#x60;submitted_at&#x60; - &#x60;submitted_by&#x60;  **Examples:** - &#x60;?sort&#x3D;submitted_at&#x60; - Sort by creation time (ascending) - &#x60;?sort&#x3D;-submitted_at&#x60; - Sort by creation time (descending) - &#x60;?sort&#x3D;status&amp;sort&#x3D;-submitted_at&#x60; - Sort by status, then by time (descending)  | [optional] 

### Return type

[**List[RunReadResponse]**](RunReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put**
> object put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put(run_id, external_id, custom_metadata_update_request)

Put Item Custom Metadata By Run

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.custom_metadata_update_request import CustomMetadataUpdateRequest
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | The run id, returned by `POST /runs/` endpoint
    external_id = 'external_id_example' # str | The `external_id` that was defined for the item by the customer that triggered the run.
    custom_metadata_update_request = aignx.codegen.CustomMetadataUpdateRequest() # CustomMetadataUpdateRequest | 

    try:
        # Put Item Custom Metadata By Run
        api_response = api_instance.put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put(run_id, external_id, custom_metadata_update_request)
        print("The response of PublicApi->put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| The run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **external_id** | **str**| The &#x60;external_id&#x60; that was defined for the item by the customer that triggered the run. | 
 **custom_metadata_update_request** | [**CustomMetadataUpdateRequest**](CustomMetadataUpdateRequest.md)|  | 

### Return type

**object**

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_run_custom_metadata_v1_runs_run_id_custom_metadata_put**
> object put_run_custom_metadata_v1_runs_run_id_custom_metadata_put(run_id, custom_metadata_update_request)

Put Run Custom Metadata

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.custom_metadata_update_request import CustomMetadataUpdateRequest
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    run_id = 'run_id_example' # str | Run id, returned by `POST /runs/` endpoint
    custom_metadata_update_request = aignx.codegen.CustomMetadataUpdateRequest() # CustomMetadataUpdateRequest | 

    try:
        # Put Run Custom Metadata
        api_response = api_instance.put_run_custom_metadata_v1_runs_run_id_custom_metadata_put(run_id, custom_metadata_update_request)
        print("The response of PublicApi->put_run_custom_metadata_v1_runs_run_id_custom_metadata_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->put_run_custom_metadata_v1_runs_run_id_custom_metadata_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**| Run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **custom_metadata_update_request** | [**CustomMetadataUpdateRequest**](CustomMetadataUpdateRequest.md)|  | 

### Return type

**object**

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_application_by_id_v1_applications_application_id_get**
> ApplicationReadResponse read_application_by_id_v1_applications_application_id_get(application_id)

Read Application By Id

Retrieve details of a specific application by its ID.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.application_read_response import ApplicationReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /api
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.PublicApi(api_client)
    application_id = 'application_id_example' # str | 

    try:
        # Read Application By Id
        api_response = api_instance.read_application_by_id_v1_applications_application_id_get(application_id)
        print("The response of PublicApi->read_application_by_id_v1_applications_application_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->read_application_by_id_v1_applications_application_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | 

### Return type

[**ApplicationReadResponse**](ApplicationReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**403** | Forbidden - You don&#39;t have permission to see this application |  -  |
**404** | Not Found - Application with the given ID does not exist |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

