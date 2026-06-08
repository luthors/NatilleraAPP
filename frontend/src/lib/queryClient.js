/**
 * queryClient — shared TanStack Query client.
 *
 * Retry policy:
 *  - Do NOT retry on 4xx errors (client mistakes should surface immediately).
 *  - Retry once on 5xx / network errors.
 */
import { QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2,   // 2 min
      gcTime: 1000 * 60 * 10,     // 10 min
      retry: (failureCount, error) => {
        if (error?.response?.status < 500) return false
        return failureCount < 1
      },
    },
    mutations: {
      retry: false,
    },
  },
})

export default queryClient
