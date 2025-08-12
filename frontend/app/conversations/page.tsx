'use client'

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDashboardStore } from '@/lib/store';
import { formatDate } from '@/lib/utils';
import { MessageCircle, User, Bot, Loader2, AlertCircle, RefreshCw, Eye, Trash2 } from 'lucide-react';

export default function ConversationsPage() {
  const [isClient, setIsClient] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const { 
    conversations, 
    loading: isLoading,
    errors: error,
    fetchConversations,
    deleteConversation,
    setConversations
  } = useDashboardStore();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient) {
      fetchConversations();
    }
  }, [fetchConversations, isClient]);

  const handleDeleteConversation = async (conversationId: string) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این گفتگو را حذف کنید؟')) {
      try {
        await deleteConversation(conversationId);
      } catch (error) {
        console.error('Error deleting conversation:', error);
      }
    }
  };

  const handleViewDetails = (conversation: any) => {
    setSelectedConversation(conversation);
    setIsModalOpen(true);
  };

  if (!isClient) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">گفتگوهای مشتریان</h1>
            <p className="text-gray-600 mt-1">مشاهده تمام گفتگوهای مشتریان با ربات</p>
          </div>
          <button
            onClick={() => fetchConversations()}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ml-2 ${isLoading ? 'animate-spin' : ''}`} />
            بروزرسانی
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageCircle className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">کل گفتگوها</p>
                <p className="text-2xl font-semibold text-gray-900">{Array.isArray(conversations) ? conversations.length : 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <User className="h-8 w-8 text-green-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">کاربران فعال</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(conversations) ? new Set(conversations.map(c => c.userId)).size : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Bot className="h-8 w-8 text-purple-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">پیام‌های امروز</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(conversations) ? conversations.filter(c => {
                    const today = new Date();
                    const convDate = new Date(c.lastMessageTime);
                    return convDate.toDateString() === today.toDateString();
                  }).length : 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 ml-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Conversations Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    کاربر
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    آخرین پیام
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تعداد پیام‌ها
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تاریخ آخرین پیام
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <Loader2 className="h-6 w-6 animate-spin text-blue-600 ml-2" />
                        <span className="text-gray-600">در حال بارگذاری گفتگوها...</span>
                      </div>
                    </td>
                  </tr>
                ) : !Array.isArray(conversations) || conversations.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                      هیچ گفتگویی یافت نشد
                    </td>
                  </tr>
                ) : Array.isArray(conversations) ? (
                  conversations.map((conversation) => (
                    <tr key={conversation.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center">
                          <User className="h-5 w-5 text-gray-400 ml-2" />
                          {conversation.userId}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                        {conversation.lastMessage}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center">
                        {conversation.messages?.length || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(new Date(conversation.lastMessageTime))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <button
                            onClick={() => handleViewDetails(conversation)}
                            className="text-blue-600 hover:text-blue-900"
                            title="مشاهده جزئیات"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteConversation(conversation.id)}
                            className="text-red-600 hover:text-red-900"
                            title="حذف گفتگو"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : null}
              </tbody>
            </table>
          </div>
        </div>

        {/* Conversation Details Modal */}
        {isModalOpen && selectedConversation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-semibold text-gray-900">جزئیات گفتگو - کاربر {selectedConversation.userId}</h2>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="space-y-4">
                  {selectedConversation.messages?.map((message: any, index: number) => (
                    <div
                      key={index}
                      className={`flex ${message.isFromUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.isFromUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-900'
                        }`}
                      >
                        <div className="flex items-center mb-1">
                          {message.isFromUser ? (
                            <User className="h-4 w-4 ml-1" />
                          ) : (
                            <Bot className="h-4 w-4 ml-1" />
                          )}
                          <span className="text-xs opacity-75">
                            {message.isFromUser ? 'کاربر' : 'ربات'}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-75 mt-1">
                          {formatDate(new Date(message.timestamp))}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 space-x-reverse p-6 border-t">
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  بستن
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 