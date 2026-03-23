import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./globals.css";

// Expose the API base URL to modules and Jest tests.
// The API layer reads `globalThis.__VITE_API_URL__`.
(globalThis as any).__VITE_API_URL__ =
  (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Keep data fresh briefly to avoid unnecessary refetches.
      staleTime: 30_000,
      // Keep cache longer to support quick back/forward navigation.
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 0,
    },
  },
});

const App = lazy(() => import("./App"));

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<div className="p-4 text-sm text-gray-500">Loading app...</div>}>
        <App />
      </Suspense>
    </QueryClientProvider>
  </React.StrictMode>,
);
