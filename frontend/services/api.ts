import type {
  Product,
  ProductListResponse,
  ScrapeJob,
  SizeGuideListResponse
} from "@/types";

export const API_BASE_URL = "https://fitler-test.onrender.com";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API error ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function scrapeWebsite(url: string): Promise<{ job_id: string }> {
  return request("/scrape", {
    method: "POST",
    body: JSON.stringify({ url })
  });
}

export function getJob(jobId: string): Promise<ScrapeJob> {
  return request(`/jobs/${jobId}`);
}

export function getLatestJob(): Promise<ScrapeJob | null> {
  return request("/jobs/latest");
}

export function getProducts(params: {
  search?: string;
  page?: number;
  page_size?: number;
  sort?: string;
}): Promise<ProductListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  if (params.sort) query.set("sort", params.sort);
  return request(`/products?${query.toString()}`);
}

export function getProduct(productId: string): Promise<Product> {
  return request(`/products/${productId}`);
}

export function getSizeGuides(params: {
  page?: number;
  page_size?: number;
}): Promise<SizeGuideListResponse> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  return request(`/size-guides?${query.toString()}`);
}

export function exportUrl(format: "json" | "csv" | "xlsx") {
  return `${API_BASE_URL}/export/${format}`;
}
