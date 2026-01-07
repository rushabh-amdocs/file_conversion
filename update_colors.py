"""
Script to update all template colors to professional corporate palette
"""

# Read the file
with open('scripts_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Old color scheme pattern
old_colors = """            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d1;
            --accent: #00d4aa;
            --border: #2d3748;
            --shadow: rgba(0, 0, 0, 0.3);"""

# New professional color scheme
new_colors = """            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);"""

# Replace all occurrences
content = content.replace(old_colors, new_colors)

# Also update any individual gradient definitions that might exist
replacements = {
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)': 'var(--primary-gradient)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)': 'var(--accent-gradient)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)': 'var(--secondary-gradient)',
    '--expfd-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);': '--expfd-gradient: var(--primary-gradient);',
    '--info-gradient: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);': '--info-gradient: var(--secondary-gradient);',
    '--success-gradient': '--primary-gradient',
    '--warning-gradient': '--secondary-gradient',
    '--mapping-gradient: linear-gradient(135deg, #30cfd0 0%, #330867 100%);': '--mapping-gradient: var(--accent-gradient);',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Update spinner colors to use professional blue
spinner_updates = {
    'border-top-color: #4facfe;': 'border-top-color: #2563eb;',
    'border-top-color: #fa709a;': 'border-top-color: #2563eb;',
    'border-top-color: #ff9a9e;': 'border-top-color: #2563eb;',
    'border-top-color: #43e97b;': 'border-top-color: #2563eb;',
    'border-top-color: #30cfd0;': 'border-top-color: #2563eb;',
    'border: 5px solid rgba(79, 172, 254, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'border: 5px solid rgba(250, 112, 154, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'border: 5px solid rgba(255, 154, 158, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'border: 5px solid rgba(67, 233, 123, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'border: 5px solid rgba(48, 207, 208, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'border: 5px solid rgba(102, 126, 234, 0.3);': 'border: 5px solid rgba(37, 99, 235, 0.3);',
    'color: #4facfe;': 'color: #3b82f6;',
    'color: #fa709a;': 'color: #3b82f6;',
    'color: #ff9a9e;': 'color: #3b82f6;',
    'color: #43e97b;': 'color: #3b82f6;',
    'color: #30cfd0;': 'color: #3b82f6;',
    'color: #667eea;': 'color: #3b82f6;',
}

for old, new in spinner_updates.items():
    content = content.replace(old, new)

# Update scrollbar colors
scrollbar_updates = {
    'rgba(102, 126, 234, 0.5)': 'rgba(37, 99, 235, 0.6)',
    'rgba(102, 126, 234, 0.8)': 'rgba(37, 99, 235, 0.8)',
    'rgba(250, 112, 154, 0.5)': 'rgba(37, 99, 235, 0.6)',
    'rgba(250, 112, 154, 0.8)': 'rgba(37, 99, 235, 0.8)',
    'rgba(255, 154, 158, 0.5)': 'rgba(37, 99, 235, 0.6)',
    'rgba(255, 154, 158, 0.8)': 'rgba(37, 99, 235, 0.8)',
    'rgba(48, 207, 208, 0.5)': 'rgba(37, 99, 235, 0.6)',
    'rgba(48, 207, 208, 0.8)': 'rgba(37, 99, 235, 0.8)',
}

for old, new in scrollbar_updates.items():
    content = content.replace(old, new)

# Update accent color references
content = content.replace('#00d4aa', '#3b82f6')
content = content.replace('var(--accent)', 'var(--accent-color)')

# Write back
with open('scripts_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated all templates to professional corporate colors!")
print("\nColor Scheme:")
print("- Primary: Professional Blue (#2563eb)")
print("- Secondary: Dark Blue (#1e40af)")
print("- Accent: Medium Blue (#3b82f6)")
print("\nAll buttons, spinners, and UI elements now use consistent corporate colors.")
