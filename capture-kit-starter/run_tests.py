#!/usr/bin/env python3
"""
Capture Kit - Profile Extraction Test Runner
Run this to validate extractors against sample data.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import sample data
from test_data.sample_data import (
    get_all_writing_samples,
    get_all_transcripts,
    get_screen_captures,
    get_daily_checkins,
    get_expected_profile,
    validate_profile
)


def test_writing_style():
    """Test the writing style extractor."""
    print("\n" + "=" * 60)
    print("TESTING: writing_style.py")
    print("=" * 60)
    
    try:
        from extractors.writing_style import extract_writing_style
    except ImportError as e:
        print(f"âŒ Could not import writing_style extractor: {e}")
        return None
    
    samples = get_all_writing_samples()
    print(f"Input: {len(samples)} text samples")
    
    try:
        result = extract_writing_style(samples)
        print(f"âœ… Extraction completed")
        print(f"\nOutput:")
        print(json.dumps(result, indent=2))
        
        # Validate against expected
        expected = get_expected_profile()["communication"]["writing_style"]
        
        print(f"\n--- Validation ---")
        
        # Check tone
        if "tone" in result:
            expected_tone = expected["tone"]
            actual_tone = result["tone"]
            match = "âœ…" if expected_tone.lower() in actual_tone.lower() or actual_tone.lower() in expected_tone.lower() else "âš ï¸"
            print(f"{match} Tone: expected '{expected_tone}', got '{actual_tone}'")
        
        # Check formality
        if "formality" in result:
            expected_form = expected["formality"]
            actual_form = result["formality"]
            match = "âœ…" if abs(expected_form - actual_form) <= 1 else "âš ï¸"
            print(f"{match} Formality: expected {expected_form}, got {actual_form}")
        
        # Check sign-off
        if "sign_off" in result:
            if isinstance(result["sign_off"], dict):
                actual_signoff = result["sign_off"].get("most_common", "")
            else:
                actual_signoff = result["sign_off"]
            expected_signoff = expected["sign_off"]["most_common"]
            match = "âœ…" if expected_signoff.lower() in actual_signoff.lower() else "âš ï¸"
            print(f"{match} Sign-off: expected '{expected_signoff}', got '{actual_signoff}'")
        
        # Check common phrases
        if "common_phrases" in result:
            expected_phrases = set(expected["common_phrases"])
            actual_phrases = set(result["common_phrases"])
            overlap = expected_phrases & actual_phrases
            print(f"{'âœ…' if overlap else 'âš ï¸'} Common phrases overlap: {overlap if overlap else 'none'}")
        
        return result
        
    except Exception as e:
        print(f"âŒ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_speaking_style():
    """Test the speaking style extractor."""
    print("\n" + "=" * 60)
    print("TESTING: speaking_style.py")
    print("=" * 60)
    
    try:
        from extractors.speaking_style import extract_speaking_style
    except ImportError as e:
        print(f"âŒ Could not import speaking_style extractor: {e}")
        return None
    
    transcripts = get_all_transcripts()
    print(f"Input: {len(transcripts)} transcripts")
    
    try:
        result = extract_speaking_style(transcripts)
        print(f"âœ… Extraction completed")
        print(f"\nOutput:")
        print(json.dumps(result, indent=2))
        
        # Validate against expected
        expected = get_expected_profile()["communication"]["speaking_style"]
        
        print(f"\n--- Validation ---")
        
        # Check directness
        if "directness" in result:
            expected_dir = expected["directness"]
            actual_dir = result["directness"]
            match = "âœ…" if abs(expected_dir - actual_dir) <= 1 else "âš ï¸"
            print(f"{match} Directness: expected {expected_dir}, got {actual_dir}")
        
        # Check vocabulary level
        if "vocabulary_level" in result:
            expected_vocab = expected["vocabulary_level"]
            actual_vocab = result["vocabulary_level"]
            match = "âœ…" if expected_vocab == actual_vocab else "âš ï¸"
            print(f"{match} Vocabulary: expected '{expected_vocab}', got '{actual_vocab}'")
        
        # Check verbal habits
        if "verbal_habits" in result:
            expected_habits = set(expected["verbal_habits"])
            actual_habits = set(result["verbal_habits"])
            overlap = expected_habits & actual_habits
            print(f"{'âœ…' if overlap else 'âš ï¸'} Verbal habits overlap: {overlap if overlap else 'none'}")
        
        return result
        
    except Exception as e:
        print(f"âŒ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_work_patterns():
    """Test the work patterns extractor."""
    print("\n" + "=" * 60)
    print("TESTING: work_patterns.py")
    print("=" * 60)
    
    try:
        from extractors.work_patterns import extract_work_patterns
    except ImportError as e:
        print(f"âŒ Could not import work_patterns extractor: {e}")
        return None
    
    screen_data = get_screen_captures()
    print(f"Input: {len(screen_data)} screen capture events")
    
    try:
        result = extract_work_patterns(screen_data)
        print(f"âœ… Extraction completed")
        print(f"\nOutput:")
        print(json.dumps(result, indent=2))
        
        # Validate against expected
        expected = get_expected_profile()["work_patterns"]
        
        print(f"\n--- Validation ---")
        
        # Check primary tools
        if "primary_tools" in result:
            expected_tools = set(expected["primary_tools"])
            actual_tools = set(result["primary_tools"])
            overlap = expected_tools & actual_tools
            match = "âœ…" if len(overlap) >= 3 else "âš ï¸"
            print(f"{match} Tools detected: {actual_tools}")
            print(f"    Expected overlap: {overlap}")
        
        # Check meeting load
        if "meeting_load" in result:
            expected_load = expected["meeting_load"]
            actual_load = result["meeting_load"]
            match = "âœ…" if expected_load == actual_load else "âš ï¸"
            print(f"{match} Meeting load: expected '{expected_load}', got '{actual_load}'")
        
        return result
        
    except Exception as e:
        print(f"âŒ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_preferences():
    """Test the preferences extractor."""
    print("\n" + "=" * 60)
    print("TESTING: preferences.py")
    print("=" * 60)
    
    try:
        from extractors.preferences import extract_preferences
    except ImportError as e:
        print(f"âŒ Could not import preferences extractor: {e}")
        return None
    
    checkins = get_daily_checkins()
    print(f"Input: {len(checkins)} daily check-in responses")
    
    try:
        result = extract_preferences(checkins)
        print(f"âœ… Extraction completed")
        print(f"\nOutput:")
        print(json.dumps(result, indent=2))
        
        # Validate against expected
        expected = get_expected_profile()["preferences"]
        
        print(f"\n--- Validation ---")
        
        # Check never_do detection
        if "never_do" in result:
            # Should detect the "no meetings before 9am" and "no sending without approval"
            never_items = result["never_do"]
            found_time_pref = any("9am" in item.lower() or "morning" in item.lower() or "before" in item.lower() for item in never_items)
            found_approval = any("approval" in item.lower() or "review" in item.lower() or "send" in item.lower() for item in never_items)
            print(f"{'âœ…' if found_time_pref else 'âš ï¸'} Detected morning meeting preference")
            print(f"{'âœ…' if found_approval else 'âš ï¸'} Detected approval requirement")
        
        return result
        
    except Exception as e:
        print(f"âŒ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_pipeline():
    """Test the complete profile generation pipeline."""
    print("\n" + "=" * 60)
    print("TESTING: Full Profile Generation Pipeline")
    print("=" * 60)
    
    try:
        from generator import generate_profile
    except ImportError as e:
        print(f"âŒ Could not import profile generator: {e}")
        print("    (This is expected until generator.py is created)")
        return None
    
    # Gather all inputs
    inputs = {
        "writing_samples": get_all_writing_samples(),
        "transcripts": get_all_transcripts(),
        "screen_captures": get_screen_captures(),
        "daily_checkins": get_daily_checkins()
    }
    
    print(f"Inputs provided:")
    for key, value in inputs.items():
        print(f"  - {key}: {len(value)} items")
    
    try:
        result = generate_profile(**inputs)
        print(f"âœ… Profile generation completed")
        print(f"\n" + "=" * 60)
        print("GENERATED PROFILE")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        # Full validation
        validation = validate_profile(result, get_expected_profile())
        print(f"\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        print(f"âœ… Matches: {validation['matches']}")
        print(f"âš ï¸  Mismatches: {validation['mismatches']}")
        print(f"âŒ Missing: {validation['missing']}")
        
        return result
        
    except Exception as e:
        print(f"âŒ Profile generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CAPTURE KIT - PROFILE EXTRACTION TEST SUITE")
    print("=" * 60)
    print("\nRunning tests against sample data for persona:")
    print("  Sarah Chen, owner of Spark Creative (marketing agency)")
    
    results = {}
    
    # Test individual extractors
    results["writing_style"] = test_writing_style()
    results["speaking_style"] = test_speaking_style()
    results["work_patterns"] = test_work_patterns()
    results["preferences"] = test_preferences()
    
    # Test full pipeline
    results["full_profile"] = test_full_pipeline()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "âœ… PASS" if result is not None else "âŒ FAIL/SKIP"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for r in results.values() if r is not None)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return results


if __name__ == "__main__":
    main()
