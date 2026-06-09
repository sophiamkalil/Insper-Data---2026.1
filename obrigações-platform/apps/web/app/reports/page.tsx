import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";

export default function ReportsPage() {
  return (
    <AppShell>
      <PageHeader
        eyebrow="Módulo"
        title="Relatórios"
        description="Área reservada para indicadores, exportações e visão executiva."
        action={
          <Link
            href="/obligations"
            className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Ir para obrigações
          </Link>
        }
      />

      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
        <p className="text-sm text-zinc-300">
          Módulo em construção.
        </p>
      </div>
    </AppShell>
  );
}