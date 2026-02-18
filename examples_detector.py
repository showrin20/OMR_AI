"""
Example usage of the optimized OMR detector for evaluating OMR sheets.
"""

import logging
from pathlib import Path
from omr.detector_optimized import OMRDetector, detect_omr_answers, evaluate_omr

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_simple_detection():
    """Example 1: Simple detection (without answer key)"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple OMR Detection")
    print("="*60)
    
    image_path = "path/to/your/omr_sheet.png"
    
    # Detect answers
    result = detect_omr_answers(
        image_path=image_path,
        expected_options=4,
        fill_threshold=40.0,
        debug=False
    )
    
    if result["status"] == "success":
        print(f"\n✓ Detection successful!")
        print(f"Total questions detected: {result['total_questions']}")
        print(f"Detected answers: {result['detected_answers']}")
    else:
        print(f"\n✗ Detection failed: {result['error']}")


def example_2_evaluation():
    """Example 2: Evaluation with answer key"""
    print("\n" + "="*60)
    print("EXAMPLE 2: OMR Evaluation with Answer Key")
    print("="*60)
    
    image_path = "path/to/your/omr_sheet.png"
    
    # Answer key: question number -> correct answer
    answer_key = {
        1: "B",   # Question 1, answer is B
        2: "A",   # Question 2, answer is A
        3: "C",   # Question 3, answer is C
        4: "B",   # Question 4, answer is B
        5: "D",   # Question 5, answer is D
        6: "B",
        7: "C",
        8: "A",
        9: "D",
        10: "B",
    }
    
    # Evaluate
    result = evaluate_omr(
        image_path=image_path,
        answer_key=answer_key,
        expected_options=4,
        fill_threshold=40.0,
        debug=False
    )
    
    if result["status"] == "success":
        print(f"\n✓ Evaluation complete!")
        print(f"Score: {result['score']}/{result['total']}")
        print(f"Percentage: {result['percentage']}%")
        print(f"Correct: {result['correct']}")
        print(f"Wrong: {result['wrong']}")
        print(f"Unmarked: {result['unmarked']}")
        print(f"\nDetailed answers: {result['detected_answers']}")
    else:
        print(f"\n✗ Evaluation failed: {result['error']}")


def example_3_custom_detector():
    """Example 3: Using the OMRDetector class directly with custom parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom OMRDetector Configuration")
    print("="*60)
    
    image_path = "path/to/your/omr_sheet.png"
    
    # Create detector with custom parameters
    detector = OMRDetector(
        fill_threshold=35.0,  # Lower threshold for light marks
        bubble_area_range=(200, 8000),  # Min and max bubble area
        aspect_ratio_range=(0.7, 1.3),  # Circular validation
        row_threshold=15.0,  # Tolerance for row grouping
        debug=True  # Enable debug visualization
    )
    
    # Detect answers
    result = detector.detect(
        image_path=image_path,
        expected_options=4
    )
    
    print(f"\nDetection result:")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total questions: {result['total_questions']}")
        print(f"Answers: {result['detected_answers']}")


def example_4_batch_evaluation():
    """Example 4: Batch evaluation of multiple sheets"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing Multiple OMR Sheets")
    print("="*60)
    
    # Answer key (same for all sheets)
    answer_key = {
        i: chr(65 + (i - 1) % 4)  # A, B, C, D, A, B, C, D, ...
        for i in range(1, 51)
    }
    
    # Assume you have OMR sheets in a folder
    sheet_folder = Path("path/to/omr_sheets/")
    sheet_files = list(sheet_folder.glob("*.png"))
    
    print(f"\nProcessing {len(sheet_files)} sheets...\n")
    
    results = []
    for sheet_path in sheet_files:
        result = evaluate_omr(
            image_path=str(sheet_path),
            answer_key=answer_key,
            expected_options=4,
            fill_threshold=40.0
        )
        
        if result["status"] == "success":
            results.append({
                "file": sheet_path.name,
                "score": result["score"],
                "total": result["total"],
                "percentage": result["percentage"]
            })
            print(f"✓ {sheet_path.name}: {result['score']}/{result['total']} ({result['percentage']}%)")
        else:
            print(f"✗ {sheet_path.name}: {result['error']}")
    
    # Summary
    if results:
        avg_percentage = sum(r["percentage"] for r in results) / len(results)
        print(f"\n{'─'*40}")
        print(f"Average percentage: {avg_percentage:.2f}%")


def example_5_debug_analysis():
    """Example 5: Debug analysis for troubleshooting"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Debug Analysis")
    print("="*60)
    
    image_path = "path/to/your/omr_sheet.png"
    
    # Create detector with debug enabled
    detector = OMRDetector(fill_threshold=40.0, debug=True)
    
    # Detect with debug info
    result = detector.detect(image_path, expected_options=4)
    
    if result["status"] == "success":
        print(f"\n✓ Detection successful!")
        print(f"Total questions: {result['total_questions']}")
        
        # Show fill details if available
        if "fill_details" in result:
            print(f"\nDetailed fill percentages:")
            for qnum, fills in sorted(result["fill_details"].items())[:5]:
                print(f"  Q{qnum}: {fills}")
    else:
        print(f"\n✗ Detection failed: {result['error']}")


if __name__ == "__main__":
    """
    To use these examples, uncomment the one you want to run:
    """
    
    # example_1_simple_detection()
    # example_2_evaluation()
    # example_3_custom_detector()
    # example_4_batch_evaluation()
    # example_5_debug_analysis()
    
    print("\n" + "="*60)
    print("OMR Detector Examples")
    print("="*60)
    print("""
    This file contains 5 example usage patterns:
    
    1. Simple Detection - Detect answers without comparing to answer key
    2. Evaluation - Detect answers and compare with answer key
    3. Custom Detector - Use OMRDetector class with custom parameters
    4. Batch Processing - Process multiple OMR sheets
    5. Debug Analysis - Analyze bubble fill percentages
    
    Uncomment any example() call above to run it.
    Make sure to update the image paths before running!
    """)
