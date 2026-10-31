import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "healthy",
    service: "ideaos-unified",
    timestamp: new Date().toISOString(),
  });
}
