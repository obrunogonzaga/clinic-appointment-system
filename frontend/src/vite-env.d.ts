/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENABLE_PDF_EXPORT: string
  readonly VITE_ENABLE_EXCEL_IMPORT: string
  readonly VITE_ENABLE_NOTIFICATIONS: string
  readonly VITE_MAX_FILE_SIZE: string
  readonly VITE_ALLOWED_FILE_TYPES: string
  readonly VITE_DEFAULT_TIMEZONE: string
  readonly VITE_DATE_FORMAT: string
  readonly VITE_TIME_FORMAT: string
  readonly VITE_ITEMS_PER_PAGE: string
  readonly VITE_DEFAULT_LANGUAGE: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly VITE_ENABLE_MOCK_API: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}