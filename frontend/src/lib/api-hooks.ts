import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./api";

// --- Types ---
export interface BusinessCard {
  id: string;
  slug: string;
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
  business?: BusinessCard;
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

export interface ContactDiscoveryCandidate {
  platform: string;
  title: string;
  href: string;
  username?: string;
  body: string;
  confidence: number;
  status: string;
  evidence: string[];
}

export interface ContactDiscoveryResponse {
  id: string;
  business_id: string;
  data: {
    candidates: ContactDiscoveryCandidate[];
    recommended_platform?: string;
  };
  created_at: string;
  updated_at: string;
}

// --- Hooks ---
export const useBusinesses = (params?: Record<string, unknown>) => {
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

export const useDiscoverBusinesses = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { query: string; region: string }) => {
      const res = await apiClient.post("/businesses/discover", data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["businesses"] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["businesses", "stats"] });
    },
  });
};

export const useLeads = (params?: Record<string, unknown>) => {
  return useQuery({
    queryKey: ["leads", params],
    queryFn: async () => {
      const res = await apiClient.get<LeadListResponse>("/crm/leads", { params });
      return res.data;
    },
  });
};

export const useCreateBusiness = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Record<string, unknown>) => {
      const res = await apiClient.post("/businesses", data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["businesses"] });
    },
  });
};

export const useCreateLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Record<string, unknown>) => {
      const res = await apiClient.post("/crm/leads", data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
};

export const useUpdateLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) => {
      const res = await apiClient.put(`/crm/leads/${id}`, data);
      return res.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["leads", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["businesses", "stats"] });
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

export const useOpportunity = (slug: string | null, biId: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug, "opportunity", biId],
    queryFn: async () => {
      if (!slug || !biId) return null;
      const res = await apiClient.get(`/businesses/${slug}/intelligence/${biId}/opportunity`);
      return res.data;
    },
    enabled: !!slug && !!biId,
    retry: false, // May 404 if not generated yet
  });
};

export const useGenerateOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ slug, biId }: { slug: string; biId: string }) => {
      const res = await apiClient.post(
        `/businesses/${slug}/intelligence/${biId}/opportunity/generate`,
      );
      return res.data;
    },
    onSuccess: (data, { slug, biId }) => {
      queryClient.invalidateQueries({ queryKey: ["businesses", slug, "opportunity", biId] });
    },
  });
};

export const useGenerateProposal = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ slug, opportunityId }: { slug: string; opportunityId: string }) => {
      const res = await apiClient.post(
        `/businesses/${slug}/opportunity/${opportunityId}/proposal/generate`,
        null,
        { params: { template_type: "standard" } },
      );
      return res.data;
    },
    onSuccess: (data, { slug, opportunityId }) => {
      queryClient.invalidateQueries({ queryKey: ["businesses", slug, "proposal", opportunityId] });
      queryClient.invalidateQueries({ queryKey: ["proposals", "all"] });
    },
  });
};

export const useProposal = (slug: string | null, opportunityId: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug, "proposal", opportunityId],
    queryFn: async () => {
      if (!slug || !opportunityId) return null;
      const res = await apiClient.get(`/businesses/${slug}/opportunity/${opportunityId}/proposal`);
      return res.data;
    },
    enabled: !!slug && !!opportunityId,
    retry: false,
  });
};

export const useAllProposals = () => {
  return useQuery({
    queryKey: ["proposals", "all"],
    queryFn: async () => {
      const res = await apiClient.get("/crm/proposals");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return res.data as Array<{ slug: string; proposal: any }>;
    },
  });
};

export const useGenerateOutreach = () => {
  return useMutation({
    mutationFn: async ({
      slug,
      opportunityId,
      contactName,
      strategy,
      channel,
    }: {
      slug: string;
      opportunityId: string;
      contactName?: string;
      strategy?: string;
      channel?: string;
    }) => {
      const res = await apiClient.get(`/businesses/${slug}/opportunity/${opportunityId}/outreach`, {
        params: { contact_name: contactName, strategy, channel },
      });
      return res.data;
    },
  });
};
export interface SocialProfile {
  platform: string;
  url: string;
  username: string;
  confidence: number;
  reasoning: string;
}

export interface SocialIntelligenceData {
  data: {
    profiles: SocialProfile[];
    recommended_platform: string | null;
    messages: Record<string, string>;
  } | null;
  created_at?: string;
}

export function useSocialIntelligence(businessId: string | undefined) {
  return useQuery<SocialIntelligenceData, Error>({
    queryKey: ["socialIntelligence", businessId],
    queryFn: async () => {
      const res = await apiClient.get(`/social-intelligence/${businessId}`);
      return res.data;
    },
    enabled: !!businessId,
  });
}

// --- Delete Hooks ---

export const useDeleteBusiness = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (slug: string) => {
      await apiClient.delete(`/businesses/${slug}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["businesses"] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
};

export const useDeleteLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/crm/leads/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["businesses", "stats"] });
    },
  });
};

export const useDeleteProposal = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ slug, proposalId }: { slug: string; proposalId: string }) => {
      await apiClient.delete(`/businesses/${slug}/proposal/${proposalId}`);
    },
    onSuccess: (data, { slug }) => {
      queryClient.invalidateQueries({ queryKey: ["businesses", slug, "proposal"] });
      queryClient.invalidateQueries({ queryKey: ["proposals", "all"] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
};

export const useContactDiscovery = (slug: string | null) => {
  return useQuery({
    queryKey: ["businesses", slug, "contact-discovery"],
    queryFn: async () => {
      if (!slug) return null;
      const res = await apiClient.get<ContactDiscoveryResponse>(
        `/businesses/${slug}/contact-discovery`,
      );
      return res.data;
    },
    enabled: !!slug,
    retry: false,
  });
};

export const useGenerateContactDiscovery = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ slug }: { slug: string }) => {
      const res = await apiClient.post<ContactDiscoveryResponse>(
        `/businesses/${slug}/contact-discovery`,
      );
      return res.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["businesses", variables.slug, "contact-discovery"],
      });
    },
  });
};
