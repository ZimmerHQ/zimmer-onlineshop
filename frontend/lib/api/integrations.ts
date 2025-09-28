// API functions for integrations

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.246:8000/api';

export interface TelegramConfig {
  bot_token_exists: boolean;
  webhook_url: string | null;
  secret_exists: boolean;
}

export interface TelegramConfigRequest {
  bot_token?: string;
  webhook_url?: string;
  secret?: string;
}

export interface TelegramTestResponse {
  ok: boolean;
  info?: {
    bot_id: number;
    bot_name: string;
    username: string;
  };
}

export interface TelegramWebhookResponse {
  ok: boolean;
  description: string;
  webhook_url?: string;
}

export const integrationsApi = {
  // Get Telegram configuration
  async getTelegramConfig(): Promise<TelegramConfig> {
    const response = await fetch(`${API_BASE}/integrations/telegram/config`);
    if (!response.ok) throw new Error('Failed to fetch Telegram configuration');
    return response.json();
  },

  // Update Telegram configuration
  async updateTelegramConfig(config: TelegramConfigRequest): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE}/integrations/telegram/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to update Telegram configuration');
    return response.json();
  },

  // Test Telegram connection
  async testTelegramConnection(): Promise<TelegramTestResponse> {
    const response = await fetch(`${API_BASE}/integrations/telegram/test`);
    if (!response.ok) throw new Error('Failed to test Telegram connection');
    return response.json();
  },

  // Set Telegram webhook
  async setTelegramWebhook(): Promise<TelegramWebhookResponse> {
    const response = await fetch(`${API_BASE}/integrations/telegram/set_webhook`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to set Telegram webhook');
    return response.json();
  },
}; 