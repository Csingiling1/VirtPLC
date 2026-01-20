import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Return type for the useAsyncOperation hook
 */
interface AsyncOperationResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

/**
 * Configuration options for async operations
 */
interface AsyncOperationOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  retryCount?: number;
  retryDelay?: number;
}

/**
 * Custom hook for safe async operations with loading states, error handling,
 * and retry logic. Follows React best practices for async operations.
 *
 * @param asyncFunction The async function to execute
 * @param options Configuration options
 * @returns Object with data, loading, error states and execute function
 */
export function useAsyncOperation<T = any>(
  asyncFunction: (...args: any[]) => Promise<T>,
  options: AsyncOperationOptions = {}
): AsyncOperationResult<T> {
  const {
    immediate = false,
    onSuccess,
    onError,
    retryCount = 0,
    retryDelay = 1000,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Use ref to track if component is mounted (prevent state updates on unmounted components)
  const isMountedRef = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      if (!isMountedRef.current) return null;

      setLoading(true);
      setError(null);

      let lastError: Error | null = null;

      for (let attempt = 0; attempt <= retryCount; attempt++) {
        try {
          if (!isMountedRef.current) return null;

          const result = await asyncFunction(...args);

          if (!isMountedRef.current) return null;

          setData(result);
          setLoading(false);

          // Call success callback
          if (onSuccess) {
            try {
              onSuccess(result);
            } catch (callbackError) {
              console.warn('Error in onSuccess callback:', callbackError);
            }
          }

          return result;

        } catch (err) {
          lastError = err instanceof Error ? err : new Error(String(err));

          // If this isn't the last attempt, wait before retrying
          if (attempt < retryCount) {
            await new Promise(resolve => setTimeout(resolve, retryDelay));
            continue;
          }

          // Last attempt failed
          break;
        }
      }

      // All attempts failed
      if (!isMountedRef.current) return null;

      setError(lastError);
      setLoading(false);

      // Call error callback
      if (onError) {
        try {
          onError(lastError!);
        } catch (callbackError) {
          console.warn('Error in onError callback:', callbackError);
        }
      }

      return null;
    },
    [asyncFunction, onSuccess, onError, retryCount, retryDelay]
  );

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
}

/**
 * Hook for debounced async operations to prevent excessive API calls
 */
export function useDebouncedAsyncOperation<T = any>(
  asyncFunction: (...args: any[]) => Promise<T>,
  delay: number,
  options: AsyncOperationOptions = {}
): AsyncOperationResult<T> & { debouncedExecute: (...args: any[]) => void } {
  const timeoutRef = useRef<NodeJS.Timeout>();

  const asyncOp = useAsyncOperation(asyncFunction, options);

  const debouncedExecute = useCallback(
    (...args: any[]) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        asyncOp.execute(...args);
      }, delay);
    },
    [asyncOp.execute, delay]
  );

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    ...asyncOp,
    debouncedExecute,
  };
}