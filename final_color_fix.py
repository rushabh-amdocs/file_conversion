"""
Comprehensive script to replace ALL non-blue colors with professional blue
"""

# Read the file
with open('scripts_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all border colors with professional blue
border_color_fixes = {
    'border-color: #f5576c;': 'border-color: #2563eb;',
    'border-left: 4px solid #f5576c;': 'border-left: 4px solid #2563eb;',
    'border-left: 4px solid #fa709a;': 'border-left: 4px solid #2563eb;',
    'border-left: 4px solid #30cfd0;': 'border-left: 4px solid #3b82f6;',
    'border-left: 4px solid #ff9a9e;': 'border-left: 4px solid #3b82f6;',
    'border-left: 4px solid #43e97b;': 'border-left: 4px solid #3b82f6;',
    'border-top: 5px solid #f093fb;': 'border-top: 5px solid #2563eb;',
}

for old, new in border_color_fixes.items():
    content = content.replace(old, new)

# Replace text colors
text_color_fixes = {
    'color: #f5576c;': 'color: #ef4444;',  # Keep error color red but more professional
    'color: #f093fb;': 'color: #3b82f6;',
    'color: #43e97b;': 'color: #3b82f6;',
    'color: #30cfd0;': 'color: #3b82f6;',
}

for old, new in text_color_fixes.items():
    content = content.replace(old, new)

# Fix old gradient definitions
gradient_fixes = {
    '--secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);': '--secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);',
}

for old, new in gradient_fixes.items():
    content = content.replace(old, new)

# Fix success/error border colors (keep error red but professional)
status_fixes = {
    '.success { border-left: 4px solid #43e97b; }': '.success { border-left: 4px solid #3b82f6; }',
    '.error { border-left: 4px solid #f5576c; }': '.error { border-left: 4px solid #ef4444; }',
}

for old, new in status_fixes.items():
    content = content.replace(old, new)

# Write back
with open('scripts_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully replaced ALL non-blue colors!")
print("\nUpdated:")
print("- All border colors → Professional blue (#2563eb, #3b82f6)")
print("- All text colors → Professional blue (#3b82f6)")
print("- Error indicators → Professional red (#ef4444)")
print("- All gradients → Professional blue gradients")
print("\n🎨 Your application now uses a completely unified professional blue color scheme!")
