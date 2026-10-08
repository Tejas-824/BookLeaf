"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuth, homeFor } from "@/lib/auth";
import { Loading } from "@/components/ui";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const auth = getAuth();
    router.replace(auth ? homeFor(auth.role) : "/login");
  }, [router]);
  return <Loading />;
}