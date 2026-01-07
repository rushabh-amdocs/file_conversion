import re

# Read the file
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define old and new color schemes
old_to_new = {
    # CSS Variables - old purple/pink gradients to professional blue
    r"--primary-gradient: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);": "--primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);",
    r"--secondary-gradient: linear-gradient\(135deg, #f093fb 0%, #f5576c 100%\);": "--secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);",
    r"--success-gradient: linear-gradient\(135deg, #4facfe 0%, #00f2fe 100%\);": "--accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);",
    r"--warning-gradient: linear-gradient\(135deg, #43e97b 0%, #38f9d7 100%\);": "",
    r"--danger-gradient: linear-gradient\(135deg, #fa709a 0%, #fee140 100%\);": "",
    r"--info-gradient: linear-gradient\(135deg, #a8edea 0%, #fed6e3 100%\);": "",
    r"--dark-gradient: linear-gradient\(135deg, #2c3e50 0%, #34495e 100%\);": "",
    r"--light-gradient: linear-gradient\(135deg, #ffecd2 0%, #fcb69f 100%\);": "",
    
    # Background colors
    r"--bg-primary: #0f0f23;": "--bg-primary: #0f172a;",
    r"--bg-secondary: #1a1a2e;": "--bg-secondary: #1e293b;",
    r"--bg-card: #16213e;": "--bg-card: rgba(30, 41, 59, 0.8);",
    
    # Text colors
    r"--text-secondary: #b8c5d1;": "--text-secondary: #cbd5e1;",
    
    # Accent colors
    r"--accent: #00d4aa;": "--primary-color: #2563eb;",
    r"--accent-hover: #00b894;": "--secondary-color: #1e40af;",
    
    # Border
    r"--border: #2d3748;": "--border: rgba(37, 99, 235, 0.2);",
    
    # Remove radial gradients from body background
    r"background: var\(--bg-primary\);\s*background-image:\s*radial-gradient\([^;]+;\s*radial-gradient\([^;]+;": "background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);",
    
    # Remove backdrop-filter
    r"backdrop-filter: blur\(10px\);\s*": "",
    
    # Remove text-shadow from h1
    r"text-shadow: 0 0 20px rgba\(102, 126, 234, 0\.3\);\s*": "",
    
    # Update button backgrounds to all use primary-gradient
    r"\.btn-secondary \{ background: var\(--secondary-gradient\); \}": ".btn-secondary { background: var(--primary-gradient); }",
    r"\.btn-success \{ background: var\(--success-gradient\); \}": ".btn-success { background: var(--primary-gradient); }",
    r"\.btn-info \{ background: var\(--info-gradient\); color: #333; \}": ".btn-info { background: var(--primary-gradient); }",
    r"\.btn-warning \{ background: var\(--warning-gradient\); color: #333; \}": ".btn-warning { background: var(--primary-gradient); }",
    r"\.btn-danger \{ background: var\(--danger-gradient\); \}": ".btn-danger { background: var(--primary-gradient); }",
    r"\.btn-dark \{ background: var\(--dark-gradient\); \}": ".btn-dark { background: var(--primary-gradient); }",
    r"\.btn-light \{ background: var\(--light-gradient\); color: #333; \}": ".btn-light { background: var(--primary-gradient); }",
    
    # Update hover effects
    r"box-shadow: 0 10px 25px rgba\(0, 0, 0, 0\.2\);": "box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);",
    r"box-shadow: 0 0 0 3px rgba\(0, 212, 170, 0\.1\);": "box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);",
    
    # Update focus and hover colors
    r"border-color: var\(--accent\);": "border-color: var(--primary-color);",
    r"background: var\(--accent\);": "background: var(--primary-color);",
    r"border-color: var\(--accent\);": "border-color: var(--primary-color);",
    
    # Update loading overlay
    r"background: rgba\(15, 15, 35, 0\.9\);": "background: rgba(15, 23, 42, 0.95);",
    r"border: 4px solid var\(--border\);\s*border-top: 4px solid var\(--accent\);": "border: 4px solid rgba(37, 99, 235, 0.2);\n            border-top: 4px solid #2563eb;",
    
    # Update z-index for loading overlay
    r"z-index: 1000;": "z-index: 9999;",
    
    # Update toast border
    r"border-left: 4px solid var\(--accent\);": "border-left: 4px solid var(--primary-color);",
    
    # Update transitions
    r"transition: all 0\.3s cubic-bezier\(0\.4, 0, 0\.2, 1\);": "transition: all 0.2s ease;",
    
    # Update breadcrumb links
    r"color: var\(--accent\);": "color: var(--primary-color);",
    r"color: var\(--accent-hover\);": "color: var(--secondary-color);",
    
    # Update footer text
    r"Created by Rushabh and Astadia Team": "Powered by Astadia TEAM",
}

# Apply replacements
for old_pattern, new_value in old_to_new.items():
    if new_value:  # Only replace if there's a new value
        content = re.sub(old_pattern, new_value, content)
    else:  # Remove the line if new_value is empty
        content = re.sub(old_pattern + r'\s*', '', content)

# Add missing CSS variables after --shadow in :root sections
content = re.sub(
    r'(--shadow: rgba\(0, 0, 0, 0\.3\);)',
    r'\1\n            --primary-color: #2563eb;\n            --secondary-color: #1e40af;\n            --accent-color: #3b82f6;\n            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);\n            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);\n            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);',
    content
)

# Write the updated content back
with open('file.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated file.py with professional blue theme")
print("Updated:")
print("  - All CSS variables to professional blue palette")
print("  - All buttons to use primary-gradient")
print("  - Background gradients to dark slate blue")
print("  - Hover effects to blue")
print("  - Loading spinner to blue")
print("  - Toast notifications to blue")
print("  - Footer text to 'Powered by Astadia TEAM'")
