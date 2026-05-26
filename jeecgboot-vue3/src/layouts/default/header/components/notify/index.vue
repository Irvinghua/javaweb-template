<template>
  <div :class="prefixCls">
    <Popover
      v-model:open="popoverVisible"
      trigger="click"
      placement="bottomRight"
      :overlayClassName="`${prefixCls}__overlay`"
      :overlayStyle="{ padding: 0 }"
    >
      <template #content>
        <div class="notif-pop">
          <!-- Header -->
          <div class="notif-pop__head">
            <span class="notif-pop__title">通知</span>
            <span class="notif-pop__spacer"></span>
            <span class="notif-pop__action" @click="handleReadAll">全部已读</span>
          </div>

          <!-- Message list -->
          <div class="notif-pop__list">
            <!-- Loading -->
            <div v-if="listLoading" class="notif-pop__empty">
              <Spin size="small" />
            </div>

            <!-- Empty state -->
            <div v-else-if="notifItems.length === 0" class="notif-pop__empty">
              <BellOutlined style="font-size: 24px; opacity: 0.25; margin-bottom: 6px;" />
              <span>暂无消息</span>
            </div>

            <!-- Items -->
            <template v-else>
              <div
                v-for="item in notifItems"
                :key="item.id"
                class="notif-item"
                :class="{ 'notif-item--unread': item.readFlag === '0' }"
                @click="handleItemClick(item)"
              >
                <!-- Icon chip -->
                <div class="notif-item__ico" :class="getIconClass(item)">
                  <!-- info (default) -->
                  <svg v-if="getIconType(item) === 'info'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  <!-- warn -->
                  <svg v-else-if="getIconType(item) === 'warn'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <!-- good / check -->
                  <svg v-else-if="getIconType(item) === 'good'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>

                <!-- Body -->
                <div class="notif-item__content">
                  <div class="notif-item__body">
                    <span class="notif-item__title-text">{{ item.titile || item.title }}</span>
                    <span v-if="item.msgAbstract" class="notif-item__desc">{{ item.msgAbstract }}</span>
                  </div>
                  <div class="notif-item__time">{{ formatTime(item.sendTime) }}</div>
                </div>
              </div>
            </template>
          </div>

          <!-- Footer -->
          <div class="notif-pop__foot">
            <button class="notif-pop__foot-btn" @click="handleViewAll">查看全部</button>
            <button class="notif-pop__foot-btn" @click="handleMessageCenter">消息中心</button>
          </div>
        </div>
      </template>

      <!-- Bell trigger -->
      <Badge :count="messageCount" :overflowCount="9" :offset="[-4, 18]" :numberStyle="numberStyle">
        <BellOutlined />
      </Badge>
    </Popover>

    <DynamicNotice ref="dynamicNoticeRef" v-bind="dynamicNoticeProps" />
    <DetailModal @register="registerDetail" />

    <sys-message-modal @register="registerMessageModal" @refresh="reloadCount" :messageCount="messageCount"></sys-message-modal>
    <!--  修改密码弹窗  -->
    <ChangePasswordModal @register="changePwdModal"></ChangePasswordModal>
  </div>
</template>

<script lang="ts">
  import { computed, defineComponent, ref, unref, reactive, onMounted, getCurrentInstance } from 'vue';
  import { Popover, Tabs, Badge, Spin } from 'ant-design-vue';
  import { BellOutlined } from '@ant-design/icons-vue';
  import { getUnreadMessageCount, editCementSend, clearAllUnReadMessage, listCementByUser } from './notify.api';
  import NoticeList from './NoticeList.vue';
  import DetailModal from '/@/views/monitor/mynews/DetailModal.vue';
  import DynamicNotice from '/@/views/monitor/mynews/DynamicNotice.vue';
  import { useModal } from '/@/components/Modal';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useGlobSetting } from '/@/hooks/setting';
  import { useUserStore } from '/@/store/modules/user';
  import { connectWebSocket, onWebSocket } from '/@/hooks/web/useWebSocket';
  import { readAllMsg } from '/@/views/monitor/mynews/mynews.api';
  import { getToken } from '/@/utils/auth';
  import md5 from 'crypto-js/md5';
  import { useRouter } from 'vue-router';

  import SysMessageModal from '/@/views/system/message/components/SysMessageModal.vue'
  import ChangePasswordModal from './ChangePasswordModal.vue'
  import { ElectronEnum } from '/@/enums/jeecgEnum';
  import { defHttp } from "@/utils/http/axios";

  export default defineComponent({
    components: {
      Popover,
      BellOutlined,
      Tabs,
      TabPane: Tabs.TabPane,
      Badge,
      Spin,
      NoticeList,
      DetailModal,
      DynamicNotice,
      SysMessageModal,
      ChangePasswordModal,
    },
    setup() {
      const { prefixCls } = useDesign('header-notify');
      const instance: any = getCurrentInstance();
      const userStore = useUserStore();
      const glob = useGlobSetting();
      const dynamicNoticeProps = reactive({ path: '', formData: {} });
      const [registerDetail, detailModal] = useModal();
      const router = useRouter();

      const chatRef = ref();

      const [registerMessageModal, { openModal: openMessageModal }] = useModal();
      const [registerBookModal, { openModal: openBookModal }] = useModal();
      const [changePwdModal, { openModal: openPwdModal }] = useModal();

      // 通知消息类型
      const noticeType = ref<string>('system');
      // 未读消息数
      const unReadNum = ref<any>({});
      // 消息列表
      const notifItems = ref<any[]>([]);
      const listLoading = ref<boolean>(false);

      function clickBadge(value) {
        openMessageModal(true, { noticeType: value });
      }

      const popoverVisible = ref<boolean>(false);

      onMounted(() => {
        initWebSocket();
      });

      const messageCount = ref<number>(0);

      function mapAnnouncement(item) {
        return {
          ...item,
          title: item.titile,
          description: item.msgAbstract,
          datetime: item.sendTime,
        };
      }

      // 获取系统消息 (unread count + recent list)
      async function loadData() {
        try {
          let msgCount = await getUnreadMessageCount();
          unReadNum.value = msgCount;
          messageCount.value = msgCount.count ? msgCount.count : 0;
          if (glob.isElectronPlatform) {
            window[ElectronEnum.ELECTRON_API].sendNotifyFlash(messageCount.value);
            window[ElectronEnum.ELECTRON_API].trayFlash();
          }
        } catch (e) {
          console.warn('系统消息通知异常：', e);
        }
      }

      // 加载消息列表 (popover打开时调用)
      async function loadNotifList() {
        listLoading.value = true;
        try {
          const res = await listCementByUser({ pageSize: 5, pageNo: 1 });
          // API 返回: { records: [...] } 或 { anntMsgList: [...], sysMsgList: [...] }
          if (res && Array.isArray(res.records)) {
            notifItems.value = res.records;
          } else if (res && Array.isArray(res.anntMsgList)) {
            notifItems.value = res.anntMsgList;
          } else if (Array.isArray(res)) {
            notifItems.value = res;
          } else {
            notifItems.value = [];
          }
        } catch (e) {
          console.warn('加载消息列表异常：', e);
          notifItems.value = [];
        } finally {
          listLoading.value = false;
        }
      }

      loadData();

      // Watch popover open to lazy-load message list
      function onPopoverVisibleChange(visible: boolean) {
        if (visible) {
          loadNotifList();
        }
      }

      // Override popoverVisible to also trigger list load
      const popoverVisibleProxy = computed({
        get: () => popoverVisible.value,
        set: (val: boolean) => {
          popoverVisible.value = val;
          onPopoverVisibleChange(val);
        },
      });

      function onNoticeClick(record) {
        try {
          editCementSend(record.id);
          loadData();
        } catch (e) {
          console.error(e);
        }
        if (record.openType === 'component') {
          dynamicNoticeProps.path = record.openPage;
          dynamicNoticeProps.formData = { id: record.busId };
          instance.refs.dynamicNoticeRef?.detail(record.openPage);
        } else {
          detailModal.openModal(true, {
            record,
            isUpdate: true,
          });
        }
        popoverVisible.value = false;
      }

      function handleItemClick(item: any) {
        onNoticeClick(item);
      }

      // 全部已读 (直接调用，无弹框确认)
      function handleReadAll() {
        clearAllUnReadMessage().then((res: any) => {
          if (res && res.success) {
            loadData();
            loadNotifList();
          }
        });
      }

      // 查看全部 → 跳转消息页面
      function handleViewAll() {
        popoverVisible.value = false;
        router.push('/monitor/mynews');
      }

      // 消息中心 → 打开完整弹窗
      function handleMessageCenter() {
        popoverVisible.value = false;
        clickBadge('');
      }

      // 初始化 WebSocket
      function initWebSocket() {
        let token = getToken();
        let wsClientId = md5(token);
        let userId = unref(userStore.getUserInfo).id + "_" + wsClientId;
        let url = glob.domainUrl?.replace('https://', 'wss://').replace('http://', 'ws://') + '/websocket/' + userId;
        connectWebSocket(url);
        onWebSocket(onWebSocketMessage);
      }

      function onWebSocketMessage(data) {
        if (data.cmd === 'topic' || data.cmd === 'user') {
          if (data.noticeType) {
            noticeType.value = data.noticeType;
          }
          setTimeout(() => {
            notification(data);
            loadData();
          }, 1000);
        }
      }

      // 桌面应用通知
      function notification(data) {
        if (glob.isElectronPlatform && (data.noticeType || data.cmd == 'email')) {
          let title = '';
          let msgTxt = '';
          let path = '';
          if (data.noticeType === 'flow') {
            title = '流程';
            path = '/task/myHandleTaskInfo';
          } else if (data.noticeType === 'file') {
            title = '文件';
            path = '/file';
          } else if (data.noticeType === 'plan') {
            title = '日程';
            path = '/plan/view';
          } else if (data.noticeType === 'system') {
            title = '系统';
            path = '/monitor/mynews';
          } else if (data.noticeType === 'meeting') {
            title = '会议';
            path = '/meeting';
          } else if (data.cmd === 'email') {
            title = '邮件';
            path = '/eoa/email?type=inbox';
          }
          msgTxt = data.msgTxt ?? '查看详情';
          window[ElectronEnum.ELECTRON_API].sendNotification(`有新的${title}消息`, msgTxt, path);
        }
      }

      // 清空消息 (legacy handler kept for compatibility)
      function onEmptyNotify() {
        popoverVisible.value = false;
        readAllMsg({}, loadData);
      }

      async function reloadCount(id) {
        try {
          await editCementSend(id);
          await loadData();
        } catch (e) {
          console.error(e);
        }
      }

      function getSystemUnreadNum() {}

      function clickAddressBook() {
        openBookModal(true, {});
      }

      function clearAllUnMessage() {
        clearAllUnReadMessage().then((res: any) => {
          if (res && res.success) {
            loadData();
          }
        });
      }

      // --- Icon helpers ---
      function getIconType(item: any): 'info' | 'warn' | 'good' {
        const priority = (item.priority || '').toUpperCase();
        const msgCategory = (item.msgCategory || '').toString();
        if (priority === 'H' || msgCategory === '2') return 'warn';
        if (priority === 'L' || msgCategory === '3') return 'good';
        return 'info';
      }

      function getIconClass(item: any): string {
        const t = getIconType(item);
        if (t === 'warn') return 'notif-item__ico--warn';
        if (t === 'good') return 'notif-item__ico--good';
        return 'notif-item__ico--info';
      }

      // Format time as relative string
      function formatTime(timeStr: string | undefined): string {
        if (!timeStr) return '';
        const date = new Date(timeStr.replace(/-/g, '/'));
        if (isNaN(date.getTime())) return timeStr;
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMin = Math.floor(diffMs / 60000);
        if (diffMin < 1) return '刚刚';
        if (diffMin < 60) return `${diffMin} 分钟前`;
        const diffH = Math.floor(diffMin / 60);
        if (diffH < 24) return `${diffH} 小时前`;
        const diffD = Math.floor(diffH / 24);
        if (diffD < 30) return `${diffD} 天前`;
        return timeStr.slice(0, 10);
      }

      // verifyIzDefaultPwd
      verifyIzDefaultPwd();

      function verifyIzDefaultPwd() {
        defHttp.get({ url: "/sys/user/verifyIzDefaultPwd" }, { isTransformResponse: false }).then((res) => {
          if (res.success) {
            if (res.message.indexOf('yes') != -1) {
              openPwdModal(true, {
                oldPassword: res.message.split("_")[1],
              });
            }
          }
        });
      }

      return {
        prefixCls,
        clickBadge,
        registerMessageModal,
        reloadCount,
        onNoticeClick,
        onEmptyNotify,
        numberStyle: {},
        popoverVisible: popoverVisibleProxy,
        registerDetail,
        dynamicNoticeProps,
        chatRef,
        getSystemUnreadNum,
        clickAddressBook,
        registerBookModal,
        messageCount,
        clearAllUnMessage,
        changePwdModal,
        // new
        notifItems,
        listLoading,
        handleItemClick,
        handleReadAll,
        handleViewAll,
        handleMessageCenter,
        getIconType,
        getIconClass,
        formatTime,
      };
    },
  });
</script>

<style lang="less">
  //noinspection LessUnresolvedVariable
  @prefix-cls: ~'@{namespace}-header-notify';

  .@{prefix-cls} {
    &__overlay {
      .ant-popover-inner {
        padding: 0 !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-pop) !important;
        border: 1px solid var(--line) !important;
        overflow: hidden;
      }

      .ant-popover-inner-content {
        padding: 0 !important;
      }
    }

    .ant-badge {
      font-size: 18px;

      .ant-badge-count {
        @badget-size: 16px;
        width: @badget-size;
        height: @badget-size;
        min-width: @badget-size;
        line-height: @badget-size;
        padding: 0;

        .ant-scroll-number-only > p.ant-scroll-number-only-unit {
          font-size: 14px;
          height: @badget-size;
        }
      }

      .ant-badge-multiple-words {
        padding: 0 0 0 2px;
        font-size: 12px;
      }

      svg {
        width: 0.9em;
      }
    }
  }
</style>

<style lang="less" scoped>
  /* Notification Popover Panel */
  .notif-pop {
    width: 340px;
    background: var(--surface);
    border-radius: 12px;
    overflow: hidden;
  }

  .notif-pop__head {
    display: flex;
    align-items: center;
    padding: 12px 14px 10px;
    font-size: 13px;
    font-weight: 600;
    color: var(--ink-900);
  }

  .notif-pop__spacer {
    flex: 1;
  }

  .notif-pop__action {
    font-size: 12px;
    color: var(--accent);
    font-weight: 500;
    cursor: pointer;
    transition: opacity var(--fast);

    &:hover {
      opacity: 0.75;
    }
  }

  .notif-pop__list {
    max-height: 360px;
    overflow-y: auto;
    padding: 0 6px;

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--line-strong);
      border-radius: 4px;
    }
  }

  .notif-pop__empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 28px 0;
    font-size: 12px;
    color: var(--ink-400);
    gap: 4px;
  }

  /* Individual notification item */
  .notif-item {
    display: flex;
    gap: 10px;
    padding: 10px 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color var(--fast);

    &:hover {
      background: var(--surface-2);
    }

    &--unread {
      background: var(--accent-50);

      &:hover {
        background: var(--accent-100);
      }
    }
  }

  .notif-item__ico {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    flex-shrink: 0;

    svg {
      width: 14px;
      height: 14px;
    }

    &--info {
      background: var(--accent-50);
      color: var(--accent);
    }

    &--warn {
      background: var(--warn-bg);
      color: var(--warn);
    }

    &--good {
      background: var(--good-bg);
      color: var(--good);
    }
  }

  .notif-item__content {
    flex: 1;
    min-width: 0;
  }

  .notif-item__body {
    font-size: 12.5px;
    color: var(--ink-700);
    line-height: 1.45;
  }

  .notif-item__title-text {
    font-weight: 600;
    color: var(--ink-900);
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .notif-item__desc {
    display: block;
    font-size: 12px;
    color: var(--ink-600);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-top: 1px;
  }

  .notif-item__time {
    font-size: 11px;
    color: var(--ink-400);
    margin-top: 3px;
  }

  /* Footer */
  .notif-pop__foot {
    padding: 6px;
    border-top: 1px solid var(--line);
    display: flex;
    gap: 4px;
  }

  .notif-pop__foot-btn {
    flex: 1;
    padding: 7px;
    background: transparent;
    border: 0;
    border-radius: 7px;
    color: var(--ink-700);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
    transition: background-color var(--fast);
    text-align: center;

    &:hover {
      background: var(--surface-2);
      color: var(--ink-900);
    }
  }
</style>
