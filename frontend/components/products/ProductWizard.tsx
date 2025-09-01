'use client'

import { useState } from 'react'
import { X, Plus, ArrowRight, ArrowLeft } from 'lucide-react'
import { useDashboardStore } from '@/lib/store'

interface ProductWizardProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface Category {
  id: number
  name: string
  prefix: string
}

export default function ProductWizard({ isOpen, onClose, onSuccess }: ProductWizardProps) {
  const [step, setStep] = useState(1)
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    image_url: '',
    tags: '',
    available_sizes: '',
    available_colors: '',
    labels: '',
    attributes: {} as Record<string, string | string[]>
  })
  const [loading, setLoading] = useState(false)
  const [attributeKey, setAttributeKey] = useState('')
  const [attributeValue, setAttributeValue] = useState('')

  const { categories, addCategory, addProduct } = useDashboardStore()

  const addAttribute = () => {
    if (attributeKey.trim() && attributeValue.trim()) {
      const key = attributeKey.trim().toLowerCase()
      const values = attributeValue.split(',').map(v => v.trim()).filter(v => v)
      
      setProductForm(prev => ({
        ...prev,
        attributes: {
          ...prev.attributes,
          [key]: values
        }
      }))
      
      setAttributeKey('')
      setAttributeValue('')
    }
  }

  const removeAttribute = (key: string) => {
    setProductForm(prev => {
      const newAttributes = { ...prev.attributes }
      delete newAttributes[key]
      return { ...prev, attributes: newAttributes }
    })
  }

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) return
    
    setLoading(true)
    try {
      await addCategory(newCategoryName.trim())
      setNewCategoryName('')
      setShowCategoryModal(false)
    } catch (error) {
      console.error('Error creating category:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNextStep = () => {
    if (step === 1 && selectedCategory) {
      setStep(2)
    }
  }

  const handlePrevStep = () => {
    if (step === 2) {
      setStep(1)
    }
  }

  const handleSubmit = async () => {
    if (!selectedCategory || !productForm.name || !productForm.price) return

    setLoading(true)
    try {
      await addProduct({
        name: productForm.name,
        description: productForm.description,
        price: parseFloat(productForm.price),
        stock: parseInt(productForm.stock) || 0,
        category_id: selectedCategory.id,
        image_url: productForm.image_url,
        tags: productForm.tags,
        sizes: [],
        available_sizes: productForm.available_sizes ? productForm.available_sizes.split(',').map(s => s.trim()).filter(s => s) : [],
        available_colors: productForm.available_colors ? productForm.available_colors.split(',').map(s => s.trim()).filter(s => s) : [],
        labels: productForm.labels ? productForm.labels.split(',').map(l => l.trim()).filter(l => l) : [],
        attributes: productForm.attributes
      })
      
      // Reset form
      setProductForm({
        name: '',
        description: '',
        price: '',
        stock: '',
        image_url: '',
        tags: '',
        available_sizes: '',
        available_colors: '',
        labels: '',
        attributes: {}
      })
      setSelectedCategory(null)
      setStep(1)
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Error creating product:', error)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setStep(1)
    setSelectedCategory(null)
    setProductForm({
      name: '',
      description: '',
      price: '',
      stock: '',
      image_url: '',
      tags: '',
      available_sizes: '',
      available_colors: ''
    })
    setNewCategoryName('')
    setShowCategoryModal(false)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {step === 1 ? 'انتخاب دسته‌بندی' : 'اطلاعات محصول'}
          </h2>
          <button
            onClick={() => {
              resetForm()
              onClose()
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center mb-6">
          <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              step >= 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              1
            </div>
            <span className="mr-2 text-sm">دسته‌بندی</span>
          </div>
          <div className={`flex-1 h-0.5 mx-4 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`} />
          <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              step >= 2 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              2
            </div>
            <span className="mr-2 text-sm">محصول</span>
          </div>
        </div>

        {/* Step 1: Category Selection */}
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                انتخاب دسته‌بندی
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category)}
                    className={`p-3 border rounded-lg text-right transition-colors ${
                      selectedCategory?.id === category.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <div className="font-medium">{category.name}</div>
                    <div className="text-sm text-gray-500">پیشوند: {category.prefix}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t pt-4">
              <button
                onClick={() => setShowCategoryModal(true)}
                className="inline-flex items-center text-blue-600 hover:text-blue-700"
              >
                <Plus className="h-4 w-4 ml-1" />
                ایجاد دسته‌بندی جدید
              </button>
            </div>

            <div className="flex justify-end pt-4">
              <button
                onClick={handleNextStep}
                disabled={!selectedCategory}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ادامه
                <ArrowLeft className="h-4 w-4 mr-2" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Product Form */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">دسته‌بندی انتخاب شده:</div>
              <div className="font-medium">{selectedCategory?.name}</div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نام محصول *
                </label>
                <input
                  type="text"
                  value={productForm.name}
                  onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  قیمت (تومان) *
                </label>
                <input
                  type="number"
                  value={productForm.price}
                  onChange={(e) => setProductForm({...productForm, price: e.target.value})}
                  required
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  موجودی
                </label>
                <input
                  type="number"
                  value={productForm.stock}
                  onChange={(e) => setProductForm({...productForm, stock: e.target.value})}
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  آدرس تصویر
                </label>
                <input
                  type="url"
                  value={productForm.image_url}
                  onChange={(e) => setProductForm({...productForm, image_url: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                توضیحات
              </label>
              <textarea
                value={productForm.description}
                onChange={(e) => setProductForm({...productForm, description: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                برچسب‌ها (جدا شده با کاما)
              </label>
              <input
                type="text"
                value={productForm.tags}
                onChange={(e) => setProductForm({...productForm, tags: e.target.value})}
                placeholder="برچسب1, برچسب2, برچسب3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  سایزها (جدا شده با کاما)
                </label>
                <input
                  type="text"
                  value={productForm.available_sizes}
                  onChange={(e) => setProductForm({...productForm, available_sizes: e.target.value})}
                  placeholder="S, M, L, XL یا 40, 41, 42"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">مثال: S, M, L, XL یا ۴۰, ۴۱, ۴۲ (فارسی یا انگلیسی)</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  رنگ‌ها (جدا شده با کاما)
                </label>
                <input
                  type="text"
                  value={productForm.available_colors}
                  onChange={(e) => setProductForm({...productForm, available_colors: e.target.value})}
                  placeholder="مشکی, سفید, قرمز"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">مثال: مشکی, سفید, قرمز</p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                برچسب‌ها (جدا شده با کاما)
              </label>
              <input
                type="text"
                value={productForm.labels}
                onChange={(e) => setProductForm({...productForm, labels: e.target.value})}
                placeholder="jeans, pants, casual, formal"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">برچسب‌های کلیدی برای جستجوی بهتر (مثال: jeans, pants, casual)</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ویژگی‌های محصول
              </label>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={attributeKey}
                    onChange={(e) => setAttributeKey(e.target.value)}
                    placeholder="نام ویژگی (مثل: material, brand)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={attributeValue}
                    onChange={(e) => setAttributeValue(e.target.value)}
                    placeholder="مقادیر (جدا شده با کاما)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={addAttribute}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>
                
                {Object.keys(productForm.attributes).length > 0 && (
                  <div className="space-y-2">
                    {Object.entries(productForm.attributes).map(([key, values]) => (
                      <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                        <div>
                          <span className="font-medium text-gray-700">{key}:</span>
                          <span className="text-gray-600 mr-2">{Array.isArray(values) ? values.join(', ') : values}</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeAttribute(key)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <button
                onClick={handlePrevStep}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                <ArrowRight className="h-4 w-4 ml-2" />
                بازگشت
              </button>
              <button
                onClick={handleSubmit}
                disabled={!productForm.name || !productForm.price || loading}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'در حال ایجاد...' : 'ایجاد محصول'}
              </button>
            </div>
          </div>
        )}

        {/* Category Creation Modal */}
        {showCategoryModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">ایجاد دسته‌بندی جدید</h3>
              <input
                type="text"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                placeholder="نام دسته‌بندی"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
              />
              <div className="flex justify-end space-x-3 space-x-reverse">
                <button
                  onClick={() => setShowCategoryModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  انصراف
                </button>
                <button
                  onClick={handleCreateCategory}
                  disabled={!newCategoryName.trim() || loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  ایجاد
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 