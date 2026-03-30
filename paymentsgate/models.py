from __future__ import annotations
import datetime
from decimal import Decimal
import json
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


from paymentsgate.enums import (
    BankPaymentSystems,
    BankType,
    CancellationReason,
    CredentialsTypes,
    Currencies,
    CurrencyTypes,
    DeepLinkDevices,
    DeepLinkType,
    EELQRBankALias,
    FeesStrategy,
    InvoiceDirection,
    InvoiceTypes,
    Languages,
    Statuses,
    TTLUnits,
    WidgetVersion,
)


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Credentials(BaseModel):
    account_id: str
    public_key: str
    private_key: str | None = None
    merchant_id: str | None = None
    project_id: str | None = None

    @classmethod
    def fromFile(cls, filename):
        data = json.load(open(filename))
        return cls(**data)

    model_config = ConfigDict(extra="ignore")


class PayInFingerprintBrowserModel(BaseRequestModel):
    acceptHeader: str
    colorDepth: int
    language: str
    screenHeight: int
    screenWidth: int
    timezone: str
    userAgent: str
    javaEnabled: bool
    windowHeight: int
    windowWidth: int


class PayInFingerprintModel(BaseRequestModel):
    fingerprint: str
    ip: str
    country: str
    city: str
    state: str
    zip: str
    browser: PayInFingerprintBrowserModel | None = None


class PayInClientCredentialsAddress(BaseRequestModel):
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country: str | None = None


class PayInClientCredentials(BaseRequestModel):
    card: PayInClientCredentialsCard | None = None
    address: PayInClientCredentialsAddress | None = None
    firstName: str
    lastName: str
    phone: str | None = None
    email: str | None = None


class PayInCredentials(BaseRequestModel):
    ownerName: str
    address: str
    city: str
    state: str
    phone: str


class PayInModel(BaseRequestModel):
    amount: float  # decimals: 2
    currency: Currencies
    country: str | None = None  # Country iso code
    invoiceId: str | None = None  # idempotent key
    clientId: str | None = None  # uniq client ref
    type: InvoiceTypes  # Invoice subtype, see documentation
    bankId: str | None = None  # ID from bank list or NSPK id
    trusted: bool | None = None
    successUrl: str | None = None
    failUrl: str | None = None
    backUrl: str | None = None
    clientCard: str | None = None
    clientName: str | None = None
    fingerprint: PayInFingerprintModel | None = None
    lang: Languages | None = None
    sync: bool | None = None  # sync h2h scheme, see documentation
    multiWidgetOptions: PayInMultiWidgetOptions | None = None
    theme: str | None = None  # personalized widget theme
    clientCredentials: PayInClientCredentials | None = None
    hostToHost: bool | None = None
    version: WidgetVersion | None = None
    description: str | None = None
    credentials: PayInCredentials | None = None


class DeepLinkUrlModel(BaseResponseModel):
    subtype: DeepLinkType
    device: DeepLinkDevices
    path: str
    description: str


class DeepLinkInfoModel(BaseResponseModel):
    urls: List[DeepLinkUrlModel]
    country: str | None = None


class PayInResponseModel(BaseResponseModel):
    id: str
    status: Statuses
    type: InvoiceTypes
    url: str | None = None
    deeplink: str | None = None
    m10: str | None = None
    cardholder: str | None = None
    account: str | None = None
    bankId: str | None = None
    accountSubType: str | None = None
    deepLinkInfo: DeepLinkInfoModel | None = None


class PayOutRecipientModel(BaseRequestModel):
    account_number: str | None = None  #  IBAN, Phone, Card, local bank account number, wallet number, etc'
    account_owner: str | None = None  # FirstName LastName or FirstName MiddleName LastName
    account_iban: str | None = None  # use only cases where iban is't primary  account id
    account_swift: str | None = None  # for swift transfers only
    account_phone: str | None = None  # additional recipient phone number, use only cases where phone is't primary  account id
    account_bic: str | None = None  # recipient bank id
    account_ewallet_name: str | None = None  # additional recipient wallet provider info
    account_email: str | None = None  # additional recipient email, use only cases where email is't primary account id
    account_bank_id: str | None = None  # recipient bankId (from API banks or RU NSPK id)
    account_internal_client_number: str | None = None  # Bank internal identifier used for method banktransferphp (Philippines)
    short_account_number: str | None = None
    account_qr_url: str | None = None
    type: CredentialsTypes | None = None  # primary credential type


class PayOutSenderModel(BaseRequestModel):
    name: str | None = None
    birthday: str | None = None
    phone: str | None = None
    passport: str | None = None


class PayOutModel(BaseRequestModel):
    currency: Currencies | None = None  # currency from, by default = usdt
    currencyTo: Currencies | None = None  # currency to, fiat only, if use quoteId - not required
    amount: Decimal | None = None  # decimals: 2, if use quoteId - not required
    invoiceId: str | None = None  # idempotent key
    clientId: str | None = None  # uniq client ref
    ttl: int | None = None
    ttl_unit: TTLUnits | None = None
    finalAmount: Decimal | None = None  # Optional, for pre-charge rate lock
    sender_name: str | None = None  # sender personal short data
    sender_personal: PayOutSenderModel | None = None
    baseCurrency: CurrencyTypes | None = None
    feesStrategy: FeesStrategy | None = None
    recipient: PayOutRecipientModel
    quoteId: str | None = None
    src_amount: str | None = None  # Optional, source amount in local currency for 2phase payout
    type: InvoiceTypes | None = None  # payout transaction scheme hint
    fiatLiquidity: bool | None = None
    refundAvailable: bool | None = None
    qrBase64String: str | None = None


class PayOutResponseModel(BaseResponseModel):
    id: str
    status: str


class GetQuoteModel(BaseRequestModel):
    currency_from: Currencies
    currency_to: Currencies
    amount: Decimal
    subtype: InvoiceTypes | None = None
    currency_original: Currencies | None = None
    src_amount: Decimal | None = None

class QuoteEntity(BaseResponseModel):
    currencyFrom: Currencies
    currencyTo: Currencies
    pair: str
    rate: float


class GetQuoteResponseModel(BaseResponseModel):
    id: str
    finalAmount: Decimal
    direction: InvoiceDirection
    fullRate: Decimal
    fullRateReverse: Decimal
    fees: Decimal
    fees_percent: Decimal
    quotes: List[QuoteEntity]
    expiredAt: datetime.datetime | None = None

    # deprecated
    currency_from: CurrencyModel | None = None
    currency_to: CurrencyModel | None = None
    currency_middle: CurrencyModel | None = None
    rate1: float | None = None
    rate2: float | None = None
    rate3: float | None = None
    net_amount: float | None = None
    metadata: object | None = None


class DepositAddressResponseModel(BaseResponseModel):
    currency: Currencies
    address: str
    expiredAt: datetime.datetime


class CurrencyModel(BaseResponseModel):
    _id: str
    type: CurrencyTypes
    code: Currencies
    symbol: str
    label: str | None = None
    decimal: int
    countryCode: str | None = None
    countryName: str | None = None
    tokenType: str | None = None
    blockchainSymbol: str | None = None
    blockchainMetaAlias: str | None = None
    isNative: bool | None = None
    tokenAddress: str | None = None
    testnet: bool | None = None


class BankLogoModel(BaseResponseModel):
    short: str
    full: str
    alt1: str | None = None
    alt2: str | None = None


class BankModel(BaseResponseModel):
    id: str = Field(..., alias="_id")
    name: str
    title: str
    title_en: str | None = None
    alias: str | None = None
    logo: BankLogoModel
    currency: Currencies
    currencyId: str
    type: BankType
    supportedPaymentSystems: List[BankPaymentSystems]
    country: str
    automationAvailable: bool | None = None
    enabled: bool
    isTopBank: bool
    tagColor: str
    fpsId: str
    tid: str | None = None
    url: str | None = None
    textColor: str | None = None


class InvoiceStatusModel(BaseResponseModel):
    name: Statuses
    createdAt: datetime.datetime
    updatedAt: datetime.datetime


class InvoiceAmountModel(BaseResponseModel):
    crypto: float
    fiat: float
    fiat_net: float


class InvoiceMetadataModel(BaseResponseModel):
    invoiceId: str | None = None
    clientId: str | None = None
    fiatAmount: float | None = None


class InvoiceModel(BaseResponseModel):
    id: str | None = Field(..., alias='_id')
    merchantId: str | None = None
    orderId: str | None = None
    projectId: str | None = None
    currencyFrom: CurrencyModel | None = None
    currencyTo: CurrencyModel | None = None
    exchangePair: str | None = None
    direction: InvoiceDirection | None = None
    amount: float | None = None
    status: InvoiceStatusModel | None = None
    amounts: InvoiceAmountModel | None = None
    metadata: InvoiceMetadataModel | None = None
    receiptUrls: List[str] | None = None
    reason: CancellationReason | None = None
    isExpired: bool | None = None
    createdAt: datetime.datetime | None = None
    updatedAt: datetime.datetime | None = None
    expiredAt: datetime.datetime | None = None
    model_config = ConfigDict(extra="ignore")

class InvoiceCredentialsModel(BaseResponseModel):
    account_number: str
    account_owner: str
    short_account_number: str | None = None
    account_iban: str | None = None
    account_swift: str | None = None
    account_phone: str | None = None
    account_bic: str | None = None
    account_ewallet_name: str | None = None
    account_email: str | None = None
    account_qr_url: str | None = None
    account_internal_client_number: str | None = None
    currency: CurrencyModel | None = None
    bank: BankModel | None = None
    type: CredentialsTypes | None = None
    model_config = ConfigDict(extra="ignore")


class AssetsAccountModel(BaseResponseModel):
    currency: CurrencyModel
    total: float
    pending: float
    pendingIn: float
    available: float
    model_config = ConfigDict(extra="ignore")


class AssetsResponseModel(BaseResponseModel):
    assets: List[AssetsAccountModel]
    model_config = ConfigDict(extra="ignore")


class PayInMultiWidgetOptions(BaseRequestModel):
    offerAmount: bool | None = None  # show amount select from best offers
    elqrBanks: List[EELQRBankALias] | None = None  # elqr bank list


class PayInClientCredentialsCard(BaseRequestModel):
    cardNumber: str
    cvv: str
    expMonth: str
    expYear: str
    holderName: str


class PayOutTlvRequestModel(BaseRequestModel):
    quoteId: str  # ID from /fx/tlv response
    invoiceId: str | None = None
    clientId: str | None = None
    sender_personal: PayOutSenderModel | None = None


class GetQuoteTlv(BaseRequestModel):
    data: str
    country: str | None = None


class TLVExtended(BaseResponseModel):
    merchant: str | None = None # MerchantName
    logo: str | None = None # MerchantLogo or merchant MCC logo
    city: str | None = None # Merchant city
    merchantId: str | None = None # uniq merchant id 
    zip: str | None = None # merchant address zip code
    qrRefId: str | None = None # uniq QR code reference id 
    invoiceId: str | None = None # Merchant invoiceId 
    merchantBank: str | None = None # Merchant bank name
    merchantIban: str | None = None # merchant iban
    merchantBankLogo: str | None = None # merchant bank logo

class QuoteTlvResponse(BaseResponseModel):
    id: str
    amount: float  # fiat local amount
    amountCrypto: float  # total crypto amount inc. fees
    currencyCode: Currencies  # local currency
    feeInCrypto: float  # total fee in crypto
    feePercent: float  # fee percent
    qrVersion: int  # qr code version, 1 - nspk, 2 - tlv encoded, 3 - tlv plain
    rate: float  # exchange rate
    tlv: TLVExtended | None = None
    isStatic: bool | None = None
    transactionCreatedAt: datetime.datetime | None = None
    transactionExpiredAt: datetime.datetime | None = None


class PayOutTlvRequest(BaseRequestModel):
    quoteId: str  # quote.id ref
    invoiceId: str | None = None
    clientId: str | None = None
    src_amount: float | None = None
    sender_personal: PayOutSenderModel | None = None

class ListMetadata(BaseResponseModel):
    page: int
    limit: int
    total: int

class InvoiceListModelWithMeta(BaseResponseModel): 
    meta: ListMetadata
    rows: List[InvoiceModel]
    model_config = ConfigDict(extra="ignore")
