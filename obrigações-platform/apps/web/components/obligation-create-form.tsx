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

  const [emailEnabled, setEmailEnabled] = useState(false);
  const [emailDestino, setEmailDestino] = useState("");

  const [manualReminderAtDate, setManualReminderAtDate] = useState("");
  const [manualReminderAtTime, setManualReminderAtTime] = useState("08:00");

  const [recurrenceMode, setRecurrenceMode] = useState("");
  const [recurrenceTime, setRecurrenceTime] = useState("08:00");
  const [recurrenceIntervalDays, setRecurrenceIntervalDays] = useState("");
  const [recurrenceWeekday, setRecurrenceWeekday] = useState("");
  const [recurrenceDayOfMonth, setRecurrenceDayOfMonth] = useState("");
  const [recurrenceMonth, setRecurrenceMonth] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    const temLembrete = !!recurrenceMode || !!manualReminderAtDate;

    if (temLembrete && !emailDestino) {
      setError("Preencha o email antes de salvar a recorrência ou o lembrete manual.");
      setLoading(false);
      return;
    }

    try {
      const manualReminderAt =
        manualReminderAtDate && manualReminderAtTime
          ? `${manualReminderAtDate}T${manualReminderAtTime}:00`
          : null;

      const created = await createObligation({
        contract_id: Number(contractId),
        document_name: documentName || null,
        item_number: itemNumber || null,
        recurrence: recurrence || null,
        obligation_text: obligationText,
        observations: observations || null,
        responsible: responsible || null,
        status,
        email_enabled: emailEnabled,
        email_destino: emailDestino || null,
        manual_reminder_at: manualReminderAt,
        recurrence_mode: recurrenceMode || null,
        recurrence_time: recurrenceTime || null,
        recurrence_interval_days: recurrenceIntervalDays
          ? Number(recurrenceIntervalDays)
          : null,
        recurrence_weekday: recurrenceWeekday ? Number(recurrenceWeekday) : null,
        recurrence_day_of_month: recurrenceDayOfMonth
          ? Number(recurrenceDayOfMonth)
          : null,
        recurrence_month: recurrenceMonth ? Number(recurrenceMonth) : null,
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
          <span>Recorrência textual</span>
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

      <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="mb-4 text-base font-semibold">Recorrência</h3>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm text-zinc-300">
            <span>Tipo</span>
            <select
              value={recurrenceMode}
              onChange={(e) => setRecurrenceMode(e.target.value)}
              className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
            >
              <option value="">Sem recorrência</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensal</option>
              <option value="yearly">Anual</option>
              <option value="manual_days">Manual por dias</option>
            </select>
          </label>

          <label className="grid gap-2 text-sm text-zinc-300">
            <span>Horário da recorrência</span>
            <input
              type="time"
              value={recurrenceTime}
              onChange={(e) => setRecurrenceTime(e.target.value)}
              className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
            />
          </label>

          <label className="grid gap-2 text-sm text-zinc-300">
            <span>Data do lembrete manual</span>
            <input
              type="date"
              value={manualReminderAtDate}
              onChange={(e) => setManualReminderAtDate(e.target.value)}
              className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
            />
          </label>

          <label className="grid gap-2 text-sm text-zinc-300">
            <span>Hora do lembrete manual</span>
            <input
              type="time"
              value={manualReminderAtTime}
              onChange={(e) => setManualReminderAtTime(e.target.value)}
              className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
            />
          </label>

          {recurrenceMode === "manual_days" ? (
            <label className="grid gap-2 text-sm text-zinc-300">
              <span>A cada quantos dias</span>
              <input
                type="number"
                min="1"
                value={recurrenceIntervalDays}
                onChange={(e) => setRecurrenceIntervalDays(e.target.value)}
                className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
              />
            </label>
          ) : null}

          {recurrenceMode === "weekly" ? (
            <label className="grid gap-2 text-sm text-zinc-300">
              <span>Dia da semana</span>
              <select
                value={recurrenceWeekday}
                onChange={(e) => setRecurrenceWeekday(e.target.value)}
                className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
              >
                <option value="">Escolher</option>
                <option value="0">Segunda</option>
                <option value="1">Terça</option>
                <option value="2">Quarta</option>
                <option value="3">Quinta</option>
                <option value="4">Sexta</option>
                <option value="5">Sábado</option>
                <option value="6">Domingo</option>
              </select>
            </label>
          ) : null}

          {recurrenceMode === "monthly" ? (
            <label className="grid gap-2 text-sm text-zinc-300">
              <span>Dia do mês</span>
              <input
                type="number"
                min="1"
                max="31"
                value={recurrenceDayOfMonth}
                onChange={(e) => setRecurrenceDayOfMonth(e.target.value)}
                className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
              />
            </label>
          ) : null}

          {recurrenceMode === "yearly" ? (
            <>
              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Mês</span>
                <select
                  value={recurrenceMonth}
                  onChange={(e) => setRecurrenceMonth(e.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                >
                  <option value="">Escolher</option>
                  <option value="1">Janeiro</option>
                  <option value="2">Fevereiro</option>
                  <option value="3">Março</option>
                  <option value="4">Abril</option>
                  <option value="5">Maio</option>
                  <option value="6">Junho</option>
                  <option value="7">Julho</option>
                  <option value="8">Agosto</option>
                  <option value="9">Setembro</option>
                  <option value="10">Outubro</option>
                  <option value="11">Novembro</option>
                  <option value="12">Dezembro</option>
                </select>
              </label>

              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Dia do mês</span>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={recurrenceDayOfMonth}
                  onChange={(e) => setRecurrenceDayOfMonth(e.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                />
              </label>
            </>
          ) : null}
        </div>

        <p className="mt-3 text-xs text-zinc-500">
          O próximo lembrete será calculado com base na recorrência e na data/hora base.
        </p>
      </div>

      <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="mb-4 text-base font-semibold">Email</h3>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex items-center gap-3 text-sm text-zinc-300 md:col-span-2">
            <input
              type="checkbox"
              checked={emailEnabled}
              onChange={(event) => setEmailEnabled(event.target.checked)}
            />
            <span>Ativar lembrete por email</span>
          </label>

          <label className="grid gap-2 text-sm text-zinc-300 md:col-span-2">
            <span>Email do destinatário</span>
            <input
              type="email"
              value={emailDestino}
              onChange={(event) => setEmailDestino(event.target.value)}
              placeholder="nome@empresa.com"
              className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
            />
          </label>
        </div>
      </div>

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