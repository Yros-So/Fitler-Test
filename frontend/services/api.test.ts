import { describe, expect, it } from "vitest";

import { exportUrl } from "@/services/api";

describe("exportUrl", () => {
  it("builds backend download endpoints", () => {
    expect(exportUrl("csv")).toBe(process.env.NEXT_PUBLIC_API_BASE_URL+"/export/csv");
    expect(exportUrl("xlsx")).toBe(process.env.NEXT_PUBLIC_API_BASE_URL+"/export/xlsx");
  });
});
