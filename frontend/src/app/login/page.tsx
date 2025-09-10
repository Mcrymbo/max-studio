"use client";
import { gql } from "@apollo/client";
import { useMutation } from "@apollo/client/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

const LOGIN = gql`
  mutation Login($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;

type LoginResult = { tokenAuth: { token: string } };
type LoginVars = { username: string; password: string };

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [login, { loading, error }] = useMutation<LoginResult, LoginVars>(LOGIN);
  const router = useRouter();

  return (
    <div className="min-h-screen grid place-items-center bg-neutral-950 text-neutral-100 px-6">
      <div className="w-full max-w-sm rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
        <h1 className="text-xl font-semibold mb-4">Sign in</h1>
        <form
          className="flex flex-col gap-3"
          onSubmit={async (e) => {
            e.preventDefault();
            const res = await login({ variables: { username, password } });
            const token = res.data?.tokenAuth?.token;
            if (token) {
              localStorage.setItem("token", token);
              router.push("/");
            }
          }}
        >
          <input
            className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error ? <div className="text-red-400 text-sm">{error.message}</div> : null}
          <button
            disabled={loading}
            className="mt-2 rounded-md bg-fuchsia-600 hover:bg-fuchsia-500 transition px-3 py-2 font-medium disabled:opacity-60"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}


