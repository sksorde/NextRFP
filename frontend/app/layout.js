import "./globals.css";

export const metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || "Enterprise Bid Intelligence Platform",
  description:
    "Enterprise Bid Intelligence Platform for RFP compliance review, Shipley-style scoring, recommendations, and knowledge base retrieval.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
