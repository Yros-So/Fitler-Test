export type ProductVariant = {
  id: string;
  external_id: string | null;
  title: string;
  sku: string | null;
  price: string | null;
  available: boolean;
  options: Record<string, unknown>;
};

export type Product = {
  id: string;
  website_id: string;
  external_id: string | null;
  name: string;
  price: string | null;
  description: string | null;
  image_urls: string[];
  vendor: string | null;
  tags: string[];
  handle: string;
  url: string;
  options: Record<string, unknown>;
  variants: ProductVariant[];
  created_at: string;
  updated_at: string;
};

export type ProductListResponse = {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
};

export type SizeGuide = {
  id: string;
  website_id: string;
  product_id: string | null;
  title: string;
  source_url: string;
  content: {
    tables?: string[][][];
    source_type?: string;
    metadata?: Record<string, unknown>;
  };
  raw_text: string | null;
  created_at: string;
  updated_at: string;
};

export type SizeGuideListResponse = {
  items: SizeGuide[];
  total: number;
  page: number;
  page_size: number;
};

export type ScrapeStatus = "pending" | "running" | "completed" | "failed";

export type ScrapeJob = {
  id: string;
  website_id: string;
  status: ScrapeStatus;
  error: string | null;
  started_at: string | null;
  finished_at: string | null;
  stats: Record<string, number>;
  created_at: string;
  updated_at: string;
};
