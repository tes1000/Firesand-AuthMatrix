import json, sys, time, requests
from UI import start_ui

AUTHMATRIX_SHEBANG = "#!AUTHMATRIX"

def detect_file_type(file_path):
    """Detect if file is authmatrix format (has shebang) or postman format"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            return "authmatrix" if first_line == AUTHMATRIX_SHEBANG else "postman"
    except Exception:
        return "unknown"

def load_and_convert_spec(file_path):
    """Load spec and convert from postman to authmatrix format if needed"""
    file_type = detect_file_type(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if file_type == "authmatrix":
        # Skip the shebang line and parse JSON
        lines = content.splitlines()
        json_content = "\n".join(lines[1:]) if lines[0].strip() == AUTHMATRIX_SHEBANG else content
        return json.loads(json_content)
    elif file_type == "postman":
        # Convert postman collection to authmatrix format
        postman_data = json.loads(content)
        return convert_postman_to_authmatrix(postman_data)
    else:
        # Try to parse as JSON and guess format
        data = json.loads(content)
        if "info" in data and "item" in data:
            return convert_postman_to_authmatrix(data)
        else:
            return data

def convert_postman_to_authmatrix(postman_data):
    """Convert a Postman collection to AuthMatrix format"""
    authmatrix_spec = {
        "base_url": extract_base_url_from_postman(postman_data),
        "default_headers": {"Accept": "application/json"},
        "roles": {
            "guest": {"auth": {"type": "none"}}
        },
        "endpoints": []
    }
    
    # Extract auth from collection level
    if "auth" in postman_data:
        auth_config = postman_data["auth"]
        if auth_config.get("type") == "bearer":
            bearer_info = next((item for item in auth_config.get("bearer", []) if item.get("key") == "token"), None)
            if bearer_info:
                authmatrix_spec["roles"]["admin"] = {
                    "auth": {"type": "bearer", "token": bearer_info.get("value", "")}
                }
    
    # Extract endpoints
    authmatrix_spec["endpoints"] = extract_requests_from_postman(postman_data)
    
    return authmatrix_spec

def extract_base_url_from_postman(postman_data):
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
            nested_result = extract_base_url_from_postman({"item": item["item"]})
            if nested_result:
                return nested_result
    
    return ""

def extract_requests_from_postman(postman_data, path_prefix=""):
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
            nested_requests = extract_requests_from_postman(item, nested_prefix)
            requests.extend(nested_requests)
    
    return requests

def run_spec(spec):
    results = {}
    for ep in spec["endpoints"]:
        name = ep.get("name") or ep["path"]
        results[name] = {}
        for role, roleSpec in spec["roles"].items():
            expect = ep.get("expect", {}).get(role)
            if not expect:
                results[name][role] = {"status": "SKIP"}
                continue

            # Build request
            url = spec["base_url"].rstrip("/") + ep["path"]
            headers = dict(spec.get("default_headers", {}))
            auth = roleSpec.get("auth", {})
            if auth.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {auth.get('token')}"

            # Run request
            start = time.time()
            try:
                r = requests.request(ep.get("method", "GET"), url, headers=headers)
                latency = int((time.time() - start) * 1000)
            except Exception as e:
                results[name][role] = {"status": "FAIL", "error": str(e)}
                continue

            # Check
            allowed = expect.get("status")
            if isinstance(allowed, list):
                ok = r.status_code in allowed
            else:
                ok = r.status_code == allowed

            if not ok:
                results[name][role] = {"status": "FAIL", "http": r.status_code}
            else:
                results[name][role] = {"status": "PASS", "http": r.status_code, "latency_ms": latency}
    return results

def print_matrix(results):
    # preserve role order from first endpoint
    roles = list(next(iter(results.values())).keys())

    # calculate widths
    ep_width = max(20, max(len(ep) for ep in results.keys()))
    col_width = 8  # fixed width per role cell

    # header
    header = "Endpoint".ljust(ep_width) + " " + " ".join(r.ljust(col_width) for r in roles)
    print(header)
    print("-" * len(header))

    # rows
    for ep, rmap in results.items():
        row = ep.ljust(ep_width)
        for r in roles:
            res = rmap[r]
            st = res["status"]
            http = str(res.get("http", ""))
            badge = "✅ " if st == "PASS" else ("⏭️ " if st == "SKIP" else "❌ ")
            cell = f"{badge}{http}".ljust(col_width)
            row += " " + cell
        print(row)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        start_ui(runner=run_spec)
    else:
        spec = load_and_convert_spec(sys.argv[1])
        results = run_spec(spec)
        print_matrix(results)