import subprocess

user_input = "F\nS\n"

result = subprocess.run(
    ['python', 'test_input.py'],
    input=user_input,
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
