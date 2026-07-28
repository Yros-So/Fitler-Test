import { describe, expect, it } from "vitest";

import { exportUrl } from "@/services/api";

describe("exportUrl", () => {
  it("builds backend download endpoints", () => {
    expect(exportUrl("csv")).toBe("http://localhost:8000/export/csv");
    expect(exportUrl("xlsx")).toBe("http://localhost:8000/export/xlsx");
  });
});
