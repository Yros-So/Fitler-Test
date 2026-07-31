"use client";

import { ArrowDownUp, ChevronLeft, ChevronRight, ExternalLink, Search } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { useDebounce } from "@/hooks/use-debounce";
import { getProducts } from "@/services/api";
import type { Product } from "@/types";

const PAGE_SIZE = 20;

export function ProductsTable() {
  // État local : recherche, page, tri. La recherche est "debouncée" pour
  // ne pas marteler l'API à chaque frappe.
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState("name");
  const debouncedSearch = useDebounce(search);
  // React Query refait la requête dès que la clé change (recherche/page/tri).
  const productsQuery = useQuery({
    queryKey: ["products", debouncedSearch, page, sort],
    queryFn: () =>
      getProducts({
        search: debouncedSearch,
        page,
        page_size: PAGE_SIZE,
        sort
      })
  });

  const total = productsQuery.data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Produits</h1>
        <p className="text-sm text-muted-foreground">
          Catalogue normalisé avec recherche, tri et pagination.
        </p>
      </div>

      <Card>
        <CardHeader className="gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <CardTitle>Catalogue</CardTitle>
            <CardDescription>{total} produit(s) indexé(s)</CardDescription>
          </div>
          <div className="grid gap-2 sm:grid-cols-[minmax(220px,320px)_150px]">
            <label className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                className="pl-9"
                onChange={(event) => {
                  setSearch(event.target.value);
                  setPage(1);
                }}
                placeholder="Rechercher"
                value={search}
              />
            </label>
            <label className="relative">
              <ArrowDownUp className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <select
                className="focus-ring h-10 w-full rounded-md border bg-card pl-9 pr-3 text-sm"
                onChange={(event) => {
                  setSort(event.target.value);
                  setPage(1);
                }}
                value={sort}
              >
                <option value="name">Nom</option>
                <option value="price">Prix</option>
                <option value="created_at">Ajout</option>
              </select>
            </label>
          </div>
        </CardHeader>
        <CardContent>
          {productsQuery.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 7 }).map((_, index) => (
                <Skeleton className="h-14 w-full" key={index} />
              ))}
            </div>
          ) : productsQuery.data?.items.length ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[44%]">Nom</TableHead>
                    <TableHead>Prix</TableHead>
                    <TableHead>Variantes</TableHead>
                    <TableHead>Disponible</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {productsQuery.data.items.map((product) => (
                    <ProductRow key={product.id} product={product} />
                  ))}
                </TableBody>
              </Table>
              <div className="mt-4 flex items-center justify-between gap-3">
                <p className="text-sm text-muted-foreground">
                  Page {page} sur {totalPages}
                </p>
                <div className="flex gap-2">
                  <Button
                    disabled={page <= 1}
                    onClick={() => setPage((value) => Math.max(1, value - 1))}
                    size="icon"
                    variant="outline"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    disabled={page >= totalPages}
                    onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
                    size="icon"
                    variant="outline"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="rounded-md border border-dashed p-8 text-center">
              <p className="font-medium">Aucun produit</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Lance un scraping pour alimenter le catalogue.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function ProductRow({ product }: { product: Product }) {
  // Nombre de variantes réellement disponibles (badge d'état stock).
  const availableCount = product.variants.filter((variant) => variant.available).length;
  return (
    <TableRow>
      <TableCell>
        <div className="flex min-w-[260px] items-center gap-3">
          <div className="h-12 w-12 overflow-hidden rounded-md border bg-muted">
            {product.image_urls[0] ? (
              <img
                alt=""
                className="h-full w-full object-cover"
                loading="lazy"
                src={product.image_urls[0]}
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xs text-muted-foreground">
                IMG
              </div>
            )}
          </div>
          <div className="min-w-0">
            <Link className="truncate font-medium hover:underline" href={`/products/${product.id}`}>
              {product.name}
            </Link>
            <p className="truncate text-xs text-muted-foreground">{product.vendor ?? product.handle}</p>
          </div>
        </div>
      </TableCell>
      <TableCell>{product.price ? `${product.price} EUR` : "-"}</TableCell>
      <TableCell>{product.variants.length}</TableCell>
      <TableCell>
        <Badge variant={availableCount > 0 ? "success" : "secondary"}>
          {availableCount > 0 ? `${availableCount} disponible(s)` : "Indisponible"}
        </Badge>
      </TableCell>
      <TableCell className="text-right">
        <div className="flex justify-end gap-2">
          <Drawer>
            <DrawerTrigger asChild>
              <Button size="sm" variant="outline">
                Détails
              </Button>
            </DrawerTrigger>
            <DrawerContent>
              <DrawerHeader>
                <DrawerTitle>{product.name}</DrawerTitle>
              </DrawerHeader>
              <div className="space-y-4 text-sm">
                <p className="text-muted-foreground">{product.description ?? "Description absente."}</p>
                <div>
                  <p className="mb-2 font-medium">Variantes</p>
                  <div className="space-y-2">
                    {product.variants.map((variant) => (
                      <div className="rounded-md border p-3" key={variant.id}>
                        <div className="flex items-center justify-between gap-3">
                          <span>{variant.title}</span>
                          <Badge variant={variant.available ? "success" : "secondary"}>
                            {variant.available ? "Disponible" : "Non disponible"}
                          </Badge>
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">{variant.sku ?? "Sans SKU"}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </DrawerContent>
          </Drawer>
          <Button asChild size="icon" variant="ghost">
            <a aria-label="Ouvrir la fiche originale" href={product.url} rel="noreferrer" target="_blank">
              <ExternalLink className="h-4 w-4" />
            </a>
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}
