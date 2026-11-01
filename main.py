import argparse
import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """Sets up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Runs bandit, flake8, pylint, or pyre on Python files when flagged. No implicit type conversion specific check is performed, and JavaScript and PHP analysis is not implemented.")
    parser.add_argument("filepath", help="Path to the file or directory to analyze.")
    parser.add_argument("--language", choices=['javascript', 'php', 'python'], default='python',
                        help="The programming language of the file(s) being analyzed.  Defaults to 'python'.")
    parser.add_argument("--report-file", help="Path to save the report to (optional).")
    parser.add_argument("--use-bandit", action="store_true", help="Use Bandit for Python analysis.")
    parser.add_argument("--use-flake8", action="store_true", help="Use Flake8 for Python analysis.")
    parser.add_argument("--use-pylint", action="store_true", help="Use Pylint for Python analysis.")
    parser.add_argument("--use-pyre", action="store_true", help="Use Pyre-check for Python analysis (requires setup).")

    return parser

# I take report_file here and never use it. Saving happens in
# main from the returned dict, so this parameter exists only
# because the three language functions share a shape.
def analyze_python(filepath, report_file, use_bandit, use_flake8, use_pylint, use_pyre):
    """Analyzes Python code for implicit conversion vulnerabilities using various tools."""
    results = {}

    # Each command is an argv list, never a split string: splitting a built
    # string on whitespace turned a path containing spaces into several
    # arguments, so the tools analysed a directory that does not exist.
    commands = {}
    if use_bandit:
        commands["bandit"] = ["bandit", "-r", filepath, "-q", "-f", "json"]
    if use_flake8:
        commands["flake8"] = ["flake8", filepath]
    if use_pylint:
        commands["pylint"] = ["pylint", filepath, "--output-format=json"]
    if use_pyre:
        commands["pyre"] = ["pyre", "check"]

    for tool, command in commands.items():
        try:
            logging.info(f"Running {tool}: {' '.join(command)}")
            kwargs = {"capture_output": True, "text": True, "check": True}
            if tool == "pyre":
                # Pyre works on a configured project, so it runs in the
                # directory holding the target rather than on the file.
                # I run pyre in the target's directory even when the target is
                # itself a directory, which puts pyre in the parent. That is a
                # known rough edge: pyre then checks whatever project the
                # parent holds, not necessarily the one named.
                kwargs["cwd"] = os.path.dirname(os.path.abspath(filepath))
            process = subprocess.run(command, **kwargs)
            results[tool] = process.stdout
        except subprocess.CalledProcessError as e:
            # A linter exits non-zero when it finds something, and its
            # findings are on stdout, so keep them instead of the bare
            # exception text whenever the tool produced output.
            logging.error(f"{tool} analysis failed: {e}")
            results[tool] = e.stdout or f"Error: {e}"
        except FileNotFoundError:
            logging.error(f"{tool} is not installed.")
            results[tool] = f"Error: {tool} is not installed."

    return results


def analyze_javascript(filepath, report_file):
    """Analyzes JavaScript code for implicit conversion vulnerabilities.  Placeholder for future implementation."""
    logging.warning("JavaScript analysis is not yet implemented.")
    return {"javascript_analysis": "Not implemented"}

def analyze_php(filepath, report_file):
    """Analyzes PHP code for implicit conversion vulnerabilities. Placeholder for future implementation."""
    logging.warning("PHP analysis is not yet implemented.")
    return {"php_analysis": "Not implemented"}


def save_report(report_file, results):
    """Saves the analysis results to a file."""
    try:
        with open(report_file, "w") as f:
            f.write("Analysis Report:\n")
            for tool, result in results.items():
                f.write(f"\n--- {tool.upper()} ---\n")
                f.write(result)
        return True
    except Exception as e:
        logging.error(f"Failed to save report: {e}")
        return False


def main():
    """Main function to drive the code analysis."""
    parser = setup_argparse()
    args = parser.parse_args()

    filepath = args.filepath
    language = args.language
    report_file = args.report_file

    # Input validation: Check if file exists
    if not os.path.exists(filepath):
        logging.error(f"File or directory not found: {filepath}")
        print(f"Error: File or directory not found: {filepath}")  # Print to console for immediate feedback
        sys.exit(1)

    if language == 'python':
        if not (args.use_bandit or args.use_flake8 or args.use_pylint or args.use_pyre):
            logging.error("No tool was selected. Pass --use-bandit, --use-flake8, --use-pylint, or --use-pyre.")
            print("Error: No tool was selected. Pass --use-bandit, --use-flake8, --use-pylint, or --use-pyre.")
            sys.exit(1)
        # Only the Python branch reaches this line. The JavaScript and
        # PHP branches above exit 1 in main, so their placeholder
        # functions in this file are never called from the CLI at all.
        results = analyze_python(filepath, report_file, args.use_bandit, args.use_flake8, args.use_pylint, args.use_pyre)
    elif language == 'javascript':
        logging.error("JavaScript analysis is not implemented.")
        print("Error: JavaScript analysis is not implemented.")
        sys.exit(1)
    elif language == 'php':
        logging.error("PHP analysis is not implemented.")
        print("Error: PHP analysis is not implemented.")
        sys.exit(1)
    else:
        logging.error(f"Unsupported language: {language}")
        print(f"Error: Unsupported language: {language}")
        sys.exit(1)

    # Print results to console
    print("\nAnalysis Results:")
    for tool, result in results.items():
        print(f"\n--- {tool.upper()} ---\n")
        print(result)


    if report_file:
        if save_report(report_file, results):
            print(f"\nReport saved to: {report_file}")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
