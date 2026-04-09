export async function fetchFormPageRows(searchForm: Record<string, unknown>) {
  const response = await fetch('/api/form/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(searchForm),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch data for form');
  }

  return response.json();
}

export const targetRoute = '/form';
