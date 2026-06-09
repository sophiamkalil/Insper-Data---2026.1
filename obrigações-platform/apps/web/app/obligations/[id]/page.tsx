import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { ObligationDetailPanel } from "@/components/obligation-detail-panel";
import { getObligationById } from "@/lib/api";

export default async function ObligationDetailPage({
  params,
}: {
  params: { id: string } | Promise<{ id: string }>;
}) {
  const resolvedParams = await Promise.resolve(params);
  const id = Number(resolvedParams.id);

  if (Number.isNaN(id)) {
    return (
      <AppShell>
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h1 className="text-2xl font-semibold">
            Obrigação inválida
          </h1>

          <p className="mt-2 text-sm text-zinc-400">
            O identificador da obrigação não é válido.
          </p>

          <Link
            href="/"
            className="mt-6 inline-block rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Voltar
          </Link>
        </div>
      </AppShell>
    );
  }

  let data;

  try {
    data = await getObligationById(id);
  } catch {
    return (
      <AppShell>
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h1 className="text-2xl font-semibold">
            Não consegui abrir a obrigação
          </h1>

          <p className="mt-2 text-sm text-zinc-400">
            A API não respondeu como esperado para esta obrigação.
          </p>

          <Link
            href="/"
            className="mt-6 inline-block rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Voltar
          </Link>
        </div>
      </AppShell>
    );
  }

  const { obligation, history } = data;

  return (
    <AppShell>
      <PageHeader
        eyebrow={`Obrigação #${obligation.id}`}
        title="Detalhe da obrigação"
        description="Visualização, atualização e histórico da obrigação."
        action={
          <Link
            href="/"
            className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-100 hover:bg-zinc-800"
          >
            Voltar
          </Link>
        }
      />

      <ObligationDetailPanel
        obligation={obligation}
        history={history}
      />
    </AppShell>
  );
}