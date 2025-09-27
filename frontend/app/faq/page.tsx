"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import DashboardLayout from "@/components/DashboardLayout";
import { Plus, Edit, Trash2, ToggleLeft, ToggleRight, Save, X, HelpCircle } from "lucide-react";

interface FAQ {
  id: number;
  question: string;
  answer: string;
  tags: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface FAQCreate {
  question: string;
  answer: string;
  tags?: string;
  is_active: boolean;
}

export default function FAQPage() {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFaq, setEditingFaq] = useState<FAQ | null>(null);
  const [formData, setFormData] = useState<FAQCreate>({
    question: '',
    answer: '',
    tags: '',
    is_active: true
  });

  const fetchFaqs = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/api/faq/?active_only=false');
      if (response.ok) {
        const data = await response.json();
        setFaqs(data);
      } else {
        console.error('Failed to fetch FAQs');
      }
    } catch (error) {
      console.error('Error fetching FAQs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFaqs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingFaq 
                ? `http://localhost:8000/api/faq/${editingFaq.id}`
        : 'http://localhost:8000/api/faq/';
      
      const method = editingFaq ? 'PATCH' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await fetchFaqs();
        setShowCreateForm(false);
        setEditingFaq(null);
        setFormData({
          question: '',
          answer: '',
          tags: '',
          is_active: true
        });
      } else {
        console.error('Failed to save FAQ');
      }
    } catch (error) {
      console.error('Error saving FAQ:', error);
    }
  };

  const handleEdit = (faq: FAQ) => {
    setEditingFaq(faq);
    setFormData({
      question: faq.question,
      answer: faq.answer,
      tags: faq.tags || '',
      is_active: faq.is_active
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا از حذف این سوال اطمینان دارید؟')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/faq/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await fetchFaqs();
      } else {
        console.error('Failed to delete FAQ');
      }
    } catch (error) {
      console.error('Error deleting FAQ:', error);
    }
  };

  const handleToggleStatus = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/faq/${id}/toggle`, {
        method: 'PATCH',
      });

      if (response.ok) {
        await fetchFaqs();
      } else {
        console.error('Failed to toggle FAQ status');
      }
    } catch (error) {
      console.error('Error toggling FAQ status:', error);
    }
  };

  const handleCancel = () => {
    setShowCreateForm(false);
    setEditingFaq(null);
    setFormData({
      question: '',
      answer: '',
      tags: '',
      is_active: true
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <HelpCircle className="h-8 w-8" />
              مدیریت سوالات متداول
            </h1>
            <p className="text-muted-foreground">
              ایجاد و ویرایش سوالات پرتکرار
            </p>
          </div>
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            افزودن سوال جدید
          </Button>
        </div>

        {/* Create/Edit Form */}
        {showCreateForm && (
          <Card>
            <CardHeader>
              <CardTitle>
                {editingFaq ? 'ویرایش سوال' : 'افزودن سوال جدید'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">سوال</label>
                  <Input
                    value={formData.question}
                    onChange={(e) => setFormData({...formData, question: e.target.value})}
                    required
                    placeholder="سوال خود را وارد کنید..."
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">پاسخ</label>
                  <Textarea
                    value={formData.answer}
                    onChange={(e) => setFormData({...formData, answer: e.target.value})}
                    required
                    placeholder="پاسخ را وارد کنید..."
                    rows={4}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">برچسب‌ها (اختیاری)</label>
                  <Input
                    value={formData.tags}
                    onChange={(e) => setFormData({...formData, tags: e.target.value})}
                    placeholder="برچسب‌ها را با کاما جدا کنید..."
                  />
                </div>
                
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  />
                  <label htmlFor="is_active" className="text-sm font-medium">فعال</label>
                </div>
                
                <div className="flex gap-2">
                  <Button type="submit" className="flex items-center gap-2">
                    <Save className="h-4 w-4" />
                    {editingFaq ? 'بروزرسانی' : 'ذخیره'}
                  </Button>
                  <Button type="button" variant="outline" onClick={handleCancel} className="flex items-center gap-2">
                    <X className="h-4 w-4" />
                    انصراف
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* FAQ List */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-8">در حال بارگذاری...</div>
          ) : faqs.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <HelpCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">هیچ سوال متداولی یافت نشد</p>
              </CardContent>
            </Card>
          ) : (
            faqs.map((faq) => (
              <Card key={faq.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{faq.question}</CardTitle>
                      <CardDescription className="mt-2">{faq.answer}</CardDescription>
                      {faq.tags && (
                        <div className="flex gap-1 mt-2">
                          {faq.tags.split(',').map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag.trim()}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={faq.is_active ? "default" : "secondary"}>
                        {faq.is_active ? 'فعال' : 'غیرفعال'}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(faq)}
                      className="flex items-center gap-1"
                    >
                      <Edit className="h-3 w-3" />
                      ویرایش
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleStatus(faq.id)}
                      className="flex items-center gap-1"
                    >
                      {faq.is_active ? (
                        <>
                          <ToggleRight className="h-3 w-3" />
                          غیرفعال کردن
                        </>
                      ) : (
                        <>
                          <ToggleLeft className="h-3 w-3" />
                          فعال کردن
                        </>
                      )}
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(faq.id)}
                      className="flex items-center gap-1"
                    >
                      <Trash2 className="h-3 w-3" />
                      حذف
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </DashboardLayout>
  );
} 