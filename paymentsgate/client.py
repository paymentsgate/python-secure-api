from __future__ import annotations
import logging
# from dataclasses import dataclass, is_dataclass, field, asdict
import json
from urllib.parse import urlencode
from pydantic import Field, BaseModel

from .types import TokenResponse
from .tokens import (
  AccessToken,
  RefreshToken
)
from .exceptions import (
    APIResponseError, 
    APIAuthenticationError
)
from .models import (
    Credentials, 
    GetQuoteModel, 
    GetQuoteResponseModel, 
    PayInModel, 
    PayInResponseModel, 
    PayOutModel, 
    PayOutResponseModel,
    InvoiceModel,
    GetQuoteTlv,
    PayOutTlvRequest,
    QuoteTlvResponse,
)
from .enums import ApiPaths
from .transport import (
  Request,
  Response
)
from .logger import Logger
from .cache import (
  AbstractCache, 
  DefaultCache
)

import requests


class ApiClient:
    def __init__(self, config: Credentials, baseUrl: str, debug: bool=False):
        self.config = config
        self.cache = DefaultCache()
        self.baseUrl = baseUrl
        
        self.REQUEST_DEBUG = False
        self.RESPONSE_DEBUG = False
        self.timeout = 180

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def PayIn(self, request: PayInModel) -> PayInResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payin,
            content_type='application/json',
            noAuth=False,
            body=request,
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if (response.success):
            return response.cast(PayInResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)
        
    def PayOut(self, request: PayOutModel) -> PayOutResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout,
            content_type='application/json',
            noAuth=False,
            signature=True,
            body=request
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if (response.success):
            return response.cast(PayOutResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)

    def PayOutTlv(self, request: PayOutTlvRequest) -> PayOutResponseModel:
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout_tlv,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=request
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(PayOutResponseModel, APIResponseError)

    def Quote(self, params: GetQuoteModel) -> GetQuoteResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.fx_quote,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=params
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(GetQuoteResponseModel, APIResponseError)
    
    def QuoteQr(self, params: GetQuoteTlv) -> QuoteTlvResponse:
        request = Request(
            method="post",
            path=ApiPaths.fx_quote_tlv,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=params
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(QuoteTlvResponse, APIResponseError)

    def Status(self, id: str) -> InvoiceModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.invoices_info.replace(':id', id),
            content_type='application/json',
            noAuth=False,
            signature=False,
        )

        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(InvoiceModel, APIResponseError)

    @property
    def token(self) -> AccessToken | None:
        # First check if valid token is cached
        token = self.cache.get_token('AccessToken')
        refresh = self.cache.get_token('RefreshToken')

        if token is not None and not token.is_expired:
            return token
        else:
            # try to refresh token
            if refresh is not None and not refresh.is_expired:
                refreshed = self._refresh_token(token, refresh)

                if (refreshed.success):
                    access = AccessToken(
                        refreshed.json_body["access_token"]
                    )
                    refresh = RefreshToken(
                        refreshed.json_body["refresh_token"],
                        int(refreshed.json_body["expires_in"]),
                    )

                    self.cache.set_token(access)
                    self.cache.set_token(refresh)

                    return access

            # try to issue token            
            response = self._get_token()
            if response.success:
                
                access = AccessToken(
                    response.json_body["access_token"]
                )
                refresh = RefreshToken(
                    response.json_body["refresh_token"],
                    int(response.json_body["expires_in"]),
                )

                self.cache.set_token(access)
                self.cache.set_token(refresh)

                return access
            else:
                raise APIAuthenticationError(response)

    def _send_request(self, request: Request) -> Response:
        """
        Send a specified Request to the GoPay REST API and process the response
        """
        # body = asdict(request.body) if is_dataclass(request.body) else request.body
        body = request.body
        # Add Bearer authentication to headers if needed
        headers = request.headers or {}
        if not request.noAuth:
            auth = self.token
            if auth is not None:
                headers["Authorization"] = f"Bearer {auth.token}"

        if (request.method == 'get'):
            params = urlencode(body)
            try:
                r = requests.request(
                    method=request.method,
                    url=f"{self.baseUrl}{request.path}?{params}",
                    headers=headers,
                    timeout=self.timeout
                )
            except:
                print('Error')
                pass
        else:
            try:
                r = requests.request(
                    method=request.method,
                    url=f"{self.baseUrl}{request.path}",
                    headers=headers,
                    json=body,
                    timeout=self.timeout
                )
            except KeyError:
                print('Error')
                pass

        # if r == None:

        # Build Response instance, try to decode body as JSON
        response = Response(raw_body=r.content, json_body={}, status_code=r.status_code)

        if (self.REQUEST_DEBUG):
            print(f"{request.method} => {self.baseUrl}{request.path} => {response.status_code}")
        
        try:
            response.json_body = r.json()
        except json.JSONDecodeError:
            pass

        self.log(request, response)
        return response

    def log(self, request: Request, response: Response):
        Logger(self, request, response)

    def _get_token(self) -> Response:
        # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_issue,
            content_type='application/json',
            noAuth=True,
            body={"account_id": self.config.account_id, "public_key": self.config.public_key},
        )
        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        return response
    
    def _refresh_token(self, access: AccessToken, refresh: RefreshToken) -> Response:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_refresh,
            content_type='application/json',
            noAuth=True,
            headers={"Authorization": f"Bearer {access.token}" },
            body={"refresh_token": refresh.token},
        )
        # Handle response
        response = self._send_request(request)
        self.log(request, response)
        return response
    
    def loadToken(self, params: TokenResponse):
        access = AccessToken(params.access_token)
        refresh = RefreshToken(params.refresh_token, int(params.expires_in))
        self.cache.set_token(access)
        self.cache.set_token(refresh)

