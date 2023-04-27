"""Schemas used internally by the process manager."""
import datetime as dt
import enum
import typing
from pathlib import Path

import pydantic
from pygeoapi.util import JobStatus


class ProcessIOType(enum.Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"


class ProcessIOFormat(enum.Enum):
    # this is built from:
    # - the jsonschema spec at: https://json-schema.org/draft/2020-12/json-schema-validation.html#name-defined-formats
    # - the OAPI - Processes spec (table 13) at: https://docs.ogc.org/is/18-062r2/18-062r2.html#ogc_process_description
    DATE_TIME = "date-time"
    DATE = "date"
    TIME = "time"
    DURATION = "duration"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    URI = "uri"
    URI_REFERENCE = "uri-reference"
    # left out `iri` and `iri-reference` as valid URIs are also valid IRIs
    UUID = "uuid"
    URI_TEMPLATE = "uri-template"
    JSON_POINTER = "json-pointer"
    RELATIVE_JSON_POINTER = "relative-json-pointer"
    REGEX = "regex"
    # the below `binary` entry does not seem to be defined in the jsonschema spec
    # nor in OAPI - Processes - but it is mentioned in OAPI - Processes spec as an example
    BINARY = "binary"
    GEOJSON_FEATURE_COLLECTION_URI = "http://www.opengis.net/def/format/ogcapi-processes/0/geojson-feature-collection"
    GEOJSON_FEATURE_URI = (
        "http://www.opengis.net/def/format/ogcapi-processes/0/geojson-feature"
    )
    GEOJSON_GEOMETRY_URI = (
        "http://www.opengis.net/def/format/ogcapi-processes/0/geojson-geometry"
    )
    OGC_BBOX_URI = "http://www.opengis.net/def/format/ogcapi-processes/0/ogc-bbox"
    GEOJSON_FEATURE_COLLECTION_SHORT_CODE = "geojson-feature-collection"
    GEOJSON_FEATURE_SHORT_CODE = "geojson-feature"
    GEOJSON_GEOMETRY_SHORT_CODE = "geojson-geometry"
    OGC_BBOX_SHORT_CODE = "ogc-bbox"


class ProcessJobControlOption(enum.Enum):
    SYNC_EXECUTE = "sync-execute"
    ASYNC_EXECUTE = "async-execute"
    DISMISS = "dismiss"


class ProcessOutputTransmissionMode(enum.Enum):
    VALUE = "value"
    REFERENCE = "reference"


class ProcessResponseType(enum.Enum):
    document = "document"
    raw = "raw"


class Link(pydantic.BaseModel):
    href: str
    type_: typing.Optional[str] = pydantic.Field(None, alias="type")
    rel: typing.Optional[str] = None
    title: typing.Optional[str] = None
    href_lang: typing.Optional[str] = pydantic.Field(None, alias="hreflang")


class ProcessMetadata(pydantic.BaseModel):
    title: str | None = None
    role: str | None = None
    href: str | None = None


class AdditionalProcessIOParameters(ProcessMetadata):
    name: str
    value: list[str | float | int | list[dict] | dict]


# this is a 'pydantification' of the schema.yml fragment, as shown
# on the OAPI - Processes spec
class ProcessIOSchema(pydantic.BaseModel):
    title: str | None
    multiple_of: float | None = pydantic.Field(alias="multipleOf")
    maximum: float | None
    exclusive_maximum: bool = pydantic.Field(False, alias="exclusiveMaximum")
    minimum: float | None
    exclusive_minimum: bool = pydantic.Field(False, alias="exclusiveMinimum")
    max_length: int = pydantic.Field(None, ge=0, alias="maxLength")
    min_length: int = pydantic.Field(0, ge=0, alias="minLength")
    pattern: str | None
    max_items: int | None = pydantic.Field(None, ge=0, alias="maxItems")
    min_items: int = pydantic.Field(0, ge=0, alias="minItems")
    unique_items: bool = pydantic.Field(False, alias="uniqueItems")
    max_properties: int | None = pydantic.Field(None, ge=0, alias="maxProperties")
    min_properties: int = pydantic.Field(0, ge=0, alias="minProperties")
    required: pydantic.conlist(str, min_items=1, unique_items=True) | None
    enum: pydantic.conlist(typing.Any, min_items=1, unique_items=False) | None
    type_: ProcessIOType | None = pydantic.Field(None, alias="type")
    not_: typing.Optional["ProcessIOSchema"] = pydantic.Field(None, alias="not")
    allOf: list["ProcessIOSchema"] | None
    oneOf: list["ProcessIOSchema"] | None
    anyOf: list["ProcessIOSchema"] | None
    items: list["ProcessIOSchema"] | None
    properties: typing.Optional["ProcessIOSchema"]
    additional_properties: typing.Union[bool, "ProcessIOSchema"] = pydantic.Field(
        True, alias="additionalProperties"
    )
    description: str | None
    format_: ProcessIOFormat | None = pydantic.Field(None, alias="format")
    default: pydantic.Json[dict] | None
    nullable: bool = False
    read_only: bool = pydantic.Field(False, alias="readOnly")
    write_only: bool = pydantic.Field(False, alias="writeOnly")
    example: pydantic.Json[dict] | None
    deprecated: bool = False
    content_media_type: str | None = pydantic.Field(None, alias="contentMediaType")
    content_encoding: str | None = pydantic.Field(None, alias="contentEncoding")
    content_schema: str | None = pydantic.Field(None, alias="contentSchema")

    class Config:
        use_enum_values = True


class ProcessOutput(pydantic.BaseModel):
    title: str | None
    description: str | None
    schema_: ProcessIOSchema = pydantic.Field(alias="schema")


class ProcessInput(ProcessOutput):
    keywords: list[str] | None
    metadata: list[ProcessMetadata] | None
    min_occurs: int = pydantic.Field(1, alias="minOccurs")
    max_occurs: int | typing.Literal["unbounded"] = pydantic.Field(1, alias="maxOccurs")
    additional_parameters: AdditionalProcessIOParameters | None


class Process(pydantic.BaseModel):
    title: dict[str, str]
    description: dict[str, str]
    keywords: list[str]
    version: str
    id: str
    job_control_options: list[ProcessJobControlOption] = pydantic.Field(
        alias="jobControlOptions"
    )
    output_transmission: list[ProcessOutputTransmissionMode] = pydantic.Field(
        [ProcessOutputTransmissionMode.VALUE], alias="outputTransmission"
    )
    links: list[Link]

    inputs: dict[str, ProcessInput]
    outputs: dict[str, ProcessOutput]
    example: typing.Optional[dict]


class AdditionalParameter(pydantic.BaseModel):
    name: str
    value: list[str | int | float | list[pydantic.Json] | pydantic.Json]


class AdditionalParameters(ProcessMetadata):
    parameters: list[AdditionalParameter]


class ProcessSummary(pydantic.BaseModel):
    """OAPI - Processes. Schema for a ProcessSummary."""

    # definition from ProcessSummary
    id: str
    version: str
    job_control_options: list[ProcessJobControlOption] | None = pydantic.Field(
        None, alias="jobControlOptions"
    )
    output_transmission: list[ProcessOutputTransmissionMode] | None = pydantic.Field(
        None, alias="outputTransmission"
    )
    links: list[Link] | None = None

    # definition from descriptionType
    title: dict[str, str] | None = None
    description: dict[str, str] | None = None
    keywords: list[str] | None = None
    metadata: list[ProcessMetadata] | None = None
    additional_parameters: AdditionalParameters | None = pydantic.Field(
        None, alias="additionalParameters"
    )


class JobStatusInfo(pydantic.BaseModel):
    """OAPI - Processes. Schema for a StatusInfo."""

    job_id: str = pydantic.Field(..., alias="jobID")
    status: JobStatus
    type: typing.Literal["process"] = "process"
    process_id: str = pydantic.Field(..., alias="processID")
    message: str | None
    created: dt.datetime | None
    started: dt.datetime | None
    finished: dt.datetime | None
    updated: dt.datetime | None
    progress: int | None = pydantic.Field(None, ge=0, le=100)
    links: list[Link] | None


class ProcessManagerConfig(pydantic.BaseModel):
    # this is taken from the schema definition of pygeoapi config
    name: str
    connection: str
    output_dir: str


class ExecutionInputBBox(pydantic.BaseModel):
    bbox: list[float] = pydantic.Field(..., min_items=4, max_items=4)
    crs: typing.Optional[str] = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"


class ExecutionInputValueNoObjectArray(pydantic.BaseModel):
    __root__: typing.List[
        typing.Union[ExecutionInputBBox, int, str, "ExecutionInputValueNoObjectArray"]
    ]


class ExecutionInputValueNoObject(pydantic.BaseModel):
    """Models the `inputValueNoObject.yml` schema defined in OAPIP."""

    __root__: typing.Union[
        ExecutionInputBBox,
        bool,
        float,
        int,
        ExecutionInputValueNoObjectArray,
        str,
    ]

    class Config:
        smart_union = True


class ExecutionFormat(pydantic.BaseModel):
    """Models the `format.yml` schema defined in OAPIP."""

    media_type: typing.Optional[str] = pydantic.Field(None, alias="mediaType")
    encoding: typing.Optional[str]
    schema_: typing.Optional[typing.Union[str, dict]] = pydantic.Field(
        None, alias="schema"
    )


class ExecutionQualifiedInputValue(pydantic.BaseModel):
    """Models the `qualifiedInputValue.yml` schema defined in OAPIP."""

    value: typing.Union[ExecutionInputValueNoObject, dict]
    format_: typing.Optional[ExecutionFormat] = None


class ExecutionOutput(pydantic.BaseModel):
    """Models the `output.yml` schema defined in OAPIP."""

    format_: typing.Optional[ExecutionFormat] = pydantic.Field(None, alias="format")
    transmission_mode: typing.Optional[ProcessOutputTransmissionMode] = pydantic.Field(
        ProcessOutputTransmissionMode.VALUE, alias="transmissionMode"
    )

    class Config:
        use_enum_values = True


class ExecutionSubscriber(pydantic.BaseModel):
    """Models the `subscriber.yml` schema defined in OAPIP."""

    success_uri: str = pydantic.Field(..., alias="successUri")
    in_progress_uri: typing.Optional[str] = pydantic.Field(None, alias="inProgressUri")
    failed_uri: typing.Optional[str] = pydantic.Field(None, alias="failedUri")


class Execution(pydantic.BaseModel):
    """Models the `execute.yml` schema defined in OAPIP."""

    inputs: typing.Optional[
        typing.Dict[
            str,
            typing.Union[
                ExecutionInputValueNoObject,
                ExecutionQualifiedInputValue,
                Link,
                typing.List[
                    typing.Union[
                        ExecutionInputValueNoObject,
                        ExecutionQualifiedInputValue,
                        Link,
                    ]
                ],
            ],
        ]
    ] = None
    outputs: typing.Optional[typing.Dict[str, ExecutionOutput]] = None
    response: typing.Optional[ProcessResponseType] = ProcessResponseType.raw
    subscriber: typing.Optional[ExecutionSubscriber] = None

    class Config:
        use_enum_values = True
