<template>
  <section class="page-shell">
    <header>
      <h1>New Form</h1>
      <p>Legacy page: form</p>
    </header>

    <form @submit.prevent="actions.search()">
      <!-- TODO: replace with real search controls -->
      <pre>{{ state.searchForm }}</pre>
      <button type="submit">Search</button>
    </form>

    <section>
      <!-- TODO: replace with real grid/detail blocks -->
      <pre>{{ state.rows }}</pre>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useFormPage } from '../../composables/useFormPage';

const { state, actions } = useFormPage();
</script>
