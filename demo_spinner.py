#!/usr/bin/env python3
"""
Demo script to show spinner functionality in Results view.

This script demonstrates the spinner widget in action without requiring
a full GUI environment. It simulates the test flow and prints what would
be displayed.
"""

import time
from typing import Dict, Any


def simulate_pending_results(endpoints: list, roles: list) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Simulate initial pending state for all endpoint/role combinations"""
    results = {}
    for endpoint in endpoints:
        results[endpoint] = {}
        for role in roles:
            results[endpoint][role] = {"status": "⏳"}  # Pending with hourglass
    return results


def simulate_result_update(results: Dict, endpoint: str, role: str, status: str, http: int = None, latency: int = None):
    """Simulate updating a single result"""
    result = {"status": status}
    if http:
        result["http"] = http
    if latency:
        result["latency_ms"] = latency
    results[endpoint][role] = result
    return result


def format_result(result: Dict[str, Any]) -> str:
    """Format a result for display (mimics the UI display logic)"""
    st = result.get("status", "")
    
    if st == "⏳":
        return "🔄 [SPINNER]"  # would be animated spinner in UI
    
    http = result.get("http", "")
    badge = "✅" if st == "PASS" else ("⏭️" if st == "SKIP" else "❌")
    text = f"{badge} {http}" if http else badge
    lat = result.get("latency_ms")
    if isinstance(lat, int):
        text += f"  {lat}ms"
    
    return text


def print_results_table(results: Dict[str, Dict[str, Dict[str, Any]]]):
    """Print results in a table format"""
    if not results:
        print("No results to display")
        return
    
    # Get roles from first endpoint
    first_endpoint = next(iter(results.values()))
    roles = list(first_endpoint.keys())
    
    # Print header
    print("\n" + "="*80)
    header = f"{'Endpoint':<30}"
    for role in roles:
        header += f" | {role:^15}"
    print(header)
    print("-"*80)
    
    # Print rows
    for endpoint_name, role_results in results.items():
        row = f"{endpoint_name:<30}"
        for role in roles:
            result = role_results.get(role, {})
            formatted = format_result(result)
            row += f" | {formatted:^15}"
        print(row)
    
    print("="*80 + "\n")


def main():
    """Run the spinner demo"""
    print("Auth Matrix - Spinner Widget Demo")
    print("="*80)
    
    # Setup test data
    endpoints = [
        "GET /api/users",
        "GET /api/admin",
        "POST /api/users",
        "DELETE /api/admin/users"
    ]
    
    roles = ["guest", "user", "admin"]
    
    # Step 1: Initialize with all pending (spinners)
    print("\n1. Initial state - All endpoints pending (spinners shown)")
    results = simulate_pending_results(endpoints, roles)
    print_results_table(results)
    print("   In the actual UI, you would see animated spinners (🔄) for each cell")
    
    time.sleep(1)
    
    # Step 2: Simulate some results coming in
    print("\n2. First results arriving - Spinners replaced with actual results")
    simulate_result_update(results, "GET /api/users", "guest", "PASS", 200, 45)
    simulate_result_update(results, "GET /api/users", "user", "PASS", 200, 42)
    print_results_table(results)
    
    time.sleep(1)
    
    # Step 3: More results
    print("\n3. More results arriving - Spinners gradually replaced")
    simulate_result_update(results, "GET /api/users", "admin", "PASS", 200, 38)
    simulate_result_update(results, "GET /api/admin", "guest", "FAIL", 403)
    simulate_result_update(results, "GET /api/admin", "user", "FAIL", 403)
    print_results_table(results)
    
    time.sleep(1)
    
    # Step 4: All results complete
    print("\n4. All results completed - No spinners remaining")
    simulate_result_update(results, "GET /api/admin", "admin", "PASS", 200, 51)
    simulate_result_update(results, "POST /api/users", "guest", "FAIL", 401)
    simulate_result_update(results, "POST /api/users", "user", "PASS", 201, 120)
    simulate_result_update(results, "POST /api/users", "admin", "PASS", 201, 98)
    simulate_result_update(results, "DELETE /api/admin/users", "guest", "FAIL", 403)
    simulate_result_update(results, "DELETE /api/admin/users", "user", "FAIL", 403)
    simulate_result_update(results, "DELETE /api/admin/users", "admin", "PASS", 204, 75)
    print_results_table(results)
    
    print("\n" + "="*80)
    print("Demo complete!")
    print("\nKey features demonstrated:")
    print("  ✓ Spinners shown for pending endpoint/role combinations")
    print("  ✓ Spinners replaced with actual results as they arrive")
    print("  ✓ Each endpoint/role tested independently")
    print("  ✓ Results include HTTP status codes and latency")
    print("="*80)


if __name__ == "__main__":
    main()
