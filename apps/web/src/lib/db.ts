import { neon } from "@neondatabase/serverless";

const FALLBACK_DB_URL =
  "postgresql://neondb_owner:npg_ZkeEbI8K7XRL@ep-wispy-brook-b5hjt92z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require";

export const DEFAULT_WORKSPACE_ID = "0386b534-0330-4743-a95a-e1df6a25bfde";

/**
 * Returns a serverless Neon SQL query runner over HTTP.
 * Automatically sanitizes Python asyncpg connection strings if present.
 */
export function getDb() {
  const rawUrl = process.env.DATABASE_URL || FALLBACK_DB_URL;
  const cleanUrl = rawUrl.replace(/^postgresql\+asyncpg:\/\//, "postgresql://");
  return neon(cleanUrl);
}
