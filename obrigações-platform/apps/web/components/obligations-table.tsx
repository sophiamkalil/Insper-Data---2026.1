import Link from "next/link";

import { StatusBadge } from "@/components/ui/status-badge";
import { Obligation } from "@/types/obligation";

interface Props {
  obligations: Obligation[];
}

export function ObligationsTable({ obligations }: Props) {
  if (obligations.length === 0) {
    return (
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-10 text-center">
        <p className="text-lg font-medium text-zinc-100">
          Nenhuma obrigação encontrada.
        </p>
        <p className="mt-2 text-sm text-zinc-400">
          Tente ajustar a busca ou o filtro de status.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="border-b border-zinc-800 bg-zinc-950">
            <tr>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                ID
              </th>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                Documento
              </th>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                Item
              </th>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                Obrigação
              </th>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                Responsável
              </th>
              <th className="px-4 py-4 text-sm font-medium text-zinc-400">
                Status
              </th>
            </tr>
          </thead>

          <tbody>
            {obligations.map((obligation) => (
              <tr
                key={obligation.id}
                className="border-b border-zinc-800 hover:bg-zinc-800/40"
              >
                <td className="px-4 py-4 text-sm text-zinc-300">
                  <Link
                    href={`/obligations/${obligation.id}`}
                    className="hover:underline"
                  >
                    #{obligation.id}
                  </Link>
                </td>

                <td className="px-4 py-4 text-sm text-zinc-300">
                  <Link
                    href={`/obligations/${obligation.id}`}
                    className="hover:underline"
                  >
                    {obligation.document_name || "-"}
                  </Link>
                </td>

                <td className="px-4 py-4 text-sm text-zinc-300">
                  <Link
                    href={`/obligations/${obligation.id}`}
                    className="hover:underline"
                  >
                    {obligation.item_number || "-"}
                  </Link>
                </td>

                <td className="max-w-[500px] px-4 py-4 text-sm text-zinc-100">
                  <Link
                    href={`/obligations/${obligation.id}`}
                    className="hover:underline"
                  >
                    {obligation.obligation_text}
                  </Link>
                </td>

                <td className="px-4 py-4 text-sm text-zinc-300">
                  <Link
                    href={`/obligations/${obligation.id}`}
                    className="hover:underline"
                  >
                    {obligation.responsible || "-"}
                  </Link>
                </td>

                <td className="px-4 py-4">
                  <Link href={`/obligations/${obligation.id}`}>
                    <StatusBadge status={obligation.status} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}