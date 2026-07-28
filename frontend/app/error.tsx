"use client";

import { RotateCcw } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export default function ErrorBoundary({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <Alert className="border-destructive/40">
      <AlertTitle>Erreur applicative</AlertTitle>
      <AlertDescription>{error.message}</AlertDescription>
      <Button className="mt-4" onClick={reset} variant="outline">
        <RotateCcw className="h-4 w-4" />
        Réessayer
      </Button>
    </Alert>
  );
}
