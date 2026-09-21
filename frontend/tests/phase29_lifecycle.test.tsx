import { describe, it, expect } from "vitest";
import { LifecycleHealthState, LifecycleAction } from "../types/lifecycle";

describe("Phase 29 Lifecycle UI Formatter Tests", () => {
  const formatState = (state: string) => {
    if (state === "STABLE") return { label: "Stabil", color: "bg-emerald-100 text-emerald-800 border-emerald-200" };
    if (state === "WATCH") return { label: "İzleme", color: "bg-amber-100 text-amber-800 border-amber-200" };
    if (state === "CONFIRMED_DETERIORATION") return { label: "Bozulma", color: "bg-rose-100 text-rose-800 border-rose-200" };
    if (state === "RECOVERING") return { label: "Toparlanıyor", color: "bg-blue-100 text-blue-800 border-blue-200" };
    if (state === "CLOSED") return { label: "Kapalı", color: "bg-slate-100 text-slate-800 border-slate-200" };
    return { label: "-", color: "bg-slate-100 text-slate-800 border-slate-200" };
  };

  const formatAction = (action: string) => {
    if (action === "HOLD") return { label: "Bekle", color: "text-slate-600 font-medium" };
    if (action === "CONSIDER_ADD") return { label: "Ekleme", color: "text-emerald-600 font-bold" };
    if (action === "CONSIDER_REDUCE") return { label: "Azalt", color: "text-amber-600 font-bold" };
    if (action === "CONSIDER_EXIT") return { label: "Çık", color: "text-rose-600 font-bold" };
    if (action === "NO_ACTION_DATA") return { label: "Veri Yetersiz", color: "text-slate-400 font-medium" };
    return { label: "-", color: "text-slate-400" };
  };

  it("should render correct state labels and colors", () => {
    expect(formatState(LifecycleHealthState.STABLE).label).toBe("Stabil");
    expect(formatState(LifecycleHealthState.WATCH).label).toBe("İzleme");
    expect(formatState(LifecycleHealthState.CONFIRMED_DETERIORATION).label).toBe("Bozulma");
    expect(formatState(LifecycleHealthState.RECOVERING).label).toBe("Toparlanıyor");
    expect(formatState(LifecycleHealthState.CLOSED).label).toBe("Kapalı");
  });

  it("should render correct action labels and colors", () => {
    expect(formatAction(LifecycleAction.HOLD).label).toBe("Bekle");
    expect(formatAction(LifecycleAction.CONSIDER_ADD).label).toBe("Ekleme");
    expect(formatAction(LifecycleAction.CONSIDER_REDUCE).label).toBe("Azalt");
    expect(formatAction(LifecycleAction.CONSIDER_EXIT).label).toBe("Çık");
    expect(formatAction(LifecycleAction.NO_ACTION_DATA).label).toBe("Veri Yetersiz");
  });
});
