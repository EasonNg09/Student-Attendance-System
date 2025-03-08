import subprocess

# Run program1.py and capture its output
output1 = subprocess.check_output(['python', 'ImageComparison.py'], text=True)

# Run program2.py and capture its output
output2 = subprocess.check_output(['python', 'PDFComparison.py'], text=True)

print("Identification Percentage:")
print(output1)

print("Verification Percentage:")
print(output2)