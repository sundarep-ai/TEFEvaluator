#!/usr/bin/env python3
"""
Test script for the new progress tracking functionality
"""

import asyncio
import json
import time
from main import run_evaluation_background, evaluation_progress

# Mock data for testing
class MockRequest:
    def __init__(self):
        self.task_a_question = "Test question A"
        self.task_a_response = "Test response A"
        self.task_b_question = "Test question B"
        self.task_b_response = "Test response B"

class MockDB:
    def add(self, obj):
        pass
    
    def commit(self):
        pass
    
    def refresh(self, obj):
        obj.id = 1

async def test_progress_tracking():
    """Test the progress tracking functionality"""
    print("Testing progress tracking...")
    
    # Create mock evaluation
    eval_id = "test-123"
    evaluation_progress[eval_id] = {
        "eval1_status": "starting",
        "eval2_status": "waiting",
        "judge_status": "waiting",
        "current_step": "eval1",
        "overall_progress": 0,
        "completed": False,
        "result": None,
        "error": None,
        "created_at": time.time()
    }
    
    # Start background evaluation
    mock_request = MockRequest()
    mock_db = MockDB()
    
    print(f"Starting evaluation with ID: {eval_id}")
    
    # Run the background task
    await run_evaluation_background(eval_id, mock_request, 1, mock_db)
    
    # Check final progress
    final_progress = evaluation_progress.get(eval_id)
    if final_progress:
        print(f"Final progress: {json.dumps(final_progress, indent=2)}")
        print(f"Evaluation completed: {final_progress['completed']}")
        if final_progress['result']:
            print(f"Score: {final_progress['result']['score']}")
    else:
        print("No progress data found")
    
    # Clean up
    if eval_id in evaluation_progress:
        del evaluation_progress[eval_id]

if __name__ == "__main__":
    print("TEF Evaluator Progress Tracking Test")
    print("=" * 40)
    
    try:
        asyncio.run(test_progress_tracking())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
