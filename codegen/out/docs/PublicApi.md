# aignx.codegen.PublicApi

All URIs are relative to */api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_application_run_v1_runs_application_run_id_cancel_post**](PublicApi.md#cancel_application_run_v1_runs_application_run_id_cancel_post) | **POST** /v1/runs/{application_run_id}/cancel | Cancel Application Run
[**create_application_run_v1_runs_post**](PublicApi.md#create_application_run_v1_runs_post) | **POST** /v1/runs | Create Application Run
[**delete_application_run_results_v1_runs_application_run_id_results_delete**](PublicApi.md#delete_application_run_results_v1_runs_application_run_id_results_delete) | **DELETE** /v1/runs/{application_run_id}/results | Delete Application Run Results
[**get_run_v1_runs_application_run_id_get**](PublicApi.md#get_run_v1_runs_application_run_id_get) | **GET** /v1/runs/{application_run_id} | Get Run
[**list_application_runs_v1_runs_get**](PublicApi.md#list_application_runs_v1_runs_get) | **GET** /v1/runs | List Application Runs
[**list_applications_v1_applications_get**](PublicApi.md#list_applications_v1_applications_get) | **GET** /v1/applications | List Applications
[**list_run_results_v1_runs_application_run_id_results_get**](PublicApi.md#list_run_results_v1_runs_application_run_id_results_get) | **GET** /v1/runs/{application_run_id}/results | List Run Results
[**list_versions_by_application_id_v1_applications_application_id_versions_get**](PublicApi.md#list_versions_by_application_id_v1_applications_application_id_versions_get) | **GET** /v1/applications/{application_id}/versions | List Versions By Application Id


# **cancel_application_run_v1_runs_application_run_id_cancel_post**
> object cancel_application_run_v1_runs_application_run_id_cancel_post(application_run_id)

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
        api_response = api_instance.cancel_application_run_v1_runs_application_run_id_cancel_post(application_run_id)
        print("The response of PublicApi->cancel_application_run_v1_runs_application_run_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->cancel_application_run_v1_runs_application_run_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 

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
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_application_run_v1_runs_post**
> RunCreationResponse create_application_run_v1_runs_post(run_creation_request)

Create Application Run

The endpoint is used to process the input items by the chosen application version. The endpoint returns the `application_run_id`. The processing fo the items is done asynchronously.  To check the status or cancel the execution, use the /v1/runs/{application_run_id} endpoint.  ### Payload  The payload includes `application_version_id` and `items` base fields.  `application_version_id` is the id used for `/v1/versions/{application_id}` endpoint.  `items` includes the list of the items to process (slides, in case of HETA application). Every item has a set of standard fields defined by the API, plus the metadata, specific to the chosen application.  Example payload structure with the comments: ``` {     application_version_id: \"heta:v1.0.0\",     items: [{         \"reference\": \"slide_1\"  <-- Input ID to connect the input and the output artifact         \"input_artifacts\": [{             \"name\": \"input_slide\"  <-- Name of the artifact defined by the application (For HETA it is\"input_slide\")             \"download_url\": \"https://...\" <-- signed URL to the input file in the S3 or GCS. Should be valid for more than 6 days             \"metadata\": { <-- The metadata fields defined by the application. (The example fields set for a slide files are provided)                 \"checksum_crc32c\": \"abc12==\",                 \"mime_type\": \"image/tiff\",                 \"height\": 100,                 \"weight\": 500,                 \"mpp\": 0.543             }         }]     }] } ```  ### Response  The endpoint returns the application run UUID. After that the job is scheduled for the execution in the background.  To check the status of the run call `v1/runs/{application_run_id}`.  ### Rejection  Apart from the authentication, authorization and malformed input error, the request can be rejected when the quota limit is exceeded. More details on quotas is described in the documentation

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
        # Create Application Run
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
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_application_run_results_v1_runs_application_run_id_results_delete**
> delete_application_run_results_v1_runs_application_run_id_results_delete(application_run_id)

Delete Application Run Results

Delete the application run results. It can only be called when the application is in a final state (meaning it's not in `received` or `pending` states). To delete the results of the running artifacts, first call `POST /v1/runs/{application_run_id}/cancel` to cancel the application run.  The output results are deleted automatically 30 days after the application run is finished.

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
**204** | Successful Response |  -  |
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_run_v1_runs_application_run_id_get**
> RunReadResponse get_run_v1_runs_application_run_id_get(application_run_id, include=include)

Get Run

Returns the details of the application run. The application run is available as soon as it is created via `POST /runs/` endpoint. To download the items results, call `/runs/{application_run_id}/results`.  The application is only available to the user who triggered it, regardless of the role.

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
    include = None # List[object] |  (optional)

    try:
        # Get Run
        api_response = api_instance.get_run_v1_runs_application_run_id_get(application_run_id, include=include)
        print("The response of PublicApi->get_run_v1_runs_application_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_run_v1_runs_application_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**| Application run id, returned by &#x60;POST /runs/&#x60; endpoint | 
 **include** | [**List[object]**](object.md)|  | [optional] 

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
**404** | Application run not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_application_runs_v1_runs_get**
> List[RunReadResponse] list_application_runs_v1_runs_get(application_id=application_id, application_version=application_version, include=include, page=page, page_size=page_size, sort=sort)

List Application Runs

The endpoint returns the application runs triggered by the caller. After the application run is created by POST /v1/runs, it becomes available for the current endpoint

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
    include = None # List[object] | Request optional output values. Used internally by the platform (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Application Runs
        api_response = api_instance.list_application_runs_v1_runs_get(application_id=application_id, application_version=application_version, include=include, page=page, page_size=page_size, sort=sort)
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
 **include** | [**List[object]**](object.md)| Request optional output values. Used internally by the platform | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)|  | [optional] 

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

List Applications

Returns the list of the applications, available to the caller.  The application is available if any of the version of the application is assigned to the user organization. To switch between organizations, the user should re-login and choose the needed organization.

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
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Applications
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
 **sort** | [**List[str]**](str.md)|  | [optional] 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_run_results_v1_runs_application_run_id_results_get**
> List[ItemResultReadResponse] list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, reference__in=reference__in, status__in=status__in, page=page, page_size=page_size, sort=sort)

List Run Results

Get the list of the results for the run items

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
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Run Results
        api_response = api_instance.list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, reference__in=reference__in, status__in=status__in, page=page, page_size=page_size, sort=sort)
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
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)|  | [optional] 

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
> List[ApplicationVersionReadResponse] list_versions_by_application_id_v1_applications_application_id_versions_get(application_id, page=page, page_size=page_size, version=version, include=include, sort=sort)

List Versions By Application Id

Returns the list of the application versions for this application, available to the caller.  The application version is available if it is assigned to the user's organization.  The application versions are assigned to the organization by the Aignostics admin. To assign or unassign a version from your organization, please contact Aignostics support team.

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
    version = 'version_example' # str |  (optional)
    include = None # List[object] |  (optional)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Versions By Application Id
        api_response = api_instance.list_versions_by_application_id_v1_applications_application_id_versions_get(application_id, page=page, page_size=page_size, version=version, include=include, sort=sort)
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
 **version** | **str**|  | [optional] 
 **include** | [**List[object]**](object.md)|  | [optional] 
 **sort** | [**List[str]**](str.md)|  | [optional] 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
