import {
  ObligationCreateRequest,
  ObligationDetailResponse,
  ObligationsResponse,
  UpdateObligationPayload,
} from "@/types/obligation";

const API_URL = "http://127.0.0.1:8000/api/v1";

type GetObligationsParams = {
  q?: string;
  status?: string;
  skip?: number;
  limit?: number;
};

export async function getObligations(
  params: GetObligationsParams = {}
): Promise<ObligationsResponse> {
  const searchParams = new URLSearchParams();

  if (params.q) searchParams.set("q", params.q);
  if (params.status) searchParams.set("status", params.status);

  if (typeof params.skip === "number") {
    searchParams.set("skip", String(params.skip));
  }

  if (typeof params.limit === "number") {
    searchParams.set("limit", String(params.limit));
  }

  const url = `${API_URL}/obligations${
    searchParams.toString() ? `?${searchParams.toString()}` : ""
  }`;

  const response = await fetch(url, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Erro ao buscar obrigações");
  }

  return response.json();
}

export async function getObligationById(
  id: number
): Promise<ObligationDetailResponse> {
  const response = await fetch(`${API_URL}/obligations/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Erro ao buscar detalhe da obrigação");
  }

  return response.json();
}

export async function updateObligation(
  id: number,
  payload: UpdateObligationPayload
): Promise<ObligationDetailResponse> {
  const response = await fetch(`${API_URL}/obligations/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Erro ao atualizar obrigação");
  }

  return response.json();
}

export async function deleteObligation(id: number) {
  const response = await fetch(`${API_URL}/obligations/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Erro ao excluir obrigação");
  }

  return response.json();
}

export async function sendObligationEmailNow(id: number, sendAt?: string | null) {
  const response = await fetch(`${API_URL}/obligations/${id}/send-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sendAt ? { send_at: sendAt } : {}),
  });

  if (!response.ok) {
    throw new Error("Erro ao enviar email");
  }

  return response.json();
}

export async function getContracts(): Promise<
  Array<{ id: number; name: string; code: string | null }>
> {
  const response = await fetch(`${API_URL}/contracts`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Erro ao buscar contratos");
  }

  return response.json();
}

export async function createObligation(payload: ObligationCreateRequest) {
  const response = await fetch(`${API_URL}/obligations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Erro ao criar obrigação");
  }

  return response.json();
}

export async function replaceSpreadsheet(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/imports/spreadsheet/replace`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Erro ao importar planilha");
  }

  return response.json();
}