import subprocess
import re
# 명령을 리스트로 만듭니다.
command = [
    "./Examples/Monocular/mono_euroc",
    "./Vocabulary/ORBvoc.txt",
    "./Examples/Monocular/EuRoC.yaml",
    "/home/hello/Desktop/data/frames",
    "/home/hello/Desktop/data/frames/timestamps.txt",
    "test"
]

# 결과를 저장할 파일
output_file = "out_result.txt"

# subprocess.run을 사용하여 명령을 foreground에서 실행하고 결과를 파일로 저장합니다.
try:
    with open(output_file, "w") as output_file_handle:
        result = subprocess.run(command, check=True, stdout=output_file_handle, stderr=subprocess.PIPE, text=True)
        print("프로세스 종료 코드:", result.returncode)
except subprocess.CalledProcessError as e:
    print("오류 발생. 종료 코드:", e.returncode)
    print("표준 에러:\n", e.stderr)



# Open the file for reading
with open(output_file, "r") as output_file_handle:
    # Read the entire contents of the file
    file_contents = output_file_handle.read()

    # Use regular expressions to extract values
    match = re.search(r"Position: x = (\S+), y = (\S+), z = (\S+)", file_contents)

    # Check if the pattern was found
    if match:
        x_value = match.group(1)
        y_value = match.group(2)
        z_value = match.group(3)

        # Print or use the extracted values
        print(f"Extracted values: x = {x_value}, y = {y_value}, z = {z_value}")
    else:
        print("Pattern not found in the file.")
