"use client";

import { ExternalLink, Ruler } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { getSizeGuides } from "@/services/api";

export function SizeGuideList() {
  // Charge les guides par pages de 50 (volume faible en pratique).
  const guidesQuery = useQuery({
    queryKey: ["size-guides"],
    queryFn: () => getSizeGuides({ page_size: 50 })
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Guides de taille</h1>
        <p className="text-sm text-muted-foreground">
          Tables HTML, pages guide et blocs de mesure normalisés.
        </p>
      </div>

      {guidesQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton className="h-28 w-full" key={index} />
          ))}
        </div>
      ) : guidesQuery.data?.items.length ? (
        <div className="grid gap-4">
          {guidesQuery.data.items.map((guide) => (
            <Card key={guide.id}>
              <CardHeader className="gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Ruler className="h-4 w-4" />
                    {guide.title}
                  </CardTitle>
                  <CardDescription>{guide.source_url}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    {Number(guide.content.metadata?.table_count ?? guide.content.tables?.length ?? 0)} table(s)
                  </Badge>
                  <Button asChild size="icon" variant="ghost">
                    <a aria-label="Ouvrir la source" href={guide.source_url} rel="noreferrer" target="_blank">
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {guide.content.tables?.length ? (
                  // Affiche les premières tables extraites (2 max) et les
                  // 8 premières lignes de chaque table.
                  guide.content.tables.slice(0, 2).map((table, index) => (
                    <Table key={`${guide.id}-${index}`}>
                      <TableHeader>
                        <TableRow>
                          {(table[0] ?? []).map((cell) => (
                            <TableHead key={cell}>{cell}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {table.slice(1, 8).map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <TableCell key={`${rowIndex}-${cellIndex}`}>{cell}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ))
                ) : (
                  <p className="text-sm leading-6 text-muted-foreground">
                    {guide.raw_text ?? "Guide détecté sans tableau structuré."}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="rounded-md border border-dashed p-8 text-center">
          <p className="font-medium">Aucun guide détecté</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Les prochains scrapings enrichiront cette vue automatiquement.
          </p>
        </div>
      )}
    </div>
  );
}
