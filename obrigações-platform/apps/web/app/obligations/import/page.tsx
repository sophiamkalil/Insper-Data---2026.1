import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { SpreadsheetImportForm } from "@/components/spreadsheet-import-form";

export default function ImportSpreadsheetPage() {
  return (
    <AppShell>
      <PageHeader
        eyebrow="Importação"
        title="Trocar planilha"
        description="Envie uma nova planilha para substituir a base atual de obrigações."
        action={
          <Link
            href="/obligations"
            className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Voltar
          </Link>
        }
      />

      <SpreadsheetImportForm />
    </AppShell>
  );
}