import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export interface RouterContext {
  queryClient: QueryClient;
  auth: ReturnType<typeof import('./lib/auth').useAuth>;
}

export const getRouter = (authContext: ReturnType<typeof import('./lib/auth').useAuth>) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5, // 5 minutes
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });

  const router = createRouter({
    routeTree,
    context: { 
      queryClient,
      auth: authContext,
    },
    scrollRestoration: true,
    defaultPreloadStaleTime: 0,
  });

  return router;
};

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}
