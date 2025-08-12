'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore, type Product } from '@/lib/store'
import { cn, formatDate, formatPrice, apiBase } from '@/lib/utils'

// Simple Toast Component
const Toast = ({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
      type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`}>
      <div className="flex items-center">
        <span className="mr-2">{type === 'success' ? '✅' : '❌'}</span>
        <span>{message}</span>
        <button onClick={onClose} className="mr-2 text-white hover:text-gray-200">×</button>
      </div>
    </div>
  )
}

// Utility function to ensure image URLs are absolute
const ensureAbsoluteUrl = (url: string): string => {
  if (!url) return `${apiBase}/static/placeholder.svg`
  
  // If already absolute, return as is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // If relative URL, make it absolute
  if (url.startsWith('/')) {
    return `${apiBase}${url}`
  }
  
  // If just filename, assume it's in static/images
      return `${apiBase}/static/images/${url}`
}
import { Plus, Edit, Trash2, Package, Loader2, Star, Eye, ShoppingCart } from 'lucide-react'

// ImagePreview component with fallback handling
const ImagePreview = ({ 
  imageUrl, 
  fallbackUrl, 
  className 
}: { 
  imageUrl: string; 
  fallbackUrl: string; 
  className?: string;
}) => {
  const [imageSrc, setImageSrc] = useState<string>(ensureAbsoluteUrl(imageUrl));
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (imageUrl) {
      setImageSrc(ensureAbsoluteUrl(imageUrl));
      setHasError(false);
    }
  }, [imageUrl]);

  const handleError = () => {
    if (!hasError && imageSrc !== ensureAbsoluteUrl(fallbackUrl)) {
      console.warn("Thumbnail failed to load, falling back to original image");
      setImageSrc(ensureAbsoluteUrl(fallbackUrl));
      setHasError(true);
    } else if (hasError) {
      // Final fallback to local placeholder
      console.warn("Both thumbnail and original image failed, using local placeholder");
      setImageSrc(`${apiBase}/static/placeholder.svg`);
    }
  };

  return (
    <img
      src={imageSrc}
      alt="Preview"
      className={className}
      onError={handleError}
    />
  );
};

interface ProductFormData {
  name: string
  description: string
  price: number
  sizes: string
  image_url: string
  stock: number
  imageFile?: File
}

interface ImageUploadResponse {
  url?: string
  thumbnail_url?: string
  filename?: string
  error?: string
  message?: string
}

const sizeOptions = [
  'XS', 'S', 'M', 'L', 'XL', 'XXL',
  '32', '34', '36', '38', '40', '42', '44',
  '6', '7', '8', '9', '10', '11', '12',
  'One Size', 'Free Size'
]

// Sample dummy products data for fallback
const dummyProducts: Product[] = [
  {
    id: '1',
    name: 'پیراهن مردانه کلاسیک',
    description: 'پیراهن مردانه با طراحی کلاسیک و کیفیت بالا، مناسب برای مناسبت‌های رسمی و روزمره',
    price: 850000,
    sizes: ['L', 'XL'],
    image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5), // 5 days ago
  },
  {
    id: '2',
    name: 'کفش ورزشی نایک',
    description: 'کفش ورزشی با کفی نرم و طراحی مدرن، مناسب برای دویدن و ورزش‌های روزانه',
    price: 1200000,
    sizes: ['40', '41', '42', '43'],
    image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
  },
  {
    id: '3',
    name: 'کیف دستی چرمی',
    description: 'کیف دستی چرمی با کیفیت بالا، دارای جیب‌های متعدد و طراحی شیک',
    price: 950000,
    sizes: ['One Size'],
    image_url: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7), // 7 days ago
  },
  {
    id: '4',
    name: 'ساعت مچی لوکس',
    description: 'ساعت مچی با طراحی لوکس و کیفیت سوئیسی، مناسب برای مناسبت‌های خاص',
    price: 2500000,
    sizes: ['Free Size'],
    image_url: 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
  },
  {
    id: '5',
    name: 'عینک آفتابی ریبن',
    description: 'عینک آفتابی با لنزهای محافظ UV و فریم سبک، مناسب برای روزهای آفتابی',
    price: 450000,
    sizes: ['One Size'],
    image_url: 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=400&fit=crop',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10), // 10 days ago
  },
  {
    id: '6',
    name: 'ژاکت پشمی زمستانی',
    description: 'ژاکت پشمی گرم و نرم، مناسب برای فصل زمستان و هوای سرد',
    price: 1800000,
    sizes: ['S', 'M', 'L', 'XL'],
    image_url: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1), // 1 day ago
  },
]

export default function ProductsPage() {
  // Hydration-safe state
  const [isClient, setIsClient] = useState(false)
  
  const { 
    products, 
    loading: isLoading,
    errors: error,
    fetchProducts,
    addProduct, 
    updateProduct, 
    deleteProduct,
    setProducts
  } = useDashboardStore()
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isImageUploading, setIsImageUploading] = useState(false)
  const [deletingProductId, setDeletingProductId] = useState<string | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    description: '',
    price: 0,
    sizes: '',
    image_url: '',
    stock: 0,
    imageFile: undefined,
  })

  // Handle hydration
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Load products from backend on component mount (only on client)
  useEffect(() => {
    if (isClient) {
      console.log('🔄 ProductsPage: Component mounted, fetching products...')
      fetchProducts().catch((error) => {
        console.warn('⚠️ ProductsPage: API failed, loading dummy data for testing:', error)
        // Load dummy data for testing if API fails
        setProducts(dummyProducts)
      })
    }
  }, [isClient]) // Removed fetchProducts and setProducts from dependencies to prevent loops

  // Debug logging for products state changes
  useEffect(() => {
    if (isClient) {
      console.log('📦 ProductsPage: Products state updated:', {
        count: products.length,
        products: products,
        isLoading,
        error
      })
    }
  }, [products, isLoading, error, isClient])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Client-side validation
    if (!formData.name.trim()) {
      alert('نام محصول الزامی است')
      return
    }
    if (!formData.description.trim()) {
      alert('توضیحات محصول الزامی است')
      return
    }
    if (formData.price <= 0) {
      alert('قیمت باید بیشتر از صفر باشد')
      return
    }
    if (!formData.sizes.trim()) {
      alert('سایز محصول الزامی است')
      return
    }
    if (!formData.imageFile && !formData.image_url.trim()) {
      alert('تصویر محصول الزامی است')
      return
    }
    
    setIsSubmitting(true)
    setIsImageUploading(false)
    
    try {
      let finalImageUrl = formData.image_url.trim()
      let uploadResult = null
      
      // If there's a new image file, upload it first
      if (formData.imageFile) {
        console.log('📤 Uploading image file:', formData.imageFile.name)
        setIsImageUploading(true)
        
        try {
          uploadResult = await uploadImage(formData.imageFile)
          console.log("Upload result:", uploadResult);
          // Use thumbnail_url if available, otherwise fallback to url
          finalImageUrl = uploadResult.thumbnail_url || uploadResult.url
          console.log('✅ Upload successful:', finalImageUrl)
          if (uploadResult.thumbnail_url) {
            console.log('📱 Using thumbnail URL for product display')
          } else {
            console.log('🖼️ Using full-size URL (no thumbnail available)')
          }
        } catch (uploadError) {
          console.log('❌ Upload failed:', uploadError instanceof Error ? uploadError.message : 'خطای نامشخص')
          setToast({ message: `خطا در آپلود تصویر: ${uploadError instanceof Error ? uploadError.message : 'خطای نامشخص'}`, type: 'error' })
          return
        } finally {
          setIsImageUploading(false)
        }
      } else if (editingProduct && !formData.imageFile) {
        // If editing and no new image, keep the original image URL
        finalImageUrl = editingProduct.image_url
        console.log('🔄 ProductsPage: Keeping original image URL for edit:', finalImageUrl)
      }
      
      // Transform form data to match API format
      const productData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        price: Number(formData.price),
        sizes: formData.sizes.split(',').map(s => s.trim()).filter(s => s.length > 0),
        image_url: finalImageUrl,
        thumbnail_url: uploadResult?.thumbnail_url || null,
        stock: Number(formData.stock)
      }
      
      console.log('💾 ProductsPage: Saving product with uploaded image:', productData)
      
      if (editingProduct) {
        console.log('✏️ ProductsPage: Updating existing product:', editingProduct.id)
        try {
          const result = await updateProduct(editingProduct.id, productData)
          if (result.success) {
            setToast({ message: 'محصول با موفقیت بروزرسانی شد', type: 'success' })
            handleCloseModal()
          } else {
            setToast({ message: 'خطا در بروزرسانی محصول', type: 'error' })
          }
        } catch (updateError) {
          console.error('❌ ProductsPage: Update failed:', updateError)
          const errorMessage = updateError instanceof Error ? updateError.message : 'خطا در بروزرسانی محصول'
          setToast({ message: `خطا در بروزرسانی محصول: ${errorMessage}`, type: 'error' })
        }
      } else {
        console.log('📝 ProductsPage: Creating new product, current count:', products.length)
        await addProduct(productData)
        console.log('📝 ProductsPage: Product created, new count:', products.length)
        setToast({ message: 'محصول جدید با موفقیت اضافه شد', type: 'success' })
        handleCloseModal()
      }
    } catch (error) {
      console.error('❌ ProductsPage: Error saving product:', error)
      const errorMessage = error instanceof Error ? error.message : 'خطای نامشخص'
      setToast({ message: `خطا در ذخیره محصول: ${errorMessage}`, type: 'error' })
    } finally {
      setIsSubmitting(false)
      setIsImageUploading(false)
    }
  }

  const handleEdit = (product: Product) => {
    console.log('✏️ ProductsPage: Editing product:', product)
    setEditingProduct(product)
    setFormData({
      name: product.name,
      description: product.description,
      price: product.price,
      sizes: product.sizes.join(', '),
      image_url: product.image_url,
      stock: product.stock || 0,
      imageFile: undefined,
    })
    setIsModalOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟')) {
      console.log('🗑️ ProductsPage: Deleting product:', id)
      setDeletingProductId(id)
      try {
        await deleteProduct(id)
      } catch (error) {
        console.error('❌ ProductsPage: Error deleting product:', error)
      } finally {
        setDeletingProductId(null)
      }
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingProduct(null)
    setFormData({
      name: '',
      description: '',
      price: 0,
      sizes: '',
      image_url: '',
      stock: 0,
      imageFile: undefined,
    })
  }

  // Function to upload image to FastAPI backend
  const uploadImage = async (file: File): Promise<{ url: string; thumbnail_url?: string }> => {
    console.log('📤 Uploading image file:', file.name)
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await fetch(`${apiBase}/upload-image`, {
        method: 'POST',
        body: formData,
      })
      
      const data: ImageUploadResponse = await response.json()
      console.log('🖼️ Image upload response:', data)
      
      // Check if response is successful and URL exists
      if (response.ok && data.url) {
        // Prefer thumbnail_url if available, fallback to url
        const imageUrl = data.thumbnail_url || data.url
        console.log('✅ Upload successful:', imageUrl)
        return { 
          url: data.url, 
          thumbnail_url: data.thumbnail_url 
        }
      } else {
        // Only throw error if response is not ok or URL is missing
        const errorMessage = data.error || data.message || 'خطا در آپلود تصویر'
        console.log('❌ Upload failed:', errorMessage)
        throw new Error(errorMessage)
      }
    } catch (error) {
      console.error('❌ Upload failed:', error)
      throw new Error(error instanceof Error ? error.message : 'خطا در آپلود تصویر')
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      console.log('🖼️ Image selected:', file.name, file.size, file.type)
      setFormData({ ...formData, imageFile: file })
      
      // Create a preview URL for the image
      const reader = new FileReader()
      reader.onload = (e) => {
        setFormData(prev => ({ ...prev, image_url: e.target?.result as string }))
      }
      reader.readAsDataURL(file)
    }
  }

  // Show loading state during SSR/hydration
  if (!isClient) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="mr-3 text-gray-500">در حال بارگذاری...</span>
        </div>
      </DashboardLayout>
    )
  }

  // Debug info display
  const debugInfo = (
    <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <h3 className="font-semibold text-yellow-800 mb-2">🔍 Debug Info:</h3>
      <div className="text-sm text-yellow-700 space-y-1">
        <p>• Client rendered: {isClient ? '✅ Yes' : '❌ No'}</p>
        <p>• Products count: {products.length}</p>
        <p>• Loading state: {isLoading ? '🔄 Loading' : '✅ Ready'}</p>
        <p>• Error state: {error ? `❌ ${error}` : '✅ No errors'}</p>
        <p>• API URL: {apiBase}/api/products</p>
        {error && error.includes('demo data') && (
          <div className="mt-2 p-2 bg-orange-100 border border-orange-300 rounded">
            <p className="text-orange-800 text-xs">
              <strong>⚠️ Demo Mode:</strong> Using sample data due to API connection issues. 
              This is normal during development or when the backend is offline.
            </p>
          </div>
        )}
      </div>
      {products.length > 0 && (
        <div className="mt-2">
          <p className="text-sm font-medium text-yellow-800">Sample product structure:</p>
          <pre className="text-xs bg-yellow-100 p-2 rounded mt-1 overflow-auto">
            {JSON.stringify(products[0], null, 2)}
          </pre>
        </div>
      )}
    </div>
  )

  return (
    <DashboardLayout>
      {/* Toast Notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">مدیریت محصولات</h1>
            <p className="text-gray-600 mt-1">کاتالوگ محصولات خود را مدیریت کنید</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 ml-2" />
            افزودن محصول
          </button>
        </div>

        {/* Debug Info */}
        {debugInfo}
        
        {/* Manual API Test Button */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-800 mb-2">🧪 Manual API Test:</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                console.log('🧪 Manual API test triggered')
                fetchProducts()
              }}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              Test API Call
            </button>
            <button
              onClick={async () => {
                console.log('🧪 Direct fetch test to API')
                try {
                  const response = await fetch(`${apiBase}/api/products`)
                  const data = await response.json()
                  console.log('🧪 Direct API response:', { status: response.status, data })
                  alert(`API Status: ${response.status}\nData: ${JSON.stringify(data, null, 2)}`)
                } catch (error) {
                  console.error('🧪 Direct API error:', error)
                  alert(`API Error: ${error}`)
                }
              }}
              className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-md hover:bg-purple-700"
            >
              Direct API Test
            </button>
            <button
              onClick={() => {
                console.log('🧪 Loading dummy data')
                setProducts(dummyProducts)
              }}
              className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
            >
              Load Dummy Data
            </button>
            <button
              onClick={() => {
                console.log('🧪 Clearing products')
                setProducts([])
              }}
              className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
            >
              Clear Products
            </button>
            <button
              onClick={() => {
                console.log('🧪 Force refresh products')
                fetchProducts()
              }}
              className="px-4 py-2 bg-orange-600 text-white text-sm font-medium rounded-md hover:bg-orange-700"
            >
              Force Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Package className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">کل محصولات</p>
                <p className="text-2xl font-semibold text-gray-900">{products.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Eye className="h-8 w-8 text-green-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">بازدید امروز</p>
                <p className="text-2xl font-semibold text-gray-900">1,234</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShoppingCart className="h-8 w-8 text-purple-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">فروش امروز</p>
                <p className="text-2xl font-semibold text-gray-900">45</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Star className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">امتیاز متوسط</p>
                <p className="text-2xl font-semibold text-gray-900">4.8</p>
              </div>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {isLoading && products.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            <span className="mr-3 text-gray-500">در حال بارگذاری محصولات...</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <p className="text-red-500 mb-2">خطا در بارگذاری محصولات</p>
              <p className="text-sm text-gray-500">{error}</p>
              <button
                onClick={() => fetchProducts()}
                className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
              >
                تلاش مجدد
              </button>
            </div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">هیچ محصولی یافت نشد</h3>
            <p className="text-gray-500 mb-4">هنوز محصولی اضافه نکرده‌اید</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 ml-2" />
              افزودن اولین محصول
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.isArray(products) && products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="aspect-square bg-gray-100 relative group">
                {/* Stock badge */}
                {typeof product.stock === 'number' && (
                  <span
                    className={
                      'absolute top-2 right-2 px-2 py-1 text-xs rounded font-bold ' +
                      (product.stock === 0
                        ? 'bg-red-500 text-white'
                        : product.stock <= 5
                        ? 'bg-orange-400 text-white'
                        : 'bg-gray-200 text-gray-700')
                    }
                  >
                    {product.stock === 0
                      ? 'ناموجود'
                      : product.stock <= 5
                      ? 'موجودی کم'
                      : `موجودی: ${product.stock}`}
                  </span>
                )}
                <img
                  src={product.thumbnail_url ? ensureAbsoluteUrl(product.thumbnail_url) : ensureAbsoluteUrl(product.image_url)}
                  alt={product.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Prevent infinite loops by nullifying onerror after first failure
                    if (e.currentTarget.src !== 'https://via.placeholder.com/400x400?text=تصویر+موجود+نیست') {
                      console.warn('⚠️ ProductsPage: Image failed to load:', product.thumbnail_url || product.image_url)
                      e.currentTarget.onerror = null // Prevent infinite loops
                      e.currentTarget.src = 'https://via.placeholder.com/400x400?text=تصویر+موجود+نیست'
                    }
                  }}
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex space-x-2">
                    <button
                      onClick={() => handleEdit(product)}
                      className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors"
                      title="ویرایش محصول"
                    >
                      <Edit className="h-4 w-4 text-gray-700" />
                    </button>
                    <button
                      onClick={() => handleDelete(product.id)}
                      disabled={deletingProductId === product.id}
                      className="p-2 bg-white rounded-full shadow-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                      title="حذف محصول"
                    >
                      {deletingProductId === product.id ? (
                        <Loader2 className="h-4 w-4 animate-spin text-gray-700" />
                      ) : (
                        <Trash2 className="h-4 w-4 text-red-600" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {product.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                      {product.description}
                    </p>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-lg font-bold text-gray-900">
                        {formatPrice(product.price)}
                      </span>
                      <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {Array.isArray(product.sizes) ? product.sizes.join(', ') : product.sizes}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 text-yellow-400 fill-current" />
                        <span className="text-sm text-gray-600">4.8</span>
                        <span className="text-xs text-gray-400">(124)</span>
                      </div>
                      <p className="text-xs text-gray-400">
                        اضافه شده {formatDate(product.createdAt)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            ))}
          </div>
        )}

        {/* Add/Edit Product Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {editingProduct ? 'ویرایش محصول' : 'افزودن محصول جدید'}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    نام محصول
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    توضیحات
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    required
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      قیمت (تومان)
                    </label>
                    <input
                      type="number"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
                      required
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      سایزها (با کاما جدا کنید)
                    </label>
                    <input
                      type="text"
                      value={formData.sizes}
                      onChange={(e) => setFormData({ ...formData, sizes: e.target.value })}
                      placeholder="مثال: 38, 39, 40 یا L, XL"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                {/* Stock input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    موجودی
                  </label>
                  <input
                    type="number"
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: Number(e.target.value) })}
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    تصویر محصول
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {formData.image_url && (
                    <div className="mt-2">
                      <ImagePreview 
                        imageUrl={formData.image_url}
                        fallbackUrl={editingProduct ? editingProduct.image_url : formData.image_url}
                        className="w-20 h-20 object-cover rounded border border-gray-200"
                      />
                      {formData.imageFile && (
                        <p className="text-xs text-gray-500 mt-1">
                          فایل انتخاب شده: {formData.imageFile.name} 
                          ({Math.round(formData.imageFile.size / 1024)} KB)
                        </p>
                      )}
                      {isImageUploading && (
                        <div className="flex items-center mt-1">
                          <Loader2 className="h-3 w-3 animate-spin text-blue-500 ml-1" />
                          <span className="text-xs text-blue-500">در حال آپلود تصویر...</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                  >
                    انصراف
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || isImageUploading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isImageUploading ? 'در حال آپلود تصویر...' : 
                     isSubmitting ? 'در حال ذخیره...' : 
                     (editingProduct ? 'ویرایش' : 'افزودن')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
} 
