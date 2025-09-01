import { useState, useEffect } from 'react';

export interface Product {
  id: number;
  code: string;
  name: string;
  description?: string;
  price: number;
  category_id: number;
  category_name?: string;
  image_url?: string;
  thumbnail_url?: string;
  stock: number;
  sizes?: string[];
  tags?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductsResponse {
  products: Product[];
  total_count: number;
  page: number;
  page_size: number;
}

// For backward compatibility
export interface ProductsListResponse extends Array<Product> {}

export function useProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchProducts = async (page = 1, pageSize = 20, categoryId?: number, searchQuery?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      let url = `${apiBase}/api/products/?page=${page}&page_size=${pageSize}`;
      if (categoryId) {
        url += `&category_id=${categoryId}`;
      }
      if (searchQuery) {
        url += `&q=${encodeURIComponent(searchQuery)}`;
      }

      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        // Backend returns array directly, not wrapped object
        const data: Product[] = await response.json();
        setProducts(data);
        setTotalCount(data.length); // For now, use array length
      } else {
        setError('خطا در دریافت محصولات');
      }
    } catch (error) {
      setError('خطا در اتصال به سرور');
    } finally {
      setLoading(false);
    }
  };

  const createProduct = async (productData: Partial<Product>): Promise<Product | null> => {
    try {
      const response = await fetch(`${apiBase}/api/products/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });

      if (response.ok) {
        const newProduct = await response.json();
        setProducts(prev => [newProduct, ...prev]);
        setTotalCount(prev => prev + 1);
        return newProduct;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'خطا در ایجاد محصول');
      }
    } catch (error) {
      throw error;
    }
  };

  const updateProduct = async (id: number, productData: Partial<Product>): Promise<Product | null> => {
    try {
      const response = await fetch(`${apiBase}/api/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });

      if (response.ok) {
        const updatedProduct = await response.json();
        setProducts(prev => prev.map(p => p.id === id ? updatedProduct : p));
        return updatedProduct;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'خطا در بروزرسانی محصول');
      }
    } catch (error) {
      throw error;
    }
  };

  const deleteProduct = async (id: number): Promise<boolean> => {
    try {
      const response = await fetch(`${apiBase}/api/products/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setProducts(prev => prev.filter(p => p.id !== id));
        setTotalCount(prev => prev - 1);
        return true;
      } else {
        throw new Error('خطا در حذف محصول');
      }
    } catch (error) {
      throw error;
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return {
    products,
    totalCount,
    loading,
    error,
    refetch: fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct
  };
} 