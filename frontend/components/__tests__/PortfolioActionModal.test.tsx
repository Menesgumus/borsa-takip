import { vi } from 'vitest';
vi.mock('next/navigation', () => ({ useRouter: () => ({ push: vi.fn(), replace: vi.fn() }) }));
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PortfolioActionModal } from "../PortfolioActionModal";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe("PortfolioActionModal Reset Behavior", () => {
    it("should reset state entirely when unmounted and remounted", async () => {
        const { rerender } = render(
            <PortfolioActionModal
                portfolioId="123"
                isOpen={true}
                onClose={() => {}}
                initialAction="BUY"
            />,
            { wrapper }
        );

        const searchInput = screen.getByLabelText("Hisse Arama") as HTMLInputElement;
        fireEvent.change(searchInput, { target: { value: "DIRTY_STATE_TEST" } });
        expect(searchInput.value).toBe("DIRTY_STATE_TEST");
        
        rerender(<></>);

        rerender(
            <PortfolioActionModal
                portfolioId="123"
                isOpen={true}
                onClose={() => {}}
                initialAction="BUY"
            />
        );

        const newSearchInput = screen.getByLabelText("Hisse Arama") as HTMLInputElement;
        expect(newSearchInput.value).toBe("");
    });
});
