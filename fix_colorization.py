"""Fix colorization patterns to use word boundaries"""

import re

# Read the file
with open('scripts_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns to fix - add word boundaries \b
replacements = [
    # SUCCESS patterns
    (r"text\.replace\(/\^\(\.\*SUCCESS\.\*\)\$/gm,", r"text.replace(/^(.*\\bSUCCESS\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*Successfully\.\*\)\$/gm,", r"text.replace(/^(.*\\bSuccessfully\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*Completed\.\*\)\$/gm,", r"text.replace(/^(.*\\bCompleted\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*completed successfully\.\*\)\$/gm,", r"text.replace(/^(.*\\bcompleted successfully\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*Created successfully\.\*\)\$/gm,", r"text.replace(/^(.*\\bCreated successfully\\b.*)$/gm,"),
    
    # ERROR patterns  
    (r"text\.replace\(/\^\(\.\*ERROR\.\*\)\$/gm,", r"text.replace(/^(.*\\bERROR\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*Failed\.\*\)\$/gm,", r"text.replace(/^(.*\\bFailed\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*failed\.\*\)\$/gm,", r"text.replace(/^(.*\\bfailed\\b.*)$/gm,"),
    (r"text\.replace\(/\^\(\.\*Exception\.\*\)\$/gm,", r"text.replace(/^(.*\\bException\\b.*)$/gm,"),
    
    # WARNING patterns
    (r"text\.replace\(/\^\(\.\*WARNING\.\*\)\$/gm,", r"text.replace(/^(.*\\bWARNING\\b.*)$/gm,"),
]

# Apply all replacements
for old_pattern, new_pattern in replacements:
    content = re.sub(old_pattern, new_pattern, content)

# Write back
with open('scripts_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all colorization patterns to use word boundaries")
print("Updated patterns for: SUCCESS, Successfully, Completed, ERROR, Failed, Exception, WARNING")
