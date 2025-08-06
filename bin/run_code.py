import subprocess

print("--- Running 1.py ---")
try:
    result = subprocess.run(
      ["python", "1.py"],
      capture_output=True, # Capture stdout and stderr
      text=True,           # Decode output as text
      check=True           # Raise CalledProcessError on non-zero exit code
    )
    print("1.py ran successfully!")
    print("Output from 1.py:")
    print(result.stdout)
except FileNotFoundError:
    print("Error: 'python' command or '1.py' not found.")
except subprocess.CalledProcessError as e:
    print(f"Error: 1.py exited with non-zero status code {e.returncode}")
    print("Stderr from 1.py:")
    print(e.stderr)