"use client";
import { gql } from "@apollo/client";
import { useMutation } from "@apollo/client/react";
import { useState } from "react";

const UPLOAD = gql`
  mutation UploadVideo($title: String!, $file: String!, $description: String, $genreName: String) {
    uploadVideo(title: $title, file: $file, description: $description, genreName: $genreName) {
      ok
    }
  }
`;

export default function AdminUploadPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [genreName, setGenreName] = useState("");
  const [serverPath, setServerPath] = useState("");
  type UploadResult = { uploadVideo: { ok: boolean } };
  type UploadVars = { title: string; file: string; description?: string; genreName?: string | null };
  const [upload, { loading, error, data }] = useMutation<UploadResult, UploadVars>(UPLOAD);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="text-2xl font-semibold">Admin: Upload Video</h1>
        <p className="mt-2 text-sm text-neutral-400">
          This backend expects a server file path. First copy your file into the backend container (e.g. /tmp/movie.mp4),
          then submit that path here to ingest and process via Jellyfin.
        </p>

        <form
          className="mt-6 grid gap-4"
          onSubmit={async (e) => {
            e.preventDefault();
            await upload({ variables: { title, file: serverPath, description, genreName: genreName || null } });
          }}
        >
          <div className="grid gap-2">
            <label className="text-sm text-neutral-300">Title</label>
            <input
              className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm text-neutral-300">Description</label>
            <textarea
              className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500 min-h-24"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm text-neutral-300">Genre</label>
            <input
              className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
              value={genreName}
              onChange={(e) => setGenreName(e.target.value)}
              placeholder="e.g. Action"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm text-neutral-300">Server file path (inside backend container)</label>
            <input
              className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
              value={serverPath}
              onChange={(e) => setServerPath(e.target.value)}
              placeholder="/tmp/movie.mp4 or /app/media/jellyfin_library/movie.mp4"
              required
            />
          </div>
          {error ? <div className="text-red-400 text-sm">{error.message}</div> : null}
          {data?.uploadVideo?.ok ? (
            <div className="text-green-400 text-sm">Upload requested. Library refresh may take a moment.</div>
          ) : null}
          <div>
            <button
              disabled={loading}
              className="rounded-md bg-fuchsia-600 hover:bg-fuchsia-500 transition px-4 py-2 font-medium disabled:opacity-60"
            >
              {loading ? "Submitting…" : "Submit"}
            </button>
          </div>
        </form>

        <div className="mt-8 border-t border-neutral-800 pt-6 text-sm text-neutral-400">
          <div className="font-medium text-neutral-300 mb-2">How to copy your file into the backend container</div>
          <code className="block bg-neutral-900 border border-neutral-800 rounded p-3 overflow-x-auto">
            docker cp /path/to/movie.mp4 maxstudio_backend:/tmp/movie.mp4
          </code>
        </div>
      </div>
    </div>
  );
}


