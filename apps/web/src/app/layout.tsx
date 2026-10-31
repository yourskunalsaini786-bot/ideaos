import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IdeaOS Studio | Content Intelligence & Repurposing with Brand Memory",
  description: "AI-powered long-form video and podcast repurposing studio with explainable clip selection and edit-learning brand memory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=JetBrains+Mono:wght@100..900&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-surface font-sans text-on-surface antialiased selection:bg-primary-container selection:text-on-primary min-h-screen">
        {children}
      </body>
    </html>
  );
}
