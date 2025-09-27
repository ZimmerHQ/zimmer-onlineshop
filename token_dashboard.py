#!/usr/bin/env python3
"""
Token Usage Dashboard - Web Interface
Provides a web dashboard for monitoring OpenAI token usage and optimization
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime
from token_tracker import tracker, get_token_dashboard, get_session_token_info
from token_calculator import calculator

app = FastAPI(title="Token Usage Dashboard", version="1.0.0")

# Templates setup
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    dashboard_data = get_token_dashboard()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "data": dashboard_data
    })

@app.get("/api/dashboard")
async def api_dashboard():
    """API endpoint for dashboard data"""
    return get_token_dashboard()

@app.get("/api/session/{session_id}")
async def api_session(session_id: str):
    """API endpoint for session data"""
    return get_session_token_info(session_id)

@app.get("/api/optimization")
async def api_optimization():
    """API endpoint for optimization recommendations"""
    return tracker.get_optimization_dashboard()

@app.get("/api/export")
async def api_export():
    """Export all token usage data"""
    filename = calculator.export_data()
    return {"filename": filename, "message": "Data exported successfully"}

@app.get("/api/sessions")
async def api_sessions():
    """Get list of all sessions"""
    return {
        "sessions": list(tracker.session_conversation_lengths.keys()),
        "total_sessions": len(tracker.session_conversation_lengths)
    }

# Create templates directory and dashboard template
import os
os.makedirs("templates", exist_ok=True)

dashboard_template = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Token Usage Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .zimmer-token { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: bold;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">Token Usage Dashboard</h1>
                    <p class="text-gray-600 mt-2">نظارت بر استفاده از توکن‌های OpenAI و بهینه‌سازی هزینه</p>
                </div>
                <div class="text-right">
                    <div class="zimmer-token inline-block">
                        🎯 Zimmer Tokens: <span id="total-zimmer">0</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-2">1 Zimmer Token = 1 token per conversation turn</p>
                </div>
            </div>
        </div>

        <!-- Global Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div class="flex items-center">
                    <div class="p-2 bg-blue-100 rounded-lg">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                    <div class="mr-4">
                        <p class="text-sm font-medium text-gray-500">کل توکن‌ها</p>
                        <p class="text-2xl font-semibold text-gray-900" id="total-tokens">0</p>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div class="flex items-center">
                    <div class="p-2 bg-green-100 rounded-lg">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                        </svg>
                    </div>
                    <div class="mr-4">
                        <p class="text-sm font-medium text-gray-500">کل هزینه</p>
                        <p class="text-2xl font-semibold text-gray-900" id="total-cost">$0.00</p>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div class="flex items-center">
                    <div class="p-2 bg-purple-100 rounded-lg">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                        </svg>
                    </div>
                    <div class="mr-4">
                        <p class="text-sm font-medium text-gray-500">جلسات فعال</p>
                        <p class="text-2xl font-semibold text-gray-900" id="active-sessions">0</p>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div class="flex items-center">
                    <div class="p-2 bg-yellow-100 rounded-lg">
                        <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="mr-4">
                        <p class="text-sm font-medium text-gray-500">رتبه کارایی</p>
                        <p class="text-2xl font-semibold text-gray-900" id="efficiency-rating">-</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Token Usage Chart -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">استفاده از توکن‌ها</h3>
                <canvas id="tokenChart" width="400" height="200"></canvas>
            </div>

            <!-- Cost Analysis Chart -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">تحلیل هزینه</h3>
                <canvas id="costChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Sessions Table -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">جلسات فعال</h3>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">شناسه جلسه</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">توکن‌ها</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">هزینه</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Zimmer Tokens</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">کارایی</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عملیات</th>
                        </tr>
                    </thead>
                    <tbody id="sessions-table" class="bg-white divide-y divide-gray-200">
                        <!-- Sessions will be loaded here -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Optimization Recommendations -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">توصیه‌های بهینه‌سازی</h3>
            <div id="optimization-recommendations">
                <!-- Recommendations will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        // Load dashboard data
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // Update global metrics
                document.getElementById('total-tokens').textContent = data.global.total_tokens.toLocaleString();
                document.getElementById('total-cost').textContent = '$' + data.global.total_cost_usd.toFixed(4);
                document.getElementById('active-sessions').textContent = data.global.system_info.active_sessions;
                document.getElementById('total-zimmer').textContent = data.global.total_zimmer_tokens.toLocaleString();
                document.getElementById('efficiency-rating').textContent = data.global.efficiency_rating;
                
                // Load sessions
                loadSessions();
                
                // Load optimization recommendations
                loadOptimization();
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        // Load sessions
        async function loadSessions() {
            try {
                const response = await fetch('/api/sessions');
                const sessions = await response.json();
                
                const tableBody = document.getElementById('sessions-table');
                tableBody.innerHTML = '';
                
                for (const sessionId of sessions.sessions) {
                    const sessionResponse = await fetch(`/api/session/${sessionId}`);
                    const sessionData = await sessionResponse.json();
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${sessionId}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${sessionData.total_tokens.toLocaleString()}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${sessionData.total_cost_usd}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${sessionData.total_zimmer_tokens.toLocaleString()}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${sessionData.efficiency_score}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button onclick="viewSession('${sessionId}')" class="text-blue-600 hover:text-blue-900">مشاهده</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                }
            } catch (error) {
                console.error('Error loading sessions:', error);
            }
        }

        // Load optimization recommendations
        async function loadOptimization() {
            try {
                const response = await fetch('/api/optimization');
                const data = await response.json();
                
                const container = document.getElementById('optimization-recommendations');
                container.innerHTML = '';
                
                if (data.total_recommendations === 0) {
                    container.innerHTML = '<p class="text-gray-500">هیچ توصیه بهینه‌سازی در دسترس نیست.</p>';
                    return;
                }
                
                data.recommendations.forEach((rec, index) => {
                    const priorityColor = rec.priority === 'High' ? 'red' : rec.priority === 'Medium' ? 'yellow' : 'green';
                    const recDiv = document.createElement('div');
                    recDiv.className = 'border border-gray-200 rounded-lg p-4 mb-4';
                    recDiv.innerHTML = `
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <h4 class="font-medium text-gray-900">${index + 1}. ${rec.category}</h4>
                                <p class="text-sm text-gray-600 mt-1">${rec.issue}</p>
                                <p class="text-sm text-gray-700 mt-2">${rec.solution}</p>
                                <p class="text-sm text-green-600 mt-1 font-medium">صرفه‌جویی احتمالی: ${rec.potential_savings}</p>
                            </div>
                            <span class="px-2 py-1 text-xs font-medium rounded-full bg-${priorityColor}-100 text-${priorityColor}-800">
                                ${rec.priority}
                            </span>
                        </div>
                    `;
                    container.appendChild(recDiv);
                });
                
            } catch (error) {
                console.error('Error loading optimization:', error);
            }
        }

        // View session details
        function viewSession(sessionId) {
            alert(`Session ${sessionId} details would be shown here`);
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', loadDashboard);
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
'''

# Write the template file
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_template)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Token Usage Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8001")
    print("🔍 API endpoints available at: http://localhost:8001/api/")
    uvicorn.run(app, host="0.0.0.0", port=8001)

