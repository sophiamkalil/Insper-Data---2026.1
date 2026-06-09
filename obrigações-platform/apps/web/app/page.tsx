import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { getObligations } from "@/lib/api";
import type { ObligationsResponse } from "@/types/obligation";

type SearchParams = {
  q?: string | string[];
  status?: string | string[];
  page?: string | string[];
};

function firstValue(value: string | string[] | undefined) {
  if (Array.isArray(value)) return value[0] ?? "";
  return value ?? "";
}

export default async function ObligationsPage({
  searchParams,
}: {
  searchParams?: SearchParams | Promise<SearchParams>;
}) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});

  const q = firstValue(resolvedSearchParams.q).trim();
  const status = firstValue(resolvedSearchParams.status) || "all";
  const page = Math.max(Number(firstValue(resolvedSearchParams.page) || "1"), 1);
  const limit = 15;
  const skip = (page - 1) * limit;

  let data: ObligationsResponse = {
    items: [],
    total: 0,
    skip,
    limit,
  };

  let error: string | null = null;

  try {
    data = await getObligations({
      q: q || undefined,
      status: status !== "all" ? status : undefined,
      skip,
      limit,
    });
  } catch {
    error = "Não foi possível carregar as obrigações no momento.";
  }

  const totalPages = Math.max(Math.ceil(data.total / limit), 1);

  const buildHref = (nextPage: number) => {
    const params = new URLSearchParams();

    if (q) params.set("q", q);
    if (status && status !== "all") params.set("status", status);
    params.set("page", String(nextPage));

    return `/obligations?${params.toString()}`;
  };

  return (
    <AppShell>
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm text-zinc-500">Área operacional</p>
          <h1 className="text-3xl font-semibold text-zinc-100">Obrigações</h1>
          <p className="mt-2 max-w-2xl text-sm text-zinc-400">
            Busque, filtre e acompanhe a base completa de obrigações contratuais.
          </p>
        </div>

        <Link
          href="/obligations/new"
          className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:opacity-90"
        >
          Nova obrigação
        </Link>
      </div>

      <form
        method="get"
        action="/obligations"
        className="mb-6 grid gap-3 rounded-2xl border border-zinc-800 bg-zinc-900 p-4 md:grid-cols-[1fr_220px_auto]"
      >
        <input
          type="text"
          name="q"
          defaultValue={q}
          placeholder="Buscar por texto, documento, responsável..."
          className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
        />

        <select
          name="status"
          defaultValue={status}
          className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
        >
          <option value="all">Todos os status</option>
          <option value="pending">Pendente</option>
          <option value="completed">Concluída</option>
          <option value="overdue">Vencida</option>
        </select>

        <input type="hidden" name="page" value="1" />

        <button
          type="submit"
          className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:opacity-90"
        >
          Filtrar
        </button>
      </form>

      {error ? (
        <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      ) : null}

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">
          <p className="text-sm text-zinc-500">Total encontrado</p>
          <p className="mt-2 text-3xl font-semibold">{data.total}</p>
        </div>

        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">
          <p className="text-sm text-zinc-500">Página atual</p>
          <p className="mt-2 text-3xl font-semibold">{page}</p>
        </div>

        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">
          <p className="text-sm text-zinc-500">Itens por página</p>
          <p className="mt-2 text-3xl font-semibold">{limit}</p>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-zinc-800 bg-zinc-950">
              <tr>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">ID</th>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">Documento</th>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">Item</th>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">Obrigação</th>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">Responsável</th>
                <th className="px-4 py-4 text-sm font-medium text-zinc-400">Status</th>
              </tr>
            </thead>

            <tbody>
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-10 text-center text-sm text-zinc-400">
                    Nenhuma obrigação encontrada.
                  </td>
                </tr>
              ) : (
                data.items.map((obligation) => (
                  <tr key={obligation.id} className="border-b border-zinc-800 hover:bg-zinc-800/40">
                    <td className="px-4 py-4 text-sm text-zinc-300">
                      <Link href={`/obligations/${obligation.id}`} className="hover:underline">
                        #{obligation.id}
                      </Link>
                    </td>
                    <td className="px-4 py-4 text-sm text-zinc-300">
                      <Link href={`/obligations/${obligation.id}`} className="hover:underline">
                        {obligation.document_name || "-"}
                      </Link>
                    </td>
                    <td className="px-4 py-4 text-sm text-zinc-300">
                      <Link href={`/obligations/${obligation.id}`} className="hover:underline">
                        {obligation.item_number || "-"}
                      </Link>
                    </td>
                    <td className="max-w-[500px] px-4 py-4 text-sm text-zinc-100">
                      <Link href={`/obligations/${obligation.id}`} className="hover:underline">
                        {obligation.obligation_text}
                      </Link>
                    </td>
                    <td className="px-4 py-4 text-sm text-zinc-300">
                      <Link href={`/obligations/${obligation.id}`} className="hover:underline">
                        {obligation.responsible || "-"}
                      </Link>
                    </td>
                    <td className="px-4 py-4 text-sm text-zinc-300">
                      <Link href={`/obligations/${obligation.id}`} className="inline-flex rounded-full bg-zinc-800 px-3 py-1 text-xs font-medium text-zinc-200 hover:opacity-90">
                        {obligation.status}
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between text-sm text-zinc-400">
        <span>
          Mostrando {data.items.length} de {data.total}
        </span>

        <div className="flex gap-2">
          <a
            href={page > 1 ? buildHref(page - 1) : "#"}
            className={`rounded-xl border border-zinc-800 px-4 py-2 ${
              page > 1
                ? "bg-zinc-900 text-zinc-100 hover:bg-zinc-800"
                : "pointer-events-none opacity-40"
            }`}
          >
            Anterior
          </a>

          <a
            href={page < totalPages ? buildHref(page + 1) : "#"}
            className={`rounded-xl border border-zinc-800 px-4 py-2 ${
              page < totalPages
                ? "bg-zinc-900 text-zinc-100 hover:bg-zinc-800"
                : "pointer-events-none opacity-40"
            }`}
          >
            Próxima
          </a>
        </div>
      </div>
    </AppShell>
  );
}