## API Concepts

If you use other languages then Python in your codebase you can natively
integrate with the webservice API of the aignostics platform. 
The following sections outline the main concepts of the API and how to use it.

### Overview
The Aignostics Platform is a comprehensive cloud-based service that allows organizations to leverage advanced computational pathology applications without the need for specialized on-premises infrastructure. With its API (described in details below) it provides a standardized, secure interface for accessing Aignostics' portfolio of computational pathology applications. These applications perform advanced tissue and cell analysis on histopathology slides, delivering quantitative measurements, visual representations, and detailed statistical data.

### Key Features
Aignostics Platform offers key features designed to maximize value for its users:

* **High-throughput processing:** You can submit 500 whole slide images (WSI) in one request
* **Multi-format support:** Support for commonly used pathology image formats (TIF, DICOM, SVS)
* **Access to Aignostics applications:** Integration with Aignostics computational pathology application like Atlas H&E TME
* **Secure Data Handling:** Maintain control of your slide data through secure self-signed URLswithout needing to transfer files into foreign organization infrastructure
* **Incremental Results Delivery:** Access results for individual slides as they complete processing, without waiting for the entire batch to finish
* **Flexible Integration:** Integrate access to Aignostics applications with your existing systems through our API

### Registration and Access
To begin using the Aignostics Platform and its applications, your organization must first be registered by our team. Currently, account creation is not self-service. Please contact us to initiate the registration process.

1. Access to the Aignostics Platform requires a formal business agreement. Once an agreement is in place between your organization and Aignostics, we will proceed with your organization's registration. If your organization does not yet have an account, please contact your dedicated account manager or email us at support@aignostics.com to express your interest.
2. To register your organization, we require the name and email address of at least one employee, who will be assigned the Organization Admin role. This user will act as the primary administrator for your organization on the platform.
3. The Organization Admin can invite and manage additional users within the same organization though a dedicated Platform Dashboard. Please note:
   1. All user accounts must be associated with your organization's official domain.
   2. We do not support the registration of private or personal email addresses.
   3. For security, Two-Factor Authentication (2FA) is mandatory for all user accounts.

The entire process typically takes 2 business days depending on the complexity of the business agreement and specific requirements.

### User management
AIgnostics Platform is available to users registered in the platform. The client organization is created by the Aignostics business support team (super admin). The customer becomes the member of the organization.

Admin of the organization can add more users, admins or members. Both roles can trigger application runs, but additionally to that admins can manage users of the organization.

### Applications
An application is a fully automated end-to-end workflow composed of one or more specific tasks (Tissue Quality Control, Tissue Segmentation, Cell Detection and Classification…). Each application is designed for a particular analysis purpose (e.g. TME analysis, biomarker scoring). For each application we define input requirements, processing tasks and output formats.

Each application can have multiple versions. Applications and its versions are assigned to your organization by Aignostics based on business agreement. Please make sure you read dedicated application documentation to understand its specific constraints regarding acceptable formats, staining method, tissue types and diseases.

Once registered to the Platform, your organization will automatically gain access to the test application for free. This application can be used to configure the workflow and to make sure that the integration works correctly, without any extra cost.

### Application run
To trigger the application run, users can use the Python client, or the REST API. The platform expects the user payload, containing the metadata of the slides and the signed URLs to the WSIs. The detailed description of the payload is different for every application and described via the /v1/applications endpoint.

When the application run is created, it can be in one of the following states:

* **received** - the application run received from the client
* **scheduled** - the application run request is valid and is scheduled for execution
* **running** - the application run execution started
* **completed** - the application run execution is done and all outputs are available for download
* **completed** with error - the application run execution is done, but some items end up in the failed state
* **rejected** - the application run request is rejected before it is scheduled
* **cancelled by the system** - the application run failed during the execution with the number of errors higher than the threshold
* **cancelled by the user** - the application run is cancelled by the user before it is finished

Only the user who created the application run can check its status, retrieve results or cancel its execution.

### Results
When the processing of an image is successfully completed, the resulting outputs become available for the download. To assess specifics of application outputs please consult application specific documentation, which you can find available in Aignostics Platform Dashboard. You will receive access to application documentations only for those applications that are available to your organization.

Application run outputs are automatically deleted 30 days after the application run has completed. However, the owner of the application run (the user who initiated it) can use the API to manually delete outputs earlier, once the run has reached a final state - completed, cancelled by the system or cancelled by the user.

### Quotas
Every organization has a limit on how many WSIs it can process in a calendar month. The following quotas exist:

* **For an organization** - assigned by the Aignostics based on defined business agreement with the organization
* **For a user** - assigned by the organization Admin to the user

When the per month quota is reached, the application run request is denied.

Other limitations may apply to your organization:

* Allowed number of users an organization can register
* Allowed number of images user can submit in one application run
* Allowed number of parallel application runs for the whole organization

Additionally, we allow organization Admin to define following limitations for its users:

* Maximum number of images the user can process per calendar month.
* Maximum number of parallel application runs for a user

To view the quota and the quota usage, please access Platform Dashboard.

### Cost
Every WSI processed by the Platform generates a cost. Usage of test application doesn't generate any cost and is free for any registered user.

When the application run is cancelled, either by the system or by the user, only the processed images are added to the cost for your organization.

**[Read the API reference documentation](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) to learn about all operations and parameters.**
