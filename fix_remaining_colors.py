"""
Script to fix all remaining non-blue colors in the UI
"""

# Read the file
with open('scripts_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all hover box-shadow effects to use professional blue
hover_fixes = {
    'box-shadow: 0 10px 25px rgba(245, 87, 108, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(79, 172, 254, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(250, 112, 154, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
}

for old, new in hover_fixes.items():
    content = content.replace(old, new)

# Fix scrollbar thumb hover effects
scrollbar_fixes = {
    'background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);': 'background: var(--secondary-gradient);',
    'background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);': 'background: var(--bg-secondary);',
}

for old, new in scrollbar_fixes.items():
    content = content.replace(old, new)

# Write back
with open('scripts_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully fixed all remaining color inconsistencies!")
print("\nFixed:")
print("- All button hover effects now use professional blue")
print("- All scrollbar hover effects now use consistent gradients")
print("\nAll UI elements now use the professional blue color scheme!")
