"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Play, RotateCw } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { useJobPolling } from "@/hooks/use-job-polling";
import { scrapeWebsite } from "@/services/api";

// Schéma de validation du formulaire (zod) : URL obligatoire et valide.
const formSchema = z.object({
  url: z.string().url("Saisis une URL valide, par exemple https://www.andre.fr")
});

type FormValues = z.infer<typeof formSchema>;

// Progression affichée selon le statut du job (indicateur visuel).
const progressByStatus = {
  pending: 20,
  running: 70,
  completed: 100,
  failed: 100
};

export function ScrapeForm() {
  const [jobId, setJobId] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { url: "" }
  });
  // Polling du job en arrière-plan une fois le scraping lancé.
  const jobQuery = useJobPolling(jobId);
  const job = jobQuery.data;

  async function onSubmit(values: FormValues) {
    // Envoie l'URL au backend : réponse immédiate avec l'id du job.
    const created = await scrapeWebsite(values.url);
    setJobId(created.job_id);
    toast.success("Scraping lancé");
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Nouveau scraping</h1>
        <p className="text-sm text-muted-foreground">
          Lance une extraction depuis une boutique Shopify publique.
        </p>
      </div>

      <Card className="max-w-3xl">
        <CardHeader>
          <CardTitle>Source Shopify</CardTitle>
          <CardDescription>Le backend utilise plusieurs stratégies de récupération.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-[1fr_auto]" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <Input
                placeholder="https://www.andre.fr"
                type="url"
                {...register("url")}
              />
              {errors.url ? (
                <p className="mt-2 text-sm text-destructive">{errors.url.message}</p>
              ) : null}
            </div>
            <Button disabled={isSubmitting} type="submit">
              {isSubmitting ? <RotateCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Scraper
            </Button>
          </form>
        </CardContent>
      </Card>

      {jobId ? (
        <Card className="max-w-3xl">
          <CardHeader>
            <CardTitle>Job {jobId}</CardTitle>
            <CardDescription>Suivi automatique toutes les deux secondes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {job ? (
              <>
                <div className="flex items-center justify-between gap-3">
                  <Badge
                    variant={
                      job.status === "completed"
                        ? "success"
                        : job.status === "failed"
                          ? "destructive"
                          : "warning"
                    }
                  >
                    {job.status}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {job.finished_at ? new Date(job.finished_at).toLocaleString("fr-FR") : "Traitement en cours"}
                  </span>
                </div>
                <Progress value={progressByStatus[job.status]} />
                {job.status === "completed" ? (
                  // Récapitulatif du job terminé : volumes écrits en base.
                  <div className="grid gap-2 text-sm sm:grid-cols-3">
                    <Result label="Produits" value={job.stats.products ?? 0} />
                    <Result label="Variantes" value={job.stats.variants ?? 0} />
                    <Result label="Guides" value={job.stats.size_guides ?? 0} />
                  </div>
                ) : null}
                {job.status === "failed" ? (
                  // Message d'erreur remonté par le backend (diagnostic).
                  <Alert className="border-destructive/40">
                    <AlertTitle>Scraping en échec</AlertTitle>
                    <AlertDescription>{job.error}</AlertDescription>
                  </Alert>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Création du job...</p>
            )}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function Result({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}
