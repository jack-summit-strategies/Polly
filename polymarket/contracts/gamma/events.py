from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class EventsParams(BaseModel):
    limit: int | None = Field(default=None, ge=0)
    offset: int | None = Field(default=None, ge=0)
    order: str | None = None          # comma-separated field names
    ascending: bool | None = None
    id: list[int] | None = None
    tag_id: int | None = None
    exclude_tag_id: list[int] | None = None
    slug: list[str] | None = None
    tag_slug: str | None = None
    related_tags: bool | None = None
    active: bool | None = None
    archived: bool | None = None
    featured: bool | None = None
    cyom: bool | None = None
    include_chat: bool | None = None
    include_template: bool | None = None
    recurrence: str | None = None
    closed: bool | None = None
    liquidity_min: float | None = None
    liquidity_max: float | None = None
    volume_min: float | None = None
    volume_max: float | None = None
    start_date_min: str | None = None   # ISO 8601 datetime string
    start_date_max: str | None = None
    end_date_min: str | None = None
    end_date_max: str | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class Event(BaseModel):
    id: str
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    resolutionSource: str | None = None
    startDate: datetime | None = None
    creationDate: datetime | None = None
    endDate: datetime | None = None
    image: str | None = None
    icon: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None
    liquidity: float | None = None
    volume: float | None = None
    openInterest: float | None = None
    sortBy: str | None = None
    category: str | None = None
    subcategory: str | None = None
    isTemplate: bool | None = None
    templateVariables: str | None = None
    published_at: str | None = None
    createdBy: str | None = None
    updatedBy: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    commentsEnabled: bool | None = None
    competitive: float | None = None
    volume24hr: float | None = None
    volume1wk: float | None = None
    volume1mo: float | None = None
    volume1yr: float | None = None
    featuredImage: str | None = None
    disqusThread: str | None = None
    parentEvent: str | None = None
    enableOrderBook: bool | None = None
    liquidityAmm: float | None = None
    liquidityClob: float | None = None
    negRisk: bool | None = None
    negRiskMarketID: str | None = None
    negRiskFeeBips: int | None = None
    commentCount: int | None = None
    imageOptimized: ImageOptimized | None = None
    iconOptimized: ImageOptimized | None = None
    featuredImageOptimized: ImageOptimized | None = None
    subEvents: list[str] | None = None
    markets: list[Market] | None = None
    series: list[Series] | None = None
    categories: list[Category] | None = None
    collections: list[Collection] | None = None
    tags: list[Tag] | None = None
    cyom: bool | None = None
    closedTime: datetime | None = None
    showAllOutcomes: bool | None = None
    showMarketImages: bool | None = None
    automaticallyResolved: bool | None = None
    enableNegRisk: bool | None = None
    automaticallyActive: bool | None = None
    eventDate: str | None = None
    startTime: datetime | None = None
    eventWeek: int | None = None
    seriesSlug: str | None = None
    score: str | None = None
    elapsed: str | None = None
    period: str | None = None
    live: bool | None = None
    ended: bool | None = None
    finishedTimestamp: datetime | None = None
    gmpChartMode: str | None = None
    eventCreators: list[EventCreator] | None = None
    tweetCount: int | None = None
    chats: list[Chat] | None = None
    featuredOrder: int | None = None
    estimateValue: bool | None = None
    cantEstimate: bool | None = None
    estimatedValue: str | None = None
    templates: list[Template] | None = None
    spreadsMainLine: float | None = None
    totalsMainLine: float | None = None
    carouselMap: str | None = None
    pendingDeployment: bool | None = None
    deploying: bool | None = None
    deployingTimestamp: datetime | None = None
    scheduledDeploymentTimestamp: datetime | None = None
    gameStatus: str | None = None


# ---------------------------------------------------------------------------
# Helper classes (for nested objects in the response)
# ---------------------------------------------------------------------------

class ImageOptimized(BaseModel):
    id: str | None = None
    imageUrlSource: str | None = None
    imageUrlOptimized: str | None = None
    imageSizeKbSource: float | None = None
    imageSizeKbOptimized: float | None = None
    imageOptimizedComplete: bool | None = None
    imageOptimizedLastUpdated: str | None = None
    relID: int | None = None
    field: str | None = None
    relname: str | None = None


class Category(BaseModel):
    id: str | None = None
    label: str | None = None
    parentCategory: str | None = None
    slug: str | None = None
    publishedAt: str | None = None
    createdBy: str | None = None
    updatedBy: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Tag(BaseModel):
    id: str | None = None
    label: str | None = None
    slug: str | None = None
    forceShow: bool | None = None
    publishedAt: str | None = None
    createdBy: int | None = None   # API returns int here
    updatedBy: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    forceHide: bool | None = None
    isCarousel: bool | None = None


class Chat(BaseModel):
    id: str | None = None
    channelId: str | None = None
    channelName: str | None = None
    channelImage: str | None = None
    live: bool | None = None
    startTime: datetime | None = None
    endTime: datetime | None = None


class FeeSchedule(BaseModel):
    exponent: float | None = None
    rate: float | None = None
    takerOnly: bool | None = None
    rebateRate: float | None = None


class Collection(BaseModel):
    id: str | None = None
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    collectionType: str | None = None
    description: str | None = None
    tags: str | None = None
    image: str | None = None
    icon: str | None = None
    headerImage: str | None = None
    layout: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None
    isTemplate: bool | None = None
    templateVariables: str | None = None
    publishedAt: str | None = None
    createdBy: str | None = None
    updatedBy: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    commentsEnabled: bool | None = None
    imageOptimized: ImageOptimized | None = None
    iconOptimized: ImageOptimized | None = None
    headerImageOptimized: ImageOptimized | None = None


class Market(BaseModel):
    id: str | None = None
    question: str | None = None
    conditionId: str | None = None
    slug: str | None = None
    twitterCardImage: str | None = None
    resolutionSource: str | None = None
    endDate: datetime | None = None
    category: str | None = None
    ammType: str | None = None
    liquidity: str | None = None        # API returns string at market level
    sponsorName: str | None = None
    sponsorImage: str | None = None
    startDate: datetime | None = None
    xAxisValue: str | None = None
    yAxisValue: str | None = None
    denominationToken: str | None = None
    fee: str | None = None
    image: str | None = None
    icon: str | None = None
    lowerBound: str | None = None
    upperBound: str | None = None
    description: str | None = None
    outcomes: str | None = None
    outcomePrices: str | None = None
    volume: str | None = None           # API returns string at market level
    active: bool | None = None
    marketType: str | None = None
    formatType: str | None = None
    lowerBoundDate: str | None = None
    upperBoundDate: str | None = None
    closed: bool | None = None
    marketMakerAddress: str | None = None
    createdBy: int | None = None        # API returns int at market level
    updatedBy: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    closedTime: str | None = None
    wideFormat: bool | None = None
    new: bool | None = None
    mailchimpTag: str | None = None
    featured: bool | None = None
    archived: bool | None = None
    resolvedBy: str | None = None
    restricted: bool | None = None
    marketGroup: int | None = None
    groupItemTitle: str | None = None
    groupItemThreshold: str | None = None
    questionID: str | None = None
    umaEndDate: str | None = None
    enableOrderBook: bool | None = None
    orderPriceMinTickSize: float | None = None
    orderMinSize: float | None = None
    umaResolutionStatus: str | None = None
    curationOrder: int | None = None
    volumeNum: float | None = None
    liquidityNum: float | None = None
    endDateIso: str | None = None
    startDateIso: str | None = None
    umaEndDateIso: str | None = None
    hasReviewedDates: bool | None = None
    readyForCron: bool | None = None
    commentsEnabled: bool | None = None
    volume24hr: float | None = None
    volume1wk: float | None = None
    volume1mo: float | None = None
    volume1yr: float | None = None
    gameStartTime: str | None = None
    secondsDelay: int | None = None
    clobTokenIds: str | None = None
    disqusThread: str | None = None
    shortOutcomes: str | None = None
    teamAID: str | None = None
    teamBID: str | None = None
    umaBond: str | None = None
    umaReward: str | None = None
    fpmmLive: bool | None = None
    volume24hrAmm: float | None = None
    volume1wkAmm: float | None = None
    volume1moAmm: float | None = None
    volume1yrAmm: float | None = None
    volume24hrClob: float | None = None
    volume1wkClob: float | None = None
    volume1moClob: float | None = None
    volume1yrClob: float | None = None
    volumeAmm: float | None = None
    volumeClob: float | None = None
    liquidityAmm: float | None = None
    liquidityClob: float | None = None
    makerBaseFee: float | None = None
    takerBaseFee: float | None = None
    customLiveness: int | None = None
    acceptingOrders: bool | None = None
    notificationsEnabled: bool | None = None
    score: float | None = None
    imageOptimized: ImageOptimized | None = None
    iconOptimized: ImageOptimized | None = None
    events: list[Any] | None = None     # circular reference back to events
    categories: list[Category] | None = None
    tags: list[Tag] | None = None
    creator: str | None = None
    ready: bool | None = None
    funded: bool | None = None
    pastSlugs: str | None = None
    readyTimestamp: datetime | None = None
    fundedTimestamp: datetime | None = None
    acceptingOrdersTimestamp: datetime | None = None
    competitive: float | None = None
    rewardsMinSize: float | None = None
    rewardsMaxSpread: float | None = None
    spread: float | None = None
    automaticallyResolved: bool | None = None
    oneDayPriceChange: float | None = None
    oneHourPriceChange: float | None = None
    oneWeekPriceChange: float | None = None
    oneMonthPriceChange: float | None = None
    oneYearPriceChange: float | None = None
    lastTradePrice: float | None = None
    bestBid: float | None = None
    bestAsk: float | None = None
    automaticallyActive: bool | None = None
    clearBookOnStart: bool | None = None
    chartColor: str | None = None
    seriesColor: str | None = None
    showGmpSeries: bool | None = None
    showGmpOutcome: bool | None = None
    manualActivation: bool | None = None
    negRiskOther: bool | None = None
    gameId: str | None = None
    groupItemRange: str | None = None
    sportsMarketType: str | None = None
    line: float | None = None
    umaResolutionStatuses: str | None = None
    pendingDeployment: bool | None = None
    deploying: bool | None = None
    deployingTimestamp: datetime | None = None
    scheduledDeploymentTimestamp: datetime | None = None
    rfqEnabled: bool | None = None
    eventStartTime: datetime | None = None
    feesEnabled: bool | None = None
    feeSchedule: FeeSchedule | None = None


class Series(BaseModel):
    id: str | None = None
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    seriesType: str | None = None
    recurrence: str | None = None
    description: str | None = None
    image: str | None = None
    icon: str | None = None
    layout: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None
    isTemplate: bool | None = None
    templateVariables: bool | None = None   # API returns bool at series level
    publishedAt: str | None = None
    createdBy: str | None = None
    updatedBy: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    commentsEnabled: bool | None = None
    competitive: str | None = None          # API returns string at series level
    volume24hr: float | None = None
    volume: float | None = None
    liquidity: float | None = None
    startDate: datetime | None = None
    pythTokenID: str | None = None
    cgAssetName: str | None = None
    score: float | None = None
    events: list[Any] | None = None         # circular reference back to events
    collections: list[Collection] | None = None
    categories: list[Category] | None = None
    tags: list[Tag] | None = None
    commentCount: int | None = None
    chats: list[Chat] | None = None


class EventCreator(BaseModel):
    id: str | None = None
    creatorName: str | None = None
    creatorHandle: str | None = None
    creatorUrl: str | None = None
    creatorImage: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Template(BaseModel):
    id: str | None = None
    eventTitle: str | None = None
    eventSlug: str | None = None
    eventImage: str | None = None
    marketTitle: str | None = None
    description: str | None = None
    resolutionSource: str | None = None
    negRisk: bool | None = None
    sortBy: str | None = None
    showMarketImages: bool | None = None
    seriesSlug: str | None = None
    outcomes: str | None = None
