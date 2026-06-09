"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createObligation } from "@/lib/api";
import type { Contract } from "@/types/obligation";

type Props = {
  contracts: Contract[];
};

export function ObligationCreateForm({ contracts }: Props) {
  const router = useRouter();

  const [contractId, setContractId] = useState(
    contracts[0]?.id ? String(contracts[0].id) : ""
  );
  const [documentName, setDocumentName] = useState("");
  const [itemNumber, setItemNumber] = useState("");
  const [recurrence, setRecurrence] = useState("");
  const [obligationText, setObligationText] = useState("");
  const [observations, setObservations] = useState("");
  const [responsible, setResponsible] = useState("");
  const [status, setStatus] = useState("pending");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const created = await createObligation({
        contract_id: Number(contractId),
        document_name: documentName || null,
        item_number: itemNumber || null,
        recurrence: recurrence || null,
        obligation_text: obligationText,
        observations: observations || null,
        responsible: responsible || null,
        status,
      });

      setMessage("Obrigação criada com sucesso.");
      router.push(`/obligations/${created.id}`);
      router.refresh();
    } catch {
      setError("Não foi possível criar a obrigação.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-6"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Contrato</span>
          <select
            value={contractId}
            onChange={(e) => setContractId(e.target.value)}
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          >
            {contracts.map((contract) => (
              <option key={contract.id} value={contract.id}>
                {contract.name} {contract.code ? `(${contract.code})` : ""}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Status</span>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          >
            <option value="pending">Pendente</option>
            <option value="completed">Concluída</option>
            <option value="overdue">Vencida</option>
          </select>
        </label>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Documento</span>
          <input
            value={documentName}
            onChange={(e) => setDocumentName(e.target.value)}
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          />
        </label>

        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Item</span>
          <input
            value={itemNumber}
            onChange={(e) => setItemNumber(e.target.value)}
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          />
        </label>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Recorrência</span>
          <input
            value={recurrence}
            onChange={(e) => setRecurrence(e.target.value)}
            placeholder="Ex.: Mensal, Anual..."
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          />
        </label>

        <label className="grid gap-2 text-sm text-zinc-300">
          <span>Responsável</span>
          <input
            value={responsible}
            onChange={(e) => setResponsible(e.target.value)}
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
          />
        </label>
      </div>

      <label className="grid gap-2 text-sm text-zinc-300">
        <span>Obrigação</span>
        <textarea
          value={obligationText}
          onChange={(e) => setObligationText(e.target.value)}
          rows={5}
          className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
        />
      </label>

      <label className="grid gap-2 text-sm text-zinc-300">
        <span>Observações</span>
        <textarea
          value={observations}
          onChange={(e) => setObservations(e.target.value)}
          rows={4}
          className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
        />
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Salvando..." : "Criar obrigação"}
        </button>

        {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
      </div>
    </form>
  );
}