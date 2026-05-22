<script lang="tsx">
  import { defineComponent, ref, unref } from 'vue';
  import AppSearchModal from './AppSearchModal.vue';
  import { useI18n } from '/@/hooks/web/useI18n';

  export default defineComponent({
    name: 'AppSearch',
    setup() {
      const showModal = ref(false);
      const { t } = useI18n();

      function changeModal(show: boolean) {
        showModal.value = show;
      }

      return () => {
        return (
          <div class="app-search-trigger" title={t('common.searchText')} onClick={changeModal.bind(null, true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <AppSearchModal onClose={changeModal.bind(null, false)} visible={unref(showModal)} />
          </div>
        );
      };
    },
  });
</script>

<style lang="less">
  .app-search-trigger {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    cursor: pointer;
    color: var(--ink-600);
    border-radius: 9px;
    transition: background-color var(--fast), color var(--fast);

    &:hover {
      background: var(--surface-2);
      color: var(--ink-900);
    }

    svg {
      width: 17px;
      height: 17px;
    }
  }
</style>
