import subprocess

# Start a shell process
shell_process = subprocess.Popen(
    ["bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

# Execute multiple commands on the shell
commands = ["ls -l", "pwd", 'echo "Hello World"', "exit"]

# Read the output from the shell process one line at a time
for command in commands:
    out, err = shell_process.communicate(command.encode())
    print(out)

# Close the input stream and wait for the shell process to finish
shell_process.stdin.close()
shell_process.wait()

# Print the error messages
error = shell_process.stderr.read()
print(error.decode())
