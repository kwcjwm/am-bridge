from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


class JsonDataclassMixin:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass
class LegacyMeta:
    sourceFile: str = ""
    windowId: str = ""
    formId: str = ""
    title: str = ""
    initialEvent: str = ""
    legacyPageType: str = ""
    includes: list[str] = field(default_factory=list)


@dataclass
class PlatformMeta:
    menuKey: str = ""
    permissionKey: str = ""
    approvalRequired: bool = False
    mailIntegration: bool = False
    sharedComponentUsage: list[str] = field(default_factory=list)


@dataclass
class DatasetColumn:
    name: str
    type: str = ""
    size: int | None = None
    required: bool | None = None
    semanticType: str = ""
    notes: str = ""


@dataclass
class DatasetModel:
    datasetId: str
    role: str = ""
    primaryUsage: str = ""
    columns: list[DatasetColumn] = field(default_factory=list)
    defaultRecords: list[dict[str, Any]] = field(default_factory=list)
    usageContexts: list[str] = field(default_factory=list)
    boundComponents: list[str] = field(default_factory=list)
    salienceScore: int = 0
    salienceReasons: list[str] = field(default_factory=list)
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class ComponentModel:
    componentId: str
    componentType: str
    parentId: str = ""
    containerPath: str = ""
    layoutGroup: str = ""
    styleKey: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    platformDependency: list[str] = field(default_factory=list)
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class BindingModel:
    bindingId: str
    componentId: str
    datasetId: str
    columnName: str = ""
    bindingType: str = ""
    direction: str = ""
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class TransactionModel:
    transactionId: str
    serviceId: str = ""
    url: str = ""
    inputDatasets: list[str] = field(default_factory=list)
    outputDatasets: list[str] = field(default_factory=list)
    parameters: str = ""
    callbackFunction: str = ""
    wrapperFunction: str = ""
    apiCandidate: str = ""
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class EventModel:
    eventId: str
    sourceComponentId: str = ""
    eventName: str = ""
    handlerFunction: str = ""
    eventType: str = ""
    triggerCondition: str = ""
    effects: list[str] = field(default_factory=list)


@dataclass
class FunctionModel:
    functionName: str
    functionType: str = ""
    parameters: list[str] = field(default_factory=list)
    callsFunctions: list[str] = field(default_factory=list)
    callsTransactions: list[str] = field(default_factory=list)
    readsDatasets: list[str] = field(default_factory=list)
    writesDatasets: list[str] = field(default_factory=list)
    controlsComponents: list[str] = field(default_factory=list)
    platformCalls: list[str] = field(default_factory=list)
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class NavigationModel:
    navigationId: str
    triggerFunction: str = ""
    navigationType: str = ""
    target: str = ""
    parameterBindings: list[str] = field(default_factory=list)
    returnHandling: str = ""


@dataclass
class StyleModel:
    styleId: str
    componentId: str = ""
    property: str = ""
    rawValue: str = ""
    tokenCandidate: str = ""
    usageScope: str = ""


@dataclass
class StateRuleModel:
    ruleId: str
    targetComponentId: str = ""
    stateProperty: str = ""
    triggerCondition: str = ""
    sourceFunction: str = ""
    expression: str = ""
    targetValue: Any = None


@dataclass
class ValidationRuleModel:
    ruleId: str
    targetField: str = ""
    validationType: str = ""
    triggerTiming: str = ""
    sourceFunction: str = ""
    expression: str = ""
    message: str = ""


@dataclass
class MessageModel:
    messageId: str
    sourceType: str = ""
    messageType: str = ""
    text: str = ""
    sourceFunction: str = ""
    targetComponentId: str = ""
    i18nKeyCandidate: str = ""
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class RealtimeSubscriptionModel:
    subscriptionId: str
    sourceType: str = ""
    sourceName: str = ""
    trigger: str = ""
    lifecycleStart: str = ""
    lifecycleEnd: str = ""
    refreshIntervalMs: int | None = None
    targetComponents: list[str] = field(default_factory=list)
    targetDatasets: list[str] = field(default_factory=list)
    errorPolicy: str = ""


@dataclass
class ChartModel:
    chartId: str
    chartType: str = ""
    title: str = ""
    datasetId: str = ""
    series: list[dict[str, Any]] = field(default_factory=list)
    refreshMode: str = ""
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageVisionViewModel:
    viewerId: str
    viewerType: str = ""
    imageSource: dict[str, Any] = field(default_factory=dict)
    overlayEnabled: bool = False
    overlayTypes: list[str] = field(default_factory=list)
    interactions: list[str] = field(default_factory=list)
    resultDatasetId: str = ""
    resultFields: list[str] = field(default_factory=list)


@dataclass
class AlarmEventModel:
    eventStreamId: str
    sourceType: str = ""
    severityField: str = ""
    statusField: str = ""
    ackFunction: str = ""
    clearFunction: str = ""
    targetComponents: list[str] = field(default_factory=list)
    refreshMode: str = ""
    colorRuleSet: str = ""


@dataclass
class CommandActionModel:
    actionId: str
    actionName: str = ""
    triggerComponentId: str = ""
    commandTarget: str = ""
    requiredRole: str = ""
    confirmationRequired: bool = False
    auditRequired: bool = False
    successCallback: str = ""
    failureCallback: str = ""


@dataclass
class ReviewWorkflowModel:
    workflowId: str
    workflowType: str = ""
    sourceDatasetId: str = ""
    states: list[str] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    approvalIntegration: bool = False
    auditRequired: bool = False


@dataclass
class PageModel(JsonDataclassMixin):
    pageId: str = ""
    pageName: str = ""
    pageType: str = "unknown"
    primaryDatasetId: str = ""
    secondaryDatasetIds: list[str] = field(default_factory=list)
    primaryTransactionIds: list[str] = field(default_factory=list)
    mainGridComponentId: str = ""
    interactionPattern: str = ""
    legacy: LegacyMeta = field(default_factory=LegacyMeta)
    platform: PlatformMeta = field(default_factory=PlatformMeta)
    layout: dict[str, Any] = field(default_factory=dict)
    datasets: list[DatasetModel] = field(default_factory=list)
    components: list[ComponentModel] = field(default_factory=list)
    bindings: list[BindingModel] = field(default_factory=list)
    transactions: list[TransactionModel] = field(default_factory=list)
    events: list[EventModel] = field(default_factory=list)
    functions: list[FunctionModel] = field(default_factory=list)
    navigation: list[NavigationModel] = field(default_factory=list)
    styles: list[StyleModel] = field(default_factory=list)
    stateRules: list[StateRuleModel] = field(default_factory=list)
    validationRules: list[ValidationRuleModel] = field(default_factory=list)
    messages: list[MessageModel] = field(default_factory=list)
    realtimeSubscriptions: list[RealtimeSubscriptionModel] = field(default_factory=list)
    charts: list[ChartModel] = field(default_factory=list)
    imageVisionViews: list[ImageVisionViewModel] = field(default_factory=list)
    alarmEvents: list[AlarmEventModel] = field(default_factory=list)
    commandActions: list[CommandActionModel] = field(default_factory=list)
    reviewWorkflows: list[ReviewWorkflowModel] = field(default_factory=list)
    notes: str = ""


@dataclass
class BackendTraceModel:
    transactionId: str
    url: str = ""
    requestMapping: str = ""
    controllerClass: str = ""
    controllerMethod: str = ""
    controllerMethodSignature: str = ""
    requestDtoType: str = ""
    responseCarrierType: str = ""
    serviceBeanName: str = ""
    serviceInterface: str = ""
    serviceImplClass: str = ""
    serviceMethod: str = ""
    daoClass: str = ""
    daoMethod: str = ""
    sqlMapId: str = ""
    sqlMapFile: str = ""
    sqlOperation: str = ""
    tableCandidates: list[str] = field(default_factory=list)
    responseFieldCandidates: list[str] = field(default_factory=list)
    querySummary: str = ""
    sourceRefs: list[str] = field(default_factory=list)


@dataclass
class RelatedPageModel:
    navigationId: str = ""
    navigationType: str = ""
    triggerFunction: str = ""
    target: str = ""
    resolvedPath: str = ""
    pageId: str = ""
    pageName: str = ""
    pageType: str = ""
    resolutionStatus: str = ""


@dataclass
class PageConversionPackage(JsonDataclassMixin):
    packageId: str
    page: PageModel
    backendTraces: list[BackendTraceModel] = field(default_factory=list)
    relatedPages: list[RelatedPageModel] = field(default_factory=list)
    openQuestions: list[str] = field(default_factory=list)
    aiHints: list[str] = field(default_factory=list)
    stageNotes: list[str] = field(default_factory=list)


@dataclass
class FileBlueprintModel:
    path: str
    purpose: str = ""
    summary: str = ""


@dataclass
class ConversionPlanModel(JsonDataclassMixin):
    packageId: str
    pageId: str
    route: str = ""
    vuePageName: str = ""
    interactionPattern: str = ""
    frontendFiles: list[FileBlueprintModel] = field(default_factory=list)
    backendFiles: list[FileBlueprintModel] = field(default_factory=list)
    executionSteps: list[str] = field(default_factory=list)
    verificationChecks: list[str] = field(default_factory=list)
    aiPrompts: dict[str, str] = field(default_factory=dict)


@dataclass
class VuePageConfigModel(JsonDataclassMixin):
    pageId: str
    pageName: str = ""
    legacySourceFile: str = ""
    pageType: str = ""
    vuePageName: str = ""
    route: str = ""
    interactionPattern: str = ""
    primaryDatasetId: str = ""
    mainGridComponentId: str = ""
    primaryTransactionIds: list[str] = field(default_factory=list)
    datasets: list[dict[str, Any]] = field(default_factory=list)
    grids: list[dict[str, Any]] = field(default_factory=list)
    searchControls: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    endpoints: list[dict[str, Any]] = field(default_factory=list)
    relatedPages: list[dict[str, Any]] = field(default_factory=list)
    frontendFiles: list[str] = field(default_factory=list)
    backendFiles: list[str] = field(default_factory=list)
    verificationChecks: list[str] = field(default_factory=list)


@dataclass
class StarterFileModel:
    path: str
    content: str = ""
    purpose: str = ""


@dataclass
class StarterBundleModel(JsonDataclassMixin):
    pageId: str
    frontendFiles: list[StarterFileModel] = field(default_factory=list)
    backendFiles: list[StarterFileModel] = field(default_factory=list)
    handoffPrompts: dict[str, str] = field(default_factory=dict)
