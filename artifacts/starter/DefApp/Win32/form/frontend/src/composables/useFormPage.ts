import { reactive } from 'vue';
import { fetchFormPageRows } from '../api/form';

export function useFormPage() {
  const state = reactive({
    searchForm: {},
    rows: [],
    loading: false,
  });

  async function search() {
    state.loading = true;
    try {
      state.rows = await fetchFormPageRows(state.searchForm);
    } finally {
      state.loading = false;
    }
  }

  return {
    state,
    actions: { search },
    meta: {
      primaryDatasetId: 'ds_scorechk',
      searchDatasetId: '',
    },
  };
}

export default useFormPage;
