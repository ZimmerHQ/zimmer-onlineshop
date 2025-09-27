'use client'

import { useState, useEffect } from 'react'
import { Plus, Trash2, Edit, Save, X } from 'lucide-react'

interface Variant {
  id?: number
  sku_code: string
  attributes: Record<string, any>
  price_override?: number
  stock_qty: number
  is_active: boolean
}

interface Product {
  id: number
  code: string
  name: string
  price: number
  attribute_schema?: Record<string, any>
}

interface VariantsManagerProps {
  product: Product | null
  variants: Variant[]
  onVariantsChange: (variants: Variant[]) => void
  onClose: () => void
}

export default function VariantsManager({ product, variants, onVariantsChange, onClose }: VariantsManagerProps) {
  const [editingVariant, setEditingVariant] = useState<Variant | null>(null)
  const [newVariant, setNewVariant] = useState<Partial<Variant>>({
    sku_code: '',
    attributes: {},
    price_override: undefined,
    stock_qty: 0,
    is_active: true
  })
  const [showAddForm, setShowAddForm] = useState(false)

  // Generate default SKU code when product changes
  useEffect(() => {
    if (product && !newVariant.sku_code) {
      const baseCode = product.code
      const existingSkus = variants.map(v => v.sku_code)
      let counter = 1
      let newSku = baseCode
      
      while (existingSkus.includes(newSku)) {
        newSku = `${baseCode}-${counter}`
        counter++
      }
      
      setNewVariant(prev => ({ ...prev, sku_code: newSku }))
    }
  }, [product, variants, newVariant.sku_code])

  const handleAddVariant = () => {
    if (!newVariant.sku_code || newVariant.stock_qty === undefined) {
      alert('لطفاً کد SKU و موجودی را وارد کنید')
      return
    }

    const variant: Variant = {
      sku_code: newVariant.sku_code,
      attributes: newVariant.attributes || {},
      price_override: newVariant.price_override,
      stock_qty: newVariant.stock_qty,
      is_active: newVariant.is_active ?? true
    }

    onVariantsChange([...variants, variant])
    setNewVariant({
      sku_code: '',
      attributes: {},
      price_override: undefined,
      stock_qty: 0,
      is_active: true
    })
    setShowAddForm(false)
  }

  const handleEditVariant = (variant: Variant) => {
    setEditingVariant({ ...variant })
  }

  const handleSaveEdit = () => {
    if (!editingVariant) return

    const updatedVariants = variants.map(v => 
      v.sku_code === editingVariant.sku_code ? editingVariant : v
    )
    onVariantsChange(updatedVariants)
    setEditingVariant(null)
  }

  const handleDeleteVariant = (skuCode: string) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این گونه را حذف کنید؟')) {
      const updatedVariants = variants.filter(v => v.sku_code !== skuCode)
      onVariantsChange(updatedVariants)
    }
  }

  const addAttribute = (key: string, value: string) => {
    if (!editingVariant) return
    
    setEditingVariant({
      ...editingVariant,
      attributes: {
        ...editingVariant.attributes,
        [key]: value
      }
    })
  }

  const removeAttribute = (key: string) => {
    if (!editingVariant) return
    
    const newAttributes = { ...editingVariant.attributes }
    delete newAttributes[key]
    
    setEditingVariant({
      ...editingVariant,
      attributes: newAttributes
    })
  }

  const addNewAttribute = (key: string, value: string) => {
    setNewVariant(prev => ({
      ...prev,
      attributes: {
        ...prev.attributes,
        [key]: value
      }
    }))
  }

  const removeNewAttribute = (key: string) => {
    const newAttributes = { ...newVariant.attributes }
    delete newAttributes[key]
    
    setNewVariant(prev => ({
      ...prev,
      attributes: newAttributes
    }))
  }

  if (!product) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            مدیریت گونه‌های محصول: {product.name} ({product.code})
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Product Info */}
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">نام محصول:</span> {product.name}
            </div>
            <div>
              <span className="font-medium">کد محصول:</span> {product.code}
            </div>
            <div>
              <span className="font-medium">قیمت پایه:</span> {new Intl.NumberFormat('fa-IR').format(product.price)} تومان
            </div>
            <div>
              <span className="font-medium">تعداد گونه‌ها:</span> {variants.length}
            </div>
          </div>
        </div>

        {/* Variants List */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">گونه‌های موجود</h4>
          {variants.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              هنوز گونه‌ای اضافه نکرده‌اید
            </div>
          ) : (
            <div className="space-y-3">
              {variants.map((variant, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  {editingVariant && editingVariant.sku_code === variant.sku_code ? (
                    // Edit Mode
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">کد SKU</label>
                          <input
                            type="text"
                            value={editingVariant.sku_code}
                            onChange={(e) => setEditingVariant({...editingVariant, sku_code: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">موجودی</label>
                          <input
                            type="number"
                            value={editingVariant.stock_qty}
                            onChange={(e) => setEditingVariant({...editingVariant, stock_qty: parseInt(e.target.value) || 0})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">قیمت اضافی (تومان)</label>
                          <input
                            type="number"
                            value={editingVariant.price_override || ''}
                            onChange={(e) => setEditingVariant({...editingVariant, price_override: e.target.value ? parseFloat(e.target.value) : undefined})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="flex items-center">
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={editingVariant.is_active}
                              onChange={(e) => setEditingVariant({...editingVariant, is_active: e.target.checked})}
                              className="ml-2"
                            />
                            فعال
                          </label>
                        </div>
                      </div>
                      
                      {/* Attributes */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">ویژگی‌ها</label>
                        <div className="space-y-2">
                          {Object.entries(editingVariant.attributes).map(([key, value]) => (
                            <div key={key} className="flex items-center space-x-2 space-x-reverse">
                              <span className="text-sm font-medium">{key}:</span>
                              <input
                                type="text"
                                value={value}
                                onChange={(e) => addAttribute(key, e.target.value)}
                                className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                              <button
                                onClick={() => removeAttribute(key)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ))}
                          <div className="flex items-center space-x-2 space-x-reverse">
                            <input
                              type="text"
                              placeholder="نام ویژگی"
                              className="px-2 py-1 border border-gray-300 rounded text-sm"
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  const key = e.currentTarget.value
                                  if (key) {
                                    addAttribute(key, '')
                                    e.currentTarget.value = ''
                                  }
                                }
                              }}
                            />
                            <span className="text-sm text-gray-500">Enter برای افزودن</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex justify-end space-x-2 space-x-reverse">
                        <button
                          onClick={() => setEditingVariant(null)}
                          className="px-3 py-1 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                        >
                          انصراف
                        </button>
                        <button
                          onClick={handleSaveEdit}
                          className="px-3 py-1 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
                        >
                          <Save className="h-4 w-4 inline ml-1" />
                          ذخیره
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View Mode
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4 space-x-reverse mb-2">
                          <span className="font-mono text-lg font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            {variant.sku_code}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            variant.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {variant.is_active ? 'فعال' : 'غیرفعال'}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="font-medium">موجودی:</span> {variant.stock_qty}
                          </div>
                          <div>
                            <span className="font-medium">قیمت:</span> {
                              variant.price_override 
                                ? new Intl.NumberFormat('fa-IR').format(variant.price_override) + ' تومان'
                                : new Intl.NumberFormat('fa-IR').format(product.price) + ' تومان (پایه)'
                            }
                          </div>
                          <div>
                            <span className="font-medium">ویژگی‌ها:</span> {
                              Object.keys(variant.attributes).length > 0 
                                ? Object.entries(variant.attributes).map(([k, v]) => `${k}: ${v}`).join(', ')
                                : 'هیچ'
                            }
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-1">
                        <button
                          onClick={() => handleEditVariant(variant)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteVariant(variant.sku_code)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add New Variant */}
        {showAddForm ? (
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h4 className="text-md font-medium text-gray-900 mb-3">افزودن گونه جدید</h4>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">کد SKU</label>
                  <input
                    type="text"
                    value={newVariant.sku_code}
                    onChange={(e) => setNewVariant({...newVariant, sku_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">موجودی</label>
                  <input
                    type="number"
                    value={newVariant.stock_qty}
                    onChange={(e) => setNewVariant({...newVariant, stock_qty: parseInt(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">قیمت اضافی (تومان)</label>
                  <input
                    type="number"
                    value={newVariant.price_override || ''}
                    onChange={(e) => setNewVariant({...newVariant, price_override: e.target.value ? parseFloat(e.target.value) : undefined})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newVariant.is_active ?? true}
                      onChange={(e) => setNewVariant({...newVariant, is_active: e.target.checked})}
                      className="ml-2"
                    />
                    فعال
                  </label>
                </div>
              </div>
              
              {/* Attributes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">ویژگی‌ها</label>
                <div className="space-y-2">
                  {Object.entries(newVariant.attributes || {}).map(([key, value]) => (
                    <div key={key} className="flex items-center space-x-2 space-x-reverse">
                      <span className="text-sm font-medium">{key}:</span>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => addNewAttribute(key, e.target.value)}
                        className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                      <button
                        onClick={() => removeNewAttribute(key)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <input
                      type="text"
                      placeholder="نام ویژگی"
                      className="px-2 py-1 border border-gray-300 rounded text-sm"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          const key = e.currentTarget.value
                          if (key) {
                            addNewAttribute(key, '')
                            e.currentTarget.value = ''
                          }
                        }
                      }}
                    />
                    <span className="text-sm text-gray-500">Enter برای افزودن</span>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end space-x-2 space-x-reverse">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-3 py-1 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                >
                  انصراف
                </button>
                <button
                  onClick={handleAddVariant}
                  className="px-3 py-1 text-sm text-white bg-green-600 rounded hover:bg-green-700"
                >
                  <Plus className="h-4 w-4 inline ml-1" />
                  افزودن
                </button>
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700"
          >
            <Plus className="h-5 w-5 inline ml-2" />
            افزودن گونه جدید
          </button>
        )}

        {/* Close Button */}
        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            بستن
          </button>
        </div>
      </div>
    </div>
  )
}
