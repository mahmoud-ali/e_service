import os
import logging
import requests
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EsaliAPIError(Exception):
    """Custom exception for Esali API errors."""
    ERROR_CODES = {
        "00": "Success",
        "01": "Invoice No Data found OR Unpaid",
        "02": "Authentication Error In Key",
        "03": "Authentication Error In username and password",
        "04": "Phone Number Was Not Set",
        "06": "Internal Error",
        "08": "Bad Request from key"
    }

    def __init__(self, code: str, description: str = ""):
        self.code = code
        self.description = description or self.ERROR_CODES.get(code, "Unknown Error")
        super().__init__(f"Error {self.code}: {self.description}")


class EsaliAPI:
    """
    Python client for the Republic of Sudan Electronic Payment and Collection System (Esali).
    """

    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the Esali API client.

        Args:
            base_url: The root URL of the Esali API service. Defaults to ESALI_BASE_URL env var.
            username: API Username. Defaults to ESALI_USERNAME env var.
            password: API Password. Defaults to ESALI_PASSWORD env var.
            api_key: The security Key provided by the Electronic Certification Authority.
                     Defaults to ESALI_API_KEY env var.
            timeout: Request timeout in seconds (default: 30).

        Raises:
            ValueError: If any required parameter is missing.
        """
        self.base_url = (base_url or os.getenv("ESALI_BASE_URL", "https://192.168.99.10:5050/")).rstrip('/')
        self.username = username or os.getenv("ESALI_USERNAME")
        self.password = password or os.getenv("ESALI_PASSWORD")
        self.key = api_key or os.getenv("ESALI_API_KEY")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = True

        # Validate required credentials
        missing = []
        if not self.username:
            missing.append("ESALI_USERNAME")
        if not self.password:
            missing.append("ESALI_PASSWORD")
        if not self.key:
            missing.append("ESALI_API_KEY")
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

        logger.info(f"EsaliAPI client initialized for user '{self.username}'")

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to handle POST requests and basic response validation."""
        url = f"{self.base_url}/{endpoint}"
        # logger.info(f"POST {url} with data: {data}")

        try:
            response = self.session.post(url, json=data, timeout=self.timeout, verify=False)
            # print(response.text)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out after {self.timeout}s")
            raise EsaliAPIError("06", f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise EsaliAPIError("06", f"Network error: {str(e)}")

        try:
            result = response.json()
            # logger.info(result)

        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            # logger.error(response.text)
            
            raise EsaliAPIError("06", f"Invalid JSON response: {str(e)}")

        # Some endpoints return a JSON string (e.g. a 2-digit error code or bare invoice id).
        if isinstance(result, str):
            s = result.strip()
            if len(s) == 2 and s.isdigit():
                if s == "00":
                    result = {
                        "Response_Code": "00",
                        "Response_Description": EsaliAPIError.ERROR_CODES.get("00", "Success"),
                    }
                else:
                    desc = EsaliAPIError.ERROR_CODES.get(s, "")
                    raise EsaliAPIError(s, desc)
            else:
                result = {
                    "Response_Code": "00",
                    "Response_Description": EsaliAPIError.ERROR_CODES.get("00", "Success"),
                    "InvoiceNo": s,
                }

        # Note: Docs show variations in key casing (Response_Code vs Response Code)
        # This helper normalizes the check for error codes

        # Check if result is a list or dict
        resp_code = None
        if isinstance(result, list):
            if len(result) > 0 and isinstance(result[0], dict):
                resp_code = result[0].get("Response_Code") or result[0].get("Response Code")
                if resp_code and resp_code != "00":
                    description = result[0].get("Response_Description") or result[0].get("Response Description")
                    logger.warning(f"API returned error code {resp_code}: {description}")
                    raise EsaliAPIError(resp_code, description)
                
        elif isinstance(result, dict):
            resp_code = result.get("Response_Code") or result.get("Response Code")
            if resp_code and resp_code != "00":
                description = result.get("Response_Description") or result.get("Response Description")
                logger.warning(f"API returned error code {resp_code}: {description}")
                raise EsaliAPIError(resp_code, description)
            
        else:
            logger.error(f"Unexpected response type: {type(result)}")
            raise EsaliAPIError("06", f"Unexpected response type: {type(result)}")

        return result
    def login_user(self) -> str:
        """
        1. APILoginUser: Authenticates credentials and returns the CenterId.
        """
        payload = {
            "UserName": self.username,
            "Password": self.password,
            "Key": self.key
        }
        response = self._post("APILoginUser", payload)
        
        return response

    def get_services(self, center_id: str) -> List[Dict[str, str]]:
        """
        2. GetServices: Retrieves service units associated with a specific CenterId.
        """
        payload = {
            "CenterId": center_id,
            "key": self.key
        }
        # Assuming the API might return a single object or a list based on docs
        return self._post("GetServices", payload)

    def get_services_detail(self, center_id: str, service_id: str, payment_method_id: str) -> Dict[str, Any]:
        """
        3. GetServicesDetail: Retrieves specific details (e.g., amount) for a service.
        """
        payload = {
            "CenterId": center_id,
            "serviceId": service_id,
            "Paymentmethodid": payment_method_id,
            "Key": self.key
        }
        return self._post("GetServicesDetail", payload)

    def get_invoice(self, service_id: str, customer_name: str, phone: str) -> Dict[str, str]:
        """
        4. GetInvoice: Generates an invoice for a single service.
        
        Args:
            phone: Must be exactly 10 digits.
        """
        if len(phone) != 10:
            raise ValueError("Phone number must be exactly 10 digits.")

        payload = {
            "UserName": self.username,
            "Password": self.password,
            "ServiceId": service_id,
            "CustomerName": customer_name,
            "Phone": phone,
            "Key": self.key
        }
        return self._post("GetInvoice", payload)

    def get_invoice_more_services(self, 
                                  services: List[Dict[int, float]], 
                                  customer_name: str, 
                                  center_id: str, 
                                  payment_method_id: str, 
                                  phone: str, 
                                  total_amount: float,
                                  note: str = "") -> Dict[str, Any]:
        """
        5. GetInvoiceMoreServices: Generates an invoice containing multiple services.
        
        Args:
            services: List of dicts like [{"ServiceId": "001", "Amount": "100.00"}, ...]
        """
        payload = {
            "userName": self.username,
            "password": self.password,
            "ServiceId": services,
            "customername": customer_name,
            "CENTERID": center_id,
            "PaymentMethodId": payment_method_id,
            "Phone": phone,
            "Note": note,
            "ServicesTotalAmount": total_amount,
            "key": self.key
        }
        response = self._post("GetInvoiceMoreServices", payload)
        return response

    def get_receipt(self, invoice_number: str) -> Dict[str, Any]:
        """
        6. GetReceipt: Returns receipt numbers for paid invoices.
        """
        payload = {
            "Username": self.username,
            "Password": self.password,
            "InvoiceNumber": invoice_number,
            "Key": self.key
        }
        return self._post("GetReceipt", payload)

    def verify_receipt(self, receipt_no: str) -> Dict[str, Any]:
        """
        7. VerifyReceipt: Verifies the validity of a receipt number.
        """
        payload = {
            "Username": self.username,
            "Password": self.password,
            "Receiptno": receipt_no,
            "Key": self.key
        }
        return self._post("VerifyReceipt", payload)
