import re

# Read the file
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all old gradient variables with new professional blue gradients
# This handles all :root sections in all templates
content = re.sub(
    r'--primary-gradient: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);',
    '--primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);',
    content
)

content = re.sub(
    r'--secondary-gradient: linear-gradient\(135deg, #f093fb 0%, #f5576c 100%\);',
    '--secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);',
    content
)

content = re.sub(
    r'--success-gradient: linear-gradient\(135deg, #4facfe 0%, #00f2fe 100%\);',
    '--accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);',
    content
)

content = re.sub(
    r'--warning-gradient: linear-gradient\(135deg, #43e97b 0%, #38f9d7 100%\);\s*',
    '',
    content
)

content = re.sub(
    r'--danger-gradient: linear-gradient\(135deg, #fa709a 0%, #fee140 100%\);\s*',
    '',
    content
)

content = re.sub(
    r'--info-gradient: linear-gradient\(135deg, #a8edea 0%, #fed6e3 100%\);\s*',
    '',
    content
)

content = re.sub(
    r'--dark-gradient: linear-gradient\(135deg, #2c3e50 0%, #34495e 100%\);\s*',
    '',
    content
)

content = re.sub(
    r'--light-gradient: linear-gradient\(135deg, #ffecd2 0%, #fcb69f 100%\);\s*',
    '',
    content
)

# Update background colors
content = re.sub(r'--bg-primary: #0f0f23;', '--bg-primary: #0f172a;', content)
content = re.sub(r'--bg-secondary: #1a1a2e;', '--bg-secondary: #1e293b;', content)
content = re.sub(r'--bg-card: #16213e;', '--bg-card: rgba(30, 41, 59, 0.8);', content)

# Update text colors
content = re.sub(r'--text-secondary: #b8c5d1;', '--text-secondary: #cbd5e1;', content)

# Update accent and border
content = re.sub(r'--accent: #00d4aa;', '--primary-color: #2563eb;', content)
content = re.sub(r'--accent-hover: #00b894;', '--secondary-color: #1e40af;', content)
content = re.sub(r'--border: #2d3748;', '--border: rgba(37, 99, 235, 0.2);', content)

# Add missing color variables after --shadow
content = re.sub(
    r'(--shadow: rgba\(0, 0, 0, 0\.3\);)(?!\s*--primary-color)',
    r'\1\n            --primary-color: #2563eb;\n            --secondary-color: #1e40af;\n            --accent-color: #3b82f6;',
    content
)

# Remove radial gradients from body background
content = re.sub(
    r'background: var\(--bg-primary\);\s*background-image:\s*radial-gradient\(circle at 20% 80%, rgba\(120, 119, 198, 0\.3\) 0%, transparent 50%\),\s*radial-gradient\(circle at 80% 20%, rgba\(255, 119, 198, 0\.3\) 0%, transparent 50%\);',
    'background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);',
    content
)

# Remove backdrop-filter from container
content = re.sub(r'backdrop-filter: blur\(10px\);\s*', '', content)

# Remove text-shadow from h1
content = re.sub(r'text-shadow: 0 0 20px rgba\(102, 126, 234, 0\.3\);\s*', '', content)

# Update all button backgrounds to use primary-gradient
content = re.sub(r'\.btn-secondary \{ background: var\(--secondary-gradient\); \}', '.btn-secondary { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-success \{ background: var\(--success-gradient\); \}', '.btn-success { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-info \{ background: var\(--info-gradient\); color: #333; \}', '.btn-info { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-warning \{ background: var\(--warning-gradient\); color: #333; \}', '.btn-warning { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-danger \{ background: var\(--danger-gradient\); \}', '.btn-danger { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-dark \{ background: var\(--dark-gradient\); \}', '.btn-dark { background: var(--primary-gradient); }', content)
content = re.sub(r'\.btn-light \{ background: var\(--light-gradient\); color: #333; \}', '.btn-light { background: var(--primary-gradient); }', content)

# Update hover box-shadow to blue
content = re.sub(
    r'box-shadow: 0 10px 25px rgba\(0, 0, 0, 0\.2\);',
    'box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);',
    content
)

content = re.sub(
    r'box-shadow: 0 5px 15px rgba\(0, 0, 0, 0\.2\);',
    'box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);',
    content
)

# Update focus box-shadow to blue
content = re.sub(
    r'box-shadow: 0 0 0 3px rgba\(0, 212, 170, 0\.1\);',
    'box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);',
    content
)

# Update border-color references
content = re.sub(r'border-color: var\(--accent\);', 'border-color: var(--primary-color);', content)
content = re.sub(r'background: var\(--accent\);', 'background: var(--primary-color);', content)

# Update loading overlay
content = re.sub(
    r'background: rgba\(15, 15, 35, 0\.9\);',
    'background: rgba(15, 23, 42, 0.95);',
    content
)

content = re.sub(
    r'border: 4px solid var\(--border\);\s*border-top: 4px solid var\(--accent\);',
    'border: 4px solid rgba(37, 99, 235, 0.2);\n            border-top: 4px solid #2563eb;',
    content
)

# Update z-index for loading overlay (but only in .loading-overlay context)
content = re.sub(
    r'(\.loading-overlay \{[^}]*z-index: )1000;',
    r'\g<1>9999;',
    content
)

# Update toast border
content = re.sub(
    r'border-left: 4px solid var\(--accent\);',
    'border-left: 4px solid var(--primary-color);',
    content
)

# Update transitions
content = re.sub(
    r'transition: all 0\.3s cubic-bezier\(0\.4, 0, 0\.2, 1\);',
    'transition: all 0.2s ease;',
    content
)

# Update breadcrumb hover color
content = re.sub(
    r'(\.breadcrumb a:hover \{[^}]*color: )var\(--accent-hover\);',
    r'\1var(--secondary-color);',
    content
)

# Update footer text
content = re.sub(
    r'Created by Rushabh and Astadia Team',
    'Powered by Astadia TEAM',
    content
)

# Write back
with open('file.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated file.py with professional blue theme!")
print("\nChanges applied:")
print("  ✓ All gradient colors updated to professional blue (#2563eb, #1e40af, #3b82f6)")
print("  ✓ All buttons now use primary-gradient (unified blue)")
print("  ✓ Background changed to dark slate gradient")
print("  ✓ Removed radial gradients and backdrop-filter")
print("  ✓ All hover effects updated to blue")
print("  ✓ Loading spinner updated to blue")
print("  ✓ Toast notifications updated to blue")
print("  ✓ Footer updated to 'Powered by Astadia TEAM'")
print("  ✓ Z-index increased to 9999 for loading overlay")
