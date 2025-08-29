import subprocess
import shutil
import os
import random
import datetime

# Path configuration
TASKS_DIR = "./tasks/subjects"   # levels: level1, level2, ...
SOLUTIONS_DIR = "./solutions"    # single solution file (.c/.cpp)
BUILD_DIR = "./build"
TRACE_DIR = "./traces"

# Ensure build and trace dirs exist
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(TRACE_DIR, exist_ok=True)

def clear_folder(folder_path):
    """Delete all files inside a folder (keep the folder itself)."""
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

def test_subject(level: str):
    level_dir = os.path.join(TASKS_DIR, level)

    # Pick a random exercise folder (numbered)
    exercises = [f for f in os.listdir(level_dir) if os.path.isdir(os.path.join(level_dir, f))]
    if not exercises:
        print(f"❌ No exercises found in {level}")
        return
    exercise = random.choice(exercises)
    subject_dir = os.path.join(level_dir, exercise)
    
    # Print only the exercise number
    print(f"\n📘 Working on {level}/exercise {exercise}\n")

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
        run_and_check(exe_file, expected_output_file, f"{level}_{exercise}")

    except subprocess.CalledProcessError as e:
        print("❌ Compilation failed!")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = os.path.join(TRACE_DIR, f"{level}_{exercise}_compile_{timestamp}.txt")
        with open(trace_file, "w", encoding="utf-8") as f:
            f.write("--- Compiler stdout ---\n")
            f.write(e.stdout or "")
            f.write("\n--- Compiler stderr ---\n")
            f.write(e.stderr or "")
        print(f"📂 Trace saved to {trace_file}")

if __name__ == "__main__":
    print("Task tester started.\n")
    current_level = None

    while True:
        if current_level is None:
            # Show levels only when choosing a new level
            levels = [f for f in os.listdir(TASKS_DIR) if os.path.isdir(os.path.join(TASKS_DIR, f))]
            if not levels:
                print("❌ No level folders found in tasks/subjects")
                break

            print("Available levels:")
            for i, lvl in enumerate(levels, 1):
                print(f"{i}. {lvl}")
            choice = input(f"Choose a level (1-{len(levels)}) or type level name (e.g., level1), or EXIT: ").strip().lower()

            if choice.upper() == "EXIT":
                clear_folder(SOLUTIONS_DIR)
                clear_folder(TRACE_DIR)
                clear_folder(BUILD_DIR)
                print("👋 Exiting program. Solutions, traces, and build cleared. Bye!")
                break

            if choice.isdigit() and 1 <= int(choice) <= len(levels):
                current_level = levels[int(choice)-1]
            elif choice in [lvl.lower() for lvl in levels]:
                current_level = next(lvl for lvl in levels if lvl.lower() == choice)
            else:
                print("❌ Invalid choice, try again.\n")
                continue

            # Immediately pick and display a random exercise after selecting the level
            test_subject(current_level)

        # Prompt after level is chosen and first exercise displayed
        user_input = input(
            "Press Enter to evaluate, New to choose another exercise, "
            "NewNew to choose another level, Exit to close the program: "
        ).strip().lower()

        if user_input == "":
            test_subject(current_level)
            print("\n--- Ready for next action ---\n")
        elif user_input == "new":
            test_subject(current_level)
            print("\n--- Ready for next action ---\n")
        elif user_input == "newnew":
            current_level = None
            print("\n🔄 Choose a new level...\n")
        elif user_input == "exit":
            clear_folder(SOLUTIONS_DIR)
            clear_folder(TRACE_DIR)
            clear_folder(BUILD_DIR)
            print("👋 Exiting program. Solutions, traces, and build cleared. Bye!")
            break
        else:
            print("❌ Invalid input, try again.\n")
