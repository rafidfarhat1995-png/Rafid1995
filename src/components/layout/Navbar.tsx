"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-primary text-white shadow-md">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold">
            <span className="text-accent">$</span>
            <span>Loonie Sense</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden sm:flex sm:items-center sm:gap-6">
            <Link
              href="/"
              className="text-sm font-medium text-white/80 transition hover:text-white"
            >
              Home
            </Link>
            <Link
              href="/tools/mortgage-preapproval"
              className="text-sm font-medium text-white/80 transition hover:text-white"
            >
              Pre-Approval Estimator
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="sm:hidden p-2"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="sm:hidden pb-4 space-y-2">
            <Link
              href="/"
              className="block text-sm font-medium text-white/80 hover:text-white"
              onClick={() => setMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/tools/mortgage-preapproval"
              className="block text-sm font-medium text-white/80 hover:text-white"
              onClick={() => setMenuOpen(false)}
            >
              Pre-Approval Estimator
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
