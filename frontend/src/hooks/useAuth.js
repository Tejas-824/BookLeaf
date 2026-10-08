"use client";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearAuth, getAuth, homeFor } from "@/lib/auth";

export default function useAuth(requiredRole) {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (!auth) {
      router.replace("/login");
      return;
    }
    if (requiredRole && auth.role !== requiredRole) {
      router.replace(homeFor(auth.role));
      return;
    }
    setUser(auth);
    setReady(true);
  }, [requiredRole, router]);

  const logout = useCallback(() => {
    clearAuth();
    router.replace("/login");
  }, [router]);

  return { user, ready, logout };
}