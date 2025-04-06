# aignx.codegen.ExternalsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_run_v1_runs_application_run_id_cancel_post**](ExternalsApi.md#cancel_run_v1_runs_application_run_id_cancel_post) | **POST** /v1/runs/{application_run_id}/cancel | Cancel Run
[**create_application_run_v1_runs_post**](ExternalsApi.md#create_application_run_v1_runs_post) | **POST** /v1/runs | Create Application Run
[**delete_run_results_v1_runs_application_run_id_results_delete**](ExternalsApi.md#delete_run_results_v1_runs_application_run_id_results_delete) | **DELETE** /v1/runs/{application_run_id}/results | Delete Run Results
[**get_run_v1_runs_application_run_id_get**](ExternalsApi.md#get_run_v1_runs_application_run_id_get) | **GET** /v1/runs/{application_run_id} | Get Run
[**get_version_v1_versions_application_version_id_get**](ExternalsApi.md#get_version_v1_versions_application_version_id_get) | **GET** /v1/versions/{application_version_id} | Get Version
[**list_application_runs_v1_runs_get**](ExternalsApi.md#list_application_runs_v1_runs_get) | **GET** /v1/runs | List Application Runs
[**list_applications_v1_applications_get**](ExternalsApi.md#list_applications_v1_applications_get) | **GET** /v1/applications | List Applications
[**list_run_results_v1_runs_application_run_id_results_get**](ExternalsApi.md#list_run_results_v1_runs_application_run_id_results_get) | **GET** /v1/runs/{application_run_id}/results | List Run Results
[**list_versions_by_application_id_v1_applications_application_id_versions_get**](ExternalsApi.md#list_versions_by_application_id_v1_applications_application_id_versions_get) | **GET** /v1/applications/{application_id}/versions | List Versions By Application Id
[**list_versions_by_application_slug_v1_applications_application_slug_versions_get**](ExternalsApi.md#list_versions_by_application_slug_v1_applications_application_slug_versions_get) | **GET** /v1/applications/{application_slug}/versions | List Versions By Application Slug
[**read_application_by_slug_v1_applications_application_slug_get**](ExternalsApi.md#read_application_by_slug_v1_applications_application_slug_get) | **GET** /v1/applications/{application_slug} | Read Application By Slug
[**register_version_v1_versions_post**](ExternalsApi.md#register_version_v1_versions_post) | **POST** /v1/versions | Register Version


# **cancel_run_v1_runs_application_run_id_cancel_post**
> object cancel_run_v1_runs_application_run_id_cancel_post(application_run_id)

Cancel Run

### Example


```python
import aignx.codegen
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_run_id = 'application_run_id_example' # str | 

    try:
        # Cancel Run
        api_response = api_instance.cancel_run_v1_runs_application_run_id_cancel_post(application_run_id)
        print("The response of ExternalsApi->cancel_run_v1_runs_application_run_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->cancel_run_v1_runs_application_run_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

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

### Example


```python
import aignx.codegen
from aignx.codegen.models.run_creation_request import RunCreationRequest
from aignx.codegen.models.run_creation_response import RunCreationResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    run_creation_request = aignx.codegen.RunCreationRequest() # RunCreationRequest | 

    try:
        # Create Application Run
        api_response = api_instance.create_application_run_v1_runs_post(run_creation_request)
        print("The response of ExternalsApi->create_application_run_v1_runs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->create_application_run_v1_runs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_creation_request** | [**RunCreationRequest**](RunCreationRequest.md)|  | 

### Return type

[**RunCreationResponse**](RunCreationResponse.md)

### Authorization

No authorization required

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

# **delete_run_results_v1_runs_application_run_id_results_delete**
> delete_run_results_v1_runs_application_run_id_results_delete(application_run_id)

Delete Run Results

### Example


```python
import aignx.codegen
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_run_id = 'application_run_id_example' # str | 

    try:
        # Delete Run Results
        api_instance.delete_run_results_v1_runs_application_run_id_results_delete(application_run_id)
    except Exception as e:
        print("Exception when calling ExternalsApi->delete_run_results_v1_runs_application_run_id_results_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

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

### Example


```python
import aignx.codegen
from aignx.codegen.models.run_read_response import RunReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_run_id = 'application_run_id_example' # str | 
    include = None # List[object] |  (optional)

    try:
        # Get Run
        api_response = api_instance.get_run_v1_runs_application_run_id_get(application_run_id, include=include)
        print("The response of ExternalsApi->get_run_v1_runs_application_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->get_run_v1_runs_application_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**|  | 
 **include** | [**List[object]**](object.md)|  | [optional] 

### Return type

[**RunReadResponse**](RunReadResponse.md)

### Authorization

No authorization required

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

# **get_version_v1_versions_application_version_id_get**
> VersionReadResponse get_version_v1_versions_application_version_id_get(application_version_id, include=include)

Get Version

### Example


```python
import aignx.codegen
from aignx.codegen.models.version_read_response import VersionReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_version_id = 'application_version_id_example' # str | 
    include = None # List[object] |  (optional)

    try:
        # Get Version
        api_response = api_instance.get_version_v1_versions_application_version_id_get(application_version_id, include=include)
        print("The response of ExternalsApi->get_version_v1_versions_application_version_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->get_version_v1_versions_application_version_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_version_id** | **str**|  | 
 **include** | [**List[object]**](object.md)|  | [optional] 

### Return type

[**VersionReadResponse**](VersionReadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_application_runs_v1_runs_get**
> List[RunReadResponse] list_application_runs_v1_runs_get(application_id=application_id, application_version_id=application_version_id, include=include, page=page, page_size=page_size, sort=sort)

List Application Runs

### Example


```python
import aignx.codegen
from aignx.codegen.models.run_read_response import RunReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_id = 'application_id_example' # str |  (optional)
    application_version_id = 'application_version_id_example' # str |  (optional)
    include = None # List[object] |  (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Application Runs
        api_response = api_instance.list_application_runs_v1_runs_get(application_id=application_id, application_version_id=application_version_id, include=include, page=page, page_size=page_size, sort=sort)
        print("The response of ExternalsApi->list_application_runs_v1_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->list_application_runs_v1_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | [optional] 
 **application_version_id** | **str**|  | [optional] 
 **include** | [**List[object]**](object.md)|  | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **sort** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**List[RunReadResponse]**](RunReadResponse.md)

### Authorization

No authorization required

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

### Example


```python
import aignx.codegen
from aignx.codegen.models.application_read_response import ApplicationReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Applications
        api_response = api_instance.list_applications_v1_applications_get(page=page, page_size=page_size, sort=sort)
        print("The response of ExternalsApi->list_applications_v1_applications_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->list_applications_v1_applications_get: %s\n" % e)
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

No authorization required

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
> List[ItemResultReadResponse] list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, page=page, page_size=page_size, reference__in=reference__in, status__in=status__in, sort=sort)

List Run Results

### Example


```python
import aignx.codegen
from aignx.codegen.models.item_result_read_response import ItemResultReadResponse
from aignx.codegen.models.item_status import ItemStatus
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_run_id = 'application_run_id_example' # str | 
    item_id__in = ['item_id__in_example'] # List[Optional[str]] |  (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    reference__in = ['reference__in_example'] # List[str] |  (optional)
    status__in = [aignx.codegen.ItemStatus()] # List[ItemStatus] |  (optional)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Run Results
        api_response = api_instance.list_run_results_v1_runs_application_run_id_results_get(application_run_id, item_id__in=item_id__in, page=page, page_size=page_size, reference__in=reference__in, status__in=status__in, sort=sort)
        print("The response of ExternalsApi->list_run_results_v1_runs_application_run_id_results_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->list_run_results_v1_runs_application_run_id_results_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_run_id** | **str**|  | 
 **item_id__in** | [**List[Optional[str]]**](str.md)|  | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **reference__in** | [**List[str]**](str.md)|  | [optional] 
 **status__in** | [**List[ItemStatus]**](ItemStatus.md)|  | [optional] 
 **sort** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**List[ItemResultReadResponse]**](ItemResultReadResponse.md)

### Authorization

No authorization required

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

### Example


```python
import aignx.codegen
from aignx.codegen.models.application_version_read_response import ApplicationVersionReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_id = 'application_id_example' # str | 
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    version = 'version_example' # str |  (optional)
    include = None # List[object] |  (optional)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Versions By Application Id
        api_response = api_instance.list_versions_by_application_id_v1_applications_application_id_versions_get(application_id, page=page, page_size=page_size, version=version, include=include, sort=sort)
        print("The response of ExternalsApi->list_versions_by_application_id_v1_applications_application_id_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->list_versions_by_application_id_v1_applications_application_id_versions_get: %s\n" % e)
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

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_versions_by_application_slug_v1_applications_application_slug_versions_get**
> List[ApplicationVersionReadResponse] list_versions_by_application_slug_v1_applications_application_slug_versions_get(application_slug, page=page, page_size=page_size, version=version, include=include, sort=sort)

List Versions By Application Slug

### Example


```python
import aignx.codegen
from aignx.codegen.models.application_version_read_response import ApplicationVersionReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_slug = 'application_slug_example' # str | 
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    version = 'version_example' # str |  (optional)
    include = None # List[object] |  (optional)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List Versions By Application Slug
        api_response = api_instance.list_versions_by_application_slug_v1_applications_application_slug_versions_get(application_slug, page=page, page_size=page_size, version=version, include=include, sort=sort)
        print("The response of ExternalsApi->list_versions_by_application_slug_v1_applications_application_slug_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->list_versions_by_application_slug_v1_applications_application_slug_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_slug** | **str**|  | 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **version** | **str**|  | [optional] 
 **include** | [**List[object]**](object.md)|  | [optional] 
 **sort** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**List[ApplicationVersionReadResponse]**](ApplicationVersionReadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_application_by_slug_v1_applications_application_slug_get**
> ApplicationReadResponse read_application_by_slug_v1_applications_application_slug_get(application_slug)

Read Application By Slug

### Example


```python
import aignx.codegen
from aignx.codegen.models.application_read_response import ApplicationReadResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    application_slug = 'application_slug_example' # str | 

    try:
        # Read Application By Slug
        api_response = api_instance.read_application_by_slug_v1_applications_application_slug_get(application_slug)
        print("The response of ExternalsApi->read_application_by_slug_v1_applications_application_slug_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->read_application_by_slug_v1_applications_application_slug_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_slug** | **str**|  | 

### Return type

[**ApplicationReadResponse**](ApplicationReadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_version_v1_versions_post**
> VersionCreationResponse register_version_v1_versions_post(version_creation_request)

Register Version

### Example


```python
import aignx.codegen
from aignx.codegen.models.version_creation_request import VersionCreationRequest
from aignx.codegen.models.version_creation_response import VersionCreationResponse
from aignx.codegen.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aignx.codegen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aignx.codegen.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aignx.codegen.ExternalsApi(api_client)
    version_creation_request = aignx.codegen.VersionCreationRequest() # VersionCreationRequest | 

    try:
        # Register Version
        api_response = api_instance.register_version_v1_versions_post(version_creation_request)
        print("The response of ExternalsApi->register_version_v1_versions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalsApi->register_version_v1_versions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **version_creation_request** | [**VersionCreationRequest**](VersionCreationRequest.md)|  | 

### Return type

[**VersionCreationResponse**](VersionCreationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
