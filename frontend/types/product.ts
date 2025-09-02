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
  available_sizes?: string[];
  available_colors?: string[];
  // NOTE: available_sizes / available_colors are UI-only helpers; do NOT include in API Product type
}; 