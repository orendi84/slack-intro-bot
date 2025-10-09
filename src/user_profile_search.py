#!/usr/bin/env python3
"""
User Profile Search Module

This module handles searching for LinkedIn profiles in Slack user profile details.
It's called as a fallback when LinkedIn links are not found in message content.
"""

import re
import signal
from typing import Optional, Dict
from mcp_adapter import get_mcp_adapter

# Pre-compile LinkedIn regex patterns for better performance
_LINKEDIN_PATTERNS = [
    re.compile(r'<https?://(?:www\.)?linkedin\.com/in/[^>]+>', re.IGNORECASE),
    re.compile(r'\(https?://(?:www\.)?linkedin\.com/in/[^)]+\)', re.IGNORECASE),
    re.compile(r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)', re.IGNORECASE),
    re.compile(r'https?://(?:www\.)?linkedin\.com/pub/[\w\-\.]+/?(?=\s|$)', re.IGNORECASE),
    re.compile(r'linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>)', re.IGNORECASE),
    re.compile(r'linkedin\.com/pub/[\w\-\.]+/?(?=\s|$|>)', re.IGNORECASE)
]

# Standard profile fields to check for LinkedIn URLs (as tuple for immutability and performance)
_STANDARD_PROFILE_FIELDS = (
    'status_text', 'title', 'phone', 'skype', 'real_name_normalized',
    'display_name', 'display_name_normalized', 'real_name', 'email'
)

def extract_linkedin_link(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text using pre-compiled regex patterns"""
    if not text:
        return None
    
    for pattern in _LINKEDIN_PATTERNS:
        match = pattern.search(text)
        if match:
            url = match.group(0)
            
            # Clean up URL by removing angle brackets and parentheses
            if url.startswith('<') and url.endswith('>'):
                url = url[1:-1]
            elif url.startswith('(') and url.endswith(')'):
                url = url[1:-1]
            
            # Ensure URL has protocol and normalize case
            if not url.startswith('http'):
                url = 'https://' + url
            
            # Normalize to lowercase for consistency
            url = url.lower()
            
            return url
    
    return None

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Profile search timed out")

def search_user_profile_for_linkedin(user_id: str, timeout_seconds: int = 30) -> Optional[str]:
    """
    Search for LinkedIn profile in Slack user profile details.
    
    Args:
        user_id: Slack user ID to search
        timeout_seconds: Maximum time to wait for profile search (default: 30)
        
    Returns:
        LinkedIn URL if found, None otherwise
        
    Guarantees:
        - Always returns within timeout_seconds
        - Always prints completion message
        - Never hangs indefinitely
    """
    search_started = False
    try:
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        search_started = True
        
        print(f"🔍 Searching profile details for user: {user_id}")
        
        # Try to get user profile using Zapier MCP (auto-detected server)
        try:
            mcp = get_mcp_adapter()
            result = mcp.slack_find_user_by_id(
                instructions=f"Get full profile details for user {user_id} to check for LinkedIn URL",
                user_id=user_id
            )
            if result:
                print(f"✅ Successfully retrieved profile for user {user_id}")
            else:
                print(f"⚠️  No profile data returned for user {user_id}")
                return None
        except Exception as e:
            print(f"⚠️  Error calling MCP function for user {user_id}: {e}")
            return None
        
        if not result or 'profile' not in result:
            print(f"⚠️  No profile data found for user {user_id}")
            return None
            
        profile = result['profile']
        
        # Debug: Print all available profile fields to see what we have
        print(f"🔍 Debug: Available profile fields for {user_id}:")
        for key, value in profile.items():
            print(f"  {key}: {value}")
        
        # Check ALL profile fields that might contain LinkedIn URLs
        profile_fields = []
        
        # Check standard profile fields (using module constant)
        for field in _STANDARD_PROFILE_FIELDS:
            value = profile.get(field, '')
            if value:
                profile_fields.append(value)
                print(f"  📝 Checking {field}: {value}")

        # Check custom fields if they exist
        fields = profile.get('fields', {})
        if fields:
            print(f"  📋 Found {len(fields)} custom fields:")
            for field_id, field_data in fields.items():
                if isinstance(field_data, dict):
                    field_value = field_data.get('value', '')
                    field_label = field_data.get('label', f'Field_{field_id}')
                    if field_value:
                        profile_fields.append(field_value)
                        print(f"    {field_label}: {field_value}")
                else:
                    profile_fields.append(str(field_data))
                    print(f"    Field_{field_id}: {field_data}")
        else:
            print(f"  📋 No custom fields found")

        # Search for LinkedIn URLs in all profile fields
        for i, field_text in enumerate(profile_fields):
            if field_text:
                print(f"  🔍 Searching field {i+1} for LinkedIn: {field_text}")
                linkedin_url = extract_linkedin_link(str(field_text))
                if linkedin_url:
                    print(f"  ✅ Found LinkedIn URL in profile field: {linkedin_url}")
                    return linkedin_url
        
        print(f"  ❌ No LinkedIn URL found in any profile fields")
        
        # Fallback: Try to get user info from recent messages
        print(f"🔄 Trying fallback: search for recent messages from user {user_id}")
        try:
            mcp = get_mcp_adapter()
            fallback_result = mcp.slack_find_message(
                instructions=f"Find recent messages from user {user_id} to extract profile information",
                query=f"from:{user_id}",
                sort_by="timestamp",
                sort_dir="desc"
            )
            
            if fallback_result and 'results' in fallback_result and fallback_result['results']:
                # Get the most recent message from this user
                recent_message = fallback_result['results'][0]
                user_info = recent_message.get('user', {})
                if user_info:
                    # Check if we can extract LinkedIn from user's display name or other fields
                    real_name = user_info.get('real_name', '')
                    if real_name and 'linkedin' in real_name.lower():
                        linkedin_match = re.search(r'https?://[^\s]+linkedin[^\s]*', real_name, re.IGNORECASE)
                        if linkedin_match:
                            print(f"✅ Found LinkedIn in fallback search: {linkedin_match.group(0)}")
                            return linkedin_match.group(0)
                    print(f"ℹ️  Fallback found user info but no LinkedIn in profile fields")
                else:
                    print(f"ℹ️  Fallback found messages but no user info")
            else:
                print(f"ℹ️  Fallback: No recent messages found from user {user_id}")
        except Exception as fallback_error:
            print(f"⚠️  Fallback method also failed: {fallback_error}")

        print(f"🏁 Profile search completed for {user_id} - No LinkedIn found")
        return None

    except TimeoutError:
        print(f"⏰ Profile search timed out for user {user_id} after {timeout_seconds} seconds")
        print(f"🏁 Profile search completed for {user_id} - Timed out")
        return None
    except Exception as e:
        print(f"⚠️  Error fetching user profile for {user_id}: {e}")
        print(f"🏁 Profile search completed for {user_id} - Error occurred")
        return None
    finally:
        # Always cancel the alarm and ensure completion message
        if search_started:
            signal.alarm(0)
            print(f"✅ Profile search process finished for {user_id}")

def search_user_profile_for_linkedin_with_fallback(user_id: str, username: str = None, timeout_seconds: int = 45) -> Optional[str]:
    """
    Enhanced search for LinkedIn profile with multiple fallback strategies.
    
    Args:
        user_id: Slack user ID to search
        username: Slack username as fallback
        timeout_seconds: Maximum time to wait for profile search (default: 45)
        
    Returns:
        LinkedIn URL if found, None otherwise
        
    Guarantees:
        - Always returns within timeout_seconds
        - Always prints completion message
        - Never hangs indefinitely
        - Provides clear feedback to daily intros process
    """
    fallback_started = False
    try:
        # Set up timeout for the entire fallback process
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        fallback_started = True
        
        print(f"🚀 Starting comprehensive profile search for {user_id} (timeout: {timeout_seconds}s)")
        
        # First try the main profile search
        linkedin_url = search_user_profile_for_linkedin(user_id, timeout_seconds=30)
        if linkedin_url:
            return linkedin_url
        
        # If no LinkedIn found and we have a username, try searching by username
        if username and username != user_id:
            print(f"🔄 Trying username-based search: {username}")
            try:
                mcp = get_mcp_adapter()
                result = mcp.slack_find_user_by_username(
                    instructions=f"Get profile details for username {username} to check for LinkedIn URL",
                    username=username
                )
                
                if result and 'profile' in result:
                    profile = result['profile']
                    # Check the same standard fields using module constant
                    for field_name in _STANDARD_PROFILE_FIELDS:
                        field_value = profile.get(field_name, '')
                        if field_value:
                            linkedin_url = extract_linkedin_link(str(field_value))
                            if linkedin_url:
                                print(f"✅ Found LinkedIn URL via username search: {linkedin_url}")
                                return linkedin_url
            except Exception as e:
                print(f"⚠️  Username-based search failed: {e}")
        
        print(f"🏁 Comprehensive profile search completed for {user_id} - No LinkedIn found")
        return None
    
    except TimeoutError:
        print(f"⏰ Comprehensive profile search timed out for user {user_id} after {timeout_seconds} seconds")
        print(f"🏁 Profile search completed for {user_id} - Timed out")
        return None
    except Exception as e:
        print(f"⚠️  Error in comprehensive profile search for {user_id}: {e}")
        print(f"🏁 Profile search completed for {user_id} - Error occurred")
        return None
    finally:
        # Always cancel the alarm and ensure completion message
        if fallback_started:
            signal.alarm(0)
            print(f"✅ Comprehensive profile search process finished for {user_id}")

def safe_profile_search_for_daily_intros(user_id: str, username: str = None) -> Optional[str]:
    """
    Safe wrapper for profile search that guarantees completion for daily intros process.
    
    This function provides an additional safety net to ensure the daily intros process
    never hangs waiting for profile search results.
    
    Args:
        user_id: Slack user ID to search
        username: Slack username as fallback
        
    Returns:
        LinkedIn URL if found, None otherwise
        
    Guarantees:
        - Always returns within 60 seconds maximum
        - Always prints completion message
        - Never hangs indefinitely
        - Provides clear feedback to daily intros process
    """
    print(f"🛡️  Starting SAFE profile search for {user_id}")
    
    try:
        # Use a maximum timeout of 60 seconds as absolute safety net
        result = search_user_profile_for_linkedin_with_fallback(
            user_id, 
            username, 
            timeout_seconds=60
        )
        
        if result:
            print(f"🎉 SAFE profile search SUCCESS for {user_id}: {result}")
        else:
            print(f"📋 SAFE profile search COMPLETED for {user_id}: No LinkedIn found")
        
        return result
        
    except Exception as e:
        print(f"🚨 SAFE profile search FAILED for {user_id}: {e}")
        print(f"📋 SAFE profile search COMPLETED for {user_id}: Exception occurred")
        return None
    
    finally:
        print(f"🏁 SAFE profile search FINISHED for {user_id}")
