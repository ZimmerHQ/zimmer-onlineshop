#!/usr/bin/env python3
"""
Token Tracking Integration for Shop Automation System
Integrates with existing chat system to track OpenAI token usage
"""

import json
import time
from datetime import datetime
from typing import Dict, Optional
import os
from token_calculator import calculator, log_chat_usage, get_session_report, get_global_report, get_optimization_plan

class TokenTracker:
    """Token tracking integration for the chat system"""
    
    def __init__(self):
        self.session_conversation_lengths = {}
        
    def track_chat_request(self, session_id: str, user_message: str, model: str = "gpt-3.5-turbo"):
        """Track a chat request (before sending to OpenAI)"""
        if session_id not in self.session_conversation_lengths:
            self.session_conversation_lengths[session_id] = 0
        self.session_conversation_lengths[session_id] += 1
        
        return {
            "session_id": session_id,
            "user_message": user_message,
            "model": model,
            "conversation_length": self.session_conversation_lengths[session_id],
            "timestamp": datetime.now().isoformat()
        }
    
    def track_chat_response(self, session_id: str, response_data: Dict, model: str = "gpt-3.5-turbo"):
        """Track a chat response (after receiving from OpenAI)"""
        # Extract token usage from OpenAI response
        # This would typically come from the OpenAI API response
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        conversation_length = self.session_conversation_lengths.get(session_id, 1)
        
        # Log the usage
        usage_record = log_chat_usage(
            session_id=session_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
            conversation_length=conversation_length
        )
        
        return usage_record
    
    def get_session_dashboard(self, session_id: str) -> Dict:
        """Get dashboard data for a specific session"""
        report = get_session_report(session_id)
        if "error" in report:
            return report
        
        # Add additional session info
        report["session_info"] = {
            "conversation_length": self.session_conversation_lengths.get(session_id, 0),
            "last_activity": datetime.now().isoformat()
        }
        
        return report
    
    def get_global_dashboard(self) -> Dict:
        """Get global dashboard data"""
        global_report = get_global_report()
        
        # Add additional global info
        global_report["system_info"] = {
            "active_sessions": len(self.session_conversation_lengths),
            "total_conversation_turns": sum(self.session_conversation_lengths.values()),
            "last_updated": datetime.now().isoformat()
        }
        
        return global_report
    
    def get_optimization_dashboard(self) -> Dict:
        """Get optimization recommendations dashboard"""
        optimization = get_optimization_plan()
        
        # Add implementation timeline
        optimization["implementation_timeline"] = {
            "immediate": [r for r in optimization["recommendations"] if r["priority"] == "High"],
            "short_term": [r for r in optimization["recommendations"] if r["priority"] == "Medium"],
            "long_term": [r for r in optimization["recommendations"] if r["priority"] == "Low"]
        }
        
        return optimization
    
    def export_session_data(self, session_id: str) -> str:
        """Export data for a specific session"""
        if session_id not in self.session_conversation_lengths:
            return None
        
        data = {
            "session_id": session_id,
            "export_timestamp": datetime.now().isoformat(),
            "session_report": self.get_session_dashboard(session_id),
            "conversation_length": self.session_conversation_lengths[session_id]
        }
        
        filename = f"session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename

# Global tracker instance
tracker = TokenTracker()

def track_openai_usage(session_id: str, prompt_tokens: int, completion_tokens: int, 
                      model: str = "gpt-3.5-turbo"):
    """Convenience function to track OpenAI usage"""
    conversation_length = tracker.session_conversation_lengths.get(session_id, 1)
    return log_chat_usage(session_id, prompt_tokens, completion_tokens, model, conversation_length)

def get_token_dashboard():
    """Get comprehensive token usage dashboard"""
    return {
        "global": tracker.get_global_dashboard(),
        "optimization": tracker.get_optimization_dashboard(),
        "active_sessions": list(tracker.session_conversation_lengths.keys())
    }

def get_session_token_info(session_id: str):
    """Get token information for a specific session"""
    return tracker.get_session_dashboard(session_id)

# Integration with existing chat system
def integrate_with_chat_router():
    """
    Integration instructions for the chat router
    Add this to your chat router to track token usage
    """
    integration_code = '''
# Add this to your chat router (routers/chat.py)

from token_tracker import track_openai_usage

# In your chat endpoint, after getting the OpenAI response:
# Extract token usage from the response
usage = response.get("usage", {})
prompt_tokens = usage.get("prompt_tokens", 0)
completion_tokens = usage.get("completion_tokens", 0)

# Track the usage
track_openai_usage(
    session_id=payload.conversation_id,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    model="gpt-3.5-turbo"  # or whatever model you're using
)
    '''
    return integration_code

if __name__ == "__main__":
    print("🔍 Token Tracker Integration")
    print("=" * 40)
    
    # Simulate some usage
    print("\n📊 Simulating token tracking...")
    
    # Track some sessions
    tracker.track_chat_request("user_001", "سلام، محصولات را ببینم", "gpt-3.5-turbo")
    tracker.track_chat_response("user_001", {
        "usage": {"prompt_tokens": 150, "completion_tokens": 100}
    }, "gpt-3.5-turbo")
    
    tracker.track_chat_request("user_002", "قیمت کفش چقدر است؟", "gpt-4")
    tracker.track_chat_response("user_002", {
        "usage": {"prompt_tokens": 200, "completion_tokens": 150}
    }, "gpt-4")
    
    # Display dashboards
    print("\n📈 Global Dashboard:")
    global_dashboard = tracker.get_global_dashboard()
    print(f"Total Tokens: {global_dashboard['total_tokens']:,}")
    print(f"Total Cost: ${global_dashboard['total_cost_usd']:.4f}")
    print(f"Active Sessions: {global_dashboard['system_info']['active_sessions']}")
    
    print("\n📋 Session Dashboards:")
    for session_id in ["user_001", "user_002"]:
        session_info = tracker.get_session_token_info(session_id)
        print(f"\nSession {session_id}:")
        print(f"  Tokens: {session_info['total_tokens']:,}")
        print(f"  Cost: {session_info['total_cost_usd']}")
        print(f"  Zimmer Tokens: {session_info['total_zimmer_tokens']:,}")
        print(f"  Efficiency: {session_info['efficiency_score']}")
    
    print("\n🎯 Optimization Dashboard:")
    optimization = tracker.get_optimization_dashboard()
    print(f"Recommendations: {optimization['total_recommendations']}")
    print(f"Estimated Savings: {optimization['estimated_total_savings']}")
    
    print("\n✨ Token Tracker ready for integration!")

