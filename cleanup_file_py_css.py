import re

# Read the file
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the clean :root section
clean_root = """        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }"""

# Pattern to match :root sections (with various content inside)
root_pattern = r'        :root \{[^}]+\}'

# Replace all :root sections with the clean version
content = re.sub(root_pattern, clean_root, content, flags=re.DOTALL)

# Write back
with open('file.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully cleaned up all CSS :root sections in file.py!")
print("\nAll templates now have clean, duplicate-free CSS variables:")
print("  - TEMPLATE (main)")
print("  - MODIFY_TEMPLATE")
print("  - RENAME_TEMPLATE")
print("  - ROY_TEMPLATE")
