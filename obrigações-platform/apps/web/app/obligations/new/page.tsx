import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { ObligationCreateForm } from "@/components/obligation-create-form";
import { getContracts } from "@/lib/api";

export default async function NewObligationPage() {
  const contracts = await getContracts();

  return (
    <AppShell>
      <PageHeader
        eyebrow="Cadastro"
        title="Nova obrigação"
        description="Crie uma nova obrigação manualmente."
        action={
          <Link
            href="/obligations"
            className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Voltar
          </Link>
        }
      />

      <ObligationCreateForm contracts={contracts} />
    </AppShell>
  );
}