"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import DashboardLayout from "@/components/DashboardLayout";
import { Bot, CheckCircle, XCircle, AlertCircle, Trash2, Settings, MessageSquare } from "lucide-react";

interface BotInfo {
  id: number;
  is_bot: boolean;
  first_name: string;
  username: string;
  can_join_groups: boolean;
  can_read_all_group_messages: boolean;
  supports_inline_queries: boolean;
}

interface WebhookInfo {
  url: string;
  has_custom_certificate: boolean;
  pending_update_count: number;
  last_error_date?: number;
  last_error_message?: string;
  max_connections: number;
  ip_address?: string;
}

interface WebhookResponse {
  success: boolean;
  message: string;
  bot_info?: BotInfo;
  webhook_info?: WebhookInfo | { bots: any[] };
}

interface BotConfig {
  bot_username: string;
  bot_name: string;
  webhook_url: string;
  is_active: boolean;
  last_error: string;
}

export default function WebhookPage() {
  const [botToken, setBotToken] = useState("");
  const [webhookUrl, setWebhookUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<WebhookResponse | null>(null);
  const [botConfigs, setBotConfigs] = useState<BotConfig[]>([]);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);

  useEffect(() => {
    loadWebhookStatus();
  }, []);

  const loadWebhookStatus = async () => {
    setIsLoadingStatus(true);
    try {
      const res = await fetch("/api/webhook/status");
      const data: WebhookResponse = await res.json();
      if (data.success && data.webhook_info && "bots" in data.webhook_info) {
        setBotConfigs(data.webhook_info.bots);
      }
    } catch (error) {
      console.error("Error loading webhook status:", error);
    } finally {
      setIsLoadingStatus(false);
    }
  };

  const handleSetupWebhook = async () => {
    if (!botToken.trim()) {
      setResponse({
        success: false,
        message: "Please enter a bot token"
      });
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch("/api/webhook/setup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bot_token: botToken,
          webhook_url: webhookUrl || undefined
        }),
      });

      const data: WebhookResponse = await res.json();
      setResponse(data);
      
      if (data.success) {
        setBotToken("");
        setWebhookUrl("");
        loadWebhookStatus();
      }
    } catch (error) {
      setResponse({
        success: false,
        message: "Failed to setup webhook. Please try again."
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteWebhook = async (botToken: string) => {
    if (!confirm("Are you sure you want to delete this webhook?")) {
      return;
    }

    try {
      const res = await fetch(`/api/webhook/${botToken}`, {
        method: "DELETE",
      });

      if (res.ok) {
        loadWebhookStatus();
      } else {
        alert("Failed to delete webhook");
      }
    } catch (error) {
      console.error("Error deleting webhook:", error);
      alert("Failed to delete webhook");
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3">
          <Bot className="h-8 w-8 text-gray-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Telegram Bot Setup</h1>
            <p className="text-gray-600">Configure your shopping assistant bot for Telegram</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Setup Form */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Setup New Bot</span>
            </CardTitle>
            <CardDescription>
              Enter your Telegram bot token to automatically configure the webhook
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bot-token">Bot Token</Label>
              <Input
                id="bot-token"
                type="password"
                placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                value={botToken}
                onChange={(e) => setBotToken(e.target.value)}
                className="border-gray-300 focus:border-black focus:ring-black"
              />
              <p className="text-sm text-gray-500">
                Get your bot token from @BotFather on Telegram
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="webhook-url">Webhook URL (Optional)</Label>
              <Input
                id="webhook-url"
                type="url"
                placeholder="https://your-domain.com/telegram/webhook"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="border-gray-300 focus:border-black focus:ring-black"
              />
              <p className="text-sm text-gray-500">
                Leave empty to use default URL: {typeof window !== 'undefined' ? window.location.origin : ''}/telegram/webhook
              </p>
            </div>

            <Button 
              onClick={handleSetupWebhook} 
              disabled={isLoading}
              className="w-full bg-black hover:bg-gray-800 text-white"
            >
              {isLoading ? "Setting up..." : "Setup Webhook"}
            </Button>

            {response && (
              <Alert className={response.success ? "border-green-500 bg-green-50" : "border-red-500 bg-red-50"}>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{response.message}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Current Status */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Bot Status</span>
            </CardTitle>
            <CardDescription>
              Manage your configured bot webhooks
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingStatus ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                <p className="text-gray-500 mt-2">Loading...</p>
              </div>
            ) : botConfigs.length > 0 ? (
              <div className="space-y-4">
                {botConfigs.map((bot, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Bot className="h-5 w-5 text-gray-600" />
                        <div>
                          <p className="font-medium text-gray-900">@{bot.bot_username}</p>
                          <p className="text-sm text-gray-500">{bot.bot_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={bot.is_active ? "default" : "secondary"} className={bot.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                          {bot.is_active ? "Active" : "Inactive"}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteWebhook(bot.bot_username)}
                          className="border-red-200 text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 space-y-1">
                      <p><span className="font-medium">Webhook:</span> {bot.webhook_url}</p>
                      {bot.last_error && (
                        <p className="text-red-600">
                          <span className="font-medium">Error:</span> {bot.last_error}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No webhooks configured</p>
                <p className="text-sm text-gray-400 mt-1">Setup your first bot to get started</p>
              </div>
            )}
            
            <Button 
              onClick={loadWebhookStatus} 
              variant="outline" 
              className="w-full mt-4 border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Refresh Status
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      <Card className="bg-white border-gray-200">
        <CardHeader>
          <CardTitle>Setup Instructions</CardTitle>
          <CardDescription>
            Follow these steps to create and configure your Telegram bot
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                <h3 className="font-semibold text-gray-900">Create Bot</h3>
              </div>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-10">
                <li>Open Telegram and search for @BotFather</li>
                <li>Send /newbot command</li>
                <li>Follow the instructions to create your bot</li>
                <li>Copy the bot token provided by BotFather</li>
              </ol>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                <h3 className="font-semibold text-gray-900">Configure Webhook</h3>
              </div>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-10">
                <li>Paste your bot token in the form above</li>
                <li>Click "Setup Webhook"</li>
                <li>The system will automatically configure the webhook</li>
                <li>Your bot will now receive messages and respond automatically</li>
              </ol>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                <h3 className="font-semibold text-gray-900">Test Your Bot</h3>
              </div>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-10">
                <li>Find your bot on Telegram (using the username you created)</li>
                <li>Send a message like "سلام" or "شلوار دارین؟"</li>
                <li>Your bot should respond with shopping assistance</li>
              </ol>
            </div>
          </div>

          <Alert className="border-blue-200 bg-blue-50">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <strong>Important:</strong> Make sure your server is accessible from the internet 
              (not just localhost) for the webhook to work properly. For development, you can use 
              services like ngrok to expose your local server.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
    </DashboardLayout>
  );
} 