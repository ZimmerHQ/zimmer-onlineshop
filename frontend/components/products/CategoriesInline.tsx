'use client'

import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Package, X, Check, AlertCircle, Eye } from 'lucide-react'

interface Category {
  id: number
  name: string
  prefix: string
  created_at: string
}

interface CategorySummary {
  id: number
  name: string
  prefix: string
  product_count: number
}

interface CategoriesInlineProps {
  onAddProduct: (categoryId: number) => void
  onCategoryChange: () => void
  onViewCategory: (categoryId: number) => void
}

export default function CategoriesInline({ onAddProduct, onCategoryChange, onViewCategory }: CategoriesInlineProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [categoriesSummary, setCategoriesSummary] = useState<CategorySummary[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingCategory, setEditingCategory] = useState<CategorySummary | null>(null)
  const [categoryForm, setCategoryForm] = useState({ name: '', prefix: '' })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchCategories()
    fetchCategoriesSummary()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/categories`)
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
      }
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const fetchCategoriesSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/categories/summary`)
      if (response.ok) {
        const data = await response.json()
        setCategoriesSummary(data)
      }
    } catch (error) {
      console.error('Error fetching categories summary:', error)
    }
  }

  const showToast = (message: string, type: 'success' | 'error') => {
    if (type === 'success') {
      setSuccess(message)
      setTimeout(() => setSuccess(null), 3000)
    } else {
      setError(message)
      setTimeout(() => setError(null), 3000)
    }
  }

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!categoryForm.name.trim()) {
      showToast('لطفاً نام دسته‌بندی را وارد کنید', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: categoryForm.name.trim() })
      })

      if (response.ok) {
        setCategoryForm({ name: '', prefix: '' })
        setShowCreateModal(false)
        fetchCategories()
        fetchCategoriesSummary()
        onCategoryChange()
        showToast('دسته‌بندی با موفقیت ایجاد شد', 'success')
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'خطا در ایجاد دسته‌بندی')
      }
    } catch (error) {
      console.error('Error creating category:', error)
      showToast(`خطا در ایجاد دسته‌بندی: ${error instanceof Error ? error.message : 'خطای نامشخص'}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleEditCategory = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingCategory || !categoryForm.name.trim() || !categoryForm.prefix.trim()) {
      showToast('لطفاً نام و پیشوند را وارد کنید', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/categories/${editingCategory.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: categoryForm.name.trim(),
          prefix: categoryForm.prefix.trim()
        })
      })

      if (response.ok) {
        setCategoryForm({ name: '', prefix: '' })
        setShowEditModal(false)
        setEditingCategory(null)
        fetchCategories()
        fetchCategoriesSummary()
        onCategoryChange()
        showToast('دسته‌بندی با موفقیت به‌روزرسانی شد', 'success')
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'خطا در به‌روزرسانی دسته‌بندی')
      }
    } catch (error) {
      console.error('Error updating category:', error)
      showToast(`خطا در به‌روزرسانی دسته‌بندی: ${error instanceof Error ? error.message : 'خطای نامشخص'}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteCategory = async (category: CategorySummary) => {
    if (category.product_count > 0) {
      showToast(`این دسته‌بندی دارای ${category.product_count} محصول است و قابل حذف نیست`, 'error')
      return
    }

    if (!confirm(`آیا مطمئن هستید که می‌خواهید دسته‌بندی "${category.name}" را حذف کنید؟`)) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/api/categories/${category.id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchCategories()
        fetchCategoriesSummary()
        onCategoryChange()
        showToast('دسته‌بندی با موفقیت حذف شد', 'success')
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'خطا در حذف دسته‌بندی')
      }
    } catch (error) {
      console.error('Error deleting category:', error)
      showToast(`خطا در حذف دسته‌بندی: ${error instanceof Error ? error.message : 'خطای نامشخص'}`, 'error')
    }
  }

  const openEditModal = (category: CategorySummary) => {
    setEditingCategory(category)
    setCategoryForm({ name: category.name, prefix: category.prefix })
    setShowEditModal(true)
  }

  const handleAddProduct = (categoryId: number) => {
    onAddProduct(categoryId)
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-medium text-gray-900">دسته‌بندی‌ها</h2>
            <p className="text-sm text-gray-600 mt-1">
              تعداد کل: {categoriesSummary.length} دسته‌بندی
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 ml-2" />
            افزودن دسته‌بندی
          </button>
        </div>
      </div>

      {/* Categories Table */}
      <div className="overflow-x-auto">
        {categoriesSummary.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">هنوز دسته‌بندی ایجاد نشده است</div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              ایجاد اولین دسته‌بندی
            </button>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  نام دسته‌بندی
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  پیشوند
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  تعداد محصول
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  عملیات
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {categoriesSummary.map((category) => (
                <tr 
                  key={category.id} 
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onViewCategory(category.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{category.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {category.prefix}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{category.product_count}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2 space-x-reverse">
                      <button
                        onClick={(e) => { 
                          e.stopPropagation(); 
                          onViewCategory(category.id); 
                        }}
                        className="text-blue-600 hover:text-blue-900 p-1"
                        title="نمایش محصولات"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => { 
                          e.stopPropagation(); 
                          onAddProduct(category.id); 
                        }}
                        className="text-green-600 hover:text-green-900 p-1"
                        title="افزودن محصول به این دسته‌بندی"
                      >
                        <Package className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => { 
                          e.stopPropagation(); 
                          openEditModal(category); 
                        }}
                        className="text-blue-600 hover:text-blue-900 p-1"
                        title="ویرایش دسته‌بندی"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => { 
                          e.stopPropagation(); 
                          handleDeleteCategory(category); 
                        }}
                        disabled={category.product_count > 0}
                        className={`p-1 ${
                          category.product_count > 0
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-red-600 hover:text-red-900'
                        }`}
                        title={
                          category.product_count > 0
                            ? 'این دسته‌بندی دارای محصول است و قابل حذف نیست'
                            : 'حذف دسته‌بندی'
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Toast Messages */}
      {error && (
        <div className="fixed top-4 right-4 z-50 flex items-center p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <AlertCircle className="h-5 w-5 ml-2" />
          {error}
        </div>
      )}
      
      {success && (
        <div className="fixed top-4 right-4 z-50 flex items-center p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          <Check className="h-5 w-5 ml-2" />
          {success}
        </div>
      )}

      {/* Create Category Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">افزودن دسته‌بندی جدید</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <form onSubmit={handleCreateCategory}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نام دسته‌بندی
                </label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                  placeholder="مثال: پوشاک مردانه"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-3 space-x-reverse">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={loading || !categoryForm.name.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'در حال ایجاد...' : 'ایجاد'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Category Modal */}
      {showEditModal && editingCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">ویرایش دسته‌بندی</h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <form onSubmit={handleEditCategory}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نام دسته‌بندی
                </label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  پیشوند (1-2 حرف بزرگ)
                </label>
                <input
                  type="text"
                  value={categoryForm.prefix}
                  onChange={(e) => setCategoryForm({ ...categoryForm, prefix: e.target.value.toUpperCase() })}
                  placeholder="A, B, AA, BB"
                  pattern="[A-Z]{1,2}"
                  maxLength={2}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  پیشوند باید 1 یا 2 حرف بزرگ باشد (مثل A، B، AA، BB)
                </p>
              </div>
              <div className="mb-4 p-3 bg-yellow-50 rounded-md border border-yellow-200">
                <div className="text-sm text-yellow-800">
                  <div className="font-medium mb-1">⚠️ توجه:</div>
                  <div>• تغییر پیشوند فقط روی محصولات جدید تأثیر می‌گذارد</div>
                  <div>• کدهای محصولات موجود تغییر نمی‌کنند</div>
                  <div>• تعداد محصول فعلی: <span className="font-medium">{editingCategory.product_count}</span></div>
                </div>
              </div>
              <div className="flex justify-end space-x-3 space-x-reverse">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={loading || !categoryForm.name.trim() || !categoryForm.prefix.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 