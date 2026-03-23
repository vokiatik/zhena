import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api";
import type { PictureItem } from "../types/picture";

export function usePictureScreening(role: string) {
  const { get, post } = useApi();
  const [pictures, setPictures] = useState<PictureItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [canCancelVerification, setCanCancelVerification] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPictures = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await get<PictureItem[]>(`/pictures/${role}`);
      setPictures(res.data);
      setCurrentIndex(0);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load pictures");
    } finally {
      setIsLoading(false);
    }
  }, [get, role]);

  useEffect(() => {
    fetchPictures();
  }, [fetchPictures]);

  const currentPicture = pictures[currentIndex] ?? null;
  const previousPicture = currentIndex > 0 ? pictures[currentIndex - 1] : null;

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

      await post(`/pictures/verify`, {
        id: currentPicture.id,
        url: updatedData.advertisement_id ?? currentPicture.advertisement_id,
        extra,
      });

      // Move to next picture
      setCurrentIndex((i) => i + 1);
      setCanCancelVerification(false);
    },
    [currentPicture, post, role]
  );

  const unverify = useCallback(
    async (updatedData: Record<string, string>) => {
      if (!currentPicture) return;

      const knownKeys = new Set(["id", "advertisement_id", "verified", "created_at"]);
      const extra: Record<string, string> = {};
      for (const [k, v] of Object.entries(updatedData)) {
        if (!knownKeys.has(k)) {
          extra[k] = v;
        }
      }

      await post(`/pictures/unverify`, {
        id: currentPicture.id,
        url: updatedData.advertisement_id ?? currentPicture.advertisement_id,
        extra,
      });
      setCanCancelVerification(false);
    },
    [currentPicture, post, role]
  );

  const goBack = useCallback(() => {
    setCurrentIndex((i) => Math.max(0, i - 1));
    setCanCancelVerification(true);
  }, []);

  return {
    pictures,
    currentPicture,
    previousPicture,
    canCancelVerification,
    currentIndex,
    total: pictures.length,
    isLoading,
    error,
    verifyAndNext,
    goBack,
    refetch: fetchPictures,
    unverify,
  };
}
