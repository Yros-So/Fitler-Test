"use client";

import { useQuery } from "@tanstack/react-query";

import { getJob } from "@/services/api";

export function useJobPolling(jobId: string | null) {
  // Interroge le statut du job tant qu'il est en cours (pending/running),
  // toutes les 2 secondes, via React Query (refetchInterval).
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId as string),
    enabled: Boolean(jobId), // désactivé tant qu'aucun job n'est lancé
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Plus de polling une fois le job terminé (completed/failed).
      return status === "pending" || status === "running" ? 2000 : false;
    }
  });
}
