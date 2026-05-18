"use client";

import { useEffect, useState } from "react";

type RouteParams = { id: string };

export type AsyncRouteParams = Promise<RouteParams>;

export function useRouteId(params: AsyncRouteParams): string {
  const syncId = (params as unknown as Partial<RouteParams>).id;
  const [id, setId] = useState(typeof syncId === "string" ? syncId : "");

  useEffect(() => {
    if (typeof syncId === "string") {
      return;
    }

    let isActive = true;
    void params.then((resolvedParams) => {
      if (isActive) {
        setId(resolvedParams.id);
      }
    });

    return () => {
      isActive = false;
    };
  }, [params, syncId]);

  return id;
}
