import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api";
import type {
  AdvertisementItem,
  AdvertisementScreeningResponse,
  AdvertisementVerifyPayload,
  ScreeningOptions,
} from "../types/advertisement";

export function useAdvertisementScreening(processId: string) {
  const { get, post } = useApi();

  const [unverified, setUnverified] = useState<AdvertisementItem[]>([]);
  const [verified, setVerified] = useState<AdvertisementItem[]>([]);
  const [declined, setDeclined] = useState<AdvertisementItem[]>([]);
  const [options, setOptions] = useState<ScreeningOptions>({
    brand: [],
    product_category: [],
    brand_category: [],
    add_category: [],
  });
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await get<AdvertisementScreeningResponse>(
        `/pictures/process/${processId}`
      );
      setUnverified(res.data.unverified);
      setVerified(res.data.verified);
      setDeclined(res.data.declined ?? []);
      setOptions(res.data.options ?? { brand: [], product_category: [], brand_category: [], add_category: [] });
      setCurrentIndex(0);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load advertisements");
    } finally {
      setIsLoading(false);
    }
  }, [get, processId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const currentAdvertisement = unverified[currentIndex] ?? null;

  const verifyAndNext = useCallback(
    async (payload: Omit<AdvertisementVerifyPayload, "id" | "process_id">) => {
      if (!currentAdvertisement) return;
      await post("/pictures/process/advertisement/verify", {
        id: currentAdvertisement.id,
        process_id: processId,
        ...payload,
      });
      const updated: AdvertisementItem = { ...currentAdvertisement, ...payload, verified: true };
      setVerified((prev) => [...prev, updated]);
      setUnverified((prev) => prev.filter((_, i) => i !== currentIndex));
    },
    [currentAdvertisement, post, processId, currentIndex]
  );

  const declineAndNext = useCallback(async () => {
    if (!currentAdvertisement) return;
    await post("/pictures/process/advertisement/decline", {
      id: currentAdvertisement.id,
      process_id: processId,
    });
    const dec: AdvertisementItem = { ...currentAdvertisement, verified: false, declined: true };
    setDeclined((prev) => [...prev, dec]);
    setUnverified((prev) => prev.filter((_, i) => i !== currentIndex));
  }, [currentAdvertisement, post, processId, currentIndex]);

  const updateVerified = useCallback(
    async (adId: string, payload: Omit<AdvertisementVerifyPayload, "id" | "process_id">) => {
      await post("/pictures/process/advertisement/verify", {
        id: adId,
        process_id: processId,
        ...payload,
      });
      setVerified((prev) =>
        prev.map((a) => (a.id === adId ? { ...a, ...payload } : a))
      );
    },
    [post, processId]
  );

  const updateDeclined = useCallback(
    async (
      adId: string,
      payload: Omit<AdvertisementVerifyPayload, "id" | "process_id">,
      newDeclined: boolean
    ) => {
      if (newDeclined) {
        setDeclined((prev) => prev.map((a) => (a.id === adId ? { ...a, ...payload, declined: true } : a)));
        return;
      }
      // Un-decline = verify
      await post("/pictures/process/advertisement/verify", {
        id: adId,
        process_id: processId,
        ...payload,
      });
      setDeclined((prev) => prev.filter((a) => a.id !== adId));
      setVerified((prev) => [...prev, { ...prev.find((a) => a.id === adId)!, ...payload, verified: true, declined: false }]);
    },
    [post, processId]
  );

  return {
    currentAdvertisement,
    unverified,
    verified,
    declined,
    options,
    total: unverified.length + verified.length + declined.length,
    isLoading,
    error,
    verifyAndNext,
    declineAndNext,
    updateVerified,
    updateDeclined,
    refetch: fetchData,
  };
}
