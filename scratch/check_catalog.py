import json
from collections import Counter

def check_catalog(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # We can't use json.load if it's broken, so let's fix it in memory first
            content = f.read()
            # Replace the known bad newline
            content_fixed = content.replace('"name": "Microsoft \n    365 (New)"', '"name": "Microsoft 365 (New)"')
            data = json.loads(content_fixed)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    print(f"Total entries: {len(data)}")

    # Check for duplicate entity_ids
    ids = [item.get('entity_id') for item in data]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        print(f"Duplicate entity_ids: {duplicates}")
    else:
        print("No duplicate entity_ids found.")

    # Check for missing fields
    required_fields = ['entity_id', 'name', 'link', 'description', 'keys']
    for i, item in enumerate(data):
        missing = [f for f in required_fields if f not in item]
        if missing:
            print(f"Entry {i} (id: {item.get('entity_id')}) is missing fields: {missing}")

    # Check for specific formatting issues
    for i, item in enumerate(data):
        if item.get('status') != 'ok':
            print(f"Entry {i} (id: {item.get('entity_id')}) has status: {item.get('status')}")

check_catalog('app/data/raw/shl_catalog.json')
