import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api";
import type { PictureItem } from "../types/picture";

interface PicturesResponse {
  unverified: PictureItem[];
  verified: PictureItem[];
}

export function usePictureScreening(role: string, processId?: string) {
  const { get, post } = useApi();
  const [unverifiedPictures, setUnverifiedPictures] = useState<PictureItem[]>([]);
  const [verifiedPictures, setVerifiedPictures] = useState<PictureItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPictures = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (processId) {
        const res = await get<PicturesResponse>(`/pictures/process/${processId}`);
        setUnverifiedPictures(res.data.unverified);
        setVerifiedPictures(res.data.verified);
      } else {
        const res = await get<PictureItem[]>(`/pictures/${role}`);
        setUnverifiedPictures(res.data);
        setVerifiedPictures([]);
      }
      setCurrentIndex(0);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load pictures");
    } finally {
      setIsLoading(false);
    }
  }, [get, role, processId]);

  useEffect(() => {
    fetchPictures();
  }, [fetchPictures]);

  const currentPicture = unverifiedPictures[currentIndex] ?? null;

  const verifyAndNext = useCallback(
    async (updatedData: Record<string, string>) => {
      if (!currentPicture) return;

      const knownKeys = new Set(["id", "advertisement_id", "verified", "created_at"]);
      const extra: Record<string, string> = {};
      for (const [k, v] of Object.entries(updatedData)) {
        if (!knownKeys.has(k)) {
          extra[k] = v;
        }
      }

      if (processId) {
        await post(`/pictures/process/verify`, {
          id: currentPicture.id,
          url: updatedData.advertisement_id ?? currentPicture.advertisement_id,
          process_id: processId,
          extra,
        });
      } else {
        await post(`/pictures/verify`, {
          id: currentPicture.id,
          url: updatedData.advertisement_id ?? currentPicture.advertisement_id,
          process_id: "",
          extra,
        });
      }

      // Move verified picture from unverified to verified
      const verifiedPicture: PictureItem = { ...currentPicture, ...updatedData, verified: true } as PictureItem;
      setVerifiedPictures((prev) => [...prev, verifiedPicture]);
      setUnverifiedPictures((prev) => prev.filter((_, i) => i !== currentIndex));
      // currentIndex stays the same; after removal the next item is now at currentIndex
    },
    [currentPicture, post, processId, currentIndex]
  );

  const updateVerified = useCallback(
    async (pictureId: string, updatedData: Record<string, string>) => {
      const knownKeys = new Set(["id", "advertisement_id", "verified", "created_at"]);
      const extra: Record<string, string> = {};
      for (const [k, v] of Object.entries(updatedData)) {
        if (!knownKeys.has(k)) extra[k] = v;
      }

      if (processId) {
        await post(`/pictures/process/verify`, {
          id: pictureId,
          url: updatedData.advertisement_id,
          process_id: processId,
          extra,
        });
      } else {
        await post(`/pictures/verify`, {
          id: pictureId,
          url: updatedData.advertisement_id,
          process_id: "",
          extra,
        });
      }

      setVerifiedPictures((prev) =>
        prev.map((p) => (p.id === pictureId ? { ...p, ...updatedData } : p))
      );
    },
    [post, processId]
  );

  return {
    unverifiedPictures,
    verifiedPictures,
    currentPicture,
    currentIndex,
    total: unverifiedPictures.length + verifiedPictures.length,
    isLoading,
    error,
    verifyAndNext,
    updateVerified,
    refetch: fetchPictures,
  };
}
