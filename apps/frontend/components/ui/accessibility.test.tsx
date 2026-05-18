import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActionBar } from "@/components/ui/ActionBar";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { WarningPanel } from "@/components/ui/WarningPanel";

describe("shared UI accessibility", () => {
  it("announces loading states as busy status regions", () => {
    render(<LoadingState label="Loading records..." />);

    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-busy", "true");
    expect(status).toHaveTextContent("Loading records...");
  });

  it("announces error states as alerts", () => {
    render(<ErrorState message="Unable to load records." title="Load failed" />);

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Load failed");
    expect(alert).toHaveTextContent("Unable to load records.");
  });

  it("uses live region semantics for warning panels that communicate state", () => {
    render(<WarningPanel tone="success">Saved successfully.</WarningPanel>);

    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-live", "polite");
    expect(status).toHaveTextContent("Saved successfully.");
  });

  it("keeps action bars responsive", () => {
    render(
      <ActionBar>
        <button type="button">Primary action</button>
      </ActionBar>,
    );

    expect(screen.getByText("Primary action").parentElement).toHaveClass("flex-col-reverse", "sm:flex-row");
  });
});
