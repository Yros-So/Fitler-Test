"use client";

import {
  BarChart3,
  Boxes,
  Download,
  Ruler,
  Search,
  Settings2
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const navigation = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/scrape", label: "Nouveau scraping", icon: Search },
  { href: "/products", label: "Produits", icon: Boxes },
  { href: "/size-guides", label: "Guides", icon: Ruler },
  { href: "/exports", label: "Exports", icon: Download }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r bg-card lg:block">
        <div className="flex h-16 items-center gap-3 border-b px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Settings2 className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold">Fitler Scraper</p>
            <p className="text-xs text-muted-foreground">Shopify catalog engine</p>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                className={cn(
                  "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                  active && "bg-muted font-medium text-foreground"
                )}
                href={item.href}
                key={item.href}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur">
          <div className="flex h-16 items-center justify-between gap-4 px-4 sm:px-6">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">Shopify Product & Size Guide Scraper</p>
              <p className="hidden text-xs text-muted-foreground sm:block">
                Scraping, contrôle qualité catalogue et exports
              </p>
            </div>
            <nav className="flex gap-1 lg:hidden">
              {navigation.map((item) => {
                const Icon = item.icon;
                const active =
                  item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
                return (
                  <Link
                    aria-label={item.label}
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground",
                      active && "bg-muted text-foreground"
                    )}
                    href={item.href}
                    key={item.href}
                  >
                    <Icon className="h-4 w-4" />
                  </Link>
                );
              })}
            </nav>
          </div>
        </header>
        <main className="px-4 py-6 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
