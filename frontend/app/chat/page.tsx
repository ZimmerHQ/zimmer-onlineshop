"use client";
import React, { useState, useRef, useEffect } from "react";
import { apiBase } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setLoading(true);

    try {
      console.log("🔗 Making API call to:", `${apiBase}/api/chat`);
      console.log("📤 Request payload:", { conversation_id: "default", message: input });
      
      const response = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          conversation_id: "default", 
          message: input 
        }),
      });

      console.log("📥 Response status:", response.status);
      console.log("📥 Response headers:", Object.fromEntries(response.headers.entries()));
      
      const data = await response.json();
      console.log("📥 Response data:", data);
      
      if (data.reply) {
        console.log("✅ Setting bot reply:", data.reply);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      } else {
        console.log("❌ No reply in response");
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "پاسخی دریافت نشد." },
        ]);
      }
    } catch (error) {
      console.error("خطا در ارسال پیام:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید." },
      ]);
    }

    setLoading(false);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 p-4 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-md p-6 flex flex-col space-y-4">
        <h1 className="text-xl font-bold text-center">💬 چت با فروشگاه</h1>
        <div className="flex-1 overflow-y-auto space-y-2 max-h-[60vh]">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center">
              سلام! به فروشگاه ما خوش آمدید 🌟
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-3 rounded-xl max-w-xs whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-500 text-white self-end ml-auto"
                  : "bg-gray-200 text-right"
              }`}
            >
              {msg.content}
            </div>
          ))}
          {loading && (
            <div className="text-gray-400 text-sm animate-pulse">
              در حال تایپ...
            </div>
          )}
          <div ref={bottomRef}></div>
        </div>
        <div className="flex items-center space-x-2 space-x-reverse" dir="rtl">
          <input
            className="flex-1 p-3 rounded-xl border focus:outline-none"
            placeholder="پیام خود را بنویسید..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700"
            onClick={sendMessage}
            disabled={loading}
          >
            ارسال
          </button>
        </div>
      </div>
    </div>
  );
}
