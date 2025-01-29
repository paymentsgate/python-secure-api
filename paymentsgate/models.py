from __future__ import annotations
from dataclasses import dataclass
import datetime
import json
from typing import Optional, List

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

from pydantic import BaseModel, ConfigDict

@dataclass
class Credentials:
  def __init__(
      self, 
      account_id: str,
      merchant_id: str,
      project_id: str,
      private_key: str,
      public_key: str
  ):
     self.account_id = account_id
     self.merchant_id = merchant_id
     self.project_id = project_id
     self.private_key = private_key
     self.public_key = public_key
  
  @classmethod
  def fromFile(cls, filename):
    data = json.load(open(filename))
    return cls(data.get('account_id'),
               data.get('merchant_id'),
               data.get('project_id'),
               data.get('private_key'),
               data.get('public_key'))


@dataclass
class PayInFingerprintBrowserModel:
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

@dataclass
class PayInFingerprintModel:
  fingerprint: str
  ip: str
  country: str
  city: str
  state: str
  zip: str
  browser: Optional[PayInFingerprintBrowserModel]

@dataclass
class PayInModel:
  amount: float
  currency: Currencies
  invoiceId: Optional[str] # idempotent key
  clientId: Optional[str]
  type: InvoiceTypes
  bankId: Optional[str]
  trusted: Optional[bool]
  successUrl: Optional[str]
  failUrl: Optional[str]
  backUrl: Optional[str]
  clientCard: Optional[str]
  fingerprint: Optional[PayInFingerprintModel]
  lang: Optional[Languages]
   
@dataclass
class PayInResponseModel:
  id: str
  status: Statuses
  type: InvoiceTypes
  url: str

@dataclass
class PayOutRecipientModel:
  account_number: str
  account_owner: Optional[str]
  account_iban: Optional[str]
  account_swift: Optional[str]
  account_phone: Optional[str]
  account_bic: Optional[str]
  account_ewallet_name: Optional[str]
  account_email: Optional[str]
  account_bank_id: Optional[str]
  type: Optional[CredentialsTypes]

@dataclass
class PayOutModel:
  currency: Optional[Currencies] # currency from, by default = usdt
  currencyTo:Currencies
  amount: float
  invoiceId: Optional[str] # idempotent key
  clientId: Optional[str]
  ttl: Optional[int]
  ttl_unit: Optional[TTLUnits]
  finalAmount: Optional[float]
  sender_name: Optional[str]
  baseCurrency: Optional[CurrencyTypes]
  feesStrategy: Optional[FeesStrategy]
  recipient: PayOutRecipientModel
  quoteId: Optional[str]
   
@dataclass
class PayOutResponseModel:
  id: str
  status: Statuses

@dataclass
class GetQuoteModel:
  currency_from: Currencies
  currency_to: Currencies
  amount: float
  subtype: InvoiceTypes

@dataclass
class QuoteEntity:
  currency_from: CurrencyModel
  currency_to: CurrencyModel
  pair: str
  rate: float

@dataclass
class GetQuoteResponseModel:
  id: Optional[str]  = None
  finalAmount: Optional[float]  = None
  direction: Optional[InvoiceDirection]  = None
  fullRate: Optional[float]  = None
  fullRateReverse: Optional[float]  = None
  fees: Optional[float]  = None
  fees_percent: Optional[float]  = None
  quotes: Optional[List[QuoteEntity]]  = None
  expiredAt: Optional[datetime.datetime] = None

  #deprecated
  currency_from: Optional[CurrencyModel] = None
  currency_to: Optional[CurrencyModel] = None
  currency_middle: Optional[CurrencyModel] = None
  rate1: Optional[float] = None
  rate2: Optional[float] = None
  rate3: Optional[float] = None
  net_amount: Optional[float] = None
  metadata: Optional[object] = None

@dataclass
class DepositAddressResponseModel:
  currency: Currencies
  address: str
  expiredAt: datetime

@dataclass
class CurrencyModel:
  _id: str
  type: CurrencyTypes
  code: Currencies
  symbol: str
  label: Optional[str]
  decimal: int
  countryCode: Optional[str]
  countryName: Optional[str]

@dataclass
class BankModel:
  name: str
  title: str
  currency: Currencies
  fpsId: str

@dataclass
class InvoiceStatusModel:
  name: Statuses
  createdAt: datetime
  updatedAt: datetime

@dataclass
class InvoiceAmountModel:
  crypto: float
  fiat: float
  fiat_net: float

@dataclass
class InvoiceMetadataModel:
  invoiceId: Optional[str]
  clientId: Optional[str]
  fiatAmount: Optional[float]

@dataclass
class InvoiceModel:
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
  createdAt: datetime
  updatedAt: datetime
  expiredAt: datetime

@dataclass
class AssetsAccountModel:
  currency: CurrencyModel;
  total: float
  pending: float
  available: float

@dataclass
class AssetsResponseModel:
  assets: List[AssetsAccountModel]

