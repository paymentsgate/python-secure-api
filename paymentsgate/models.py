from __future__ import annotations
import datetime
import json
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


from paymentsgate.enums import (
  Currencies, 
  InvoiceTypes, 
  Languages, 
  Statuses, 
  TTLUnits, 
  CurrencyTypes, 
  FeesStrategy,
  InvoiceDirection,
  CredentialsTypes
)

class BaseRequestModel(BaseModel):
  model_config = ConfigDict(extra='forbid')

class BaseResponseModel(BaseModel):
  model_config = ConfigDict(extra='ignore')


class Credentials(BaseModel):
  account_id: str
  public_key: str
  private_key: Optional[str] = Field(default=None)
  merchant_id: Optional[str] = Field(default=None)
  project_id: Optional[str] = Field(default=None)
  
  @classmethod
  def fromFile(cls, filename):
    data = json.load(open(filename))
    return cls(**data)
  
  model_config = ConfigDict(extra='ignore')


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
  browser: Optional[PayInFingerprintBrowserModel]

class PayInModel(BaseRequestModel):
  amount: float # decimals: 2
  currency: Currencies
  country: Optional[str]  # Country iso code
  invoiceId: Optional[str] # idempotent key
  clientId: Optional[str] # uniq client ref
  type: InvoiceTypes # Invoice subtype, see documentation 
  bankId: Optional[str] # ID from bank list or NSPK id
  trusted: Optional[bool]
  successUrl: Optional[str]
  failUrl: Optional[str]
  backUrl: Optional[str]
  clientCard: Optional[str]
  clientName: Optional[str]
  fingerprint: Optional[PayInFingerprintModel]
  lang: Optional[Languages]
  sync: Optional[bool] # sync h2h scheme, see documentation
  multiWidgetOptions: Optional[PayInMultiWidgetOptions]
  theme: Optional[str] # personalized widget theme
   
class PayInResponseModel(BaseResponseModel):
  id: str
  status: Statuses
  type: InvoiceTypes
  url: Optional[str]
  deeplink: Optional[str]
  m10: Optional[str]
  cardholder: Optional[str]
  account: Optional[str]
  bankId: Optional[str]
  accountSubType: Optional[str]

class PayOutRecipientModel(BaseRequestModel):
  account_number: str #  IBAN, Phone, Card, local bank account number, wallet number, etc'
  account_owner: Optional[str] # FirstName LastName or FirstName MiddleName LastName
  account_iban: Optional[str] # use only cases where iban is't primary  account id  
  account_swift: Optional[str] # for swift transfers only
  account_phone: Optional[str] # additional recipient phone number, use only cases where phone is't primary  account id
  account_bic: Optional[str] # recipient bank id
  account_ewallet_name: Optional[str] # additional recipient wallet provider info
  account_email: Optional[str] # additional recipient email, use only cases where email is't primary account id
  account_bank_id: Optional[str] # recipient bankId (from API banks or RU NSPK id)
  account_internal_client_number: Optional[str] # Bank internal identifier used for method banktransferphp (Philippines)
  type: Optional[CredentialsTypes] # primary credential type

class PayOutModel(BaseRequestModel):
  currency: Optional[Currencies] # currency from, by default = usdt
  currencyTo: Optional[Currencies] # currency to, fiat only, if use quoteId - not required
  amount: Optional[float] # decimals: 2, if use quoteId - not required
  invoiceId: Optional[str] # idempotent key
  clientId: Optional[str] # uniq client ref
  ttl: Optional[int]
  ttl_unit: Optional[TTLUnits]
  finalAmount: Optional[float] # Optional, for pre-charge rate lock
  sender_name: Optional[str] # sender personal short data
  sender_personal: Optional[PayOutSenderModel]
  baseCurrency: Optional[CurrencyTypes]
  feesStrategy: Optional[FeesStrategy]
  recipient: PayOutRecipientModel
  quoteId: Optional[str]
  src_amount: Optional[str] # Optional, source amount in local currency for 2phase payout
  type: Optional[InvoiceTypes] # payout transaction scheme hint
   
class PayOutResponseModel(BaseResponseModel):
  id: str
  status: Statuses

class GetQuoteModel(BaseRequestModel):
  currency_from: Currencies
  currency_to: Currencies
  amount: float
  subtype: Optional[InvoiceTypes]
  currency_original: Optional[Currencies]

class QuoteEntity(BaseResponseModel):
  currencyFrom: Currencies
  currencyTo: Currencies
  pair: str
  rate: float

class GetQuoteResponseModel(BaseResponseModel):
  id: str
  finalAmount: float
  direction: InvoiceDirection
  fullRate: float
  fullRateReverse: float
  fees: float
  fees_percent: float
  quotes: List[QuoteEntity]
  expiredAt: Optional[datetime.datetime] = Field(default=None)

  #deprecated
  currency_from: Optional[CurrencyModel] = Field(default=None)
  currency_to: Optional[CurrencyModel] = Field(default=None)
  currency_middle: Optional[CurrencyModel] = Field(default=None)
  rate1: Optional[float] = Field(default=None)
  rate2: Optional[float] = Field(default=None)
  rate3: Optional[float] = Field(default=None)
  net_amount: Optional[float] = Field(default=None)
  metadata: Optional[object] = Field(default=None)


class DepositAddressResponseModel(BaseResponseModel):
  currency: Currencies
  address: str
  expiredAt: datetime.datetime


class CurrencyModel(BaseResponseModel):
  _id: str
  type: CurrencyTypes
  code: Currencies
  symbol: str
  label: Optional[str] = Field(default=None)
  decimal: int
  countryCode: Optional[str] = Field(default=None)
  countryName: Optional[str] = Field(default=None)

class BankModel(BaseResponseModel):
  name: str
  title: str
  currency: Currencies
  fpsId: str

class InvoiceStatusModel(BaseResponseModel):
  name: Statuses
  createdAt: datetime.datetime
  updatedAt: datetime.datetime

class InvoiceAmountModel(BaseResponseModel):
  crypto: float
  fiat: float
  fiat_net: float

class InvoiceMetadataModel(BaseResponseModel):
  invoiceId: Optional[str]
  clientId: Optional[str]
  fiatAmount: Optional[float]

class InvoiceModel(BaseResponseModel):
  _id: str
  orderId: str
  projectId: str
  currencyFrom: CurrencyModel
  currencyTo: CurrencyModel
  direction: InvoiceDirection
  amount: float
  status: InvoiceStatusModel
  amounts: InvoiceAmountModel
  metadata: InvoiceMetadataModel
  receiptUrls: List[str]
  isExpired: bool
  createdAt: datetime.datetime
  updatedAt: datetime.datetime
  expiredAt: datetime.datetime

class AssetsAccountModel(BaseResponseModel):
  currency: CurrencyModel;
  total: float
  pending: float
  available: float

class AssetsResponseModel(BaseResponseModel):
  assets: List[AssetsAccountModel]

class PayInMultiWidgetOptions(BaseRequestModel):
  offerAmount: Optional[bool] # show amount select from best offers
  elqrBanks: Optional[str] # elqr bank list

class PayOutSenderModel(BaseRequestModel):
  name: Optional[str]
  birthday: Optional[str]
  phone: Optional[str]
  passport: Optional[str]

class PayOutTlvRequestModel(BaseRequestModel):
  quoteId: str # ID from /fx/tlv response
  invoiceId: Optional[str]
  clientId: Optional[str]
  sender_personal: Optional[PayOutSenderModel]

class GetQuoteTlv(BaseRequestModel):
  data: str

class QuoteTlvResponse(BaseResponseModel):
  id: str
  amount: float # fiat local amount
  amountCrypto: float # total crypto amount inc. fees
  currencyCode: Currencies # local currency
  feeInCrypto: float # total fee in crypto
  feePercent: float # fee percent
  qrVersion: int # qr code version, 1 - nspk, 2 - tlv encoded, 3 - tlv plain
  rate: float # exchange rate 
  merchant: Optional[str] = Field(default=None) # merchant title
  logo: Optional[str] = Field(default=None) # merchant logo

class PayOutTlvRequest(BaseRequestModel):
  quoteId: str # quote.id ref
  invoiceId: Optional[str] = Field(default=None)
  clientId: Optional[str] = Field(default=None)
  src_amount: Optional[float] = Field(default=None)
  sender_personal: Optional[PayOutSenderModel] = Field(default=None)