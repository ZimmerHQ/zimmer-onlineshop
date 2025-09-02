'use client'

import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore } from '@/lib/store'
import { Plus, Package, Filter, Edit, Trash2, Upload, X, RefreshCw, Search, Eye } from 'lucide-react'
import ProductWizard from '@/components/products/ProductWizard'
import BulkImportModal from '@/components/imports/BulkImportModal'
import FiltersBar from '@/components/products/FiltersBar'
import CategoriesInline from '@/components/products/CategoriesInline'
import { useProducts } from '@/lib/hooks/useProducts'
import { useCategories } from '@/lib/hooks/useCategories'
// import { useDebounce } from '@/lib/hooks/useDebounce'
import { apiBase } from '@/lib/utils'

// URL sync utility function
function setQuery(router: any, searchParams: URLSearchParams, patch: Record<string, string | null>) {
  const params = new URLSearchParams(searchParams.toString())
  Object.entries(patch).forEach(([k, v]) => {
    if (v === null || v === "") params.delete(k)
    else params.set(k, String(v))
  })
  router.replace(`?${params.toString()}`)
}

export default function ProductsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isClient, setIsClient] = useState(false)
  
  // Tab state - sync with URL
  const [activeTab, setActiveTab] = useState<'products' | 'categories'>(
    searchParams.get("tab") === "categories" ? "categories" : "products"
  )
  
  // Modal states
  const [showProductWizard, setShowProductWizard] = useState(false)
  const [showProductModal, setShowProductModal] = useState(false)
  const [showBulkImport, setShowBulkImport] = useState(false)
  
  // Onboarding state
  const [categoriesExist, setCategoriesExist] = useState<boolean | null>(null)
  
  // Search and filter state - separate input and applied query
  const [searchInput, setSearchInput] = useState(
    searchParams.get("q") || ''
  )
  const [searchQuery, setSearchQuery] = useState(
    searchParams.get("q") || ''
  )
  
  // Category filter - sync with URL
  const [selectedCategory, setSelectedCategory] = useState(
    searchParams.get("category_id") || 'all'
  )
  
  // Remove automatic search - only search when button is clicked
  // const debouncedSearchQuery = useDebounce(searchInput, 500)
  
  // Form states
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    sizes: '',
    image_url: ''
  })

  // Image upload states
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Use new hooks for data fetching
  const { products, totalCount, loading: isLoading, error: productsError, refetch: refetchProducts } = useProducts()
  const { categories, loading: categoriesLoading, error: categoriesError, refetch: refetchCategories } = useCategories()
  
  const { 
    addProduct,
    deleteProduct
  } = useDashboardStore()

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (isClient) {
      // Check if categories exist for onboarding
      checkCategoriesExist()
      
      // Check for category preselection from URL
      const categoryFromUrl = searchParams.get('category_id')
      if (categoryFromUrl) {
        setSelectedCategory(categoryFromUrl)
        setProductForm(prev => ({ ...prev, category_id: categoryFromUrl }))
      }
    }
  }, [isClient, searchParams])
  
  // Sync tab state with URL
  useEffect(() => {
    const tab = searchParams.get("tab")
    if (tab === "categories" || tab === "products") {
      setActiveTab(tab)
    }
  }, [searchParams])
  
  // Sync category filter with URL
  useEffect(() => {
    const categoryFromUrl = searchParams.get("category_id")
    if (categoryFromUrl) {
      setSelectedCategory(categoryFromUrl)
    } else {
      setSelectedCategory('all')
    }
  }, [searchParams])
  
  // Remove automatic search effect - only search when button is clicked
  // useEffect(() => {
  //   const timer = setTimeout(() => {
  //     setSearchQuery(searchInput)
  //   }, 500)
  //   
  //   return () => clearTimeout(timer)
  // }, [searchInput])
  
  useEffect(() => {
    // Refetch products when debounced search or category changes
    if (isClient) {
      const categoryId = selectedCategory && selectedCategory !== 'all' ? parseInt(selectedCategory) : undefined
      refetchProducts(1, 20, categoryId, searchQuery)
    }
  }, [searchQuery, selectedCategory, isClient])

  const checkCategoriesExist = async () => {
    try {
      const response = await fetch(`${apiBase}/api/categories/exists`)
      if (response.ok) {
        const data = await response.json()
        setCategoriesExist(data.exists)
      }
    } catch (error) {
      console.error('Error checking categories:', error)
      setCategoriesExist(false)
    }
  }

  // Category drill-down function
  const goToProductsWithCategory = useCallback((categoryId: number) => {
    // Switch tab, set category_id, reset page to 1
    const params = new URLSearchParams(searchParams.toString())
    params.set("tab", "products")
    params.set("category_id", String(categoryId))
    params.delete("page") // Reset pagination
    router.replace(`?${params.toString()}`)
    
    // Optional: scroll into view
    setTimeout(() => {
      const el = document.getElementById("products-section")
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" })
    }, 0)
  }, [router, searchParams])

  const handleFiltersChange = (filters: any) => {
    // Update search and category filters
    setSearchInput(filters.search || '')
    setSearchQuery(filters.search || '')
    setSelectedCategory(filters.category || 'all')
  }

  const handleSearch = () => {
    setSearchQuery(searchInput)
    setQuery(router, searchParams, { q: searchInput || null, page: "1" })
  }

  const handleClearSearch = () => {
    setSearchInput('')
    setSearchQuery('')
    setQuery(router, searchParams, { q: null, page: "1" })
  }

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('لطفاً یک فایل تصویری انتخاب کنید')
        return
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('حجم فایل نباید بیشتر از 5 مگابایت باشد')
        return
      }

      setSelectedImage(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const uploadImage = async (file: File): Promise<string> => {
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await fetch('http://localhost:8000/upload-image', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Upload failed')
      }
      
      const data = await response.json()
      return data.url
    } catch (error) {
      console.error('Upload error:', error)
      // Fallback: use a placeholder image
      return 'https://via.placeholder.com/300x300?text=Product+Image'
    }
  }

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate required fields
    if (!productForm.name.trim()) {
      alert('لطفاً نام محصول را وارد کنید');
      return;
    }
    if (!productForm.price || parseFloat(productForm.price) <= 0) {
      alert('لطفاً قیمت معتبر وارد کنید');
      return;
    }
    if (!productForm.stock || parseInt(productForm.stock) < 0) {
      alert('لطفاً موجودی معتبر وارد کنید');
      return;
    }
    if (!productForm.category_id) {
      alert('لطفاً دسته‌بندی را انتخاب کنید');
      return;
    }
    
    setUploading(true)
    
    try {
      let imageUrl = productForm.image_url
      
      // Upload image if selected
      if (selectedImage) {
        imageUrl = await uploadImage(selectedImage)
      }
      
      // Build attributes from sizes and other fields
      const attributes: Record<string, string[]> = {};
      if (productForm.sizes && productForm.sizes.trim()) {
        const sizesArray = productForm.sizes.split(',').map(s => s.trim()).filter(s => s);
        if (sizesArray.length > 0) {
          attributes.size = sizesArray;
        }
      }
      
      const productData = {
        name: productForm.name,
        description: productForm.description || "",
        price: parseFloat(productForm.price) || 0,
        stock: parseInt(productForm.stock) || 0,
        category_id: parseInt(productForm.category_id) || 0,
        image_url: imageUrl || productForm.image_url || undefined,
        tags: [],
        labels: [],
        attributes: Object.keys(attributes).length > 0 ? attributes : undefined,
        is_active: true
      };
      
      console.log('Sending product data:', productData);
      
      await addProduct(productData)
      
      setShowProductModal(false)
      setProductForm({
        name: '',
        description: '',
        price: '',
        stock: '',
        category_id: '',
        sizes: '',
        image_url: ''
      })
      removeImage()
      alert('محصول با موفقیت اضافه شد!')
      refetchProducts()
    } catch (error) {
      console.error('Error adding product:', error)
      console.error('Error type:', typeof error)
      console.error('Error details:', JSON.stringify(error, null, 2))
      
      let errorMessage = 'خطا در افزودن محصول'
      if (error instanceof Error) {
        errorMessage = error.message
      } else if (typeof error === 'object' && error !== null) {
        errorMessage = JSON.stringify(error)
      } else if (typeof error === 'string') {
        errorMessage = error
      }
      
      alert(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteProduct = async (id: number) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟')) {
      try {
        await deleteProduct(id)
        alert('محصول با موفقیت حذف شد!')
        refetchProducts()
      } catch (error) {
        console.error('Error deleting product:', error)
        alert('خطا در حذف محصول')
      }
    }
  }

  const handleAddProductFromCategory = (categoryId: number) => {
    setSelectedCategory(categoryId.toString())
    setProductForm(prev => ({ ...prev, category_id: categoryId.toString() }))
    setShowProductModal(true)
    setActiveTab('products')
  }

  const handleCategoryChange = () => {
    refetchCategories()
    refetchProducts()
  }

  // Onboarding guard
  if (categoriesExist === false) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="max-w-md mx-auto text-center py-12">
            <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">اول دسته‌بندی بسازید</h2>
            <div className="text-gray-600 mb-6">
              برای شروع کار با محصولات، ابتدا باید حداقل یک دسته‌بندی ایجاد کنید.
            </div>
            <button
              onClick={() => setActiveTab('categories')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 ml-2" />
              افزودن دسته‌بندی
            </button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!isClient || isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <div className="mt-2 text-gray-600">در حال بارگذاری...</div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">مدیریت محصولات و دسته‌بندی‌ها</h1>
            <div className="text-gray-600 mt-1">کاتالوگ محصولات و دسته‌بندی‌های خود را مدیریت کنید</div>
          </div>
          <div className="flex space-x-3 space-x-reverse">
            {activeTab === 'products' && (
              <>
                <button 
                  onClick={() => setShowBulkImport(true)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
                >
                  <Upload className="h-4 w-4 ml-2" />
                  درون‌ریزی گروهی
                </button>
                <button 
                  onClick={() => setShowProductModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 ml-2" />
                  افزودن محصول
                </button>
              </>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => {
                setActiveTab('products')
                setQuery(router, searchParams, { tab: "products" })
              }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'products'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Package className="h-4 w-4 inline ml-2" />
              محصولات
            </button>
            <button
              onClick={() => {
                setActiveTab('categories')
                setQuery(router, searchParams, { tab: "categories" })
              }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'categories'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Filter className="h-4 w-4 inline ml-2" />
              دسته‌بندی‌ها
            </button>
          </nav>
        </div>

        {/* Content */}
        {activeTab === 'products' ? (
          <div id="products-section" className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">محصولات</h2>
            
            {/* Category Filter Chip */}
            {selectedCategory !== 'all' && (
              <div className="mb-4 flex items-center gap-2 text-sm">
                <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-blue-700">
                  دسته‌بندی فعال: {categories?.find(c => c.id.toString() === selectedCategory)?.name}
                </span>
                <button
                  type="button"
                  className="text-red-600 underline hover:text-red-700"
                  onClick={() => {
                    setSelectedCategory('all')
                    setQuery(router, searchParams, { category_id: null, page: "1" })
                  }}
                >
                  نمایش همه
                </button>
              </div>
            )}
            
            {/* Enhanced Search Bar */}
            <div className="mb-6">
              <div className="flex items-center space-x-3 space-x-reverse">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleSearch()
                      }
                    }}
                    placeholder="جستجو در محصولات..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                </div>
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                >
                  جستجو
                </button>
                <button
                  onClick={handleClearSearch}
                  className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
                >
                  پاک کردن
                </button>
              </div>
              
              {/* Category Filter */}
              <div className="mt-3">
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    const newCategory = e.target.value
                    setSelectedCategory(newCategory)
                    setQuery(router, searchParams, { 
                      category_id: newCategory === 'all' ? null : newCategory,
                      page: "1" 
                    })
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">همه دسته‌بندی‌ها</option>
                  {categories?.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Results Summary */}
            <div className="text-sm text-gray-600 mb-4">
              {totalCount > 0 ? (
                <div>تعداد کل محصولات: {totalCount}</div>
              ) : (
                <div>هیچ محصولی یافت نشد</div>
              )}
            </div>
            
            {products.length === 0 ? (
              <div className="text-center py-8">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">هیچ محصولی یافت نشد</h3>
                <div className="text-gray-500 mb-4">هنوز محصولی اضافه نکرده‌اید</div>
                <button
                  onClick={() => setShowProductModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 ml-2" />
                  افزودن اولین محصول
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product) => (
                  <div key={product.id} className="border border-gray-200 rounded-lg p-4">
                    {/* Product Thumbnail */}
                    <div className="mb-3">
                                              {product.image_url ? (
                          <img
                            src={product.image_url}
                          alt={product.name}
                          className="w-full h-32 object-cover rounded-lg border"
                          onError={(e) => {
                            e.currentTarget.src = '/placeholder.svg';
                          }}
                        />
                      ) : (
                        <div className="w-full h-32 bg-gray-200 rounded-lg flex items-center justify-center">
                          <Package className="h-12 w-12 text-gray-400" />
                        </div>
                      )}
                    </div>
                    
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-gray-900">{product.name}</h3>
                      <div className="flex space-x-1">
                        <button
                          onClick={() => {
                            setProductForm({
                              name: product.name,
                              description: product.description || '',
                              price: product.price.toString(),
                              stock: (product.stock || 0).toString(),
                              category_id: product.category_id.toString(),
                              sizes: product.attributes?.size?.join(', ') || '',
                              image_url: product.image_url || ''
                            })
                            setShowProductModal(true)
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteProduct(product.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-500">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-lg font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                          {product.code}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          product.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {product.is_active ? 'فعال' : 'غیرفعال'}
                        </span>
                      </div>
                      
                      {product.description && <div className="text-gray-600 mb-2">{product.description}</div>}
                      
                      <div className="space-y-1">
                        <div className="flex justify-between">
                          <span>قیمت:</span>
                          <span className="font-medium">{new Intl.NumberFormat('fa-IR').format(product.price)} تومان</span>
                        </div>
                        <div className="flex justify-between">
                          <span>موجودی:</span>
                          <div className="flex items-center space-x-2 space-x-reverse">
                            <span className={`font-medium ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {product.stock || 0}
                            </span>
                            {product.stock <= 5 && product.stock > 0 && (
                              <span className="px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">
                                کم‌موجودی
                              </span>
                            )}
                          </div>
                        </div>
                        {product.stock <= 5 && product.stock > 0 && (
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>آستانه:</span>
                            <span>5</span>
                          </div>
                        )}
                        {product.category_name && (
                          <div className="flex justify-between">
                            <span>دسته‌بندی:</span>
                            <span className="text-blue-600">{product.category_name}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <CategoriesInline 
            onAddProduct={handleAddProductFromCategory}
            onCategoryChange={handleCategoryChange}
            onViewCategory={goToProductsWithCategory}
          />
        )}

        {/* Product Modal */}
        {showProductModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">افزودن محصول جدید</h3>
                <form onSubmit={handleAddProduct}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">نام محصول</label>
                    <input
                      type="text"
                      value={productForm.name}
                      onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                      placeholder="نام محصول"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">توضیحات</label>
                    <textarea
                      value={productForm.description}
                      onChange={(e) => setProductForm({...productForm, description: e.target.value})}
                      placeholder="توضیحات محصول"
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">قیمت (تومان)</label>
                    <input
                      type="number"
                      value={productForm.price}
                      onChange={(e) => setProductForm({...productForm, price: e.target.value})}
                      placeholder="0"
                      min="0"
                      step="0.01"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">موجودی</label>
                    <input
                      type="number"
                      value={productForm.stock}
                      onChange={(e) => setProductForm({...productForm, stock: e.target.value})}
                      placeholder="0"
                      min="0"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">دسته‌بندی</label>
                    <select
                      value={productForm.category_id}
                      onChange={(e) => setProductForm({...productForm, category_id: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">انتخاب کنید</option>
                      {categories?.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">سایزها (جدا شده با کاما)</label>
                    <input
                      type="text"
                      value={productForm.sizes}
                      onChange={(e) => setProductForm({...productForm, sizes: e.target.value})}
                      placeholder="S, M, L, XL"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">تصویر اصلی (URL)</label>
                    <input
                      type="url"
                      value={productForm.image_url}
                      onChange={(e) => setProductForm({...productForm, image_url: e.target.value})}
                      placeholder="https://example.com/image.jpg"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  

                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">آپلود تصویر</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageSelect}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {imagePreview && (
                      <div className="mt-2">
                        <img src={imagePreview} alt="Preview" className="w-20 h-20 object-cover rounded" />
                        <button
                          type="button"
                          onClick={removeImage}
                          className="mt-1 text-sm text-red-600 hover:text-red-700"
                        >
                          حذف تصویر
                        </button>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowProductModal(false)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                      انصراف
                    </button>
                    <button
                      type="submit"
                      disabled={uploading}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {uploading ? 'در حال آپلود...' : 'افزودن'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Bulk Import Modal */}
        <BulkImportModal
          isOpen={showBulkImport}
          onClose={() => setShowBulkImport(false)}
          onImport={async (file: File) => {
            // Handle bulk import logic here
            // For now, just log the file and close the modal
            console.log('Bulk import file:', file.name)
            // TODO: Implement actual bulk import logic
          }}
          onSuccess={() => {
            // Refresh products after successful import
            refetchProducts(1, 20, selectedCategory === 'all' ? undefined : parseInt(selectedCategory), searchQuery)
          }}
        />
      </div>
    </DashboardLayout>
  )
} 
