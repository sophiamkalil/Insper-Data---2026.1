"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { label: "Dashboard", href: "/" },
  { label: "Obrigações", href: "/obligations" },
  { label: "Contratos", href: "/contracts" },
  { label: "Relatórios", href: "/reports" },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="border-b border-zinc-800 bg-zinc-950 lg:h-screen lg:w-72 lg:border-b-0 lg:border-r">
      <div className="p-6 lg:p-8">
        <div className="mb-10">
          <div className="text-sm uppercase tracking-[0.3em] text-zinc-500">
            Projeto
          </div>

          <h1 className="mt-2 text-2xl font-semibold text-zinc-100">
            Obrigações Platform
          </h1>

          <p className="mt-2 text-sm text-zinc-400">
            Gestão de obrigações contratuais
          </p>
        </div>

        <nav className="space-y-2 text-sm">
          {items.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-xl px-4 py-3 transition ${
                  active
                    ? "bg-zinc-900 text-zinc-100"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}