export function AppTopbar() {
  const today = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
  }).format(new Date());

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/95 backdrop-blur">
      <div className="flex items-center justify-between px-6 py-4 lg:px-8">
        <div>
          <p className="text-sm text-zinc-500">
            Painel operacional
          </p>

          <p className="text-sm capitalize text-zinc-300">
            {today}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-300">
            API online
          </span>
        </div>
      </div>
    </header>
  );
}