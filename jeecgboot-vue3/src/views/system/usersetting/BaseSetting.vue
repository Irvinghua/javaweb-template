<!--
  UI Redesign: 按 profile.html 设计稿重做，三张卡片：
    1) .profile-hero —— 头像 + 姓名 + 标签 + 使用天数 / 上次登录
    2) .info-section —— 详细资料 + 联系信息 双栏 + 底部编辑按钮
    3) .sign-section —— 个性签名（上传 + 开启状态）
  业务逻辑（getUserData / updateAvatar / editRealName / openEditModal / 上传 / 开关）保持不变
-->
<template>
  <div :class="[`${prefixCls}`, 'base-setting-redesign']">
    <!-- ===== Hero ===== -->
    <div class="card profile-hero">
      <div class="avatar-xl">
        <CropperAvatar
          :uploadApi="uploadImg"
          :showBtn="false"
          :value="avatar"
          :btnProps="{ preIcon: 'ant-design:cloud-upload-outlined' }"
          @change="updateAvatar"
          width="84"
        />
      </div>
      <div class="hero-meta">
        <div class="hero-name">
          <template v-if="!isEdit">
            <span class="hero-name__text">{{ userInfo.realname }}</span>
            <a-tooltip content="编辑姓名">
              <button class="icon-edit" @click="editHandleClick" aria-label="编辑姓名">
                <Icon icon="ant-design:edit-outlined" :size="13" />
              </button>
            </a-tooltip>
          </template>
          <template v-else>
            <a-input ref="accountNameEdit" :maxlength="100" v-model:value="userInfo.realname" @blur="editRealName" style="max-width: 220px" />
          </template>
        </div>
        <div class="hero-sub" v-if="userInfo.createTimeText">
          已使用本平台 <b>{{ userInfo.createTimeText }}</b>
        </div>
      </div>
    </div>

    <!-- ===== 详细资料 + 联系信息 ===== -->
    <div class="card info-section">
      <div class="info-grid-2">
        <div>
          <div class="block-title">详细资料 <span class="sub">基础个人信息</span></div>
          <div class="kv-row">
            <span class="k">生日</span>
            <span class="v" :class="{ empty: !userInfo.birthday || userInfo.birthday === '未填写' }">{{ userInfo.birthday || '未填写' }}</span>
          </div>
          <div class="kv-row">
            <span class="k">性别</span>
            <span class="v" :class="{ empty: !userInfo.sexText }">{{ userInfo.sexText || '未填写' }}</span>
          </div>
          <div class="kv-row last">
            <span class="k">职位</span>
            <span class="v" :class="{ empty: !userInfo.postText }">{{ userInfo.postText || '未填写' }}</span>
          </div>
        </div>
        <div>
          <div class="block-title">联系信息 <span class="sub">便于他人联系到您</span></div>
          <div class="kv-row">
            <span class="k">邮箱</span>
            <span class="v" :class="{ empty: !userInfo.email }">{{ userInfo.email || '未填写' }}</span>
          </div>
          <div class="kv-row last">
            <span class="k">手机</span>
            <span class="v" :class="{ empty: !userInfo.phone }">{{ userInfo.phone || '未填写' }}</span>
          </div>
        </div>
      </div>
      <div class="section-foot">
        <a-button type="primary" ghost @click="openEditModal">
          <template #icon><Icon icon="ant-design:edit-outlined" /></template>
          编辑资料
        </a-button>
      </div>
    </div>

    <!-- ===== 个性签名 ===== -->
    <div class="card sign-section">
      <div class="block-title">个性签名 <span class="sub">用于工单、合同等场景的电子签名</span></div>
      <div class="sign-row">
        <label>签名图片</label>
        <div class="sign-row__body">
          <a-upload
            accept="jpg,jpeg,png"
            :max-count="1"
            :multiple="false"
            name="file"
            :headers="uploadHeader"
            :action="uploadUrl"
            v-model:fileList="uploadFileList"
            @beforeUpload="beforeUpload"
            @change="handleChange"
            list-type="picture-card"
            @preview="handlePreview"
            class="sign-upload"
          >
            <div v-if="uploadVisible" class="uz-inner">
              <UploadOutlined />
              <div class="ant-upload-text">上传</div>
            </div>
          </a-upload>
          <a-modal :width="500" :open="previewVisible" :footer="null" @cancel="handleCancel">
            <img alt="example" style="width: 100%" :src="previewImage" />
          </a-modal>
          <div class="sign-tips">
            <div>建议尺寸 <b>200×80</b>，大小不超过 1M，格式为 PNG 或 JPEG</div>
            <div>方法一：手写后扫描成图片上传</div>
            <div>方法二：使用在线生成工具 <a href="http://www.diyiziti.com/qianming" target="_blank">在线生成签名</a></div>
          </div>
        </div>
      </div>
      <div class="sign-row sign-row--switch">
        <label>开启状态</label>
        <div class="sign-row__body">
          <a-switch v-model:checked="userInfo.signEnable" :checkedValue="1" :unCheckedValue="0" @change="handleEnableSignChange" />
          <span class="sign-row__hint">开启后，签名将自动加载到流程审批等场景</span>
        </div>
      </div>
    </div>
  </div>
  <UserAccountModal @register="registerModal" @success="getUserDetail"></UserAccountModal>
</template>
<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { CollapseContainer } from '/@/components/Container';
import { CropperAvatar } from '/@/components/Cropper';
import { useMessage } from '/@/hooks/web/useMessage';
import headerImg from '/@/assets/images/header.jpg';
import { defHttp } from '/@/utils/http/axios';
import { useUserStore } from '/@/store/modules/user';
import { uploadImg } from '/@/api/sys/upload';
import { getFileAccessHttpUrl, getRandom } from '/@/utils/common/compUtils';
import dayjs from 'dayjs';
import { ajaxGetDictItems, getDictItemsByCode, initDictOptions } from '/@/utils/dict';
import { userEdit, getUserData, queryNameByCodes } from './UserSetting.api';
import UserAccountModal from './commponents/UserAccountModal.vue';
import { useModal } from '/@/components/Modal';
import { cloneDeep } from 'lodash-es';
import { useDesign } from '/@/hooks/web/useDesign';
import { getToken } from "@/utils/auth";
import { uploadUrl } from "@/api/common/api";
import { UploadOutlined } from "@ant-design/icons-vue";

//TODO 当字典租户隔离时，数据会查不到，默认一个
const sexOption = getDictItemsByCode("sex") || [{text:'男',value:'1'},{text:'女',value:'2'}];
const { createMessage } = useMessage();
const userStore = useUserStore();
  const { prefixCls } = useDesign('j-base-setting-container');
//是否编辑
const isEdit = ref<boolean>(false);
//用户信息
const userInfo = ref<any>({});
//编辑时input触发事件
const accountNameEdit = ref();
const [registerModal, { openModal }] = useModal();
//头像动态计算
const avatar = computed(() => {
  return getFileAccessHttpUrl(userInfo.value.avatar) || headerImg;
});
//headers
const uploadHeader = computed(() => {
  let headers = {};
  headers['X-Access-Token'] = getToken();
  return headers;
});
const { createMessage: $message } = useMessage();
//上传列表
const uploadFileList = ref<any>([]);
//计算是否可以继续上传
const uploadVisible = computed(() => {
  if(!uploadFileList){
    return true;
  }
  return uploadFileList.value.length < 1;
});
//图片预览
const previewVisible = ref<boolean>(false);
//图片预览路径
const previewImage = ref<string>('');

/**
 * 更新用户头像
 */
function updateAvatar(src: string, data: string) {
  const userinfo = userStore.getUserInfo;
  userinfo.avatar = data;
  userStore.setUserInfo(userinfo);
  if (data) {
    updateUserInfo({ avatar: data, id: userinfo.id });
  }
}

/**
 * 更新用户信息
 * @params 参数
 */
function updateUserInfo(params) {
  userEdit(params).then((res) => {
    if (!res.success) {
      createMessage.warn(res.message);
    }
  });
}

/**
 * 编辑按钮点击事件
 */
function editHandleClick() {
  isEdit.value = true;
  setTimeout(() => {
    accountNameEdit.value.focus();
  }, 100);
}

/**
 * 修改真实姓名
 */
function editRealName() {
  if (userInfo.value.realname) {
    updateUserInfo({ realname: userInfo.value.realname, id: userInfo.value.id });
    userStore.setUserInfo(userInfo.value);
  } else {
    createMessage.warn("请输入姓名");
  }
  isEdit.value = false;
}

/**
 * 获取生日信息
 */
function getBirthDay(val) {
  if (val) {
    return dayjs(val).format("YYYY-MM-DD");
  } else {
    return "未填写";
  }
}

/**
 * 获取性别
 * @param val
 */
function getSex(val) {
  let findOption = sexOption.find(item => parseInt(item.value) === val);
  let sex = "未填写";
  if (findOption) {
    sex = findOption.text;
  }
  return sex;
}

/**
 * 打开编辑弹窗
 */
function openEditModal() {
  let value = cloneDeep(userInfo.value);
  openModal(true, {
    record: value
  });
}

/**
 * 获取用户信息
 */
function getUserDetail() {
  uploadFileList.value = [];
  getUserData().then((async res => {
    if (res.success) {
      if (res.result) {
        res.result.sexText = getSex(res.result.sex);
        res.result.birthday = getBirthDay(res.result.birthday);
        res.result.createTimeText = getDiffDay(res.result.createTime);
        userInfo.value = res.result;
        if(userInfo.value.sign){
          let sign = userInfo.value.sign;
          let url = getFileAccessHttpUrl(sign);
          uploadFileList.value.push({
            uid: getRandom(10),
            name: getFileName(sign),
            status: 'done',
            url: url,
            response: {
              status: 'history',
              message: sign,
            },
          })
        }
      } else {
        userInfo.value = {};
      }
    }
  }));
}

/**
 * 获取使用时间
 * @param date
 */
function getDiffDay(date) {
  // 计算两个日期之间的天数差值
  let totalDays, diffDate
  let createDate = Date.parse(date);
  let nowDate = new Date().getTime();
  // 将两个日期都转换为毫秒格式，然后做差
  diffDate = Math.abs(nowDate - createDate) // 取相差毫秒数的绝对值
  totalDays = Math.floor(diffDate / (1000 * 3600 * 24)) // 向下取整
  return totalDays+" 天";
}

/**
 * 上传图片之前进行验证
 * 
 * @param file
 */
function beforeUpload({ file }) {
  const isJpgOrPng = file.type === "image/jpeg" || file.type === "image/png" || file.type === "image/jpg";
  if (!isJpgOrPng) {
    $message.error("上传文件格式只能是jpg/png");
    return false;
  }
  const isLimit = file.size / 1024 / 1024 < 1;
  if (!isLimit) {
    $message.error("上传图片大小不能超过 1MB!");
    return false;
  }
  return true;
}

/**
 * 上传成功事件
 */
function handleChange({ file, fileList }) {
  if (file.status === 'error') {
    createMessage.error(`${file.name} 上传失败.`);
  }
  if (file.status === 'done' && file.response.success === false) {
    const failIndex = uploadFileList.value.findIndex((item) => item.uid === file.uid);
    if (failIndex != -1) {
      uploadFileList.value.splice(failIndex, 1);
    }
    createMessage.warning(file.response.message);
    return;
  }
  if (file.status != 'uploading') {
    fileList.forEach((file) => {
      if (file.status === 'done') {
        //上传成功事件
        uploadSuccess(file.response.message);
      }
    });
    if (file.status === 'removed') {
      handleDelete();
    }
  }
}

/**
 * 移除
 */
function handleDelete() {
  updateUser({ sign: "", id: userInfo.value.id },"删除个性签名成功")
}

/**
 * 上传成功事件
 * @param url
 */
function uploadSuccess(url) {
   updateUser({ sign: url, id: userInfo.value.id },"上传个性签名成功")
}

function updateUser(params,message) {
  userEdit(params).then((res) => {
    if(res.success){
      createMessage.success(message);
    }
  });
}

/**
 * 图片预览
 * @param file
 */
function handlePreview(file) {
  previewImage.value = file.url || file.thumbUrl;
  previewVisible.value = true;
}

/**
 * 获取文件名
 * @param path
 */
function getFileName(path) {
  if (path.lastIndexOf('\\') >= 0) {
    let reg = new RegExp('\\\\', 'g');
    path = path.replace(reg, '/');
  }
  return path.substring(path.lastIndexOf('/') + 1);
}

/**
 * 图片预览关闭
 */
function handleCancel() {
  previewVisible.value = false;
}

/**
 * 个性签名开启状态更新
 */
function handleEnableSignChange() {
  updateUser({ signEnable: userInfo.value.signEnable, id: userInfo.value.id },"修改成功")
}

onMounted(async () => {
  getUserDetail();
});
</script>

<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: profile.html .profile-hero / .info-section / .sign-section
  // ----------------------------------------------------
  .base-setting-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card {
    background: var(--surface, #fff);
    border-radius: var(--radius-card, 18px);
    box-shadow: var(--shadow-card, 0 2px 12px rgba(15, 23, 42, 0.05));
  }

  // ---------- Hero ----------
  .profile-hero {
    padding: 24px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .avatar-xl {
    width: 84px;
    height: 84px;
    flex-shrink: 0;
    border-radius: 50%;
    overflow: hidden;
    background: linear-gradient(135deg, #7e8dff, var(--accent, #5b6cff));
    border: 3px solid #fff;
    box-shadow: 0 6px 18px rgba(91, 108, 255, 0.28);
    display: grid;
    place-items: center;

    :deep(.ant-upload),
    :deep(.cropper-img) {
      border-radius: 50%;
    }
  }

  .hero-meta {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .hero-name {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 700;
    color: var(--ink-900);

    .icon-edit {
      width: 26px;
      height: 26px;
      border-radius: 7px;
      border: 1px solid var(--line);
      background: var(--surface, #fff);
      display: grid;
      place-items: center;
      color: var(--ink-500);
      cursor: pointer;
      transition: background-color 0.15s, color 0.15s;
      padding: 0;

      &:hover {
        background: var(--surface-2, #f7f8fb);
        color: var(--accent-600);
      }
    }
  }

  .hero-sub {
    font-size: 13px;
    color: var(--ink-500);

    b {
      color: var(--accent-600);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      padding: 0 2px;
    }
  }

  // ---------- 区块标题 ----------
  .block-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--ink-900);
    margin-bottom: 4px;

    &::before {
      content: '';
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent, #5b6cff);
    }

    .sub {
      font-size: 12px;
      color: var(--ink-400);
      font-weight: 400;
      margin-left: 4px;
    }
  }

  // ---------- 详细资料 / 联系信息 双栏 ----------
  .info-section {
    padding: 22px 28px;
  }

  .info-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0 56px;
  }

  .kv-row {
    display: grid;
    grid-template-columns: 88px 1fr;
    align-items: center;
    gap: 12px;
    padding: 13px 0;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    &.last {
      border-bottom: 0;
    }

    .k {
      color: var(--ink-500);
      font-size: 13px;
    }

    .v {
      color: var(--ink-900);
      font-size: 14px;
      font-weight: 500;

      &.empty {
        color: var(--ink-400);
        font-weight: 400;
      }
    }
  }

  .section-foot {
    margin-top: 12px;
    padding-top: 14px;
    border-top: 1px dashed var(--line, rgba(15, 23, 42, 0.07));
    display: flex;
    justify-content: flex-end;
  }

  // ---------- 个性签名 ----------
  .sign-section {
    padding: 22px 28px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .sign-row {
    display: grid;
    grid-template-columns: 88px 1fr;
    align-items: start;
    gap: 16px;

    &--switch {
      align-items: center;
    }

    > label {
      color: var(--ink-500);
      font-size: 13px;
      padding-top: 10px;
    }

    &--switch > label {
      padding-top: 0;
    }

    &__body {
      display: flex;
      gap: 18px;
      align-items: flex-start;
      flex-wrap: wrap;
    }

    &--switch .sign-row__body {
      align-items: center;
      gap: 12px;
    }

    &__hint {
      font-size: 13px;
      color: var(--ink-500);
    }
  }

  .sign-tips {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12.5px;
    color: var(--ink-500);
    line-height: 1.7;

    b {
      color: var(--ink-900);
      font-weight: 600;
    }

    a {
      color: var(--accent-600);
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  // 签名上传缩略图尺寸 200×80
  :deep(.sign-upload) {
    .ant-upload.ant-upload-select,
    .ant-upload-list-item-container {
      width: 200px !important;
      height: 80px !important;
    }
    .ant-upload-list-item-thumbnail .ant-upload-list-item-image {
      object-fit: cover !important;
    }
  }

  .uz-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--ink-500);

    .anticon {
      font-size: 18px;
    }
  }
</style>
