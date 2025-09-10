"use client";
import { gql } from "@apollo/client";
import { useQuery } from "@apollo/client/react";
import Hls from "hls.js";
import { useEffect, useRef } from "react";
import { useParams } from "next/navigation";

const VIDEO = gql`
  query Video($id: ID!) {
    video(id: $id) {
      id
      title
      description
      duration_seconds
      thumbnail_url
      playback_url
      genre
    }
  }
`;

type VideoData = {
  video: {
    id: string;
    title: string;
    description?: string | null;
    duration_seconds: number;
    thumbnail_url?: string | null;
    playback_url?: string | null;
    genre?: string | null;
  };
};

type VideoVars = { id: string };

export default function VideoPage() {
  const params = useParams<{ id: string }>();
  const { data, loading } = useQuery<VideoData, VideoVars>(VIDEO, { variables: { id: params.id } });
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const src = data?.video?.playback_url;
    const video = videoRef.current;
    if (!video || !src) return;

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(src);
      hls.attachMedia(video);
      return () => hls.destroy();
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src;
    }
  }, [data]);

  if (loading) {
    return <div className="min-h-screen grid place-items-center text-neutral-400">Loading…</div>;
  }

  const v = data?.video;
  if (!v) {
    return <div className="min-h-screen grid place-items-center">Not found</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="text-3xl md:text-4xl font-semibold">{v.title}</h1>
        <div className="mt-6 rounded-lg overflow-hidden bg-black border border-neutral-800">
          <video ref={videoRef} controls className="w-full h-auto" poster={v.thumbnail_url ?? undefined} />
        </div>
        <p className="mt-6 text-neutral-300 leading-relaxed">{v.description}</p>
      </div>
    </div>
  );
}


