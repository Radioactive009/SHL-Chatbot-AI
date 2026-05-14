import json

def find_json_errors(filepath):
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to load and find the first error
    try:
        json.loads(content)
        print("No errors found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error at line {e.lineno}, col {e.colno}: {e.msg}")
        # We can try to fix it in memory or just report it.
        # But wait, if there's a newline in a string, we can try to find it.
        pass

    # Better approach: find all literal newlines in strings
    in_string = False
    for i, char in enumerate(content):
        if char == '"' and (i == 0 or content[i-1] != '\\'):
            in_string = not in_string
        if char == '\n' and in_string:
            # Find line number
            line_no = content.count('\n', 0, i) + 1
            print(f"Literal newline inside string at line {line_no}")

find_json_errors('app/data/raw/shl_catalog.json')
