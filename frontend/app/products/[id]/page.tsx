import { ExternalLink } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { getProduct } from "@/services/api";

type ProductPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;

  try {
    const product = await getProduct(id);
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal">{product.name}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{product.vendor ?? product.handle}</p>
          </div>
          <Button asChild variant="outline">
            <a href={product.url} rel="noreferrer" target="_blank">
              <ExternalLink className="h-4 w-4" />
              Voir la fiche
            </a>
          </Button>
        </div>

        <section className="grid gap-4 lg:grid-cols-[360px_1fr]">
          <Card>
            <CardHeader>
              <CardTitle>Images</CardTitle>
              <CardDescription>{product.image_urls.length} image(s)</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              {product.image_urls.length ? (
                product.image_urls.slice(0, 4).map((image) => (
                  <img
                    alt=""
                    className="aspect-[4/3] w-full rounded-md border object-cover"
                    key={image}
                    src={image}
                  />
                ))
              ) : (
                <div className="flex aspect-[4/3] items-center justify-center rounded-md border bg-muted text-sm text-muted-foreground">
                  Aucune image
                </div>
              )}
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-6 text-muted-foreground">
                  {product.description ?? "Description absente."}
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Variantes</CardTitle>
                <CardDescription>{product.variants.length} variante(s)</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Titre</TableHead>
                      <TableHead>SKU</TableHead>
                      <TableHead>Prix</TableHead>
                      <TableHead>Disponibilité</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {product.variants.map((variant) => (
                      <TableRow key={variant.id}>
                        <TableCell>{variant.title}</TableCell>
                        <TableCell>{variant.sku ?? "-"}</TableCell>
                        <TableCell>{variant.price ?? "-"}</TableCell>
                        <TableCell>
                          <Badge variant={variant.available ? "success" : "secondary"}>
                            {variant.available ? "Disponible" : "Indisponible"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    );
  } catch (error) {
    return (
      <Alert className="border-destructive/40">
        <AlertTitle>Produit introuvable</AlertTitle>
        <AlertDescription>
          {error instanceof Error ? error.message : "Impossible de charger le produit."}
        </AlertDescription>
      </Alert>
    );
  }
}
