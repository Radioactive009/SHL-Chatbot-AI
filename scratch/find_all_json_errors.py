import json

def find_all_json_errors(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    content = "".join(lines)
    
    try:
        json.loads(content)
        print("No errors found.")
    except json.JSONDecodeError as e:
        print(f"First error: line {e.lineno}, col {e.colno}: {e.msg}")
        print(f"Context: {lines[e.lineno-1].strip()}")

    # Check for unescaped newlines in strings manually
    in_string = False
    for i, line in enumerate(lines):
        line_no = i + 1
        # Simple check for odd number of unescaped quotes
        quotes = 0
        escaped = False
        for char in line:
            if char == '\\':
                escaped = not escaped
            elif char == '"' and not escaped:
                quotes += 1
                escaped = False
            else:
                escaped = False
        
        if quotes % 2 != 0:
            print(f"Line {line_no} has an unclosed string (odd number of quotes: {quotes})")

find_all_json_errors('app/data/raw/shl_catalog.json')
