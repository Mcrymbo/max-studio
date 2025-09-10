"use client";
import { ApolloClient, InMemoryCache,  createHttpLink } from "@apollo/client";
import { ApolloProvider } from "@apollo/client/react";
import { setContext } from "@apollo/client/link/context";
import React from "react";

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000/graphql/",
  fetchOptions: { mode: "cors" },
});

const authLink = setContext((_, { headers }) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") || undefined : undefined;
  return {
    headers: {
      ...headers,
      authorization: token ? `JWT ${token}` : "",
    },
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

export default function Providers({ children }: { children: React.ReactNode }) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}


