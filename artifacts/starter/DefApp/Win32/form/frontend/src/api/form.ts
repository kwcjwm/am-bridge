export interface FormPageSearchCondition {
  testCategory: string;
}

export interface FormPageRow {
  stuno: string;
  stuname: string;
  avgscore: string;
  rank: string;
  denseRank: string;
}

export interface FormPageLookupOption {
  value: string;
  label: string;
  raw: Record<string, unknown>;
}

export interface FormPageBackendLookupOption {
  value: string;
  label: string;
}

async function requestJson<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchFormPageRows(searchForm: FormPageSearchCondition): Promise<FormPageRow[]> {
  return requestJson<FormPageRow[]>('/api/form/search', {
    method: 'POST',
    body: JSON.stringify(searchForm),
  });
}

export async function fetchTestCategoryOptions(): Promise<FormPageLookupOption[]> {
  const rows = await requestJson<FormPageBackendLookupOption[]>("/api/form/lookups/testcategory");
  return rows.map((row) => ({
    value: String(row.value ?? ''),
    label: String(row.label ?? row.value ?? ''),
    raw: row as Record<string, unknown>,
  }));
}

export const targetRoute = "/form";
export const legacySearchEndpoint = "http://127.0.0.1:8080/miplatform/testScoreChk.do";
