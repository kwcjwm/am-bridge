<template>
  <section class="page-shell">
    <header class="page-header">
      <div>
        <p class="eyebrow">grid-page</p>
        <h1>New Form</h1>
        <p class="legacy-source">Legacy page: form</p>
      </div>
      <dl class="meta-summary">
        <div><dt>Primary dataset</dt><dd>{{ meta.primaryDatasetId }}</dd></div>
        <div><dt>Legacy endpoint</dt><dd>{{ meta.legacyEndpoint || 'manual review required' }}</dd></div>
      </dl>
    </header>

    <form class="search-panel" @submit.prevent="actions.search()">
      <label class="search-field">
        <span>시험</span>
        <select v-model="state.searchForm.testCategory">
          <option value="">Select 시험</option>
          <option v-for="option in state.lookups.testCategory" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
      <div class="search-actions">
        <button type="submit" class="" :disabled="state.loading || state.bootstrapping">성적조회</button>
        <button type="button" class="secondary" @click="actions.openButton1Subview()" :disabled="state.loading || state.bootstrapping">과목 담당교수</button>
        <button type="button" class="secondary" @click="actions.openScholarshipPopup()" :disabled="state.loading || state.bootstrapping">장학금대상</button>
      </div>
      <p v-if="state.error" class="error-banner">{{ state.error }}</p>
    </form>

    <section class="result-panel">
      <div class="result-toolbar">
        <h2>Result grid</h2>
        <span>{{ state.rows.length }} rows</span>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
            <th>학생번호</th>
            <th>학생명</th>
            <th>평균점수</th>
            <th>등수</th>
            <th>석차</th>
            </tr>
          </thead>
          <tbody v-if="state.rows.length > 0">
            <tr v-for="(row, rowIndex) in state.rows" :key="row.stuno ?? rowIndex">
            <td>{{ row.stuno ?? '-' }}</td>
            <td>{{ row.stuname ?? '-' }}</td>
            <td>{{ row.avgscore ?? '-' }}</td>
            <td>{{ row.rank ?? '-' }}</td>
            <td>{{ row.denseRank ?? '-' }}</td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td :colspan="columns.length || 1" class="empty-cell">
                {{ state.loading || state.bootstrapping ? 'Loading legacy flow...' : 'No rows returned yet.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside v-if="meta.relatedPages.length > 0" class="related-pages">
      <h2>Related screens</h2>
      <ul><li><strong>과목 담당교수</strong>: scurl (unresolved)</li></ul>
      <ul><li><strong>장학금대상</strong>: scholarship (resolved)</li></ul>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { useFormPage } from '../../composables/useFormPage';
const { state, actions, columns, meta } = useFormPage();
</script>

<style scoped>
.page-shell { display: grid; gap: 1.5rem; }
.page-header, .search-panel, .result-panel, .related-pages { border: 1px solid #d7dce5; border-radius: 14px; padding: 1rem 1.25rem; background: #fff; }
.page-header { display: flex; justify-content: space-between; gap: 1rem; align-items: start; }
.eyebrow { margin: 0 0 0.25rem; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: #5b6472; }
.legacy-source, .empty-note, .empty-cell { color: #5b6472; }
.meta-summary { display: grid; gap: 0.75rem; margin: 0; }
.meta-summary dt { font-size: 0.75rem; color: #5b6472; }
.meta-summary dd { margin: 0.15rem 0 0; font-weight: 600; }
.search-panel { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; align-items: end; }
.search-field { display: grid; gap: 0.4rem; }
.search-field span { font-weight: 600; }
.search-field input, .search-field select { min-height: 40px; border: 1px solid #c9d2df; border-radius: 10px; padding: 0.65rem 0.8rem; }
.search-actions { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }
.search-actions button { min-height: 40px; border: none; border-radius: 10px; padding: 0.7rem 1rem; background: #0f4c81; color: #fff; cursor: pointer; }
.search-actions button.secondary { background: #5b6472; }
.error-banner { margin: 0; color: #b42318; }
.result-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.75rem; border-bottom: 1px solid #e4e9f0; text-align: left; }
th { background: #f7f9fc; font-size: 0.9rem; }
.related-pages ul { margin: 0; padding-left: 1.1rem; }
</style>
