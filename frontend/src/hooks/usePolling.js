"use client";
import { useCallback, useEffect, useRef, useState } from "react";

export default function usePolling(fetcher, intervalMs = 8000, key = "") {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher; // always use the latest fetcher
  const seq = useRef(0); // id of the latest request
  const inflight = useRef(false);

  const refresh = useCallback(async () => {
    const mine = ++seq.current;
    inflight.current = true;
    try {
      const result = await fetcherRef.current();
      if (mine === seq.current) {
        setData(result);
        setError("");
      }
    } catch (e) {
      if (mine === seq.current) setError(e.message || "Something went wrong.");
    } finally {
      if (mine === seq.current) {
        inflight.current = false;
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    refresh(); // when key changes (new filters / new id) fetch right away
    const timer = setInterval(() => {
      if (!document.hidden && !inflight.current) refresh();
    }, intervalMs);
    const onVisible = () => {
      if (!document.hidden) refresh(); // catch up when user returns to the tab
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [refresh, intervalMs, key]);

  return { data, error, loading, refresh, setData };
}