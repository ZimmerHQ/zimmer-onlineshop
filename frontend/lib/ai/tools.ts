import { apiBase } from '@/lib/utils'

// Tool for searching products (minimal info for suggestions)
export const searchProductsTool = async ({ 
  q, 
  code, 
  category_id, 
  limit = 20 
}: {
  q?: string
  code?: string
  category_id?: number
  limit?: number
}) => {
  try {
    const params = new URLSearchParams()
    
    // Prioritize code search if provided
    if (code) {
      params.set('code', code)
    } else if (q) {
      params.set('q', q)
    }
    
    if (category_id) params.set('category_id', category_id.toString())
    params.set('limit', limit.toString())
    
    const response = await fetch(`${apiBase}/api/products/search?${params.toString()}`)
    
    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`)
    }
    
    const products = await response.json()
    
    if (products.length === 0) {
      return {
        success: true,
        message: code ? `هیچ محصولی با کد "${code}" یافت نشد` : 'هیچ محصولی یافت نشد',
        products: []
      }
    }
    
    // Format products for chat display with structured attributes
    const formattedProducts = products.map((product: any) => ({
      id: product.id,
      code: product.code,
      name: product.name,
      price: product.price,
      stock: product.total_stock,
      category: product.category_name,
      image: product.thumbnail_url,
      available_sizes: product.available_sizes || [],
      available_colors: product.available_colors || []
    }))
    
    return {
      success: true,
      message: code ? 
        `محصول با کد "${code}" یافت شد:` : 
        `${formattedProducts.length} محصول یافت شد:`,
      products: formattedProducts
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در جستجوی محصولات: ${error instanceof Error ? error.message : 'خطای نامشخص'}`,
      products: []
    }
  }
}

// Tool for getting detailed product information
export const getProductDetailsTool = async ({ 
  code, 
  id 
}: {
  code?: string
  id?: number
}) => {
  try {
    let url: string
    
    if (code) {
      url = `${apiBase}/api/products/code/${code}`
    } else if (id) {
      url = `${apiBase}/api/products/id/${id}`
    } else {
      throw new Error('کد محصول یا شناسه باید مشخص شود')
    }
    
    const response = await fetch(url)
    
    if (!response.ok) {
      if (response.status === 404) {
        return {
          success: false,
          message: 'محصول یافت نشد'
        }
      }
      throw new Error(`دریافت اطلاعات محصول ناموفق: ${response.statusText}`)
    }
    
    const product = await response.json()
    
    // Format product details for chat display with structured attributes
    const formattedProduct = {
      id: product.id,
      code: product.code,
      name: product.name,
      description: product.description,
      price: product.price,
      total_stock: product.total_stock,
      category: product.category,
      images: product.images,
      variants: product.variants,
      available_sizes: product.available_sizes || [],
      available_colors: product.available_colors || [],
      tags: product.tags
    }
    
    return {
      success: true,
      message: 'اطلاعات محصول دریافت شد',
      product: formattedProduct
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در دریافت اطلاعات محصول: ${error instanceof Error ? error.message : 'خطای نامشخص'}`
    }
  }
}

// Tool for creating draft orders
export const createOrderTool = async ({ 
  customer_name, 
  contact, 
  items 
}: {
  customer_name: string
  contact: string
  items: Array<{
    product_id: number
    variant_id?: number
    quantity: number
  }>
}) => {
  try {
    // Create draft order
    const draftResponse = await fetch(`${apiBase}/api/orders/draft`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        customer_name,
        contact,
        items,
        note: null
      })
    })
    
    if (!draftResponse.ok) {
      const errorData = await draftResponse.json().catch(() => ({}))
      throw new Error(errorData.detail || `ایجاد سفارش ناموفق: ${draftResponse.statusText}`)
    }
    
    const draftOrder = await draftResponse.json()
    
    return {
      success: true,
      message: 'سفارش پیش‌نویس ایجاد شد. لطفاً تأیید کنید.',
      order: {
        id: draftOrder.id,
        order_number: draftOrder.order_number,
        customer_name: draftOrder.customer_name,
        total_amount: draftOrder.total_amount,
        items: draftOrder.items.map((item: any) => ({
          product_name: item.product_name,
          variant_size: item.variant_size,
          variant_color: item.variant_color,
          quantity: item.quantity,
          unit_price: item.unit_price,
          total_price: item.total_price
        }))
      },
      requiresConfirmation: true
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در ایجاد سفارش: ${error instanceof Error ? error.message : 'خطای نامشخص'}`,
      requiresConfirmation: false
    }
  }
}

// Tool for confirming draft orders
export const confirmOrderTool = async ({ order_id }: { order_id: number }) => {
  try {
    const response = await fetch(`${apiBase}/api/orders/confirm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ order_id })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `تأیید سفارش ناموفق: ${response.statusText}`)
    }
    
    const confirmedOrder = await response.json()
    
    return {
      success: true,
      message: 'سفارش با موفقیت تأیید شد و در انتظار تأیید ادمین است.',
      order: {
        id: confirmedOrder.id,
        order_number: confirmedOrder.order_number,
        status: confirmedOrder.status,
        total_amount: confirmedOrder.total_amount
      }
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در تأیید سفارش: ${error instanceof Error ? error.message : 'خطای نامشخص'}`
    }
  }
}

// Tool for checking product availability
export const checkAvailabilityTool = async ({ 
  product_id, 
  code 
}: {
  product_id?: number
  code?: string
}) => {
  try {
    let url: string
    
    if (code) {
      url = `${apiBase}/api/products/code/${code}`
    } else if (product_id) {
      url = `${apiBase}/api/products/id/${product_id}`
    } else {
      throw new Error('کد محصول یا شناسه باید مشخص شود')
    }
    
    const response = await fetch(url)
    
    if (!response.ok) {
      if (response.status === 404) {
        return {
          success: false,
          message: 'محصول یافت نشد'
        }
      }
      throw new Error(`بررسی موجودی ناموفق: ${response.statusText}`)
    }
    
    const product = await response.json()
    
    // Format availability information with structured attributes
    const availability = {
      product_name: product.name,
      code: product.code,
      total_stock: product.total_stock,
      available_sizes: product.available_sizes || [],
      available_colors: product.available_colors || [],
      variants: product.variants.map((variant: any) => ({
        size: variant.size,
        color: variant.color,
        stock: variant.stock,
        price_delta: variant.price_delta
      }))
    }
    
    return {
      success: true,
      message: 'اطلاعات موجودی دریافت شد',
      availability
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در بررسی موجودی: ${error instanceof Error ? error.message : 'خطای نامشخص'}`
    }
  }
}

// Tool for getting categories summary
export const getCategoriesSummaryTool = async () => {
  try {
    const response = await fetch(`${apiBase}/api/categories/`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch categories: ${response.statusText}`)
    }
    
    const categories = await response.json()
    
    const summary = categories.map((category: any) => ({
      id: category.id,
      name: category.name,
      prefix: category.prefix,
      product_count: category.product_count || 0
    }))
    
    return {
      success: true,
      message: `${summary.length} دسته‌بندی یافت شد`,
      categories: summary
    }
  } catch (error) {
    return {
      success: false,
      message: `خطا در دریافت دسته‌بندی‌ها: ${error instanceof Error ? error.message : 'خطای نامشخص'}`,
      categories: []
    }
  }
}

// Tool for checking if categories exist
export const checkCategoriesExistTool = async () => {
  try {
    const response = await fetch(`${apiBase}/api/categories/`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch categories: ${response.statusText}`)
    }
    
    const categories = await response.json()
    
    return {
      success: true,
      exists: categories.length > 0,
      count: categories.length,
      message: categories.length > 0 ? 
        `${categories.length} دسته‌بندی موجود است` : 
        'هیچ دسته‌بندی موجود نیست'
    }
  } catch (error) {
    return {
      success: false,
      exists: false,
      count: 0,
      message: `خطا در بررسی دسته‌بندی‌ها: ${error instanceof Error ? error.message : 'خطای نامشخص'}`
    }
  }
}

// Export all tools
export const chatbotTools = {
  searchProducts: searchProductsTool,
  getProductDetails: getProductDetailsTool,
  createOrder: createOrderTool,
  confirmOrder: confirmOrderTool,
  checkAvailability: checkAvailabilityTool,
  getCategoriesSummary: getCategoriesSummaryTool,
  checkCategoriesExist: checkCategoriesExistTool
} 