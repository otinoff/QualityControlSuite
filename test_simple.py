#!/usr/bin/env python3
"""
Test script for fastqcli.py simplified mode
"""

import os
import sys
from pathlib import Path

# Add current directory to module search path
sys.path.insert(0, str(Path(__file__).parent))

from fastqcli import analyze_with_sequali, has_command

def test_simple_analysis():
    """Test simple analysis without JSON"""
    
    print("=== SIMPLE ANALYSIS TEST ===")
    
    # Check if Sequali is available
    if not has_command('sequali'):
        print("[FAIL] Sequali not installed or not available")
        return False
    
    print("[OK] Sequali is available")
    
    # Look for test file
    test_files = [
        "test_sample.fastq",
        "perfect_sample.fastq", 
        "correct_sample.fastq"
    ]
    
    test_file = None
    for filename in test_files:
        file_path = Path(filename)
        if file_path.exists():
            test_file = str(file_path)
            break
    
    if not test_file:
        print("[FAIL] No test file found")
        # Create simple test file
        test_file = "test_simple.fastq"
        create_test_fastq(test_file)
    
    print(f"[FILE] Using test file: {test_file}")
    
    # Create output directory
    output_dir = "test_results_simple"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n--- TEST 1: HTML only (no JSON) ---")
    success = analyze_with_sequali(
        test_file,
        output_dir=output_dir,
        save_json=False,  # IMPORTANT: No JSON!
        save_html=True    # Only HTML
    )
    
    if success:
        print("[OK] Test 1 passed")
        
        # Check if HTML file was created
        html_files = list(Path(output_dir).glob("*.html"))
        if html_files:
            print(f"[FILE] Found HTML file: {html_files[0].name}")
        else:
            print("[FAIL] HTML file not found")
            return False
    else:
        print("[FAIL] Test 1 failed")
        return False
    
    print("\n--- TEST 2: JSON only (no HTML) ---")
    success = analyze_with_sequali(
        test_file,
        output_dir=output_dir,
        save_json=True,   # Only JSON
        save_html=False   # No HTML
    )
    
    if success:
        print("[OK] Test 2 passed")
        
        # Check if JSON file was created
        json_files = list(Path(output_dir).glob("*.json"))
        if json_files:
            print(f"[FILE] Found JSON file: {json_files[0].name}")
        else:
            print("[FAIL] JSON file not found")
            return False
    else:
        print("[FAIL] Test 2 failed")
        return False
    
    print("\n--- TEST 3: Both formats ---")
    success = analyze_with_sequali(
        test_file,
        output_dir=output_dir,
        save_json=True,   # JSON
        save_html=True    # HTML
    )
    
    if success:
        print("[OK] Test 3 passed")
        
        # Check if both files were created
        html_files = list(Path(output_dir).glob("*.html"))
        json_files = list(Path(output_dir).glob("*.json"))
        
        if html_files and json_files:
            print(f"[FILE] Found files: {html_files[0].name}, {json_files[0].name}")
        else:
            print("[FAIL] One of the files not found")
            return False
    else:
        print("[FAIL] Test 3 failed")
        return False
    
    print("\n[SUCCESS] All tests passed!")
    return True

def create_test_fastq(filename):
    """Create simple test FASTQ file"""
    test_content = """@TEST_READ_1
ACGTACGTACGT
+
IIIIIIIIIIIIII
@TEST_READ_2
TGCATGCATGCATGCATGCA
+
IIIIIIIIIIIIIIII
@TEST_READ_3
GCTAGCTAGCTA
+
IIIIIIIIIIII
"""
    
    with open(filename, 'w') as f:
        f.write(test_content)
    
    print(f"[FILE] Created test file: {filename}")

if __name__ == "__main__":
    test_simple_analysis()