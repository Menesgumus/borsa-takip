content = '''"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { fetchApi } from "@/lib/api";

export default function RiskRedirectPage() {
  const router = useRouter();
  const { data: portfolios, isLoading } = useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios/"),
  });

  useEffect(() => {
    if (!isLoading && portfolios) {
      if ((portfolios as any).length > 0) {
        router.replace(/portfolios/ + (portfolios as any)[0].id + /risk);
      } else {
        router.replace("/portfolios");
      }
    }
  }, [isLoading, portfolios, router]);

  return (
    <div className="flex items-center justify-center h-[50vh] text-slate-500">
      Risk yönetimi sayfasýna yönlendiriliyorsunuz...
    </div>
  );
}
'''
with open('frontend/app/(protected)/risk/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
