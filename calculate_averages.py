#!/usr/bin/env python3
"""
Calculate average Zimmer Token metrics
"""

from token_calculator import calculator

def calculate_averages():
    """Calculate average Zimmer Token metrics"""
    
    # Test multiple scenarios to get averages
    scenarios = [
        {'tokens': 1000, 'turns': 1, 'model': 'gpt-3.5-turbo', 'desc': 'Short conversation'},
        {'tokens': 1000, 'turns': 5, 'model': 'gpt-3.5-turbo', 'desc': 'Medium conversation'},
        {'tokens': 1000, 'turns': 10, 'model': 'gpt-3.5-turbo', 'desc': 'Long conversation'},
        {'tokens': 1000, 'turns': 5, 'model': 'gpt-4', 'desc': 'GPT-4 conversation'},
        {'tokens': 2000, 'turns': 5, 'model': 'gpt-3.5-turbo', 'desc': 'High token usage'},
        {'tokens': 500, 'turns': 20, 'model': 'gpt-3.5-turbo', 'desc': 'Very long conversation'},
        {'tokens': 1500, 'turns': 3, 'model': 'gpt-3.5-turbo', 'desc': 'Medium-high usage'},
        {'tokens': 800, 'turns': 8, 'model': 'gpt-3.5-turbo', 'desc': 'Medium-long conversation'},
        {'tokens': 1200, 'turns': 6, 'model': 'gpt-3.5-turbo', 'desc': 'Balanced conversation'},
        {'tokens': 3000, 'turns': 15, 'model': 'gpt-3.5-turbo', 'desc': 'Very high usage'},
    ]
    
    ratios = []
    costs_per_zimmer = []
    zimmer_tokens_list = []
    total_costs = []
    total_tokens = []
    total_turns = []
    
    print("🎯 Average Zimmer Token Calculations")
    print("=" * 60)
    
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
        
        ratios.append(ratio)
        costs_per_zimmer.append(cost_per_zimmer)
        zimmer_tokens_list.append(usage.zimmer_tokens)
        total_costs.append(usage.cost_usd)
        total_tokens.append(usage.total_tokens)
        total_turns.append(scenario['turns'])
        
        print(f"Test {i:2d}: {ratio:6.2f}:1 ratio, ${cost_per_zimmer:8.6f} per Zimmer, ${usage.cost_usd:8.6f} total - {scenario['desc']}")
    
    print("\n" + "=" * 60)
    print("📊 AVERAGE METRICS:")
    print(f"Average ratio: {sum(ratios)/len(ratios):.2f} OpenAI tokens per 1 Zimmer token")
    print(f"Average cost per Zimmer: ${sum(costs_per_zimmer)/len(costs_per_zimmer):.6f}")
    print(f"Average Zimmer tokens: {sum(zimmer_tokens_list)/len(zimmer_tokens_list):.1f}")
    print(f"Average total cost: ${sum(total_costs)/len(total_costs):.6f}")
    print(f"Average total tokens: {sum(total_tokens)/len(total_tokens):.0f}")
    print(f"Average conversation turns: {sum(total_turns)/len(total_turns):.1f}")
    
    print("\n🎯 KEY INSIGHTS:")
    print(f"• 1 Zimmer Token = {sum(ratios)/len(ratios):.1f} OpenAI tokens (on average)")
    print(f"• Cost of 1 Zimmer Token = ${sum(costs_per_zimmer)/len(costs_per_zimmer):.6f} (on average)")
    print(f"• Average conversation has {sum(total_turns)/len(total_turns):.1f} turns")
    print(f"• Average conversation uses {sum(total_tokens)/len(total_tokens):.0f} OpenAI tokens")
    print(f"• Average conversation costs ${sum(total_costs)/len(total_costs):.6f}")

if __name__ == "__main__":
    calculate_averages()
