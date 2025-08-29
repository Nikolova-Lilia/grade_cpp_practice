import subprocess
import shutil
import os
import random
import datetime

# Path configuration
TASKS_DIR = "./tasks/subjects"   # where difficulty folders live (subject1, subject2, ...)
SOLUTIONS_DIR = "./solutions"    # where your single solution file lives
BUILD_DIR = "./build"
TRACE_DIR = "./traces"

# Ensure build and trace dirs exist
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(TRACE_DIR, exist_ok=True)

def clear_folder(folder_path):
    """Delete all files inside a folder (but keep the folder itself)."""
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

def normalize_output(text: str) -> list[str]:
    """Normalize program output for flexible comparison."""
    lines = text.strip().splitlines()
    return [line.strip() for line in lines if line.strip()]

def run_and_check(exe_file: str, expected_output_file: str, subject: str):
    result = subprocess.run([exe_file], capture_output=True, text=True)
    actual_output = result.stdout.strip()

    print("\n--- Program output ---")
    print(actual_output if actual_output else "[no output]")
    if result.stderr:
        print("⚠️ Runtime errors:", result.stderr)

    if os.path.isfile(expected_output_file):
        with open(expected_output_file, "r", encoding="utf-8") as f:
            expected_output = f.read().strip()

        norm_actual = normalize_output(actual_output)
        norm_expected = normalize_output(expected_output)

        if norm_actual == norm_expected:
            print("✅ Output matches expected!")
        else:
            print("❌ Output does NOT match expected!")
            print("--- Expected ---")
            print("\n".join(norm_expected))
            print("--- Got ---")
            print("\n".join(norm_actual))

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_file = os.path.join(TRACE_DIR, f"{subject}_trace_{timestamp}.txt")
            with open(trace_file, "w", encoding="utf-8") as f:
                f.write("❌ Output mismatch!\n")
                f.write("--- Expected ---\n")
                f.write("\n".join(norm_expected) + "\n")
                f.write("--- Got ---\n")
                f.write("\n".join(norm_actual) + "\n")
            print(f"📂 Mismatch trace saved to {trace_file}")

def test_subject(difficulty: str):
    difficulty_dir = os.path.join(TASKS_DIR, difficulty)

    # Pick a random exercise folder (numbered)
    exercises = [f for f in os.listdir(difficulty_dir) if os.path.isdir(os.path.join(difficulty_dir, f))]
    if not exercises:
        print(f"❌ No exercises found in {difficulty}")
        return
    exercise = random.choice(exercises)
    subject_dir = os.path.join(difficulty_dir, exercise)
    print(f"\n📘 Testing {difficulty}/{exercise}")

    # Print exercise description
    subject_txt = os.path.join(subject_dir, "subject.txt")
    if os.path.isfile(subject_txt):
        print("\n--- Exercise Description ---")
        with open(subject_txt, "r", encoding="utf-8") as f:
            print(f.read().strip())
        print("-----------------------------\n")

    # Clear build folder
    clear_folder(BUILD_DIR)

    # Get solution file (must be single .c/.cpp file)
    solution_files = [f for f in os.listdir(SOLUTIONS_DIR) if f.endswith((".c", ".cpp"))]
    if len(solution_files) != 1:
        print("❌ You must place exactly ONE solution file (.c or .cpp) in ./solutions/")
        return

    solution_file = os.path.join(SOLUTIONS_DIR, solution_files[0])
    dst_file = os.path.join(BUILD_DIR, solution_files[0])
    shutil.copy(solution_file, dst_file)

    exe_file = os.path.join(BUILD_DIR, "program.out")
    if solution_file.endswith(".cpp"):
        compiler = ["c++", "-std=c++17", "-o", exe_file, dst_file]
    else:
        compiler = ["gcc", "-std=c11", "-o", exe_file, dst_file]

    try:
        subprocess.run(compiler, check=True, capture_output=True, text=True)
        print("✅ Compilation successful!")

        expected_output_file = os.path.join(subject_dir, "output", "output.txt")
        run_and_check(exe_file, expected_output_file, f"{difficulty}_{exercise}")

    except subprocess.CalledProcessError as e:
        print("❌ Compilation failed!")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = os.path.join(TRACE_DIR, f"{difficulty}_{exercise}_compile_{timestamp}.txt")
        with open(trace_file, "w", encoding="utf-8") as f:
            f.write("--- Compiler stdout ---\n")
            f.write(e.stdout or "")
            f.write("\n--- Compiler stderr ---\n")
            f.write(e.stderr or "")
        print(f"📂 Trace saved to {trace_file}")

if __name__ == "__main__":
    print("Task tester started. Type EXIT to quit.\n")

    while True:
        # Prompt for difficulty
        difficulties = [f for f in os.listdir(TASKS_DIR) if os.path.isdir(os.path.join(TASKS_DIR, f))]
        if not difficulties:
            print("❌ No difficulty folders found in tasks/subjects")
            break

        print("Available difficulty levels:")
        for i, diff in enumerate(difficulties, 1):
            print(f"{i}. {diff}")
        choice = input(f"Choose a difficulty (1-{len(difficulties)}), or type EXIT: ").strip()

        if choice.upper() == "EXIT":
            clear_folder(SOLUTIONS_DIR)
            clear_folder(TRACE_DIR)
            clear_folder(BUILD_DIR)
            print("👋 Exiting program. Solutions, traces, and build cleared. Bye!")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(difficulties)):
            print("❌ Invalid choice, try again.\n")
            continue

        current_difficulty = difficulties[int(choice)-1]

        test_subject(current_difficulty)
        print("\n--- Done testing. You can choose another difficulty or type EXIT ---\n")
