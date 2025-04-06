# API v1 Reference
---
title: - url: ''
language_tabs:
toc_footers: []
includes: []
search: true
highlight_theme: darkula
---











          - Aignostics H&E TME application
          title: Description
          type: string
        name:
          examples:
          - HETA
          title: Name
          type: string
        regulatory_classes:
          examples:
          - - RuO
          items:
            type: string
          title: Regulatory Classes
          type: array
        slug:
          examples:
          - heta
          title: Slug
          type: string
      required:
      - application_id
      - name
      - slug
      - regulatory_classes
      - description
      title: ApplicationReadResponse
      type: object
    ApplicationRunStatus:
      enum:
      - canceled_system
      - canceled_user
      - completed
      - completed_with_error
      - received
      - rejected
      - running
      - scheduled
      title: ApplicationRunStatus
      type: string
    ApplicationVersionReadResponse:
      properties:
        application_id:
          format: uuid
          title: Application Id
          type: string
        application_version_id:
          format: uuid
          title: Application Version Id
          type: string
        application_version_slug:
          examples:
          - tissue-segmentation-qc:v0.0.1
          pattern: ^(?:|-)*:v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$
          title: Application Version Slug
          type: string
        changelog:
          title: Changelog
          type: string
        flow_id:
          anyOf:
          - format: uuid
            type: string
          - type: 'null'
          title: Flow Id
        input_artifacts:
          items:
            $ref: '#/components/schemas/InputArtifactReadResponse'
          title: Input Artifacts
          type: array
        output_artifacts:
          items:
            $ref: '#/components/schemas/OutputArtifactReadResponse'
          title: Output Artifacts
          type: array
        version:
          title: Version
          type: string
      required:
      - application_version_id
      - application_version_slug
      - version
      - application_id
      - changelog
      - input_artifacts
      - output_artifacts
      title: ApplicationVersionReadResponse
      type: object
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          title: Detail
          type: array
      title: HTTPValidationError
      type: object
    InputArtifact:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - image/tiff
          pattern: ^\w+/\w+(?:[-+.]|\w)+\w+$
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
      required:
      - name
      - mime_type
      - metadata_schema
      title: InputArtifact
      type: object
    InputArtifactCreationRequest:
      properties:
        download_url:
          examples:
          - https://example.com/case-no-1-slide.tiff
          format: uri
          maxLength: 2083
          minLength: 1
          title: Download Url
          type: string
        metadata:
          examples:
          - checksum_crc32c: 752f9554
            height: 2000
            height_mpp: 0.5
            width: 10000
            width_mpp: 0.5
          title: Metadata
          type: object
        name:
          examples:
          - slide
          title: Name
          type: string
      required:
      - name
      - download_url
      - metadata
      title: InputArtifactCreationRequest
      type: object
    InputArtifactReadResponse:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - image/tiff
          pattern: ^\w+/\w+(?:[-+.]|\w)+\w+$
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
      required:
      - name
      - mime_type
      - metadata_schema
      title: InputArtifactReadResponse
      type: object
    InputArtifactSchemaCreationRequest:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - application/vnd.apache.parquet
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
      required:
      - name
      - mime_type
      - metadata_schema
      title: InputArtifactSchemaCreationRequest
      type: object
    ItemCreationRequest:
      properties:
        input_artifacts:
          items:
            $ref: '#/components/schemas/InputArtifactCreationRequest'
          title: Input Artifacts
          type: array
        reference:
          examples:
          - case-no-1
          title: Reference
          type: string
      required:
      - reference
      - input_artifacts
      title: ItemCreationRequest
      type: object
    ItemResultReadResponse:
      properties:
        application_run_id:
          format: uuid
          title: Application Run Id
          type: string
        error:
          anyOf:
          - type: string
          - type: 'null'
          title: Error
        item_id:
          format: uuid
          title: Item Id
          type: string
        output_artifacts:
          items:
            $ref: '#/components/schemas/OutputArtifactResultReadResponse'
          title: Output Artifacts
          type: array
        reference:
          title: Reference
          type: string
        status:
          $ref: '#/components/schemas/ItemStatus'
      required:
      - item_id
      - application_run_id
      - reference
      - status
      - error
      - output_artifacts
      title: ItemResultReadResponse
      type: object
    ItemStatus:
      enum:
      - pending
      - canceled_user
      - canceled_system
      - error_user
      - error_system
      - succeeded
      title: ItemStatus
      type: string
    OutputArtifact:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - application/vnd.apache.parquet
          pattern: ^\w+/\w+(?:[-+.]|\w)+\w+$
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
        scope:
          $ref: '#/components/schemas/OutputArtifactScope'
        visibility:
          $ref: '#/components/schemas/OutputArtifactVisibility'
      required:
      - name
      - mime_type
      - metadata_schema
      - scope
      - visibility
      title: OutputArtifact
      type: object
    OutputArtifactReadResponse:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - application/vnd.apache.parquet
          pattern: ^\w+/\w+(?:[-+.]|\w)+\w+$
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
        scope:
          $ref: '#/components/schemas/OutputArtifactScope'
      required:
      - name
      - mime_type
      - metadata_schema
      - scope
      title: OutputArtifactReadResponse
      type: object
    OutputArtifactResultReadResponse:
      properties:
        download_url:
          anyOf:
          - format: uri
            maxLength: 2083
            minLength: 1
            type: string
          - type: 'null'
          title: Download Url
        metadata:
          title: Metadata
          type: object
        mime_type:
          examples:
          - application/vnd.apache.parquet
          pattern: ^\w+/\w+(?:[-+.]|\w)+\w+$
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
        output_artifact_id:
          format: uuid
          title: Output Artifact Id
          type: string
      required:
      - output_artifact_id
      - name
      - mime_type
      - metadata
      - download_url
      title: OutputArtifactResultReadResponse
      type: object
    OutputArtifactSchemaCreationRequest:
      properties:
        metadata_schema:
          title: Metadata Schema
          type: object
        mime_type:
          examples:
          - application/vnd.apache.parquet
          title: Mime Type
          type: string
        name:
          title: Name
          type: string
        scope:
          $ref: '#/components/schemas/OutputArtifactScope'
        visibility:
          $ref: '#/components/schemas/OutputArtifactVisibility'
      required:
      - name
      - mime_type
      - scope
      - visibility
      - metadata_schema
      title: OutputArtifactSchemaCreationRequest
      type: object
    OutputArtifactScope:
      enum:
      - item
      - global
      title: OutputArtifactScope
      type: string
    OutputArtifactVisibility:
      enum:
      - internal
      - external
      title: OutputArtifactVisibility
      type: string
    PayloadInputArtifact:
      properties:
        download_url:
          format: uri
          minLength: 1
          title: Download Url
          type: string
        input_artifact_id:
          format: uuid
          title: Input Artifact Id
          type: string
        metadata:
          title: Metadata
          type: object
      required:
      - metadata
      - download_url
      title: PayloadInputArtifact
      type: object
    PayloadItem:
      properties:
        input_artifacts:
          additionalProperties:
            $ref: '#/components/schemas/PayloadInputArtifact'
          title: Input Artifacts
          type: object
        item_id:
          format: uuid
          title: Item Id
          type: string
        output_artifacts:
          additionalProperties:
            $ref: '#/components/schemas/PayloadOutputArtifact'
          title: Output Artifacts
          type: object
      required:
      - item_id
      - input_artifacts
      - output_artifacts
      title: PayloadItem
      type: object
    PayloadOutputArtifact:
      properties:
        data:
          $ref: '#/components/schemas/TransferUrls'
        metadata:
          $ref: '#/components/schemas/TransferUrls'
        output_artifact_id:
          format: uuid
          title: Output Artifact Id
          type: string
      required:
      - output_artifact_id
      - data
      - metadata
      title: PayloadOutputArtifact
      type: object
    RunCreationRequest:
      properties:
        application_version:
          anyOf:
          - format: uuid
            type: string
          - $ref: '#/components/schemas/SlugVersionRequest'
          examples:
          - efbf9822-a1e5-4045-a283-dbf26e8064a9
          title: Application Version
        items:
          items:
            $ref: '#/components/schemas/ItemCreationRequest'
          title: Items
          type: array
      required:
      - application_version
      - items
      title: RunCreationRequest
      type: object
    RunCreationResponse:
      properties:
        application_run_id:
          format: uuid
          title: Application Run Id
          type: string
      required:
      - application_run_id
      title: RunCreationResponse
      type: object
    RunReadResponse:
      properties:
        application_run_id:
          format: uuid
          title: Application Run Id
          type: string
        application_version_id:
          format: uuid
          title: Application Version Id
          type: string
        organization_id:
          title: Organization Id
          type: string
        status:
          $ref: '#/components/schemas/ApplicationRunStatus'
        triggered_at:
          format: date-time
          title: Triggered At
          type: string
        triggered_by:
          title: Triggered By
          type: string
        user_payload:
          anyOf:
          - $ref: '#/components/schemas/UserPayload'
          - type: 'null'
      required:
      - application_run_id
      - application_version_id
      - organization_id
      - status
      - triggered_at
      - triggered_by
      title: RunReadResponse
      type: object
    SlugVersionRequest:
      properties:
        application_slug:
          pattern: ^(-?)*$
          title: Application Slug
          type: string
        version:
          title: Version
          type: string
      required:
      - application_slug
      - version
      title: SlugVersionRequest
      type: object
    TransferUrls:
      properties:
        download_url:
          format: uri
          minLength: 1
          title: Download Url
          type: string
        upload_url:
          format: uri
          minLength: 1
          title: Upload Url
          type: string
      required:
      - upload_url
      - download_url
      title: TransferUrls
      type: object
    UserPayload:
      properties:
        application_id:
          format: uuid
          title: Application Id
          type: string
        application_run_id:
          format: uuid
          title: Application Run Id
          type: string
        global_output_artifacts:
          anyOf:
          - additionalProperties:
              $ref: '#/components/schemas/PayloadOutputArtifact'
            type: object
          - type: 'null'
          title: Global Output Artifacts
        items:
          items:
            $ref: '#/components/schemas/PayloadItem'
          title: Items
          type: array
      required:
      - application_id
      - application_run_id
      - global_output_artifacts
      - items
      title: UserPayload
      type: object
    ValidationError:
      properties:
        loc:
          items:
            anyOf:
            - type: string
            - type: integer
          title: Location
          type: array
        msg:
          title: Message
          type: string
        type:
          title: Error Type
          type: string
      required:
      - loc
      - msg
      - type
      title: ValidationError
      type: object
    VersionCreationRequest:
      properties:
        application_id:
          format: uuid
          title: Application Id
          type: string
        changelog:
          title: Changelog
          type: string
        flow_id:
          format: uuid
          title: Flow Id
          type: string
        input_artifacts:
          items:
            $ref: '#/components/schemas/InputArtifactSchemaCreationRequest'
          title: Input Artifacts
          type: array
        output_artifacts:
          items:
            $ref: '#/components/schemas/OutputArtifactSchemaCreationRequest'
          title: Output Artifacts
          type: array
        version:
          title: Version
          type: string
      required:
      - version
      - application_id
      - flow_id
      - changelog
      - input_artifacts
      - output_artifacts
      title: VersionCreationRequest
      type: object
    VersionCreationResponse:
      properties:
        application_version_id:
          format: uuid
          title: Application Version Id
          type: string
      required:
      - application_version_id
      title: VersionCreationResponse
      type: object
    VersionReadResponse:
      properties:
        application_id:
          format: uuid
          title: Application Id
          type: string
        application_version_id:
          format: uuid
          title: Application Version Id
          type: string
        changelog:
          title: Changelog
          type: string
        created_at:
          format: date-time
          title: Created At
          type: string
        flow_id:
          anyOf:
          - format: uuid
            type: string
          - type: 'null'
          title: Flow Id
        input_artifacts:
          items:
            $ref: '#/components/schemas/InputArtifact'
          title: Input Artifacts
          type: array
        output_artifacts:
          items:
            $ref: '#/components/schemas/OutputArtifact'
          title: Output Artifacts
          type: array
        version:
          title: Version
          type: string
      required:
      - application_version_id
      - version
      - application_id
      - changelog
      - input_artifacts
      - output_artifacts
      - created_at
      title: VersionReadResponse
      type: object
info:
  title: PAPI API Reference
  version: 1.0.0
openapi: 3.1.0
paths:
  /v1/applications:
    get:
      operationId: list_applications_v1_applications_get
      parameters:
      - in: query
        name: page
        required: false
        schema:
          default: 1
          minimum: 1
          title: Page
          type: integer
      - in: query
        name: page_size
        required: false
        schema:
          default: 50
          maximum: 100
          minimum: 5
          title: Page Size
          type: integer
      - in: query
        name: sort
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Sort
      responses:
        '200':
          content:
            application/json:
              schema:
                items:
                  $ref: '#/components/schemas/ApplicationReadResponse'
                title: Response List Applications V1 Applications Get
                type: array
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: List Applications
      tags:
      - Externals
  /v1/applications/{application_id}/versions:
    get:
      operationId: 
list_versions_by_application_id_v1_applications__application_id__versions_get
      parameters:
      - in: path
        name: application_id
        required: true
        schema:
          format: uuid
          title: Application Id
          type: string
      - in: query
        name: page
        required: false
        schema:
          default: 1
          minimum: 1
          title: Page
          type: integer
      - in: query
        name: page_size
        required: false
        schema:
          default: 50
          maximum: 100
          minimum: 5
          title: Page Size
          type: integer
      - in: query
        name: version
        required: false
        schema:
          anyOf:
          - type: string
          - type: 'null'
          title: Version
      - in: query
        name: include
        required: false
        schema:
          anyOf:
          - maxItems: 1
            minItems: 1
            prefixItems:
            - type: string
            type: array
          - type: 'null'
          title: Include
      - in: query
        name: sort
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Sort
      responses:
        '200':
          content:
            application/json:
              schema:
                items:
                  $ref: '#/components/schemas/ApplicationVersionReadResponse'
                title: Response List Versions By Application Id V1 Applications 
Application
                  Id  Versions Get
                type: array
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: List Versions By Application Id
      tags:
      - Externals
  /v1/applications/{application_slug}:
    get:
      operationId: 
read_application_by_slug_v1_applications__application_slug__get
      parameters:
      - in: path
        name: application_slug
        required: true
        schema:
          title: Application Slug
          type: string
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApplicationReadResponse'
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Read Application By Slug
      tags:
      - Externals
  /v1/applications/{application_slug}/versions:
    get:
      operationId: 
list_versions_by_application_slug_v1_applications__application_slug__versions_ge
t
      parameters:
      - in: path
        name: application_slug
        required: true
        schema:
          pattern: ^(-?)*$
          title: Application Slug
          type: string
      - in: query
        name: page
        required: false
        schema:
          default: 1
          minimum: 1
          title: Page
          type: integer
      - in: query
        name: page_size
        required: false
        schema:
          default: 50
          maximum: 100
          minimum: 5
          title: Page Size
          type: integer
      - in: query
        name: version
        required: false
        schema:
          anyOf:
          - type: string
          - type: 'null'
          title: Version
      - in: query
        name: include
        required: false
        schema:
          anyOf:
          - maxItems: 1
            minItems: 1
            prefixItems:
            - type: string
            type: array
          - type: 'null'
          title: Include
      - in: query
        name: sort
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Sort
      responses:
        '200':
          content:
            application/json:
              schema:
                items:
                  $ref: '#/components/schemas/ApplicationVersionReadResponse'
                title: Response List Versions By Application Slug V1 
Applications  Application
                  Slug  Versions Get
                type: array
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: List Versions By Application Slug
      tags:
      - Externals
  /v1/runs:
    get:
      operationId: list_application_runs_v1_runs_get
      parameters:
      - in: query
        name: application_id
        required: false
        schema:
          anyOf:
          - format: uuid
            type: string
          - type: 'null'
          title: Application Id
      - in: query
        name: application_version_id
        required: false
        schema:
          anyOf:
          - format: uuid
            type: string
          - type: 'null'
          title: Application Version Id
      - in: query
        name: include
        required: false
        schema:
          anyOf:
          - maxItems: 1
            minItems: 1
            prefixItems:
            - type: string
            type: array
          - type: 'null'
          title: Include
      - in: query
        name: page
        required: false
        schema:
          default: 1
          minimum: 1
          title: Page
          type: integer
      - in: query
        name: page_size
        required: false
        schema:
          default: 50
          maximum: 100
          minimum: 5
          title: Page Size
          type: integer
      - in: query
        name: sort
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Sort
      responses:
        '200':
          content:
            application/json:
              schema:
                items:
                  $ref: '#/components/schemas/RunReadResponse'
                title: Response List Application Runs V1 Runs Get
                type: array
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: List Application Runs
      tags:
      - Externals
    post:
      operationId: create_application_run_v1_runs_post
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RunCreationRequest'
        required: true
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RunCreationResponse'
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Create Application Run
      tags:
      - Externals
  /v1/runs/{application_run_id}:
    get:
      operationId: get_run_v1_runs__application_run_id__get
      parameters:
      - in: path
        name: application_run_id
        required: true
        schema:
          format: uuid
          title: Application Run Id
          type: string
      - in: query
        name: include
        required: false
        schema:
          anyOf:
          - maxItems: 1
            minItems: 1
            prefixItems:
            - type: string
            type: array
          - type: 'null'
          title: Include
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RunReadResponse'
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Get Run
      tags:
      - Externals
  /v1/runs/{application_run_id}/cancel:
    post:
      operationId: cancel_run_v1_runs__application_run_id__cancel_post
      parameters:
      - in: path
        name: application_run_id
        required: true
        schema:
          format: uuid
          title: Application Run Id
          type: string
      responses:
        '202':
          content:
            application/json:
              schema: {}
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Cancel Run
      tags:
      - Externals
  /v1/runs/{application_run_id}/results:
    delete:
      operationId: 
delete_run_results_v1_runs__application_run_id__results_delete
      parameters:
      - in: path
        name: application_run_id
        required: true
        schema:
          format: uuid
          title: Application Run Id
          type: string
      responses:
        '204':
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Delete Run Results
      tags:
      - Externals
    get:
      operationId: list_run_results_v1_runs__application_run_id__results_get
      parameters:
      - in: path
        name: application_run_id
        required: true
        schema:
          format: uuid
          title: Application Run Id
          type: string
      - in: query
        name: item_id__in
        required: false
        schema:
          anyOf:
          - items:
              format: uuid
              type: string
            type: array
          - type: 'null'
          title: Item Id  In
      - in: query
        name: page
        required: false
        schema:
          default: 1
          minimum: 1
          title: Page
          type: integer
      - in: query
        name: page_size
        required: false
        schema:
          default: 50
          maximum: 100
          minimum: 5
          title: Page Size
          type: integer
      - in: query
        name: reference__in
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Reference  In
      - in: query
        name: status__in
        required: false
        schema:
          anyOf:
          - items:
              $ref: '#/components/schemas/ItemStatus'
            type: array
          - type: 'null'
          title: Status  In
      - in: query
        name: sort
        required: false
        schema:
          anyOf:
          - items:
              type: string
            type: array
          - type: 'null'
          title: Sort
      responses:
        '200':
          content:
            application/json:
              schema:
                items:
                  $ref: '#/components/schemas/ItemResultReadResponse'
                title: Response List Run Results V1 Runs  Application Run Id  
Results
                  Get
                type: array
          description: Successful Response
        '404':
          description: Application run not found
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: List Run Results
      tags:
      - Externals
  /v1/versions:
    post:
      operationId: register_version_v1_versions_post
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VersionCreationRequest'
        required: true
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VersionCreationResponse'
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Register Version
      tags:
      - Externals
  /v1/versions/{application_version_id}:
    get:
      operationId: get_version_v1_versions__application_version_id__get
      parameters:
      - in: path
        name: application_version_id
        required: true
        schema:
          format: uuid
          title: Application Version Id
          type: string
      - in: query
        name: include
        required: false
        schema:
          anyOf:
          - maxItems: 1
            minItems: 1
            prefixItems:
            - type: string
            type: array
          - type: 'null'
          title: Include
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VersionReadResponse'
          description: Successful Response
        '422':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
          description: Validation Error
      summary: Get Version
      tags:
      - Externals
servers:
- url: ''

> components:

>   schemas:

>     ApplicationReadResponse:

>       properties:

>         application_id:

>           format: uuid

>           title: Application Id

>           type: string

>         description:

>           examples:
