from PySide6 import QtCore
from typing import Dict, Any, List, Tuple
import json

AUTHMATRIX_SHEBANG = "#!AUTHMATRIX"

class SpecStore(QtCore.QObject):
    specChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.spec: Dict[str, Any] = {
            "base_url": "",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "guest": {"auth": {"type": "none"}}  # Default guest role
            },       # role -> {"auth": {"type": "bearer"/"none", "token": str}}
            "endpoints": [],   # list of {name, path, method, expect: role->{"status": int|[int], "contains": [str], "not_contains": [str]}}
        }
        self._original_postman_data = None  # Store original Postman data for export

    def load_spec_from_content(self, content: str) -> bool:
        """Load spec from JSON content, auto-detecting format"""
        try:
            # Check for shebang
            lines = content.splitlines()
            has_shebang = lines and lines[0].strip() == AUTHMATRIX_SHEBANG
            
            if has_shebang:
                # AuthMatrix format - skip shebang and parse
                json_content = "\n".join(lines[1:])
                self.spec = json.loads(json_content)
                self._original_postman_data = None
            else:
                # Try to parse as JSON
                data = json.loads(content)
                
                # Check if it's a Postman collection
                if self.is_postman_collection(data):
                    self._original_postman_data = data
                    self.spec = self.convert_postman_to_authmatrix(data)
                else:
                    # Assume it's AuthMatrix format without shebang
                    self.spec = data
                    self._original_postman_data = None
            
            # Ensure required fields exist
            self.spec.setdefault("base_url", "")
            self.spec.setdefault("default_headers", {"Accept": "application/json"})
            self.spec.setdefault("roles", {"guest": {"auth": {"type": "none"}}})
            self.spec.setdefault("endpoints", [])
            
            self.specChanged.emit()
            return True
            
        except Exception as e:
            print(f"Error loading spec: {e}")
            return False

    def is_postman_collection(self, data: dict) -> bool:
        """Check if data is a Postman collection"""
        return isinstance(data, dict) and "info" in data and "item" in data

    def convert_postman_to_authmatrix(self, postman_data: dict) -> dict:
        """Convert Postman collection to AuthMatrix format"""
        authmatrix_spec = {
            "base_url": self.extract_base_url_from_postman(postman_data),
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "guest": {"auth": {"type": "none"}}
            },
            "endpoints": []
        }
        
        # Extract auth from collection level if present (for legacy/external Postman imports)
        # This will create a basic admin role if the collection has auth
        if "auth" in postman_data:
            auth_config = postman_data["auth"]
            if auth_config.get("type") == "bearer":
                bearer_info = next((item for item in auth_config.get("bearer", []) if item.get("key") == "token"), None)
                if bearer_info:
                    authmatrix_spec["roles"]["admin"] = {
                        "auth": {"type": "bearer", "token": bearer_info.get("value", "")}
                    }
        
        # Extract endpoints
        authmatrix_spec["endpoints"] = self.extract_requests_from_postman(postman_data)
        
        return authmatrix_spec

    def extract_base_url_from_postman(self, postman_data: dict) -> str:
        """Extract base URL from postman collection"""
        if "item" not in postman_data:
            return ""
        
        # Try to find first request with a URL
        for item in postman_data["item"]:
            if "request" in item and "url" in item["request"]:
                url_info = item["request"]["url"]
                if isinstance(url_info, str):
                    # Simple string URL
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(url_info)
                        return f"{parsed.scheme}://{parsed.netloc}"
                    except:
                        pass
                elif isinstance(url_info, dict) and "host" in url_info:
                    # Object format URL
                    host_parts = url_info.get("host", [])
                    if host_parts:
                        protocol = url_info.get("protocol", "https")
                        port = url_info.get("port", "")
                        host = ".".join(host_parts)
                        if port:
                            return f"{protocol}://{host}:{port}"
                        else:
                            return f"{protocol}://{host}"
            
            # Check nested items
            if "item" in item:
                nested_result = self.extract_base_url_from_postman({"item": item["item"]})
                if nested_result:
                    return nested_result
        
        return ""

    def extract_requests_from_postman(self, postman_data: dict, path_prefix: str = "") -> List[dict]:
        """Extract requests from postman collection recursively"""
        requests = []
        
        for item in postman_data.get("item", []):
            if "request" in item:
                # This is a request item
                request = item["request"]
                method = request.get("method", "GET")
                
                # Extract path from URL
                url_info = request.get("url", {})
                path = "/"
                
                if isinstance(url_info, str):
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(url_info)
                        path = parsed.path or "/"
                    except:
                        path = "/"
                elif isinstance(url_info, dict):
                    path_parts = url_info.get("path", [])
                    if path_parts:
                        path = "/" + "/".join(str(p) for p in path_parts)
                    else:
                        path = "/"
                
                # Use item name or generate from path
                name = item.get("name", f"{method} {path}")
                
                requests.append({
                    "name": name,
                    "method": method,
                    "path": path,
                    "expect": {}  # Will be configured by user later
                })
            
            elif "item" in item:
                # This is a folder with nested items
                folder_name = item.get("name", "")
                nested_prefix = f"{path_prefix}/{folder_name}" if folder_name else path_prefix
                nested_requests = self.extract_requests_from_postman(item, nested_prefix)
                requests.extend(nested_requests)
        
        return requests

    def export_as_authmatrix(self) -> str:
        """Export current spec as AuthMatrix format with shebang"""
        json_content = json.dumps(self.spec, indent=2)
        return f"{AUTHMATRIX_SHEBANG}\n{json_content}"

    def export_as_postman(self) -> str:
        """Export as Postman collection format"""
        if self._original_postman_data:
            # If we have original Postman data, update it with current changes
            return json.dumps(self._update_postman_collection(), indent=2)
        else:
            # Convert from AuthMatrix to Postman format
            return json.dumps(self._convert_authmatrix_to_postman(), indent=2)

    def _update_postman_collection(self) -> dict:
        """Update original Postman collection with current auth and endpoint changes"""
        # Create a copy of the original data
        updated_collection = json.loads(json.dumps(self._original_postman_data))
        
        # Remove any auth configuration - auth is handled by AuthMatrix only
        if "auth" in updated_collection:
            del updated_collection["auth"]
        
        # TODO: Could update endpoints/items here if needed in the future
        # For now, we keep the original structure but remove auth
        
        return updated_collection

    def _convert_authmatrix_to_postman(self) -> dict:
        """Convert current AuthMatrix spec to Postman collection format"""
        postman_collection = {
            "info": {
                "name": "AuthMatrix Export",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Note: We deliberately do NOT include auth in the Postman export
        # Auth handling is purely an AuthMatrix responsibility
        # This keeps the Postman collection clean and importable by both Postman and AuthMatrix
        
        # Convert endpoints to Postman items
        for endpoint in self.spec.get("endpoints", []):
            item = {
                "name": endpoint.get("name", endpoint.get("path", "")),
                "request": {
                    "method": endpoint.get("method", "GET"),
                    "url": {
                        "raw": f"{self.spec.get('base_url', '')}{endpoint.get('path', '')}",
                        "host": self.spec.get('base_url', '').replace('https://', '').replace('http://', '').split('/')[0].split('.'),
                        "path": endpoint.get('path', '/').strip('/').split('/') if endpoint.get('path', '/') != '/' else []
                    },
                    "header": []
                }
            }
            
            # Add default headers (but not auth headers)
            for key, value in self.spec.get("default_headers", {}).items():
                if key.lower() != "authorization":  # Skip auth headers
                    item["request"]["header"].append({
                        "key": key,
                        "value": value
                    })
            
            postman_collection["item"].append(item)
        
        return postman_collection

    def export_as_postman_collections(self) -> Dict[str, str]:
        """
        Export as multiple Postman collections, one per role.
        
        Each collection includes:
        - Role-specific authentication configuration
        - Only endpoints that expect success (2xx status) for that role
        
        Returns:
            Dict mapping role names to JSON collection strings
        """
        collections = {}
        
        for role_name, role_config in self.spec.get("roles", {}).items():
            # Create collection for this role
            collection_name = f"{role_name.capitalize()} Collection"
            postman_collection = {
                "info": {
                    "name": collection_name,
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "item": []
            }
            
            # Add role-specific authentication
            auth_config = role_config.get("auth", {})
            if auth_config.get("type") == "bearer":
                postman_collection["auth"] = {
                    "type": "bearer",
                    "bearer": [
                        {
                            "key": "token",
                            "value": auth_config.get("token", ""),
                            "type": "string"
                        }
                    ]
                }
            # If auth type is "none", we don't add auth field
            
            # Add endpoints that expect success for this role
            for endpoint in self.spec.get("endpoints", []):
                # Check if this endpoint has an expectation for this role
                expectations = endpoint.get("expect", {})
                role_expectation = expectations.get(role_name)
                
                # Include endpoint if:
                # 1. There's an expectation for this role AND
                # 2. The expected status is a success code (2xx)
                if role_expectation:
                    expected_status = role_expectation.get("status")
                    # Handle both single status code and list of status codes
                    if expected_status is not None:
                        status_list = [expected_status] if isinstance(expected_status, int) else expected_status
                        # Include if any expected status is in 2xx range
                        if any(200 <= s < 300 for s in status_list):
                            item = {
                                "name": endpoint.get("name", endpoint.get("path", "")),
                                "request": {
                                    "method": endpoint.get("method", "GET"),
                                    "url": {
                                        "raw": f"{self.spec.get('base_url', '')}{endpoint.get('path', '')}",
                                        "host": self.spec.get('base_url', '').replace('https://', '').replace('http://', '').split('/')[0].split('.'),
                                        "path": endpoint.get('path', '/').strip('/').split('/') if endpoint.get('path', '/') != '/' else []
                                    },
                                    "header": []
                                }
                            }
                            
                            # Add default headers (but not auth headers - auth is at collection level)
                            for key, value in self.spec.get("default_headers", {}).items():
                                if key.lower() != "authorization":
                                    item["request"]["header"].append({
                                        "key": key,
                                        "value": value
                                    })
                            
                            postman_collection["item"].append(item)
            
            # Only add collection if it has at least one endpoint
            if postman_collection["item"]:
                collections[role_name] = json.dumps(postman_collection, indent=2)
        
        return collections

    # project
    def set_base_url(self, url: str):
        self.spec["base_url"] = (url or "").strip()
        self.specChanged.emit()

    def set_header(self, key: str, val: str):
        k = (key or "").strip()
        if not k:
            return
        self.spec["default_headers"][k] = val
        self.specChanged.emit()

    def remove_header(self, key: str):
        self.spec["default_headers"].pop(key, None)
        self.specChanged.emit()

    # endpoints (bulk parse + table edits)
    def parse_endpoints_text(self, text: str) -> List[Tuple[str,str,str]]:
        """
        Accept lines like:
          /users
          GET /users
          POST /login Login
        Returns list of tuples: (name, method, path)
        """
        out: List[Tuple[str,str,str]] = []
        for raw in (text or "").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            method = "GET"
            path = ""
            name = ""

            if len(parts) == 1:
                path = parts[0]
                name = parts[0]
            else:
                # If first token looks like an HTTP verb, treat it as method
                if parts[0].upper() in {"GET","POST","PUT","PATCH","DELETE"}:
                    method = parts[0].upper()
                    path = parts[1] if len(parts) >= 2 else ""
                    name = " ".join(parts[2:]) if len(parts) >= 3 else (path or "")
                else:
                    # No method: first token is path, rest is name
                    path = parts[0]
                    name = " ".join(parts[1:]) if len(parts) >= 2 else parts[0]

            if not path.startswith("/"):
                # be forgiving: add leading slash if omitted
                path = "/" + path
            if not name:
                name = path
            out.append((name, method, path))
        return out

    def set_endpoints(self, rows: List[Tuple[str,str,str]]):
        self.spec["endpoints"] = [
            {"name": n, "method": m, "path": p, "expect": {}} for (n,m,p) in rows
        ]
        self.specChanged.emit()

    def update_endpoint_row(self, index: int, name: str, method: str, path: str):
        if 0 <= index < len(self.spec["endpoints"]):
            self.spec["endpoints"][index].update({"name": name, "method": method, "path": path})
            self.specChanged.emit()

    def add_endpoint(self, name: str, method: str, path: str):
        """Add a new endpoint to the list."""
        endpoint = {"name": name, "method": method, "path": path, "expect": {}}
        self.spec["endpoints"].append(endpoint)
        self.specChanged.emit()

    def delete_endpoint(self, index: int):
        """Delete an endpoint by index."""
        if 0 <= index < len(self.spec["endpoints"]):
            del self.spec["endpoints"][index]
            self.specChanged.emit()

    # roles/tokens
    def add_role(self, role: str, auth_type: str, token: str):
        rid = (role or "").strip()
        if not rid:
            return False, "Role/Name is required"

        # role auth
        auth = {}
        if "bearer" in (auth_type or "").lower():
            auth = {"type": "bearer", "token": token}
        else:
            auth = {"type": "none"}

        # upsert role auth
        self.spec["roles"][rid] = {"auth": auth}

        self.specChanged.emit()
        return True, None

    def remove_role(self, rid: str):
        if rid in self.spec["roles"]:
            del self.spec["roles"][rid]
            for ep in self.spec["endpoints"]:
                if "expect" in ep and rid in ep["expect"]:
                    del ep["expect"][rid]
            self.specChanged.emit()

    # endpoint expectations
    def set_endpoint_expectation(self, endpoint_index: int, role: str, status: Any = None, contains: List[str] = None, not_contains: List[str] = None):
        """Set expectation for a specific role on a specific endpoint."""
        if not (0 <= endpoint_index < len(self.spec["endpoints"])):
            return False, "Invalid endpoint index"
        
        if role not in self.spec["roles"]:
            return False, f"Role '{role}' does not exist"
        
        ep = self.spec["endpoints"][endpoint_index]
        ep.setdefault("expect", {})
        ep["expect"][role] = {}
        
        if status is not None:
            ep["expect"][role]["status"] = status
        if contains:
            ep["expect"][role]["contains"] = contains
        if not_contains:
            ep["expect"][role]["not_contains"] = not_contains
            
        self.specChanged.emit()
        return True, None

    def remove_endpoint_expectation(self, endpoint_index: int, role: str):
        """Remove expectation for a specific role on a specific endpoint."""
        if not (0 <= endpoint_index < len(self.spec["endpoints"])):
            return False, "Invalid endpoint index"
        
        ep = self.spec["endpoints"][endpoint_index]
        if "expect" in ep and role in ep["expect"]:
            del ep["expect"][role]
            
        self.specChanged.emit()
        return True, None