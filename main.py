import argparse
import logging
import os
import subprocess
import shlex  # For safely splitting command lines
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """Sets up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Identifies potential security vulnerabilities arising from implicit type conversions.")
    parser.add_argument("filepath", help="Path to the file or directory to analyze.")
    parser.add_argument("--language", choices=['javascript', 'php', 'python'], default='python',
                        help="The programming language of the file(s) being analyzed.  Defaults to 'python'.")
    parser.add_argument("--report-file", help="Path to save the report to (optional).")
    parser.add_argument("--use-bandit", action="store_true", help="Use Bandit for Python analysis.")
    parser.add_argument("--use-flake8", action="store_true", help="Use Flake8 for Python analysis.")
    parser.add_argument("--use-pylint", action="store_true", help="Use Pylint for Python analysis.")
    parser.add_argument("--use-pyre", action="store_true", help="Use Pyre-check for Python analysis (requires setup).")

    return parser

def analyze_python(filepath, report_file, use_bandit, use_flake8, use_pylint, use_pyre):
    """Analyzes Python code for implicit conversion vulnerabilities using various tools."""
    results = {}

    if use_bandit:
        try:
            command = f"bandit -r {filepath} -q -f json"
            logging.info(f"Running Bandit: {command}")
            process = subprocess.run(shlex.split(command), capture_output=True, text=True, check=True)
            results['bandit'] = process.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Bandit analysis failed: {e}")
            results['bandit'] = f"Error: {e}"

    if use_flake8:
        try:
            command = f"flake8 {filepath}"
            logging.info(f"Running Flake8: {command}")
            process = subprocess.run(shlex.split(command), capture_output=True, text=True, check=True)
            results['flake8'] = process.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Flake8 analysis failed: {e}")
            results['flake8'] = f"Error: {e}"

    if use_pylint:
        try:
            command = f"pylint {filepath} --output-format=json"
            logging.info(f"Running Pylint: {command}")
            process = subprocess.run(shlex.split(command), capture_output=True, text=True, check=True)
            results['pylint'] = process.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Pylint analysis failed: {e}")
            results['pylint'] = f"Error: {e}"

    if use_pyre:
        try:
            # Pyre might require initialization in the project directory
            command = "pyre check"
            logging.info(f"Running Pyre: {command}")
            process = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=os.path.dirname(filepath), check=True) # Run in project directory
            results['pyre'] = process.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Pyre analysis failed: {e}")
            results['pyre'] = f"Error: {e}"

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
    except Exception as e:
        logging.error(f"Failed to save report: {e}")


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
        return

    if language == 'python':
        results = analyze_python(filepath, report_file, args.use_bandit, args.use_flake8, args.use_pylint, args.use_pyre)
    elif language == 'javascript':
        results = analyze_javascript(filepath, report_file)
    elif language == 'php':
        results = analyze_php(filepath, report_file)
    else:
        logging.error(f"Unsupported language: {language}")
        print(f"Error: Unsupported language: {language}")
        return

    # Print results to console
    print("\nAnalysis Results:")
    for tool, result in results.items():
        print(f"\n--- {tool.upper()} ---\n")
        print(result)


    if report_file:
        save_report(report_file, results)
        print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()

# Usage Examples:

# 1. Analyze a Python file using Bandit and save the report:
# python main.py my_python_file.py --use-bandit --report-file bandit_report.txt

# 2. Analyze a Python directory using Bandit, Flake8, and Pylint:
# python main.py my_python_directory --use-bandit --use-flake8 --use-pylint

# 3. Analyze a JavaScript file (note: JavaScript analysis is a placeholder):
# python main.py my_javascript_file.js --language javascript

# 4.  Analyze a PHP file and save results
# python main.py my_php_file.php --language php --report-file php_report.txt