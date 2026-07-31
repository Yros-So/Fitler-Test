"use client";

import { Download, FileJson, FileSpreadsheet, TableProperties } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { exportUrl } from "@/services/api";

// Les trois formats d'export proposés par la plateforme.
const formats = [
  {
    format: "json" as const,
    label: "JSON",
    description: "Structure complète avec variantes et images.",
    icon: FileJson
  },
  {
    format: "csv" as const,
    label: "CSV",
    description: "Format tabulaire compatible import métier.",
    icon: TableProperties
  },
  {
    format: "xlsx" as const,
    label: "XLSX",
    description: "Classeur Excel prêt pour contrôle catalogue.",
    icon: FileSpreadsheet
  }
];

export function ExportActions() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Exports</h1>
        <p className="text-sm text-muted-foreground">
          Télécharge les données extraites dans les formats attendus.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        {formats.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.format}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {item.label}
                </CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <a href={exportUrl(item.format)}>
                    <Download className="h-4 w-4" />
                    Télécharger
                  </a>
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </section>
    </div>
  );
}
