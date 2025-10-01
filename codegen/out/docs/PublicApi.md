# aignx.codegen.PublicApi

All URIs are relative to */api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**application_version_details_v1_versions_application_version_id_get**](PublicApi.md#application_version_details_v1_versions_application_version_id_get) | **GET** /v1/versions/{application_version_id} | Application Version Details
[**cancel_application_run_v1_runs_application_run_id_cancel_post**](PublicApi.md#cancel_application_run_v1_runs_application_run_id_cancel_post) | **POST** /v1/runs/{application_run_id}/cancel | Cancel Application Run
[**create_application_run_v1_runs_post**](PublicApi.md#create_application_run_v1_runs_post) | **POST** /v1/runs | Initiate Application Run
[**delete_application_run_results_v1_runs_application_run_id_results_delete**](PublicApi.md#delete_application_run_results_v1_runs_application_run_id_results_delete) | **DELETE** /v1/runs/{application_run_id}/results | Delete Application Run Results
[**get_item_v1_items_item_id_get**](PublicApi.md#get_item_v1_items_item_id_get) | **GET** /v1/items/{item_id} | Get Item
[**get_me_v1_me_get**](PublicApi.md#get_me_v1_me_get) | **GET** /v1/me | Get current user
[**get_run_v1_runs_application_run_id_get**](PublicApi.md#get_run_v1_runs_application_run_id_get) | **GET** /v1/runs/{application_run_id} | Get run details
[**list_application_runs_v1_runs_get**](PublicApi.md#list_application_runs_v1_runs_get) | **GET** /v1/runs | List Application Runs
[**list_applications_v1_applications_get**](PublicApi.md#list_applications_v1_applications_get) | **GET** /v1/applications | List available applications
[**list_run_results_v1_runs_application_run_id_results_get**](PublicApi.md#list_run_results_v1_runs_application_run_id_results_get) | **GET** /v1/runs/{application_run_id}/results | List Run Results
[**list_versions_by_application_id_v1_applications_application_id_versions_get**](PublicApi.md#list_versions_by_application_id_v1_applications_application_id_versions_get) | **GET** /v1/applications/{application_id}/versions | List Available Application Versions
[**read_application_by_id_v1_applications_application_id_get**](PublicApi.md#read_application_by_id_v1_applications_application_id_get) | **GET** /v1/applications/{application_id} | Read Application By Id


# **application_version_details_v1_versions_application_version_id_get**
> VersionReadResponse application_version_details_v1_versions_application_version_id_get(application_version_id)

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
    application_version_id = 'application_version_id_example' # str | 

    try:
        # Application Version Details
        api_response = api_instance.application_version_details_v1_versions_application_version_id_get(application_version_id)
        print("The response of PublicApi->application_version_details_v1_versions_application_version_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->application_version_details_v1_versions_application_version_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_version_id** | **str**|  | 

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
**404** | Not Found - Application version with given ID does not exist |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_application_run_v1_runs_application_run_id_cancel_post**
> cancel_application_run_v1_runs_application_run_id_cancel_post(application_run_id)

Cancel Application Run

The application run can be canceled by the user who created the application run.  The execution can be canceled any time while the application is not in a final state. The pending items will not be processed and will not add to the cost.  When the application is canceled, the already completed items stay available for download.

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
    application_run_id = 'application_run_id_example' # str | Application run id, returned by `POST /runs/` endpoint

    try:
        # Cancel Application Run
        api_instance.cancel_application_run_v1_runs_application_run_id_cancel_post(application_run_id)
    except Exception as e:
        print("Exception when calling PublicApi->cancel_application_run_v1_runs_application_run_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 

### Return type

void (empty response body)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Run cancelled successfully |  -  |
**404** | Run not found |  -  |
**403** | Forbidden - You don&#39;t have permission to cancel this run |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_application_run_v1_runs_post**
> RunCreationResponse create_application_run_v1_runs_post(run_creation_request)

Initiate Application Run

This endpoint initiates a processing run for a selected application version and returns an `application_run_id` for tracking purposes.  Slide processing occurs asynchronously, allowing you to retrieve results for individual slides as soon as they complete processing. The system typically processes slides in batches of four, though this number may be reduced during periods of high demand. Below is an example of the required payload for initiating an Atlas H&E TME processing run.   ### Payload  The payload includes `application_version_id` and `items` base fields.  `application_version_id` is the id used for `/v1/versions/{application_id}` endpoint.  `items` includes the list of the items to process (slides, in case of HETA application). Every item has a set of standard fields defined by the API, plus the metadata, specific to the chosen application.  Example payload structure with the comments: ``` {     application_version_id: \"he-tme:v1.0.0-beta\",     items: [{         \"reference\": \"slide_1\",         \"input_artifacts\": [{             \"name\": \"user_slide\",             \"download_url\": \"https://...\",             \"metadata\": {                 \"specimen\": {                   \"disease\": \"LUNG_CANCER\",                   \"tissue\": \"LUNG\"                 },                 \"staining_method\": \"H&E\",                 \"width_px\": 136223,                 \"height_px\": 87761,                 \"resolution_mpp\": 0.2628238,                 \"media-type\":\"image/tiff\",                 \"checksum_base64_crc32c\": \"64RKKA==\"             }         }]     }] } ```  | Parameter  | Description | | :---- | :---- | | `application_version_id` required | Unique ID for the application (must include version) | | `items` required | List of submitted items (WSIs) with parameters described below. | | `reference` required | Unique WSI name or ID for easy reference to results, provided by the caller. The reference should be unique across all items of the application run.  | | `input_artifacts` required | List of provided artifacts for a WSI; at the moment Atlas H&E-TME receives only 1 artifact per slide (the slide itself), but for some other applications this can be a slide and an segmentation map  | | `name` required | Type of artifact; Atlas H&E-TME supports only `\"input_slide\"` | | `download_url` required | Signed URL to the input file in the S3 or GCS; Should be valid for at least 6 days | | `specimen: disease` required | Supported cancer types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) | | `specimen: tissue` required | Supported tissue types for Atlas H&E-TME (see full list in Atlas H&E-TME manual) | | `staining_method` required | WSI stain /bio-marker; Atlas H&E-TME supports only `\"H&E\"` | | `width_px` required | Integer value. Number of pixels of the WSI in the X dimension. | | `height_px` required | Integer value. Number of pixels of the WSI in the Y dimension. | | `resolution_mpp` required | Resolution of WSI in micrometers per pixel; check allowed range in Atlas H&E-TME manual | | `media-type` required | Supported media formats; available values are: image/tiff  (for .tiff or .tif WSI) application/dicom (for DICOM ) application/zip (for zipped DICOM) application/octet-stream  (for .svs WSI) | | `checksum_base64_crc32c` required | Base64 encoded big-endian CRC32C checksum of the WSI image |    ### Response  The endpoint returns the application run UUID. After that the job is scheduled for the execution in the background.  To check the status of the run call `v1/runs/{application_run_id}`.  ### Rejection  Apart from the authentication, authorization and malformed input error, the request can be rejected when the quota limit is exceeded. More details on quotas is described in the documentation

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
        # Initiate Application Run
        api_response = api_instance.create_application_run_v1_runs_post(run_creation_request)
        print("The response of PublicApi->create_application_run_v1_runs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->create_application_run_v1_runs_post: %s\n" % e)
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

# **delete_application_run_results_v1_runs_application_run_id_results_delete**
> delete_application_run_results_v1_runs_application_run_id_results_delete(application_run_id)

Delete Application Run Results

This endpoint allows the caller to explicitly delete outputs generated by an application. It can only be invoked when the application run has reached a final state (COMPLETED, COMPLETED_WITH_ERROR, CANCELED_USER, or CANCELED_SYSTEM). Note that by default, all outputs are automatically deleted 30 days after the application run finishes,  regardless of whether the caller explicitly requests deletion.

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
    application_run_id = 'application_run_id_example' # str | Application run id, returned by `POST /runs/` endpoint

    try:
        # Delete Application Run Results
        api_instance.delete_application_run_results_v1_runs_application_run_id_results_delete(application_run_id)
    except Exception as e:
        print("Exception when calling PublicApi->delete_application_run_results_v1_runs_application_run_id_results_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 

### Return type

void (empty response body)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | All application outputs successfully deleted |  -  |
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_item_v1_items_item_id_get**
> ItemReadResponse get_item_v1_items_item_id_get(item_id)

Get Item

Retrieve details of a specific item (slide) by its ID.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.item_read_response import ItemReadResponse
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
    item_id = 'item_id_example' # str | 

    try:
        # Get Item
        api_response = api_instance.get_item_v1_items_item_id_get(item_id)
        print("The response of PublicApi->get_item_v1_items_item_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_item_v1_items_item_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item_id** | **str**|  | 

### Return type

[**ItemReadResponse**](ItemReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**403** | Forbidden - You don&#39;t have permission to see this item |  -  |
**404** | Not Found - Item with given ID does not exist |  -  |
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

# **get_run_v1_runs_application_run_id_get**
> RunReadResponse get_run_v1_runs_application_run_id_get(application_run_id)

Get run details

This endpoint allows the caller to retrieve the current status of an application run along with other relevant run details.  A run becomes available immediately after it is created through the POST `/runs/` endpoint.   To download the output results, use GET `/runs/{application_run_id}/` results to get outputs for all slides. Access to a run is restricted to the user who created it.

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
    application_run_id = 'application_run_id_example' # str | Application run id, returned by `POST /runs/` endpoint

    try:
        # Get run details
        api_response = api_instance.get_run_v1_runs_application_run_id_get(application_run_id)
        print("The response of PublicApi->get_run_v1_runs_application_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_run_v1_runs_application_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 

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
**404** | Application run not found because it was deleted. |  -  |
**403** | Forbidden - You don&#39;t have permission to see this run |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_application_runs_v1_runs_get**
> List[RunReadResponse] list_application_runs_v1_runs_get(application_id=application_id, application_version=application_version, metadata=metadata, page=page, page_size=page_size, sort=sort)

List Application Runs

List application runs with filtering, sorting, and pagination capabilities.  Returns paginated application runs that were triggered by the user.

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
    application_version = 'application_version_example' # str | Optional application version filter (optional)
    metadata = '$.project' # str | Use PostgreSQL JSONPath expressions to filter runs by their metadata. #### URL Encoding Required **Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.  #### Examples (Clear Format): - **Field existence**: `$.project` - Runs that have a project field defined - **Exact value match**: `$.project ? (@ == \"cancer-research\")` - Runs with specific project value - **Numeric comparison**: `$.duration_hours ? (@ < 2)` - Runs with duration less than 2 hours - **Array operations**: `$.tags[*] ? (@ == \"production\")` - Runs tagged with \"production\" - **Complex conditions**: `$.resources ? (@.gpu_count > 2 && @.memory_gb >= 16)` - Runs with high resource requirements  #### Examples (URL-Encoded Format): - **Field existence**: `%24.project` - **Exact value match**: `%24.project%20%3F%20(%40%20%3D%3D%20%22cancer-research%22)` - **Numeric comparison**: `%24.duration_hours%20%3F%20(%40%20%3C%202)` - **Array operations**: `%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22production%22)` - **Complex conditions**: `%24.resources%20%3F%20(%40.gpu_count%20%3E%202%20%26%26%20%40.memory_gb%20%3E%3D%2016)`  #### Notes - JSONPath expressions are evaluated using PostgreSQL's `@?` operator - The `$.` prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use `&&` for AND operations and `||` for OR operations - Regular expressions use `like_regex` with standard regex syntax - **Remember to URL-encode the entire JSONPath expression when making HTTP requests**               (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.  **Available fields:** - `application_run_id` - `application_version_id` - `organization_id` - `status` - `triggered_at` - `triggered_by`  **Examples:** - `?sort=triggered_at` - Sort by creation time (ascending) - `?sort=-triggered_at` - Sort by creation time (descending) - `?sort=status&sort=-triggered_at` - Sort by status, then by time (descending)  (optional)

    try:
        # List Application Runs
        api_response = api_instance.list_application_runs_v1_runs_get(application_id=application_id, application_version=application_version, metadata=metadata, page=page, page_size=page_size, sort=sort)
        print("The response of PublicApi->list_application_runs_v1_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_application_runs_v1_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**| Optional application ID filter | [optional] 
 **application_version** | **str**| Optional application version filter | [optional] 
 **metadata** | **str**| Use PostgreSQL JSONPath expressions to filter runs by their metadata. #### URL Encoding Required **Important**: JSONPath expressions contain special characters that must be URL-encoded when used in query parameters. Most HTTP clients handle this automatically, but when constructing URLs manually, ensure proper encoding.  #### Examples (Clear Format): - **Field existence**: &#x60;$.project&#x60; - Runs that have a project field defined - **Exact value match**: &#x60;$.project ? (@ &#x3D;&#x3D; \&quot;cancer-research\&quot;)&#x60; - Runs with specific project value - **Numeric comparison**: &#x60;$.duration_hours ? (@ &lt; 2)&#x60; - Runs with duration less than 2 hours - **Array operations**: &#x60;$.tags[*] ? (@ &#x3D;&#x3D; \&quot;production\&quot;)&#x60; - Runs tagged with \&quot;production\&quot; - **Complex conditions**: &#x60;$.resources ? (@.gpu_count &gt; 2 &amp;&amp; @.memory_gb &gt;&#x3D; 16)&#x60; - Runs with high resource requirements  #### Examples (URL-Encoded Format): - **Field existence**: &#x60;%24.project&#x60; - **Exact value match**: &#x60;%24.project%20%3F%20(%40%20%3D%3D%20%22cancer-research%22)&#x60; - **Numeric comparison**: &#x60;%24.duration_hours%20%3F%20(%40%20%3C%202)&#x60; - **Array operations**: &#x60;%24.tags%5B*%5D%20%3F%20(%40%20%3D%3D%20%22production%22)&#x60; - **Complex conditions**: &#x60;%24.resources%20%3F%20(%40.gpu_count%20%3E%202%20%26%26%20%40.memory_gb%20%3E%3D%2016)&#x60;  #### Notes - JSONPath expressions are evaluated using PostgreSQL&#39;s &#x60;@?&#x60; operator - The &#x60;$.&#x60; prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use &#x60;&amp;&amp;&#x60; for AND operations and &#x60;||&#x60; for OR operations - Regular expressions use &#x60;like_regex&#x60; with standard regex syntax - **Remember to URL-encode the entire JSONPath expression when making HTTP requests**               | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)| Sort the results by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.  **Available fields:** - &#x60;application_run_id&#x60; - &#x60;application_version_id&#x60; - &#x60;organization_id&#x60; - &#x60;status&#x60; - &#x60;triggered_at&#x60; - &#x60;triggered_by&#x60;  **Examples:** - &#x60;?sort&#x3D;triggered_at&#x60; - Sort by creation time (ascending) - &#x60;?sort&#x3D;-triggered_at&#x60; - Sort by creation time (descending) - &#x60;?sort&#x3D;status&amp;sort&#x3D;-triggered_at&#x60; - Sort by status, then by time (descending)  | [optional] 

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
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_applications_v1_applications_get**
> List[ApplicationReadResponse] list_applications_v1_applications_get(page=page, page_size=page_size, sort=sort)

List available applications

Returns the list of the applications, available to the caller.  The application is available if any of the versions of the application is assigned to the caller’s organization. The response is paginated and sorted according to the provided parameters.

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

[**List[ApplicationReadResponse]**](ApplicationReadResponse.md)

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

# **list_run_results_v1_runs_application_run_id_results_get**
> List[ItemResultReadResponse] list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, reference__in=reference__in, status__in=status__in, metadata=metadata, page=page, page_size=page_size, sort=sort)

List Run Results

List results for items in an application run with filtering, sorting, and pagination capabilities.  Returns paginated results for items within a specific application run. Results can be filtered by item IDs, references, status, and custom metadata using JSONPath expressions.  ## JSONPath Metadata Filtering Use PostgreSQL JSONPath expressions to filter results by their metadata.  ### Examples: - **Field existence**: `$.case_id` - Results that have a case_id field defined - **Exact value match**: `$.priority ? (@ == \"high\")` - Results with high priority - **Numeric comparison**: `$.confidence_score ? (@ > 0.95)` - Results with high confidence - **Array operations**: `$.flags[*] ? (@ == \"reviewed\")` - Results flagged as reviewed - **Complex conditions**: `$.metrics ? (@.accuracy > 0.9 && @.recall > 0.8)` - Results meeting performance thresholds  ## Notes - JSONPath expressions are evaluated using PostgreSQL's `@?` operator - The `$.` prefix is automatically added to root-level field references if missing - String values in conditions must be enclosed in double quotes - Use `&&` for AND operations and `||` for OR operations

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.item_result_read_response import ItemResultReadResponse
from aignx.codegen.models.item_status import ItemStatus
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
    application_run_id = 'application_run_id_example' # str | Application run id, returned by `POST /runs/` endpoint
    item_id__in = ['item_id__in_example'] # List[str] | Filter for items ids (optional)
    reference__in = ['reference__in_example'] # List[str] | Filter for items by their reference from the input payload (optional)
    status__in = [aignx.codegen.ItemStatus()] # List[ItemStatus] | Filter for items in certain statuses (optional)
    metadata = '$.project' # str | JSONPath expression to filter results by their metadata (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.                 **Available fields:** - `item_id` - `application_run_id` - `reference` - `status` - `metadata`  **Examples:** - `?sort=item_id` - Sort by id of the item (ascending) - `?sort=-application_run_id` - Sort by id of the run (descending) - `?sort=status&sort=-item_idt` - Sort by status, then by id of the item (descending) (optional)

    try:
        # List Run Results
        api_response = api_instance.list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, reference__in=reference__in, status__in=status__in, metadata=metadata, page=page, page_size=page_size, sort=sort)
        print("The response of PublicApi->list_run_results_v1_runs_application_run_id_results_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_run_results_v1_runs_application_run_id_results_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **item_id__in** | [**List[str]**](str.md)| Filter for items ids | [optional] 
 **reference__in** | [**List[str]**](str.md)| Filter for items by their reference from the input payload | [optional] 
 **status__in** | [**List[ItemStatus]**](ItemStatus.md)| Filter for items in certain statuses | [optional] 
 **metadata** | **str**| JSONPath expression to filter results by their metadata | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)| Sort the results by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.                 **Available fields:** - &#x60;item_id&#x60; - &#x60;application_run_id&#x60; - &#x60;reference&#x60; - &#x60;status&#x60; - &#x60;metadata&#x60;  **Examples:** - &#x60;?sort&#x3D;item_id&#x60; - Sort by id of the item (ascending) - &#x60;?sort&#x3D;-application_run_id&#x60; - Sort by id of the run (descending) - &#x60;?sort&#x3D;status&amp;sort&#x3D;-item_idt&#x60; - Sort by status, then by id of the item (descending) | [optional] 

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
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_versions_by_application_id_v1_applications_application_id_versions_get**
> List[ApplicationVersionReadResponse] list_versions_by_application_id_v1_applications_application_id_versions_get(application_id, page=page, page_size=page_size, version=version, sort=sort)

List Available Application Versions

Returns a list of available application versions for a specific application.  A version is considered available when it has been assigned to your organization. Within a major version, all minor and patch updates are automatically accessible unless a specific version has been deprecated. Major version upgrades, however, require explicit assignment and may be subject to contract modifications before becoming available to your organization.

### Example

* OAuth Authentication (OAuth2AuthorizationCodeBearer):

```python
import aignx.codegen
from aignx.codegen.models.application_version_read_response import ApplicationVersionReadResponse
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
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    version = 'version_example' # str | Semantic version of the application, example: `1.0.13` (optional)
    sort = ['sort_example'] # List[str] | Sort the results by one or more fields. Use `+` for ascending and `-` for descending order.  **Available fields:** - `application_version_id` - `version` - `application_id` - `changelog` - `created_at`  **Examples:** - `?sort=application_id` - Sort by application_id ascending - `?sort=-version` - Sort by version descending - `?sort=+application_id&sort=-created_at` - Sort by application_id ascending, then created_at descending (optional)

    try:
        # List Available Application Versions
        api_response = api_instance.list_versions_by_application_id_v1_applications_application_id_versions_get(application_id, page=page, page_size=page_size, version=version, sort=sort)
        print("The response of PublicApi->list_versions_by_application_id_v1_applications_application_id_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->list_versions_by_application_id_v1_applications_application_id_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **version** | **str**| Semantic version of the application, example: &#x60;1.0.13&#x60; | [optional] 
 **sort** | [**List[str]**](str.md)| Sort the results by one or more fields. Use &#x60;+&#x60; for ascending and &#x60;-&#x60; for descending order.  **Available fields:** - &#x60;application_version_id&#x60; - &#x60;version&#x60; - &#x60;application_id&#x60; - &#x60;changelog&#x60; - &#x60;created_at&#x60;  **Examples:** - &#x60;?sort&#x3D;application_id&#x60; - Sort by application_id ascending - &#x60;?sort&#x3D;-version&#x60; - Sort by version descending - &#x60;?sort&#x3D;+application_id&amp;sort&#x3D;-created_at&#x60; - Sort by application_id ascending, then created_at descending | [optional] 

### Return type

[**List[ApplicationVersionReadResponse]**](ApplicationVersionReadResponse.md)

### Authorization

[OAuth2AuthorizationCodeBearer](../README.md#OAuth2AuthorizationCodeBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of application versions for a given application ID available to the caller |  -  |
**401** | Unauthorized - Invalid or missing authentication |  -  |
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

