"""
Script to update hover effects to match professional colors
"""

# Read the file
with open('scripts_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update hover box-shadow colors to use professional blue
hover_updates = {
    'box-shadow: 0 10px 25px rgba(245, 87, 108, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(79, 172, 254, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(250, 112, 154, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    'box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);': 'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
}

for old, new in hover_updates.items():
    content = content.replace(old, new)

# Update any remaining border-left-color to use professional blue
content = content.replace('border-left-color: #43e97b;', 'border-left-color: #3b82f6;')
content = content.replace('border-left-color: #fa709a;', 'border-left-color: #2563eb;')
content = content.replace('border-left: 4px solid #fa709a;', 'border-left: 4px solid #2563eb;')
content = content.replace('border-left: 4px solid #30cfd0;', 'border-left: 4px solid #3b82f6;')
content = content.replace('border-left: 4px solid #43e97b;', 'border-left: 4px solid #3b82f6;')

# Update info-box colors
content = content.replace('border-left: 4px solid var(--accent-color);', 'border-left: 4px solid #3b82f6;')

# Write back
with open('scripts_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated hover effects and accent colors!")
print("All UI elements now use consistent professional blue palette.")
