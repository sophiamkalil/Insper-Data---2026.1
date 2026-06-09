"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { replaceSpreadsheet } from "@/lib/api";

export function SpreadsheetImportForm() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);

    if (!file) {
      setError("Escolha um arquivo .xlsx primeiro.");
      return;
    }

    setLoading(true);

    try {
      const result = await replaceSpreadsheet(file);
      setMessage(
        `Planilha importada com sucesso. ${result.imported} obrigações carregadas.`
      );

      router.refresh();
      router.push("/obligations");
    } catch {
      setError("Não foi possível importar a planilha.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-6"
    >
      <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4 text-sm text-yellow-200">
        Atenção: a importação substitui a base atual de obrigações.
      </div>

      <label className="grid gap-2 text-sm text-zinc-300">
        <span>Arquivo .xlsx</span>
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
        />
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Importando..." : "Importar e substituir"}
        </button>

        {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
      </div>
    </form>
  );
}