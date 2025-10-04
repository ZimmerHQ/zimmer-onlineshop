"""
Dashboard router for Zimmer automation system.
Provides Persian UI for token management and user dashboard.
"""

from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import Optional
from database import get_db
from app.services.users_service import UsersService
import uuid

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    user_id: str = Query(..., description="Zimmer user ID"),
    automation_id: str = Query(..., description="Automation ID"),
    tokens: Optional[int] = Query(None, description="Initial token amount"),
    demo_tokens: Optional[int] = Query(None, description="Initial demo token amount"),
    user_email: Optional[str] = Query(None, description="User email"),
    user_name: Optional[str] = Query(None, description="User name")
):
    """
    Get the user dashboard with Persian UI.
    
    Args:
        user_id: The Zimmer user ID (required)
        automation_id: The automation ID (required)
        tokens: Initial token amount (optional)
        demo_tokens: Initial demo token amount (optional)
        user_email: User email (optional)
        user_name: User name (optional)
        
    Returns:
        HTML dashboard with Persian labels and token management
    """
    # Validate required parameters
    if not user_id or not automation_id:
        raise HTTPException(
            status_code=400,
            detail="user_id and automation_id are required"
        )
    
    # Get database session
    db = next(get_db())
    users_service = UsersService(db)
    
    try:
        # Ensure user exists
        user = users_service.ensure_user(
            user_id=user_id,
            automation_id=automation_id,
            email=user_email,
            name=user_name,
            tokens=tokens,
            demo_tokens=demo_tokens
        )
        
        # Create a new session
        session_id = users_service.create_session(user_id, automation_id)
        
        # Get base URL for API calls
        base_url = str(request.base_url).rstrip('/')
        
        # Generate HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>داشبورد زیمر</title>
            <style>
                body {{
                    font-family: 'Tahoma', 'Arial', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #f0f0f0;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 2.5em;
                }}
                .token-display {{
                    display: flex;
                    justify-content: space-around;
                    margin: 30px 0;
                    flex-wrap: wrap;
                }}
                .token-card {{
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    min-width: 200px;
                    margin: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .token-card.demo {{
                    background: linear-gradient(135deg, #FF9800, #F57C00);
                }}
                .token-card h3 {{
                    margin: 0 0 10px 0;
                    font-size: 1.2em;
                }}
                .token-card .amount {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .controls {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .control-group {{
                    margin: 20px 0;
                }}
                .control-group label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .control-group input {{
                    padding: 10px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    width: 200px;
                    font-size: 16px;
                }}
                .btn {{
                    background: #3498db;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 5px;
                    transition: background 0.3s;
                }}
                .btn:hover {{
                    background: #2980b9;
                }}
                .btn:disabled {{
                    background: #bdc3c7;
                    cursor: not-allowed;
                }}
                .status {{
                    margin: 20px 0;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }}
                .status.success {{
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }}
                .status.error {{
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }}
                .hidden {{
                    display: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>خوش آمدید</h1>
                    <p>داشبورد مدیریت توکن‌های زیمر</p>
                </div>
                
                <div class="token-display">
                    <div class="token-card">
                        <h3>توکن‌های باقیمانده</h3>
                        <div class="amount" id="tokens-remaining">{user.tokens_remaining}</div>
                    </div>
                    <div class="token-card demo">
                        <h3>توکن آزمایشی</h3>
                        <div class="amount" id="demo-tokens">{user.demo_tokens}</div>
                    </div>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label for="consume-amount">مقدار مصرف توکن:</label>
                        <input type="number" id="consume-amount" min="1" value="1">
                    </div>
                    <div class="control-group">
                        <label for="consume-action">نوع عملیات:</label>
                        <input type="text" id="consume-action" placeholder="مثال: chat, search, etc." value="chat">
                    </div>
                    <button class="btn" onclick="consumeTokens()">مصرف توکن</button>
                </div>
                
                <div id="status" class="status hidden"></div>
            </div>
            
            <script>
                // Store user data in localStorage
                const userData = {{
                    user_id: '{user_id}',
                    automation_id: '{automation_id}',
                    session_id: '{session_id}',
                    base_url: '{base_url}'
                }};
                localStorage.setItem('zimmer_user', JSON.stringify(userData));
                
                // Function to consume tokens
                async function consumeTokens() {{
                    const amount = parseInt(document.getElementById('consume-amount').value);
                    const action = document.getElementById('consume-action').value;
                    
                    if (!amount || amount <= 0) {{
                        showStatus('لطفاً مقدار معتبری وارد کنید', 'error');
                        return;
                    }}
                    
                    if (!action.trim()) {{
                        showStatus('لطفاً نوع عملیات را وارد کنید', 'error');
                        return;
                    }}
                    
                    try {{
                        const response = await fetch('{base_url}/api/consume-tokens', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                user_id: '{user_id}',
                                automation_id: '{automation_id}',
                                tokens_consumed: amount,
                                action: action,
                                session_id: '{session_id}'
                            }})
                        }});
                        
                        const result = await response.json();
                        
                        if (response.ok && result.success) {{
                            // Update token display
                            document.getElementById('tokens-remaining').textContent = result.remaining_tokens;
                            showStatus(`توکن با موفقیت مصرف شد. باقیمانده: ${{result.remaining_tokens}}`, 'success');
                        }} else {{
                            showStatus(`خطا: ${{result.detail || 'خطای نامشخص'}}`, 'error');
                        }}
                    }} catch (error) {{
                        showStatus(`خطای شبکه: ${{error.message}}`, 'error');
                    }}
                }}
                
                // Function to show status messages
                function showStatus(message, type) {{
                    const statusDiv = document.getElementById('status');
                    statusDiv.textContent = message;
                    statusDiv.className = `status ${{type}}`;
                    statusDiv.classList.remove('hidden');
                    
                    // Hide after 5 seconds
                    setTimeout(() => {{
                        statusDiv.classList.add('hidden');
                    }}, 5000);
                }}
                
                // Make consumeTokens available globally
                window.consumeTokens = consumeTokens;
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating dashboard: {str(e)}"
        )
    finally:
        db.close()

