import { onMounted, reactive } from 'vue';
import {
  fetchFormPageRows,
  type FormPageLookupOption as LookupOption,
  type FormPageRow,
  type FormPageSearchCondition, fetchTestCategoryOptions
} from '../api/form';

const columns = [
  { key: "stuno", label: "학생번호" },
  { key: "stuname", label: "학생명" },
  { key: "avgscore", label: "평균점수" },
  { key: "rank", label: "등수" },
  { key: "denseRank", label: "석차" }
] as const;

function createDefaultSearchForm(): FormPageSearchCondition {
  return {
    testCategory: '',
  };
}

export function useFormPage() {
  const state = reactive({
    searchForm: createDefaultSearchForm(),
    rows: [] as FormPageRow[],
    lookups: {
      testCategory: [] as LookupOption[],
    },
    loading: false,
    bootstrapping: false,
    error: '',
  });

  function validateSearch() {
    if (!state.searchForm.testCategory) { throw new Error("어떤 시험입니까? 콤보박스에서 확인해주세요"); }
  }

  async function search() {
    state.error = '';
    state.loading = true;
    try {
      validateSearch();
      state.rows = await fetchFormPageRows(state.searchForm);
    } catch (error) {
      state.error = error instanceof Error ? error.message : 'Failed to load rows.';
    } finally {
      state.loading = false;
    }
  }

  async function loadTestCategoryOptions() {
    state.lookups.testCategory = await fetchTestCategoryOptions();
  }

  function openButton1Subview() {
    console.info("TODO: mount related subview contract for scurl.");
  }

  function openScholarshipPopup() {
    const popupUrl = "/scholarship";
    // TODO: port legacy popup parameter binding: "param="+Quote(param)
    window.open(popupUrl, '_blank', "width=600,height=300,resizable=no");
  }

  async function initialize() {
    state.bootstrapping = true;
    state.error = '';
    try {
      await loadTestCategoryOptions();
    } catch (error) {
      state.error = error instanceof Error ? error.message : 'Failed to initialize page.';
    } finally {
      state.bootstrapping = false;
    }
  }

  onMounted(() => {
    void initialize();
  });

  return {
    state,
    columns,
    actions: {
      search,
      openButton1Subview,
      openScholarshipPopup
    },
    meta: {
      primaryDatasetId: "ds_scorechk",
      mainGridComponentId: "Grid0",
      legacyEndpoint: "http://127.0.0.1:8080/miplatform/testScoreChk.do",
      sqlMapId: "sampleDAO.ScoreChk",
      relatedPages: [
        { kind: "subview", target: "scurl", status: "unresolved" },
        { kind: "popup", target: "scholarship", status: "resolved" }
      ],
    },
  };
}

export default useFormPage;
