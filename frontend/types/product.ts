export type ProductAttributes = Record<string, string[]>;

export type ProductCreateRequest = {
  name: string;
  description?: string;
  price: number;
  stock: number;
  category_id: number;
  image_url?: string;
  tags?: string;          // Backend expects comma-separated string
  labels?: string[];      // Backend expects array of strings
  attributes?: ProductAttributes; // e.g. { size: ["M","L"], color: ["black"] }
  is_active?: boolean;
};

export type ProductUpdateRequest = Partial<ProductCreateRequest>;

export type Product = {
  id: number;
  code: string;
  name: string;
  description?: string;
  price: number;
  stock: number;
  category_id: number;
  image_url?: string;
  tags?: string;          // Backend returns comma-separated string
  labels?: string[];      // Backend returns array of strings
  attributes?: ProductAttributes;
  is_active: boolean;
  createdAt?: string;
  updatedAt?: string;
  // Computed fields from API response
  category_name?: string;
  category?: string;  // Used in chat page
  available_sizes?: string[];
  available_colors?: string[];
  image?: string;  // Used in chat page (alternative to image_url)
  // Analytics fields
  sales?: number;
  revenue?: number;
  // Additional fields used in AI tools
  total_stock?: number;
  thumbnail_url?: string;
  images?: string[];
  variants?: any[];  // Product variants
  variants_count?: number;  // Number of variants for this product
  // Snake_case properties from API response
  created_at?: string;
  updated_at?: string;
  // NOTE: available_sizes / available_colors are UI-only helpers; do NOT include in API Product type
}; 