#!/usr/bin/env python3
"""
Test script for AI question generation endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ai_question_generation():
    """Test the new AI question generation endpoints"""
    
    print("🧪 Testing AI Question Generation Endpoints")
    print("=" * 50)
    
    # Test Task A question generation
    print("\n📝 Testing Task A Question Generation...")
    try:
        response = requests.get(f"{BASE_URL}/api/questions/generate/task-a")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task A Question Generated Successfully!")
            print(f"📋 Question: {data.get('question', 'No question found')}")
        else:
            print(f"❌ Task A generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Task A generation: {e}")
    
    # Test Task B question generation
    print("\n📝 Testing Task B Question Generation...")
    try:
        response = requests.get(f"{BASE_URL}/api/questions/generate/task-b")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task B Question Generated Successfully!")
            print(f"📋 Question: {data.get('question', 'No question found')}")
        else:
            print(f"❌ Task B generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Task B generation: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_ai_question_generation()
