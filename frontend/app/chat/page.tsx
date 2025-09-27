"use client";
import React, { useState, useRef, useEffect } from "react";
import { apiBase } from "@/lib/utils";
import { searchProductsTool, getCategoriesSummaryTool, checkCategoriesExistTool } from "@/lib/ai/tools";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";

interface Message {
  role: "user" | "assistant";
  content: string;
  products?: any[]; // For product search results
}

interface ChatResponse {
  reply: string;
  order_id?: number;
  status?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Enhanced message handling with product search
  const handleUserMessage = async (userInput: string) => {
    const newMessage: Message = { role: "user", content: userInput };
    setMessages((prev) => [...prev, newMessage]);
    setLoading(true);
    // Don't clear input until response arrives

    try {
      let botReply = "";
      let products: any[] = [];

      // Check if user is asking about products
      const productKeywords = [
        'محصول', 'موجود', 'دارید', 'چی', 'لیست', 'قیمت', 'کد', 'دسته‌بندی',
        'product', 'available', 'have', 'what', 'list', 'price', 'code', 'category'
      ];

      const isProductQuery = productKeywords.some(keyword => 
        userInput.toLowerCase().includes(keyword.toLowerCase())
      );

      if (isProductQuery) {
        console.log('🔍 User asking about products, searching...');
        
        try {
          // For general product list requests, get all products instead of searching
          const isGeneralProductRequest = userInput.toLowerCase().includes('لیست') || 
                                        userInput.toLowerCase().includes('فهرست') || 
                                        userInput.toLowerCase().includes('محصولات') ||
                                        userInput.toLowerCase().includes('کالاها') ||
                                        userInput.toLowerCase().includes('همه') ||
                                        userInput.toLowerCase().includes('تمام');
          
          let searchResult;
          if (isGeneralProductRequest) {
            // Get all products for general requests
            searchResult = await searchProductsTool({ 
              q: '', // Empty query to get all products
              limit: 10 
            });
          } else {
            // Search for specific products
            searchResult = await searchProductsTool({ 
              q: userInput, 
              limit: 5 
            });
          }
          
          if (searchResult.success && searchResult.products.length > 0) {
            products = searchResult.products;
            botReply = `بله! ${searchResult.message}\n\n`;
            searchResult.products.forEach((product: any, index: number) => {
              botReply += `${index + 1}. **${product.name}**\n`;
              botReply += `   کد: ${product.code}\n`;
              botReply += `   قیمت: ${product.price.toLocaleString()} تومان\n`;
              botReply += `   دسته‌بندی: ${product.category}\n`;
              botReply += `   موجودی: ${product.stock} عدد\n`;
              
              // Show available sizes and colors if available
              if (product.available_sizes && product.available_sizes.length > 0) {
                botReply += `   سایزهای موجود: ${product.available_sizes.join(', ')}\n`;
              }
              if (product.available_colors && product.available_colors.length > 0) {
                botReply += `   رنگ‌های موجود: ${product.available_colors.join(', ')}\n`;
              }
              
              botReply += '\n';
            });
            botReply += "برای اطلاعات دقیق‌تر درباره محصول خاصی، کد محصول را بگویید یا شماره آن را انتخاب کنید.";
          } else {
            // If no products found, fall back to backend agent
            console.log('No products found in frontend search, falling back to backend agent...');
            const response = await fetch(`${apiBase}/api/chat`, {
              method: "POST",
              mode: 'cors',
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ 
                conversation_id: "default", 
                message: userInput 
              }),
            });
            
            const data: ChatResponse = await response.json();
            botReply = data.reply || "متأسفانه محصولی مطابق درخواست شما پیدا نکردم. لطفاً کلمات کلیدی دیگری امتحان کنید یا از دسته‌بندی خاصی بپرسید.";
          }
        } catch (searchError) {
          console.error('Product search failed:', searchError);
          botReply = "متأسفانه در جستجوی محصولات مشکلی پیش آمد. لطفاً دوباره تلاش کنید.";
        }
      } else {
        // Regular chat message - send to backend
        console.log("🔗 Making API call to:", `${apiBase}/api/chat`);
        console.log("📤 Request payload:", { conversation_id: "default", message: userInput });
        
        const response = await fetch(`${apiBase}/api/chat`, {
          method: "POST",
          mode: 'cors',
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            conversation_id: "default", 
            message: userInput 
          }),
        });

        console.log("📥 Response status:", response.status);
        
        const data: ChatResponse = await response.json();
        console.log("📥 Response data:", data);
        
        if (data.reply) {
          botReply = data.reply;
        } else {
          botReply = "پاسخی دریافت نشد.";
        }
      }

      // Add bot reply with products if available
      const botMessage: Message = { 
        role: "assistant", 
        content: botReply,
        products: products.length > 0 ? products : undefined
      };
      
      setMessages((prev) => [...prev, botMessage]);
      
    } catch (error) {
      console.error("خطا در ارسال پیام:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید." },
      ]);
    }

    setLoading(false);
    // Clear input only after response is received
    setInput("");
  };

  const sendMessage = () => {
    if (!input.trim()) return;
    handleUserMessage(input);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Add welcome message with product search instructions
  useEffect(() => {
    const welcomeMessage: Message = {
      role: "assistant",
      content: `سلام! به فروشگاه ما خوش آمدید 🌟\n\nمن می‌توانم به سوالات شما درباره محصولات پاسخ دهم و اطلاعات دقیق شامل سایزها و رنگ‌های موجود را ارائه کنم:\n\n• "چه محصولاتی موجوده؟"\n• "قیمت کفش چقدره؟"\n• "محصولات دسته‌بندی پوشاک"\n• "کد محصول A0001"\n• "سایزهای موجود برای محصول X"\n• "رنگ‌های موجود برای محصول Y"\n\nچطور می‌تونم کمکتون کنم؟`
    };
    setMessages([welcomeMessage]);
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-text-strong">💬 چت با فروشگاه</h1>
          <p className="text-text-muted mt-1">دستیار خرید هوشمند شما</p>
        </div>

        {/* Chat Container */}
        <Card className="h-[70vh] flex flex-col">
          <CardContent className="flex-1 flex flex-col p-6">
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-xl max-w-2xl whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary-500 text-white self-end ml-auto"
                      : "bg-bg-soft text-text-strong self-start mr-auto"
                  }`}
                >
              {msg.content}
              
                  {/* Show product images if available */}
                  {msg.products && msg.products.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-card/20">
                      <div className="text-sm text-text-muted mb-2">تصاویر محصولات:</div>
                      <div className="flex flex-wrap gap-2">
                        {msg.products.map((product, idx) => (
                          <div key={idx} className="text-center">
                            {product.image ? (
                              <img 
                                src={product.image} 
                                alt={product.name}
                                className="w-16 h-16 object-cover rounded-lg border border-card/20"
                                onError={(e) => {
                                  e.currentTarget.src = '/placeholder.svg';
                                }}
                              />
                            ) : (
                              <div className="w-16 h-16 bg-bg-soft rounded-lg flex items-center justify-center">
                                <span className="text-xs text-text-muted">بدون تصویر</span>
                              </div>
                            )}
                            <div className="text-xs text-text-muted mt-1 ltr font-mono">{product.code}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="text-text-muted text-sm animate-pulse">
                  در حال جستجو...
                </div>
              )}
              <div ref={bottomRef}></div>
            </div>
            
            {/* Input Area */}
            <div className="flex items-center space-x-2 space-x-reverse" dir="rtl">
              <input
                className="flex-1 p-3 bg-card border border-card/20 rounded-xl text-text-strong placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="سوال خود را درباره محصولات بپرسید..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />
              <button
                className="bg-primary-500 text-white px-4 py-2 rounded-xl hover:bg-primary-600 transition-all duration-200 zimmer-focus-ring"
                onClick={sendMessage}
                disabled={loading}
              >
                ارسال
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
