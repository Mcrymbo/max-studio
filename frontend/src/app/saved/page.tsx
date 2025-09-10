"use client";
import { gql } from "@apollo/client";
import { useQuery } from "@apollo/client/react";
import Link from "next/link";

// Assuming the backend exposes saved videos via VideosQuery or AccountsQuery (adjust when available)
const SAVED = gql`
  query Videos {
    videos {
      id
      title
      description
      thumbnail_url
    }
  }
`;

type VideosData = {
  videos: Array<{
    id: string;
    title: string;
    description?: string | null;
    thumbnail_url?: string | null;
  }>;
};

export default function SavedPage() {
  const { data, loading } = useQuery<VideosData>(SAVED);
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="text-2xl font-semibold">Saved</h1>
        {loading ? (
          <div className="py-24 text-center text-neutral-400">Loading…</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-6">
            {(data?.videos ?? []).map((v) => (
              <Link key={v.id} href={`/video/${v.id}`} className="group rounded-lg overflow-hidden bg-neutral-900 border border-neutral-800">
                <div className="aspect-[2/3] bg-neutral-800" />
                <div className="p-3">
                  <div className="line-clamp-1 font-medium group-hover:text-fuchsia-400">{v.title}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


