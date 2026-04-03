import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api";
import type { PictureAttribute } from "../types/picture_attributes";

export function usePictureScreeningSettings(processId?: string) {
  const { get } = useApi();
  const [settings, setSettings] = useState<PictureAttribute[]>([]);
  const [isLoading, setIsLoading] = useState(!!processId);

  const fetchSettings = useCallback(async () => {
    if (!processId) return;
    setIsLoading(true);
    try {
      const res = await get<PictureAttribute[]>(
        `/pictures/process/${processId}/settings`
      );
      setSettings(res.data);
    } catch {
      setSettings([]);
    } finally {
      setIsLoading(false);
    }
  }, [get, processId]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return { settings, isLoading };
}
