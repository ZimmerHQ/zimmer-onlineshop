#!/usr/bin/env python3
"""
OpenAI Token Usage Calculator and Optimization System
Tracks token usage per session and provides optimization recommendations
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dataclasses import dataclass, asdict
import requests

@dataclass
class TokenUsage:
    """Token usage data for a single session"""
    session_id: str
    timestamp: datetime
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float
    conversation_length: int
    zimmer_tokens: int  # Our custom metric

@dataclass
class SessionMetrics:
    """Aggregated metrics for a session"""
    session_id: str
    total_tokens: int
    total_cost_usd: float
    total_zimmer_tokens: int
    conversation_turns: int
    avg_tokens_per_turn: float
    efficiency_score: float  # 0-100, higher is better
    optimization_potential: str

class TokenCalculator:
    """Main token calculator and optimizer"""
    
    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self.session_data: Dict[str, List[TokenUsage]] = {}
        self.model_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        }
        
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on model and token usage"""
        if model not in self.model_costs:
            model = "gpt-3.5-turbo"  # Default fallback
            
        input_cost = (prompt_tokens / 1000) * self.model_costs[model]["input"]
        output_cost = (completion_tokens / 1000) * self.model_costs[model]["output"]
        return input_cost + output_cost
    
    def calculate_zimmer_tokens(self, total_tokens: int, conversation_length: int, model: str) -> int:
        """
        Calculate Zimmer Tokens - our custom efficiency metric
        1 Zimmer Token = 1 token used per meaningful conversation turn
        
        Formula: total_tokens / max(conversation_length, 1) * efficiency_multiplier
        """
        base_zimmer = total_tokens / max(conversation_length, 1)
        
        # Efficiency multipliers based on model
        efficiency_multipliers = {
            "gpt-4": 1.0,      # Baseline
            "gpt-4-turbo": 0.8,  # More efficient
            "gpt-3.5-turbo": 0.6,  # Less efficient but cheaper
            "gpt-3.5-turbo-16k": 0.7,
        }
        
        multiplier = efficiency_multipliers.get(model, 1.0)
        return int(base_zimmer * multiplier)
    
    def log_usage(self, session_id: str, prompt_tokens: int, completion_tokens: int, 
                  model: str, conversation_length: int = 1):
        """Log token usage for a session"""
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        zimmer_tokens = self.calculate_zimmer_tokens(total_tokens, conversation_length, model)
        
        usage = TokenUsage(
            session_id=session_id,
            timestamp=datetime.now(),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
            cost_usd=cost,
            conversation_length=conversation_length,
            zimmer_tokens=zimmer_tokens
        )
        
        self.usage_history.append(usage)
        
        if session_id not in self.session_data:
            self.session_data[session_id] = []
        self.session_data[session_id].append(usage)
        
        return usage
    
    def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get aggregated metrics for a session"""
        if session_id not in self.session_data:
            return None
            
        session_usages = self.session_data[session_id]
        total_tokens = sum(u.total_tokens for u in session_usages)
        total_cost = sum(u.cost_usd for u in session_usages)
        total_zimmer = sum(u.zimmer_tokens for u in session_usages)
        conversation_turns = len(session_usages)
        avg_tokens_per_turn = total_tokens / max(conversation_turns, 1)
        
        # Calculate efficiency score (0-100)
        # Lower tokens per turn = higher efficiency
        max_efficient_tokens = 500  # Baseline for "efficient" conversation
        efficiency_score = max(0, 100 - (avg_tokens_per_turn / max_efficient_tokens * 100))
        
        # Determine optimization potential
        if efficiency_score >= 80:
            optimization_potential = "Excellent - No optimization needed"
        elif efficiency_score >= 60:
            optimization_potential = "Good - Minor optimizations possible"
        elif efficiency_score >= 40:
            optimization_potential = "Fair - Moderate optimizations recommended"
        else:
            optimization_potential = "Poor - Major optimizations required"
        
        return SessionMetrics(
            session_id=session_id,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            total_zimmer_tokens=total_zimmer,
            conversation_turns=conversation_turns,
            avg_tokens_per_turn=avg_tokens_per_turn,
            efficiency_score=efficiency_score,
            optimization_potential=optimization_potential
        )
    
    def get_global_metrics(self) -> Dict:
        """Get global metrics across all sessions"""
        if not self.usage_history:
            return {"error": "No usage data available"}
            
        total_tokens = sum(u.total_tokens for u in self.usage_history)
        total_cost = sum(u.cost_usd for u in self.usage_history)
        total_sessions = len(self.session_data)
        total_zimmer_tokens = sum(u.zimmer_tokens for u in self.usage_history)
        
        # Model usage breakdown
        model_usage = {}
        for usage in self.usage_history:
            model = usage.model
            if model not in model_usage:
                model_usage[model] = {"tokens": 0, "cost": 0, "sessions": 0}
            model_usage[model]["tokens"] += usage.total_tokens
            model_usage[model]["cost"] += usage.cost_usd
            model_usage[model]["sessions"] += 1
        
        return {
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "total_sessions": total_sessions,
            "total_zimmer_tokens": total_zimmer_tokens,
            "avg_tokens_per_session": total_tokens / max(total_sessions, 1),
            "avg_cost_per_session": total_cost / max(total_sessions, 1),
            "model_breakdown": model_usage,
            "efficiency_rating": self.calculate_global_efficiency()
        }
    
    def calculate_global_efficiency(self) -> str:
        """Calculate overall system efficiency rating"""
        if not self.usage_history:
            return "No data"
            
        total_tokens = sum(u.total_tokens for u in self.usage_history)
        total_conversations = sum(u.conversation_length for u in self.usage_history)
        avg_tokens_per_conversation = total_tokens / max(total_conversations, 1)
        
        if avg_tokens_per_conversation <= 300:
            return "Excellent (≤300 tokens/conversation)"
        elif avg_tokens_per_conversation <= 500:
            return "Good (≤500 tokens/conversation)"
        elif avg_tokens_per_conversation <= 800:
            return "Fair (≤800 tokens/conversation)"
        else:
            return "Poor (>800 tokens/conversation)"
    
    def generate_optimization_plan(self) -> Dict:
        """Generate optimization recommendations"""
        if not self.usage_history:
            return {"error": "No usage data available"}
        
        recommendations = []
        
        # Analyze token usage patterns
        avg_tokens = sum(u.total_tokens for u in self.usage_history) / len(self.usage_history)
        high_token_sessions = [s for s in self.session_data.values() 
                              if sum(u.total_tokens for u in s) > avg_tokens * 1.5]
        
        # Model usage analysis
        model_usage = {}
        for usage in self.usage_history:
            model = usage.model
            if model not in model_usage:
                model_usage[model] = {"tokens": 0, "cost": 0, "count": 0}
            model_usage[model]["tokens"] += usage.total_tokens
            model_usage[model]["cost"] += usage.cost_usd
            model_usage[model]["count"] += 1
        
        # Generate recommendations
        if len(high_token_sessions) > len(self.session_data) * 0.3:
            recommendations.append({
                "category": "Conversation Length",
                "priority": "High",
                "issue": f"{len(high_token_sessions)} sessions using excessive tokens",
                "solution": "Implement conversation summarization and context window management",
                "potential_savings": "20-40% token reduction"
            })
        
        # Model optimization
        if "gpt-4" in model_usage and "gpt-3.5-turbo" in model_usage:
            gpt4_usage = model_usage["gpt-4"]["tokens"]
            gpt35_usage = model_usage["gpt-3.5-turbo"]["tokens"]
            
            if gpt4_usage > gpt35_usage * 2:
                recommendations.append({
                    "category": "Model Selection",
                    "priority": "Medium",
                    "issue": "Overusing expensive GPT-4 model",
                    "solution": "Use GPT-3.5-turbo for simpler queries, GPT-4 only for complex reasoning",
                    "potential_savings": "60-70% cost reduction"
                })
        
        # Prompt optimization
        avg_prompt_tokens = sum(u.prompt_tokens for u in self.usage_history) / len(self.usage_history)
        if avg_prompt_tokens > 1000:
            recommendations.append({
                "category": "Prompt Engineering",
                "priority": "High",
                "issue": f"Average prompt length is {avg_prompt_tokens:.0f} tokens",
                "solution": "Optimize system prompts and reduce context window size",
                "potential_savings": "15-30% token reduction"
            })
        
        # Session management
        if len(self.session_data) > 10:
            avg_session_length = sum(len(s) for s in self.session_data.values()) / len(self.session_data)
            if avg_session_length > 10:
                recommendations.append({
                    "category": "Session Management",
                    "priority": "Medium",
                    "issue": f"Average session length is {avg_session_length:.1f} turns",
                    "solution": "Implement session timeout and conversation archiving",
                    "potential_savings": "10-20% token reduction"
                })
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "estimated_total_savings": "30-60% token and cost reduction",
            "implementation_priority": sorted(recommendations, key=lambda x: x["priority"], reverse=True)
        }
    
    def export_data(self, filename: str = None):
        """Export usage data to JSON file"""
        if not filename:
            filename = f"token_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "global_metrics": self.get_global_metrics(),
            "session_data": {sid: [asdict(u) for u in usages] for sid, usages in self.session_data.items()},
            "optimization_plan": self.generate_optimization_plan()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return filename

# Global calculator instance
calculator = TokenCalculator()

def log_chat_usage(session_id: str, prompt_tokens: int, completion_tokens: int, 
                   model: str = "gpt-3.5-turbo", conversation_length: int = 1):
    """Convenience function to log chat usage"""
    return calculator.log_usage(session_id, prompt_tokens, completion_tokens, model, conversation_length)

def get_session_report(session_id: str):
    """Get detailed report for a session"""
    metrics = calculator.get_session_metrics(session_id)
    if not metrics:
        return {"error": f"Session {session_id} not found"}
    
    return {
        "session_id": session_id,
        "total_tokens": metrics.total_tokens,
        "total_cost_usd": f"${metrics.total_cost_usd:.4f}",
        "total_zimmer_tokens": metrics.total_zimmer_tokens,
        "conversation_turns": metrics.conversation_turns,
        "avg_tokens_per_turn": f"{metrics.avg_tokens_per_turn:.1f}",
        "efficiency_score": f"{metrics.efficiency_score:.1f}/100",
        "optimization_potential": metrics.optimization_potential
    }

def get_global_report():
    """Get global usage report"""
    return calculator.get_global_metrics()

def get_optimization_plan():
    """Get optimization recommendations"""
    return calculator.generate_optimization_plan()

# Example usage and testing
if __name__ == "__main__":
    print("🔢 OpenAI Token Calculator & Optimization System")
    print("=" * 60)
    
    # Simulate some usage data
    print("\n📊 Simulating usage data...")
    
    # Session 1: Efficient conversation
    log_chat_usage("session_001", 150, 100, "gpt-3.5-turbo", 3)
    log_chat_usage("session_001", 200, 120, "gpt-3.5-turbo", 3)
    log_chat_usage("session_001", 180, 110, "gpt-3.5-turbo", 3)
    
    # Session 2: Inefficient conversation
    log_chat_usage("session_002", 800, 400, "gpt-4", 2)
    log_chat_usage("session_002", 1000, 500, "gpt-4", 2)
    
    # Session 3: Mixed usage
    log_chat_usage("session_003", 300, 200, "gpt-3.5-turbo", 5)
    log_chat_usage("session_003", 500, 300, "gpt-4", 5)
    log_chat_usage("session_003", 250, 150, "gpt-3.5-turbo", 5)
    
    # Display reports
    print("\n📈 Global Report:")
    global_report = get_global_report()
    print(f"Total Tokens: {global_report['total_tokens']:,}")
    print(f"Total Cost: ${global_report['total_cost_usd']:.4f}")
    print(f"Total Sessions: {global_report['total_sessions']}")
    print(f"Total Zimmer Tokens: {global_report['total_zimmer_tokens']:,}")
    print(f"Efficiency Rating: {global_report['efficiency_rating']}")
    
    print("\n📋 Session Reports:")
    for session_id in ["session_001", "session_002", "session_003"]:
        report = get_session_report(session_id)
        print(f"\nSession {session_id}:")
        print(f"  Tokens: {report['total_tokens']:,}")
        print(f"  Cost: {report['total_cost_usd']}")
        print(f"  Zimmer Tokens: {report['total_zimmer_tokens']:,}")
        print(f"  Efficiency: {report['efficiency_score']}")
        print(f"  Status: {report['optimization_potential']}")
    
    print("\n🎯 Optimization Plan:")
    optimization = get_optimization_plan()
    print(f"Total Recommendations: {optimization['total_recommendations']}")
    print(f"Estimated Savings: {optimization['estimated_total_savings']}")
    
    for i, rec in enumerate(optimization['recommendations'], 1):
        print(f"\n{i}. {rec['category']} ({rec['priority']} Priority)")
        print(f"   Issue: {rec['issue']}")
        print(f"   Solution: {rec['solution']}")
        print(f"   Savings: {rec['potential_savings']}")
    
    # Export data
    filename = calculator.export_data()
    print(f"\n💾 Data exported to: {filename}")
    
    print("\n✨ Token Calculator setup complete!")

