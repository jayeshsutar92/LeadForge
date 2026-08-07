import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./api";

// --- Types ---
export interface BusinessCard {
  id: string;
  name: string;
  category: string;
  city: string;
  country: string;
  website?: string;
  rating?: number;
  reviews?: number;
  opportunity_score: number;
  created_at: string;
}

export interface BusinessListResponse {
  total: number;
  results: BusinessCard[];
}

export interface LeadResponse {
  id: string;
  business_id: string;
  status: string;
  priority: number;
  source: string;
  tags: string[];
  next_follow_up?: string;
  notes: string;
  assigned_to?: string;
  last_contacted?: string;
  created_at: string;
  updated_at: string;
}

export interface LeadListResponse {
  total: number;
  results: LeadResponse[];
}

// --- Hooks ---
export const useBusinesses = (params?: any) => {
  return useQuery({
    queryKey: ["businesses", params],
    queryFn: async () => {
      const res = await apiClient.get<BusinessListResponse>("/businesses", { params });
      return res.data;
    },
  });
};

export const useBusinessStats = () => {
  return useQuery({
    queryKey: ["businesses", "stats"],
    queryFn: async () => {
      const res = await apiClient.get("/businesses/stats");
      return res.data;
    },
  });
};

export const useLeads = (params?: any) => {
  return useQuery({
    queryKey: ["leads", params],
    queryFn: async () => {
      const res = await apiClient.get<LeadListResponse>("/crm/leads", { params });
      return res.data;
    },
  });
};

export const useLeadDetail = (leadId: string | null) => {
  return useQuery({
    queryKey: ["leads", leadId],
    queryFn: async () => {
      if (!leadId) return null;
      const res = await apiClient.get(`/crm/leads/${leadId}`);
      return res.data;
    },
    enabled: !!leadId,
  });
};

export const useBusinessDetail = (slug: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug],
    queryFn: async () => {
      if (!slug) return null;
      const res = await apiClient.get(`/businesses/${slug}`);
      return res.data;
    },
    enabled: !!slug,
  });
};

export const useIntelligence = (slug: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug, "intelligence"],
    queryFn: async () => {
      if (!slug) return null;
      const res = await apiClient.get(`/businesses/${slug}/intelligence/latest`);
      return res.data;
    },
    enabled: !!slug,
    retry: false, // May 404 if not analyzed yet
  });
};

export const useTriggerAnalysis = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (slug: string) => {
      const res = await apiClient.post(`/businesses/${slug}/intelligence/analyze`);
      return res.data;
    },
    onSuccess: (data, slug) => {
      queryClient.invalidateQueries({ queryKey: ["businesses", slug, "intelligence"] });
    },
  });
};

export const useGenerateProposal = () => {
  return useMutation({
    mutationFn: async ({ slug, opportunityId }: { slug: string; opportunityId: string }) => {
      const res = await apiClient.post(
        `/businesses/${slug}/opportunity/${opportunityId}/proposal/generate`,
      );
      return res.data;
    },
  });
};

export const useLegacyProposal = (slug: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug, "proposal"],
    queryFn: async () => {
      if (!slug) return null;
      const res = await apiClient.get(`/businesses/${slug}/proposal`);
      return res.data;
    },
    enabled: !!slug,
  });
};

export const useGenerateOutreach = () => {
  return useMutation({
    mutationFn: async ({
      slug,
      opportunityId,
      contactName,
    }: {
      slug: string;
      opportunityId: string;
      contactName?: string;
    }) => {
      const res = await apiClient.get(`/businesses/${slug}/opportunity/${opportunityId}/outreach`, {
        params: { contact_name: contactName },
      });
      return res.data;
    },
  });
};
