#!/usr/bin/env python3
"""
Split the demoapi.json collection into 3 role-based collections:
- admin.postman_collection.json: All endpoints with admin auth
- user.postman_collection.json: Regular + login endpoints with user auth  
- guest.postman_collection.json: Only login endpoints with no auth
"""

import json
import copy

def main():
    # Read the original demoapi.json file
    with open('demoapi.json', 'r', encoding='utf-8') as f:
        demo_collection = json.load(f)

    print(f"Original collection has {len(demo_collection['item'])} top-level items")

    # Count items in the first item array (where all endpoints are)
    main_items = demo_collection['item'][0]['item'] if demo_collection['item'] else []
    print(f"Found {len(main_items)} endpoints in the collection")

    # Categorize endpoints
    internal_endpoints = []
    login_endpoints = []
    regular_endpoints = []

    for i, item in enumerate(main_items):
        if 'request' in item and 'url' in item['request']:
            raw_url = item['request']['url'].get('raw', '')
            path_parts = item['request']['url'].get('path', [])
            
            # Check headers for referer with internal
            referer_has_internal = False
            if 'header' in item['request']:
                for header in item['request']['header']:
                    if header.get('key', '').lower() == 'referer':
                        referer_value = header.get('value', '')
                        if 'internal' in referer_value.lower():
                            referer_has_internal = True
                            break
            
            # Check if it's an internal endpoint
            has_internal_in_url = '/internal/' in raw_url or 'internal' in raw_url.lower()
            has_internal_in_path = any('internal' in str(part).lower() for part in path_parts)
            
            if has_internal_in_url or has_internal_in_path or referer_has_internal:
                internal_endpoints.append(item)
                print(f"Found internal endpoint {i}: {item.get('name', 'No name')}")
                if referer_has_internal:
                    print(f"  (detected via referer header)")
            # Check if it's a login endpoint  
            elif '/login' in raw_url or any('login' in str(part).lower() for part in path_parts):
                login_endpoints.append(item)
            else:
                regular_endpoints.append(item)

    print(f"\nCategorization results:")
    print(f"Internal endpoints: {len(internal_endpoints)}")
    print(f"Login endpoints: {len(login_endpoints)}")
    print(f"Regular endpoints: {len(regular_endpoints)}")
    print(f"Total: {len(internal_endpoints) + len(login_endpoints) + len(regular_endpoints)}")

    # Create base collection structure for each role
    def create_base_collection(name, auth_config=None):
        collection = copy.deepcopy(demo_collection)
        collection['info']['name'] = name
        if auth_config:
            collection['auth'] = auth_config
        else:
            # Remove auth entirely for guest
            if 'auth' in collection:
                del collection['auth']
        return collection

    # Admin collection - all endpoints with admin bearer token
    admin_collection = create_base_collection("Admin Collection", {
        "type": "bearer",
        "bearer": [
            {
                "key": "token",
                "value": "admin_bearer_token_here",
                "type": "string"
            }
        ]
    })

    # User collection - exclude internal endpoints, with user bearer token  
    user_collection = create_base_collection("User Collection", {
        "type": "bearer", 
        "bearer": [
            {
                "key": "token",
                "value": "user_bearer_token_here",
                "type": "string"
            }
        ]
    })

    # Guest collection - only login and public endpoints, no auth
    guest_collection = create_base_collection("Guest Collection")

    # Set the items for each collection
    admin_collection['item'][0]['item'] = main_items  # All endpoints
    user_collection['item'][0]['item'] = regular_endpoints + login_endpoints  # No internal
    guest_collection['item'][0]['item'] = login_endpoints  # Only login endpoints

    print(f"\nFinal collection sizes:")
    print(f"Admin collection: {len(admin_collection['item'][0]['item'])} endpoints")
    print(f"User collection: {len(user_collection['item'][0]['item'])} endpoints") 
    print(f"Guest collection: {len(guest_collection['item'][0]['item'])} endpoints")

    # Write the collections to files
    collections = [
        (admin_collection, 'admin.postman_collection.json'),
        (user_collection, 'user.postman_collection.json'),
        (guest_collection, 'guest.postman_collection.json')
    ]

    for collection, filename in collections:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        print(f"Created {filename}")

    print("\nCollection splitting complete! You now have 3 separate Postman collections:")
    print("- admin.postman_collection.json: All endpoints with admin auth")
    print("- user.postman_collection.json: Regular + login endpoints with user auth")
    print("- guest.postman_collection.json: Only login endpoints with no auth")

if __name__ == "__main__":
    main()