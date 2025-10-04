import { useState, useEffect } from 'react';

export interface Category {
  id: number;
  name: string;
  prefix: string;
  product_count: number;
}

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.246:8000';

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${apiBase}/api/categories/summary`, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      } else {
        setError('خطا در دریافت دسته‌بندی‌ها');
      }
    } catch (error) {
      setError('خطا در اتصال به سرور');
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async (name: string): Promise<Category | null> => {
    try {
      const response = await fetch(`${apiBase}/api/categories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });

      if (response.ok) {
        const newCategory = await response.json();
        setCategories(prev => [...prev, newCategory]);
        return newCategory;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'خطا در ایجاد دسته‌بندی');
      }
    } catch (error) {
      throw error;
    }
  };

  const deleteCategory = async (id: number): Promise<boolean> => {
    try {
      const response = await fetch(`${apiBase}/api/categories/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setCategories(prev => prev.filter(cat => cat.id !== id));
        return true;
      } else {
        throw new Error('خطا در حذف دسته‌بندی');
      }
    } catch (error) {
      throw error;
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  return {
    categories,
    loading,
    error,
    refetch: fetchCategories,
    createCategory,
    deleteCategory
  };
} 