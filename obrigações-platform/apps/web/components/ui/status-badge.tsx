interface StatusBadgeProps {
  status: string;
  className?: string;
}

function getStatusConfig(status: string) {
  switch (status) {
    case "completed":
      return {
        label: "Concluída",
        className: "bg-emerald-500/20 text-emerald-400",
      };
    case "overdue":
      return {
        label: "Vencida",
        className: "bg-red-500/20 text-red-400",
      };
    case "pending":
    default:
      return {
        label: "Pendente",
        className: "bg-yellow-500/20 text-yellow-400",
      };
  }
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const config = getStatusConfig(status);

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${config.className} ${className}`}
    >
      {config.label}
    </span>
  );
}