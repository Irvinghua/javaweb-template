<template>
  <template v-if="getShow">
    <LoginFormTitle />

    <!-- 步骤指示器 -->
    <div class="fpf-steps">
      <div
        v-for="(step, i) in steps"
        :key="i"
        class="fpf-step"
        :class="{
          'fpf-step--active': currentTab === i,
          'fpf-step--done': currentTab > i,
        }"
      >
        <div class="fpf-step-dot">
          <svg v-if="currentTab > i" class="fpf-step-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="fpf-step-label">{{ step }}</span>
        <div v-if="i < steps.length - 1" class="fpf-step-line"></div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="fpf-step-content">
      <step1 v-if="currentTab === 0" @nextStep="nextStep" />
      <step2 v-if="currentTab === 1" @nextStep="nextStep" @prevStep="prevStep" :accountInfo="accountInfo" />
      <step3 v-if="currentTab === 2" @prevStep="prevStep" @finish="finish" />
    </div>
  </template>
</template>

<script lang="ts" setup>
  import { reactive, ref, computed, unref } from 'vue';
  import LoginFormTitle from './LoginFormTitle.vue';
  import { useLoginState, useFormRules, LoginStateEnum } from './useLogin';
  import step1 from '../forget-password/step1.vue';
  import step2 from '../forget-password/step2.vue';
  import step3 from '../forget-password/step3.vue';

  const { handleBackLogin, getLoginState } = useLoginState();
  const { getFormRules } = useFormRules();

  const formRef = ref();
  const loading = ref(false);
  const currentTab = ref(0);
  const formData = reactive({
    account: '',
    mobile: '',
    sms: '',
  });
  const steps = ['手机验证', '更改密码', '完成'];
  const getShow = computed(() => unref(getLoginState) === LoginStateEnum.RESET_PASSWORD);
  const accountInfo = reactive({
    obj: {
      username: '',
      phone: '',
      smscode: '',
    },
  });

  /**
   * 下一步
   * @param data
   */
  function nextStep(data) {
    accountInfo.obj = data;
    if (currentTab.value < 4) {
      currentTab.value += 1;
    }
  }

  /**
   * 上一步
   * @param data
   */
  function prevStep(data) {
    accountInfo.obj = data;
    if (currentTab.value > 0) {
      currentTab.value -= 1;
    }
  }

  /**
   * 结束
   */
  function finish() {
    currentTab.value = 0;
  }
</script>

<style lang="less" scoped>
  /* 步骤指示器 */
  .fpf-steps {
    display: flex;
    align-items: flex-start;
    margin-bottom: 24px;
    gap: 0;
  }

  .fpf-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    flex: 1;

    &:last-child .fpf-step-line {
      display: none;
    }
  }

  .fpf-step-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--surface-2);
    border: 1.5px solid var(--line-strong);
    color: var(--ink-400);
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    transition:
      background-color var(--fast),
      border-color var(--fast),
      color var(--fast);
    z-index: 1;
    position: relative;

    .fpf-step--active & {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }

    .fpf-step--done & {
      background: var(--good);
      border-color: var(--good);
      color: #fff;
    }
  }

  .fpf-step-check {
    width: 14px;
    height: 14px;
  }

  .fpf-step-label {
    font-size: 11.5px;
    color: var(--ink-400);
    margin-top: 6px;
    text-align: center;
    white-space: nowrap;
    transition: color var(--fast);

    .fpf-step--active & {
      color: var(--accent);
      font-weight: 600;
    }

    .fpf-step--done & {
      color: var(--good);
    }
  }

  .fpf-step-line {
    position: absolute;
    top: 14px;
    left: 50%;
    width: 100%;
    height: 1.5px;
    background: var(--line);
    z-index: 0;
    transition: background-color var(--fast);

    .fpf-step--done & {
      background: var(--good);
    }
  }

  .fpf-step-content {
    padding: 4px 0;
  }
</style>
