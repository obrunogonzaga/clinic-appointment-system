export interface Tag {
  id: string;
  name: string;
  color: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface TagListResponse {
  success: boolean;
  message?: string;
  data: Tag[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface TagCreateRequest {
  name: string;
  color: string;
}

export interface TagUpdateRequest {
  name?: string;
  color?: string;
  is_active?: boolean;
}

export interface TagMutationResponse {
  success: boolean;
  message?: string;
  data: Tag;
}

export interface TagDeleteResponse {
  success: boolean;
  message: string;
}
