def find_odd_quotes(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            # Count unescaped quotes
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
                print(f"Line {i+1}: {line.strip()}")

find_odd_quotes('app/data/raw/shl_catalog.json')
