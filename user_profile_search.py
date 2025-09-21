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

def extract_linkedin_link(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text using regex"""
    if not text:
        return None
    
    # Enhanced LinkedIn URL patterns
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[^\s\)]+',
        r'https?://(?:www\.)?linkedin\.com/pub/[^\s\)]+',
        r'linkedin\.com/in/[^\s\)]+',
        r'linkedin\.com/pub/[^\s\)]+',
    ]
    
    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            # Ensure URL has protocol
            if not url.startswith('http'):
                url = 'https://' + url
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
    """
    try:
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
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
        
        # Standard profile fields
        standard_fields = [
            'status_text', 'title', 'phone', 'skype', 'real_name_normalized',
            'display_name', 'display_name_normalized', 'real_name', 'email'
        ]
        
        for field in standard_fields:
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
                            return linkedin_match.group(0)
                    print(f"ℹ️  Fallback found user info but no LinkedIn in profile fields")
                else:
                    print(f"ℹ️  Fallback found messages but no user info")
            else:
                print(f"ℹ️  Fallback: No recent messages found from user {user_id}")
        except Exception as fallback_error:
            print(f"⚠️  Fallback method also failed: {fallback_error}")

        return None

    except TimeoutError:
        print(f"⏰ Profile search timed out for user {user_id}")
        return None
    except Exception as e:
        print(f"⚠️  Error fetching user profile for {user_id}: {e}")
        return None
    finally:
        # Always cancel the alarm
        signal.alarm(0)

def search_user_profile_for_linkedin_with_fallback(user_id: str, username: str = None, timeout_seconds: int = 45) -> Optional[str]:
    """
    Enhanced search for LinkedIn profile with multiple fallback strategies.
    
    Args:
        user_id: Slack user ID to search
        username: Slack username as fallback
        timeout_seconds: Maximum time to wait for profile search (default: 45)
        
    Returns:
        LinkedIn URL if found, None otherwise
    """
    try:
        # Set up timeout for the entire fallback process
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
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
                    # Check the same fields as above
                    for field_name in ['status_text', 'title', 'display_name', 'real_name']:
                        field_value = profile.get(field_name, '')
                        if field_value:
                            linkedin_url = extract_linkedin_link(str(field_value))
                            if linkedin_url:
                                print(f"✅ Found LinkedIn URL via username search: {linkedin_url}")
                                return linkedin_url
            except Exception as e:
                print(f"⚠️  Username-based search failed: {e}")
        
        return None
    
    except TimeoutError:
        print(f"⏰ Profile search with fallback timed out for user {user_id}")
        return None
    except Exception as e:
        print(f"⚠️  Error in fallback profile search for {user_id}: {e}")
        return None
    finally:
        # Always cancel the alarm
        signal.alarm(0)
