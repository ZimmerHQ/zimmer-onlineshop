#!/usr/bin/env python3
"""
Simple test script to check database connection.
"""
import os

from database import get_db
from services.chat_order import create_order_from_chat
from services.chat_state import get_state, set_state

conv_id = 'test123'
db = next(get_db())

# Set up test state
test_state = {
    'selected_product': {
        'id': 1,
        'name': 'شلوار جین',
        'code': 'A0001',
        'price': 150000.0
    },
    'wanted': {
        'qty': 1,
        'size': None,
        'color': None
    }
}
set_state(conv_id, test_state)
print(f'Initial state: {get_state(conv_id)}')

try:
    order = create_order_from_chat(db, conv_id, {}, {'product_id': 1, 'quantity': 1, 'meta': {'size': None, 'color': None}})
    print(f'Order created: {order.order_number}')
    print(f'State after: {get_state(conv_id)}')
except Exception as e:
    print(f'Error: {e}')
    print(f'State after error: {get_state(conv_id)}') 