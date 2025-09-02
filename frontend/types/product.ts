export type ProductAttributes = Record<string, string[]>;

export type ProductCreateRequest = {
  name: string;
  description?: string;
  price: number;
  stock: number;
  category_id: number;
  image_url?: string;
  tags?: string[];        // legacy/simple tags if we keep them
  labels?: string[];      // normalized labels
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
  tags?: string[];
  labels?: string[];
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
  // Snake_case properties from API response
  created_at?: string;
  updated_at?: string;
  // NOTE: available_sizes / available_colors are UI-only helpers; do NOT include in API Product type
}; 