import subprocess
import os

script_dir = r'C:\File_conversion'
rexx_exe = os.path.join(script_dir, 'rexx.exe')
rexx_script = os.path.join(script_dir, 'RoysEbcdicRecTypesV6.rexx')
input_file = r'C:\File_conversion\occ\input\RF01U.SJ358W.T3.PFB55.ERRIMAGE.txt'

# Create input data
user_input = f"{input_file}\nV\n6229\n1\nX(3)\n"

print("=== Creating temp input file ===")
temp_input_file = os.path.join(script_dir, 'temp_rexx_input.txt')
with open(temp_input_file, 'w') as f:
    f.write(user_input)

print(f"Temp file contents:\n{user_input}")
print("\n=== Running REXX with stdin redirection ===")

cmd = [rexx_exe, rexx_script, '--rdw']

with open(temp_input_file, 'r') as stdin_file:
    result = subprocess.run(
        cmd,
        stdin=stdin_file,
        capture_output=True,
        text=True,
        cwd=script_dir,
        timeout=30
    )

print(f"Return code: {result.returncode}")
print(f"\nSTDOUT:\n{result.stdout}")
if result.stderr:
    print(f"\nSTDERR:\n{result.stderr}")

# Clean up
try:
    os.remove(temp_input_file)
    print("\nTemp file cleaned up")
except:
    pass
