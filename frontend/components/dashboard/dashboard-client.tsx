"use client";

import { Activity, Boxes, Clock, Ruler } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getLatestJob, getProducts, getSizeGuides } from "@/services/api";
import type { ScrapeStatus } from "@/types";

const statusLabels: Record<ScrapeStatus, string> = {
  pending: "En attente",
  running: "En cours",
  completed: "Terminé",
  failed: "Échec"
};

const statusVariants: Record<ScrapeStatus, "secondary" | "warning" | "success" | "destructive"> = {
  pending: "secondary",
  running: "warning",
  completed: "success",
  failed: "destructive"
};

export function DashboardClient() {
  // Trois requêtes parallèles : total produits, total guides, dernier job.
  const productsQuery = useQuery({
    queryKey: ["dashboard-products"],
    queryFn: () => getProducts({ page_size: 1 })
  });
  const guidesQuery = useQuery({
    queryKey: ["dashboard-guides"],
    queryFn: () => getSizeGuides({ page_size: 1 })
  });
  const latestJobQuery = useQuery({
    queryKey: ["latest-job"],
    queryFn: getLatestJob
  });

  const latestJob = latestJobQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Vue opérationnelle du catalogue extrait et du dernier scraping.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          icon={<Boxes className="h-4 w-4" />}
          label="Produits"
          loading={productsQuery.isLoading}
          value={productsQuery.data?.total ?? 0}
        />
        <MetricCard
          icon={<Ruler className="h-4 w-4" />}
          label="Guides de taille"
          loading={guidesQuery.isLoading}
          value={guidesQuery.data?.total ?? 0}
        />
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4" />
              Dernier scraping
            </CardTitle>
            <CardDescription>Statut et volume écrit en base</CardDescription>
          </CardHeader>
          <CardContent>
            {latestJobQuery.isLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : latestJob ? (
              <div className="space-y-3">
                <Badge variant={statusVariants[latestJob.status]}>
                  {statusLabels[latestJob.status]}
                </Badge>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <Stat label="Produits" value={latestJob.stats.products ?? 0} />
                  <Stat label="Variantes" value={latestJob.stats.variants ?? 0} />
                  <Stat label="Guides" value={latestJob.stats.size_guides ?? 0} />
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucun scraping lancé.</p>
            )}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Qualité catalogue
            </CardTitle>
            <CardDescription>Indicateurs rapides pour orienter le contrôle.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-3">
            <Stat label="Pages produit détectées" value={productsQuery.data?.total ?? 0} />
            <Stat label="Guides normalisés" value={guidesQuery.data?.total ?? 0} />
            <Stat
              // Couverture guide : % de guides rapportés au catalogue (proxy).
              label="Couverture guide"
              value={
                productsQuery.data?.total
                  ? `${Math.round(((guidesQuery.data?.total ?? 0) / productsQuery.data.total) * 100)}%`
                  : "0%"
              }
            />
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  loading,
  value
}: {
  icon: React.ReactNode;
  label: string;
  loading: boolean;
  value: number;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          {icon}
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? <Skeleton className="h-8 w-24" /> : <p className="text-3xl font-semibold">{value}</p>}
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}
