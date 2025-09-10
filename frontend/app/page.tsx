"use client";
import { gql } from "@apollo/client";
import { useQuery } from "@apollo/client/react";
import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";

const VIDEOS = gql`
  query Videos($genre: String) {
    videos(genre: $genre) {
      id
      title
      description
      duration_seconds
      thumbnail_url
      genre
    }
  }
`;

type VideoItem = {
  id: string;
  title: string;
  description?: string | null;
  duration_seconds: number;
  thumbnail_url?: string | null;
  genre?: string | null;
};

type VideosData = { videos: VideoItem[] };
type VideosVars = { genre?: string };

export default function Home() {
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState<string | undefined>(undefined);
  const { data, loading } = useQuery<VideosData, VideosVars>(VIDEOS, { variables: { genre } });

  const items = useMemo(() => {
    const list: VideoItem[] = data?.videos ?? [];
    if (!query) return list;
    const q = query.toLowerCase();
    return list.filter((v) =>
      (v.title || "").toLowerCase().includes(q) || (v.description || "").toLowerCase().includes(q)
    );
  }, [data, query]);

  const genres: string[] = useMemo(() => {
    const list: VideoItem[] = data?.videos ?? [];
    const s = new Set<string>();
    for (const v of list) {
      if (v.genre) s.add(v.genre);
    }
    return Array.from(s);
  }, [data]);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <section className="relative isolate overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-fuchsia-700/20 via-purple-700/10 to-neutral-950" />
        <div className="relative z-10 mx-auto max-w-7xl px-6 py-16">
          <div className="flex flex-col gap-6">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Explore Movies
            </h1>
            <p className="max-w-2xl text-neutral-300">
              Beautiful, professional, and elegant streaming experience powered by Jellyfin.
            </p>
            <div className="flex flex-col md:flex-row gap-3">
              <input
                className="w-full md:w-96 rounded-md bg-neutral-900/80 border border-neutral-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
                placeholder="Search by title or description"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <select
                className="w-full md:w-56 rounded-md bg-neutral-900/80 border border-neutral-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
                value={genre || ""}
                onChange={(e) => setGenre(e.target.value || undefined)}
              >
                <option value="">All genres</option>
                {genres.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-16">
        {loading ? (
          <div className="py-24 text-center text-neutral-400">Loading…</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {items.map((v) => (
              <Link
                key={v.id}
                href={`/video/${encodeURIComponent(v.id)}`}
                className="group rounded-lg overflow-hidden bg-neutral-900 border border-neutral-800 hover:border-fuchsia-600/50 transition"
              >
                <div className="aspect-[2/3] relative">
                  {v.thumbnail_url ? (
                    <Image src={v.thumbnail_url} alt={v.title} fill className="object-cover" />
                  ) : (
                    <div className="absolute inset-0 grid place-items-center text-neutral-500">No image</div>
                  )}
                </div>
                <div className="p-3">
                  <div className="line-clamp-1 font-medium group-hover:text-fuchsia-400">{v.title}</div>
                  <div className="mt-1 text-xs text-neutral-400 line-clamp-2">{v.description}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
