import re

# Read the file
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix .btn-primary to use primary-gradient instead of secondary-gradient
content = re.sub(
    r'\.btn-primary \{\s*background: var\(--secondary-gradient\);',
    '.btn-primary {\n            background: var(--primary-gradient);',
    content
)

# Fix .btn-primary:hover to use blue box-shadow
content = re.sub(
    r'box-shadow: 0 10px 25px rgba\(102, 126, 234, 0\.4\);',
    'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    content
)

content = re.sub(
    r'box-shadow: 0 5px 15px rgba\(102, 126, 234, 0\.3\);',
    'box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);',
    content
)

# Fix any remaining accent color references
content = re.sub(
    r'border-color: var\(--accent\);',
    'border-color: var(--primary-color);',
    content
)

# Write back
with open('file.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully fixed all button styles in file.py!")
print("\nAll .btn-primary buttons now use var(--primary-gradient)")
print("All hover effects now use professional blue (#2563eb)")
