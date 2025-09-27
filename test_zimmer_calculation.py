#!/usr/bin/env python3
"""
Test Zimmer Token calculations with different scenarios
"""

from token_calculator import calculator

def test_zimmer_calculations():
    """Test Zimmer Token calculations with different scenarios"""
    
    print("🎯 Zimmer Token Calculations - Different Scenarios")
    print("=" * 60)
    
    # Test different scenarios
    scenarios = [
        {'tokens': 1000, 'turns': 1, 'model': 'gpt-3.5-turbo', 'desc': 'Short conversation (1 turn)'},
        {'tokens': 1000, 'turns': 5, 'model': 'gpt-3.5-turbo', 'desc': 'Medium conversation (5 turns)'},
        {'tokens': 1000, 'turns': 10, 'model': 'gpt-3.5-turbo', 'desc': 'Long conversation (10 turns)'},
        {'tokens': 1000, 'turns': 5, 'model': 'gpt-4', 'desc': 'GPT-4 medium conversation'},
        {'tokens': 2000, 'turns': 5, 'model': 'gpt-3.5-turbo', 'desc': 'High token usage (5 turns)'},
        {'tokens': 500, 'turns': 20, 'model': 'gpt-3.5-turbo', 'desc': 'Very long conversation (20 turns)'},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        usage = calculator.log_usage(
            f'test_{i}', 
            scenario['tokens'], 
            0, 
            scenario['model'], 
            scenario['turns']
        )
        
        ratio = usage.total_tokens / usage.zimmer_tokens
        cost_per_zimmer = usage.cost_usd / usage.zimmer_tokens
        
        print(f"\nScenario {i}: {scenario['desc']}")
        print(f"  OpenAI tokens: {usage.total_tokens:,}")
        print(f"  Conversation turns: {scenario['turns']}")
        print(f"  Model: {scenario['model']}")
        print(f"  Zimmer tokens: {usage.zimmer_tokens:,}")
        print(f"  Ratio: {ratio:.2f} OpenAI tokens per 1 Zimmer token")
        print(f"  Cost per Zimmer token: ${cost_per_zimmer:.6f}")
        print(f"  Total cost: ${usage.cost_usd:.6f}")
    
    print("\n" + "=" * 60)
    print("📊 KEY INSIGHTS:")
    print("• Zimmer Tokens = OpenAI tokens ÷ conversation turns × efficiency multiplier")
    print("• Lower conversation turns = Higher Zimmer Tokens")
    print("• GPT-4 has higher efficiency multiplier than GPT-3.5-turbo")
    print("• More conversation turns = Lower Zimmer Tokens (more efficient)")
    print("• 1 Zimmer Token represents the 'efficiency' of token usage per turn")

if __name__ == "__main__":
    test_zimmer_calculations()
