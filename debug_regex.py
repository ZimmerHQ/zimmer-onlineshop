#!/usr/bin/env python3
"""
Debug script to test regex patterns and code extraction
"""

import re

# Test the regex pattern
CODE_RE = re.compile(r"\b([A-Z]{1,3}-?\d{3,})\b", re.IGNORECASE)

def extract_code(text: str):
    if not text: return None
    m = CODE_RE.search(text)
    return m.group(1).upper() if m else None

# Test cases
test_cases = [
    "A0001",
    "A0001 ",
    " A0001",
    " A0001 ",
    "کد A0001 رو میخوام",
    "A-0001",
    "ABC123",
    "A123",
    "A12",
    "شلوار دارین"
]

print("Testing regex pattern and code extraction:")
print("=" * 50)

for test in test_cases:
    result = extract_code(test)
    print(f"'{test}' -> '{result}'")

print("\nRegex pattern:", CODE_RE.pattern) 