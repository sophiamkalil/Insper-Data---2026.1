"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import {
  deleteObligation,
  sendObligationEmailNow,
  updateObligation,
} from "@/lib/api";
import {
  Obligation,
  ObligationStatusHistory,
} from "@/types/obligation";

type Props = {
  obligation: Obligation;
  history: ObligationStatusHistory[];
};

function formatDateTime(dateString: string | null) {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString("pt-BR");
}

function formatDate(dateString: string | null) {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString("pt-BR");
}

export function ObligationDetailPanel({ obligation, history }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const [status, setStatus] = useState(obligation.status);
  const [observations, setObservations] = useState(obligation.observations ?? "");
  const [note, setNote] = useState("");

  const [emailEnabled, setEmailEnabled] = useState(obligation.email_enabled);
  const [emailDestino, setEmailDestino] = useState(obligation.email_destino ?? "");

  const [manualReminderAtDate, setManualReminderAtDate] = useState(
    obligation.manual_reminder_at ? obligation.manual_reminder_at.slice(0, 10) : ""
  );
  const [manualReminderAtTime, setManualReminderAtTime] = useState(
    obligation.manual_reminder_at ? obligation.manual_reminder_at.slice(11, 16) : "08:00"
  );

  const [recurrenceMode, setRecurrenceMode] = useState(
    obligation.recurrence_mode ?? ""
  );
  const [recurrenceTime, setRecurrenceTime] = useState(
    obligation.recurrence_time ?? "08:00"
  );
  const [recurrenceIntervalDays, setRecurrenceIntervalDays] = useState(
    obligation.recurrence_interval_days ? String(obligation.recurrence_interval_days) : ""
  );
  const [recurrenceWeekday, setRecurrenceWeekday] = useState(
    obligation.recurrence_weekday !== null && obligation.recurrence_weekday !== undefined
      ? String(obligation.recurrence_weekday)
      : ""
  );
  const [recurrenceDayOfMonth, setRecurrenceDayOfMonth] = useState(
    obligation.recurrence_day_of_month ? String(obligation.recurrence_day_of_month) : ""
  );
  const [recurrenceMonth, setRecurrenceMonth] = useState(
    obligation.recurrence_month ? String(obligation.recurrence_month) : ""
  );

  const [triggerFamily, setTriggerFamily] = useState(
    obligation.trigger_family ?? ""
  );
  const [triggerType, setTriggerType] = useState(obligation.trigger_type ?? "");
  const [conditionRaw, setConditionRaw] = useState(obligation.condition_raw ?? "");
  const [conditionCanonical, setConditionCanonical] = useState(
    obligation.condition_canonical ?? ""
  );
  const [conditionStatus, setConditionStatus] = useState(
    obligation.condition_status ?? "pendente"
  );

  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [emailMessage, setEmailMessage] = useState<string | null>(null);

  const statusLabel = useMemo(() => {
    if (status === "completed") return "Concluída";
    if (status === "overdue") return "Vencida";
    return "Pendente";
  }, [status]);

  const recurrenceLabel = useMemo(() => {
    if (recurrenceMode === "weekly") return "Semanal";
    if (recurrenceMode === "monthly") return "Mensal";
    if (recurrenceMode === "yearly") return "Anual";
    if (recurrenceMode === "manual_days") return "Manual por dias";
    return "-";
  }, [recurrenceMode]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);

    const temLembrete =
      !!recurrenceMode ||
      !!manualReminderAtDate ||
      !!obligation.manual_reminder_at;

    if (temLembrete && !emailDestino) {
      setError("Preencha o email antes de salvar a recorrência ou o lembrete manual.");
      return;
    }

    try {
      const manualReminderAt =
        manualReminderAtDate && manualReminderAtTime
          ? `${manualReminderAtDate}T${manualReminderAtTime}:00`
          : null;

      await updateObligation(obligation.id, {
        status,
        observations,
        note: note || undefined,
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
        trigger_family: triggerFamily || null,
        trigger_type: triggerType || null,
        condition_raw: conditionRaw || null,
        condition_canonical: conditionCanonical || null,
        condition_status: conditionStatus || null,
      });

      setMessage("Obrigação atualizada com sucesso.");
      setNote("");

      startTransition(() => {
        router.refresh();
      });
    } catch {
      setError("Não foi possível atualizar a obrigação.");
    }
  }

  async function handleDelete() {
    const confirmed = window.confirm(
      "Tem certeza que deseja excluir esta obrigação?"
    );

    if (!confirmed) return;

    try {
      await deleteObligation(obligation.id);
      router.push("/obligations");
      router.refresh();
    } catch {
      setError("Não foi possível excluir a obrigação.");
    }
  }

  async function handleSendEmailNow() {
    setEmailMessage(null);
    setError(null);

    try {
      await sendObligationEmailNow(obligation.id);

      setEmailMessage("Email enviado com sucesso.");
      startTransition(() => {
        router.refresh();
      });
    } catch {
      setEmailMessage(null);
      setError("Não foi possível enviar o email agora.");
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
        <h2 className="mb-4 text-lg font-semibold">Dados principais</h2>

        <div className="space-y-3 text-sm text-zinc-300">
          <p>
            <span className="text-zinc-500">Documento:</span>{" "}
            {obligation.document_name || "-"}
          </p>
          <p>
            <span className="text-zinc-500">Item:</span>{" "}
            {obligation.item_number || "-"}
          </p>
          <p>
            <span className="text-zinc-500">Recorrência textual:</span>{" "}
            {obligation.recurrence || "-"}
          </p>
          <p>
            <span className="text-zinc-500">Responsável:</span>{" "}
            {obligation.responsible || "-"}
          </p>
          <p>
            <span className="text-zinc-500">Linha de origem:</span>{" "}
            {obligation.source_row || "-"}
          </p>
          <p>
            <span className="text-zinc-500">Status atual:</span>{" "}
            {statusLabel}
          </p>
          <p>
            <span className="text-zinc-500">Tipo de recorrência:</span>{" "}
            {recurrenceLabel}
          </p>
          <p>
            <span className="text-zinc-500">Próximo lembrete recorrente:</span>{" "}
            {formatDateTime(obligation.next_recurrence_at)}
          </p>
          <p>
            <span className="text-zinc-500">Próximo lembrete real:</span>{" "}
            {formatDateTime(obligation.next_reminder_at)}
          </p>
          <p>
            <span className="text-zinc-500">Último envio:</span>{" "}
            {formatDateTime(obligation.last_email_sent_at)}
          </p>
          <p>
            <span className="text-zinc-500">Lembrete manual:</span>{" "}
            {formatDateTime(obligation.manual_reminder_at)}
          </p>
          <p>
            <span className="text-zinc-500">Lembrete manual enviado em:</span>{" "}
            {formatDateTime(obligation.manual_reminder_sent_at)}
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
        <h2 className="mb-4 text-lg font-semibold">Texto da obrigação</h2>
        <p className="text-sm leading-6 text-zinc-300">
          {obligation.obligation_text}
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 lg:col-span-2">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold">Editar obrigação</h2>

          <button
            type="button"
            onClick={handleDelete}
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/20"
          >
            Excluir obrigação
          </button>
        </div>

        <form className="grid gap-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-2 text-sm text-zinc-300">
              <span>Status</span>
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value)}
                className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none"
              >
                <option value="pending">Pendente</option>
                <option value="completed">Concluída</option>
                <option value="overdue">Vencida</option>
              </select>
            </label>

            <label className="grid gap-2 text-sm text-zinc-300">
              <span>Nota do histórico</span>
              <input
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Ex.: ajustado após revisão da equipe"
                className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
              />
            </label>
          </div>

          <label className="grid gap-2 text-sm text-zinc-300">
            <span>Observações</span>
            <textarea
              value={observations}
              onChange={(event) => setObservations(event.target.value)}
              rows={5}
              className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
            />
          </label>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <h3 className="mb-4 text-base font-semibold">Recorrência</h3>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Tipo</span>
                <select
                  value={recurrenceMode}
                  onChange={(event) => setRecurrenceMode(event.target.value)}
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
                  onChange={(event) => setRecurrenceTime(event.target.value)}
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
                    onChange={(event) =>
                      setRecurrenceIntervalDays(event.target.value)
                    }
                    className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                  />
                </label>
              ) : null}

              {recurrenceMode === "weekly" ? (
                <label className="grid gap-2 text-sm text-zinc-300">
                  <span>Dia da semana</span>
                  <select
                    value={recurrenceWeekday}
                    onChange={(event) => setRecurrenceWeekday(event.target.value)}
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
                    onChange={(event) =>
                      setRecurrenceDayOfMonth(event.target.value)
                    }
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
                      onChange={(event) => setRecurrenceMonth(event.target.value)}
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
                      onChange={(event) =>
                        setRecurrenceDayOfMonth(event.target.value)
                      }
                      className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                    />
                  </label>
                </>
              ) : null}
            </div>

            <p className="mt-3 text-xs text-zinc-500">
              O próximo lembrete recorrente é calculado com base no tipo escolhido e no horário definido.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <h3 className="mb-4 text-base font-semibold">Lembrete manual</h3>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Data manual</span>
                <input
                  type="date"
                  value={manualReminderAtDate}
                  onChange={(e) => setManualReminderAtDate(e.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                />
              </label>

              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Hora manual</span>
                <input
                  type="time"
                  value={manualReminderAtTime}
                  onChange={(e) => setManualReminderAtTime(e.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                />
              </label>
            </div>

            <p className="mt-3 text-xs text-zinc-500">
              Esse lembrete é pontual e não apaga a recorrência.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <h3 className="mb-4 text-base font-semibold">Condição acionadora</h3>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Tipo de gatilho</span>
                <select
                  value={triggerFamily}
                  onChange={(event) => setTriggerFamily(event.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                >
                  <option value="">Sem definir</option>
                  <option value="weekly">Semanal</option>
                  <option value="monthly">Mensal</option>
                  <option value="yearly">Anual</option>
                  <option value="manual_days">Manual por dias</option>
                  <option value="eventual">Eventual</option>
                </select>
              </label>

              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Tipo resumido</span>
                <input
                  value={triggerType}
                  onChange={(event) => setTriggerType(event.target.value)}
                  placeholder="Ex.: sob condição, prazo numérico..."
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
                />
              </label>

              <label className="grid gap-2 text-sm text-zinc-300 md:col-span-2">
                <span>Condição bruta</span>
                <textarea
                  value={conditionRaw}
                  onChange={(event) => setConditionRaw(event.target.value)}
                  rows={3}
                  placeholder="Texto da condição acionadora"
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
                />
              </label>

              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Condição padronizada</span>
                <input
                  value={conditionCanonical}
                  onChange={(event) =>
                    setConditionCanonical(event.target.value)
                  }
                  placeholder="Ex.: aprovação da ANTT"
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
                />
              </label>

              <label className="grid gap-2 text-sm text-zinc-300">
                <span>Status da condição</span>
                <select
                  value={conditionStatus}
                  onChange={(event) => setConditionStatus(event.target.value)}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-100 outline-none"
                >
                  <option value="pendente">Pendente</option>
                  <option value="cumprida">Cumprida</option>
                </select>
              </label>
            </div>

            <p className="mt-3 text-xs text-zinc-500">
              Quando o tipo for “eventual”, o lembrete só dispara após a condição ser marcada como cumprida.
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

              <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-300 md:col-span-2">
                <span className="text-zinc-500">Próximo lembrete real:</span>{" "}
                {formatDateTime(obligation.next_reminder_at)}
              </div>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleSendEmailNow}
                className="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-3 text-sm font-medium text-zinc-100 transition hover:bg-zinc-800"
              >
                Enviar agora
              </button>

              <div className="text-sm text-zinc-400">
                <span className="text-zinc-500">Status envio:</span>{" "}
                {obligation.status_envio || "não enviado"}
              </div>

              <div className="text-sm text-zinc-400">
                <span className="text-zinc-500">Último envio:</span>{" "}
                {formatDateTime(obligation.last_email_sent_at)}
              </div>
            </div>

            {emailMessage ? (
              <p className="mt-3 text-sm text-emerald-400">{emailMessage}</p>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={isPending}
              className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isPending ? "Salvando..." : "Salvar alterações"}
            </button>

            {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
            {error ? <p className="text-sm text-red-400">{error}</p> : null}
          </div>
        </form>
      </section>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 lg:col-span-2">
        <h2 className="mb-4 text-lg font-semibold">Histórico de status</h2>

        {history.length === 0 ? (
          <p className="text-sm text-zinc-400">
            Nenhuma alteração de status registrada ainda.
          </p>
        ) : (
          <div className="space-y-3">
            {history.map((item) => (
              <div
                key={item.id}
                className="rounded-xl border border-zinc-800 bg-zinc-950 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm text-zinc-100">
                    <span className="text-zinc-500">De:</span>{" "}
                    {item.old_status || "-"}{" "}
                    <span className="text-zinc-500">para</span>{" "}
                    {item.new_status}
                  </p>

                  <p className="text-xs text-zinc-500">
                    {new Date(item.changed_at).toLocaleString("pt-BR")}
                  </p>
                </div>

                {item.note ? (
                  <p className="mt-2 text-sm text-zinc-400">{item.note}</p>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}