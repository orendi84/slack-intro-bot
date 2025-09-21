#!/usr/bin/env python3
"""
Test suite for LinkedIn extraction functionality
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_profile_search import extract_linkedin_link, search_user_profile_for_linkedin
from daily_intros import extract_linkedin_link as daily_extract_linkedin_link

class TestLinkedInExtraction(unittest.TestCase):
    """Test LinkedIn URL extraction functionality"""
    
    def test_basic_linkedin_urls(self):
        """Test extraction of basic LinkedIn URLs"""
        test_cases = [
            ("Check out my profile: https://linkedin.com/in/johndoe", "https://linkedin.com/in/johndoe"),
            ("Visit https://www.linkedin.com/in/jane-smith for more info", "https://www.linkedin.com/in/jane-smith"),
            ("My LinkedIn: https://linkedin.com/in/bob-wilson-123", "https://linkedin.com/in/bob-wilson-123"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_linkedin_urls_in_angle_brackets(self):
        """Test extraction of LinkedIn URLs in angle brackets"""
        test_cases = [
            ("<https://linkedin.com/in/johndoe>", "https://linkedin.com/in/johndoe"),
            ("<https://www.linkedin.com/in/jane-smith>", "https://www.linkedin.com/in/jane-smith"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_linkedin_urls_in_parentheses(self):
        """Test extraction of LinkedIn URLs in parentheses"""
        test_cases = [
            ("(https://linkedin.com/in/johndoe)", "https://linkedin.com/in/johndoe"),
            ("(https://www.linkedin.com/in/jane-smith)", "https://www.linkedin.com/in/jane-smith"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_linkedin_pub_urls(self):
        """Test extraction of LinkedIn pub URLs"""
        test_cases = [
            ("https://linkedin.com/pub/johndoe", "https://linkedin.com/pub/johndoe"),
            ("https://www.linkedin.com/pub/jane-smith-123", "https://www.linkedin.com/pub/jane-smith-123"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_urls_without_protocol(self):
        """Test extraction of LinkedIn URLs without protocol"""
        test_cases = [
            ("linkedin.com/in/johndoe", "https://linkedin.com/in/johndoe"),
            ("linkedin.com/pub/jane-smith", "https://linkedin.com/pub/jane-smith"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_no_linkedin_url(self):
        """Test text without LinkedIn URLs"""
        test_cases = [
            "Hello, I'm John Doe",
            "Check out my website: https://example.com",
            "Contact me at john@example.com",
            "No LinkedIn profile here",
            "",
            None,
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertIsNone(result)
    
    def test_multiple_linkedin_urls(self):
        """Test text with multiple LinkedIn URLs (should return first one)"""
        text = "Check https://linkedin.com/in/first and also https://linkedin.com/in/second"
        result = extract_linkedin_link(text)
        self.assertEqual(result, "https://linkedin.com/in/first")
    
    def test_case_insensitive_extraction(self):
        """Test case insensitive LinkedIn URL extraction"""
        test_cases = [
            ("LINKEDIN.COM/IN/JOHNDOE", "https://linkedin.com/in/johndoe"),
            ("https://LinkedIn.com/in/JaneSmith", "https://linkedin.com/in/janesmith"),  # Now expects lowercase
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_complex_linkedin_urls(self):
        """Test extraction of complex LinkedIn URLs"""
        test_cases = [
            ("https://linkedin.com/in/john-doe-123456/", "https://linkedin.com/in/john-doe-123456/"),
            ("https://www.linkedin.com/in/jane.smith.abc/", "https://www.linkedin.com/in/jane.smith.abc/"),
            ("https://linkedin.com/in/user_name-123/", "https://linkedin.com/in/user_name-123/"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)
    
    def test_extraction_with_context(self):
        """Test LinkedIn extraction with surrounding context"""
        test_cases = [
            ("Hi! I'm John. LinkedIn: https://linkedin.com/in/johndoe Thanks!", "https://linkedin.com/in/johndoe"),
            ("Welcome! Check my profile https://linkedin.com/in/jane-smith for more info.", "https://linkedin.com/in/jane-smith"),
            ("Connect with me: linkedin.com/in/bob-wilson LinkedIn profile", "https://linkedin.com/in/bob-wilson"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)

class TestDailyIntrosLinkedInExtraction(unittest.TestCase):
    """Test LinkedIn extraction from daily_intros module"""
    
    def test_consistency_with_user_profile_search(self):
        """Test that both modules extract LinkedIn URLs consistently"""
        test_text = "Hi! Check out my LinkedIn: https://linkedin.com/in/testuser"
        
        profile_result = extract_linkedin_link(test_text)
        daily_result = daily_extract_linkedin_link(test_text)
        
        self.assertEqual(profile_result, daily_result)
        self.assertEqual(profile_result, "https://linkedin.com/in/testuser")
    
    def test_daily_intros_specific_patterns(self):
        """Test daily_intros specific LinkedIn patterns"""
        test_cases = [
            ("<https://linkedin.com/in/johndoe>", "https://linkedin.com/in/johndoe"),
            ("(https://linkedin.com/in/jane-smith)", "https://linkedin.com/in/jane-smith"),
            ("https://linkedin.com/in/bob-wilson LinkedIn", "https://linkedin.com/in/bob-wilson"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = daily_extract_linkedin_link(text)
                self.assertEqual(result, expected)

class TestLinkedInExtractionEdgeCases(unittest.TestCase):
    """Test edge cases for LinkedIn extraction"""
    
    def test_empty_and_none_inputs(self):
        """Test handling of empty and None inputs"""
        test_cases = ["", None, "   ", "\n\t"]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertIsNone(result)
    
    def test_malformed_urls(self):
        """Test handling of malformed LinkedIn URLs"""
        test_cases = [
            "https://linkedin.com/in/",  # No username
            "linkedin.com/in/",  # No username
            "https://linkedin.com/",  # No path
            "https://notlinkedin.com/in/user",  # Wrong domain
            "https://linkedin.com/in/",  # Empty username
            "https://linkedin.com/in/user-",  # Trailing dash
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                # Some patterns might match but should be filtered out
                if result:
                    # If a result is returned, it should be a valid LinkedIn URL
                    self.assertIn('linkedin.com', result)
                    self.assertIn('/in/', result)
                    # Should have a username after /in/
                    parts = result.split('/in/')
                    if len(parts) > 1:
                        username = parts[1].split('/')[0].split('?')[0]
                        self.assertTrue(len(username) > 0, f"Empty username in {result}")
    
    def test_very_long_text(self):
        """Test LinkedIn extraction in very long text"""
        long_text = "This is a very long text. " * 1000 + "https://linkedin.com/in/johndoe " + "More text. " * 1000
        result = extract_linkedin_link(long_text)
        self.assertEqual(result, "https://linkedin.com/in/johndoe")
    
    def test_special_characters_in_username(self):
        """Test LinkedIn URLs with special characters in username"""
        test_cases = [
            ("https://linkedin.com/in/user-name_123", "https://linkedin.com/in/user-name_123"),
            ("https://linkedin.com/in/user.name", "https://linkedin.com/in/user.name"),
            ("https://linkedin.com/in/user_name", "https://linkedin.com/in/user_name"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_linkedin_link(text)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
