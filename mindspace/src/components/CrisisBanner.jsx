import { Phone, MessageSquare, X } from 'lucide-react';
import { useState } from 'react';

export default function CrisisBanner({ visible }) {
  const [dismissed, setDismissed] = useState(false);

  if (!visible || dismissed) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mx-4 mb-3 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-red-800 font-semibold text-sm mb-2">
            I hear you — you&apos;re not alone in this.
          </p>
          <p className="text-red-700 text-sm mb-3">
            If you&apos;re having thoughts of harming yourself, please reach out to a crisis counselor right now:
          </p>
          <div className="flex flex-col gap-2">
            <a
              href="tel:988"
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-3 py-2 rounded-lg transition-colors w-fit"
            >
              <Phone size={14} />
              Call or Text 988 — Suicide & Crisis Lifeline
            </a>
            <p className="text-red-600 text-xs flex items-center gap-1">
              <MessageSquare size={12} />
              Or text HOME to 741741 (Crisis Text Line)
            </p>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-red-400 hover:text-red-600 transition-colors mt-0.5"
          aria-label="Dismiss crisis banner"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
