from __future__ import annotations
import logging
from dataclasses import dataclass, is_dataclass, field, asdict
import json
from urllib.parse import urlencode

from paymentsgate.tokens import (
  AccessToken,
  RefreshToken
)
from paymentsgate.exceptions import (
    APIResponseError, 
    APIAuthenticationError
)
from paymentsgate.models import (
    Credentials, 
    GetQuoteModel, 
    GetQuoteResponseModel, 
    PayInModel, 
    PayInResponseModel, 
    PayOutModel, 
    PayOutResponseModel,
    InvoiceModel
)
from paymentsgate.enums import ApiPaths
from paymentsgate.transport import (
  Request,
  Response
)
from paymentsgate.logger import Logger
from paymentsgate.cache import (
  AbstractCache, 
  DefaultCache
)

import requests

@dataclass
class ApiClient:
    baseUrl: str = field(default="", init=False)
    timeout: int = field(default=180, init=True)
    logger: Logger = Logger
    cache: AbstractCache = field(default_factory=DefaultCache)
    config: Credentials = field(default_factory=dict, init=False)

    REQUEST_DEBUG: bool = False
    RESPONSE_DEBUG: bool = False

    def __init__(self, config: Credentials, baseUrl: str, debug: bool=False):
        self.config = config
        self.cache = DefaultCache()
        self.baseUrl = baseUrl
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
        self.logger(request, response)
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
        self.logger(request, response)
        if (response.success):
            return response.cast(PayOutResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)

    def Quote(self, params: GetQuoteModel) -> GetQuoteResponseModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.fx_quote,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=params
        )

        # Handle response
        response = self._send_request(request)
        self.logger(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(GetQuoteResponseModel, APIResponseError)
    
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
        self.logger(request, response)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(InvoiceModel, APIResponseError)

    @property
    def token(self) -> AccessToken | None:
        # First check if valid token is cached
        token = self.cache.get_token('access')
        refresh = self.cache.get_token('refresh')
        if token is not None and not token.is_expired:
            return token
        else:
            # try to refresh token
            if refresh is not None and not refresh.is_expired:
                refreshed = self._refresh_token()

                if (refreshed.success):
                    access = AccessToken(
                        response.json["access_token"]
                    )
                    refresh = RefreshToken(
                        response.json["refresh_token"],
                        int(response.json["expires_in"]),
                    )
                    self.cache.set_token(access)
                    self.cache.set_token(refresh)

                    return access

            # try to issue token            
            response = self._get_token()
            if response.success:
                
                access = AccessToken(
                    response.json["access_token"]
                )
                refresh = RefreshToken(
                    response.json["refresh_token"],
                    int(response.json["expires_in"]),
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
        body = asdict(request.body) if is_dataclass(request.body) else request.body
        # Add Bearer authentication to headers if needed
        headers = request.headers or {}
        if not request.noAuth:
            auth = self.token
            if auth is not None:
                headers["Authorization"] = f"Bearer {auth.token}"

        if (request.method == 'get'):
            params = urlencode(body)
            r = requests.request(
                method=request.method,
                url=f"{self.baseUrl}{request.path}?{params}",
                headers=headers,
                timeout=self.timeout
            )
        else:
            r = requests.request(
                method=request.method,
                url=f"{self.baseUrl}{request.path}",
                headers=headers,
                json=body,
                timeout=self.timeout
            )

        # Build Response instance, try to decode body as JSON
        response = Response(raw_body=r.content, json={}, status_code=r.status_code)

        if (self.REQUEST_DEBUG):
            print(f"{request.method} => {self.baseUrl}{request.path} => {response.status_code}")
        
        try:
            response.json = r.json()
        except json.JSONDecodeError:
            pass

        self.logger(request, response)
        return response

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
        self.logger(request, response)
        return response
    
    def _refresh_token(self) -> Response:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_refresh,
            content_type='application/json',
            body={"refresh_token": self.refreshToken},
        )
        # Handle response
        response = self._send_request(request)
        self.logger(request, response)
        return response
