import { describe, expect, it } from "vitest";

import { exportUrl } from "@/services/api";

describe("exportUrl", () => {
  it("builds backend download endpoints", () => {
    expect(exportUrl("csv")).toBe("https://fitler-test.onrender.com/export/csv");
    expect(exportUrl("xlsx")).toBe("https://fitler-test.onrender.com/export/xlsx");
  });
});
