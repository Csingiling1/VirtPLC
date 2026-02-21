import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export class ApiError extends Error {
  public status: number;
  public details?: any;

  constructor(message: string, status: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

// HTTP Methods
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// API Client configuration
interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

/**
 * Type-safe API client wrapper with error handling, retries, and interceptors.
 * Follows clean architecture principles for API communication.
 */
class ApiClient {
  private client: AxiosInstance;
  private config: ApiClientConfig;

  constructor(config: ApiClientConfig) {
    this.config = {
      timeout: 10000,
      retries: 3,
      retryDelay: 1000,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors for authentication and error handling
   */
  private setupInterceptors(): void {
    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        // Log successful responses in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (!originalRequest) {
          return Promise.reject(this.createApiError(error));
        }

        // Handle token refresh for 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAuthToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Token refresh failed, redirect to login
            this.handleAuthFailure();
            return Promise.reject(this.createApiError(error));
          }
        }

        // Handle retries for network errors
        if (this.shouldRetry(error) && (originalRequest._retryCount || 0) < this.config.retries!) {
          originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

          await this.delay(this.config.retryDelay! * originalRequest._retryCount);
          return this.client(originalRequest);
        }

        return Promise.reject(this.createApiError(error));
      }
    );
  }

  /**
   * Generic request method with type safety
   */
  async request<T = any>(
    method: HttpMethod,
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.request({
        method,
        url,
        data,
        ...config,
      });

      // Return the actual response data directly
      return response.data;
    } catch (error) {
      throw error instanceof ApiError ? error : this.createApiError(error as AxiosError);
    }
  }

  // Convenience methods for common HTTP operations
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('GET', url, undefined, config);
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('POST', url, data, config);
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', url, data, config);
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', url, data, config);
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', url, undefined, config);
  }

  /**
   * Create a standardized API error
   */
  private createApiError(error: AxiosError): ApiError {
    const status = error.response?.status || 0;
    const message = error.response?.data?.message ||
                   error.response?.data?.error ||
                   error.message ||
                   'An unexpected error occurred';

    return new ApiError(message, status, error.response?.data);
  }

  /**
   * Check if an error should be retried
   */
  private shouldRetry(error: AxiosError): boolean {
    // Retry on network errors or 5xx server errors
    return !error.response ||
           error.response.status >= 500 ||
           error.code === 'ECONNABORTED' ||
           error.code === 'ENOTFOUND';
  }

  /**
   * Get authentication token from storage
   */
  private getAuthToken(): string | null {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  }

  /**
   * Refresh authentication token
   */
  private async refreshAuthToken(): Promise<string | null> {
    try {
      // Implement token refresh logic here
      // This would typically call a refresh endpoint
      return null; // Placeholder
    } catch {
      return null;
    }
  }

  /**
   * Handle authentication failure
   */
  private handleAuthFailure(): void {
    // Clear stored tokens and redirect to login
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    } catch {
      // Handle localStorage errors
    }
  }

  /**
   * Generate a unique request ID for tracking
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Utility method for delays
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://backend:8080',
});

export default apiClient;
export { ApiClient };