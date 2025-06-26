<template>
  <Toast />
  <Menubar :model="items">
    <template #start>
      <span style="margin-right: 15px; margin-left: 5px">2FAUTH</span>
    </template>
    <template #item="{ item, props, hasSubmenu, root }">
      <a v-ripple class="flex items-center" v-bind="props.action">
        <span v-if="item.icon" :class="[item.icon, 'mr-2']" />
        <span @click="router.push(`${item.path}`)">{{ item.label }}</span>
      </a>
    </template>
    <template #end>
      <div style="display: flex; margin-right: 5px">
        <Button
          v-if="isLogin"
          style="white-space: nowrap; width: 80px"
          variant="text"
          size="small"
          severity="contrast"
        >{{ userData.username }}</Button>
        <Button
          v-if="isLogin"
          icon="pi pi-sign-out"
          label="登出"
          @click="onLogout"
          style="margin-left: 10px; white-space: nowrap; width: 80px"
          variant="text"
          size="small"
        />
        <Button
          v-if="!isLogin"
          icon="pi pi-sign-in"
          label="登录"
          @click="showLoginDialog = true"
        />
      </div>
    </template>
  </Menubar>
  <Loading class="loading" :active="loading" is-full-page=true color="#4ade80" height="25" width="55" loader="bars" />

  <Dialog
    v-model:visible="showLoginDialog"
    modal
    header="登录"
    :style="{ width: '25rem' }"
    :closable="false"
  >
    <div style="display: flex; flex-direction: column">
      <Message
        v-if="showLoginMessage"
        :severity="LoginMsgSeverity"
        style="margin-top: 5px;margin-bottom: 5px"
      >{{ LoginMsgContent }}</Message>
      <Message
        v-if="!cfg.enable_registration"
        severity="warn"
        style="margin-top: 5px"
      >管理员已关闭新用户注册</Message>
      <label for="username" style="margin-bottom: 10px; margin-top: 10px">账号名</label>
      <InputText id="username" class="flex-auto" v-model="username" variant="filled" :invalid="!username" />
      <label for="password" style="margin-bottom: 10px; margin-top: 10px">密码</label>
      <InputText id="password" class="flex-auto" v-model="password" variant="filled" type="password" :invalid="!password" />
    </div>
    <template #footer>
      <Button type="button" label="注册" v-if="cfg.enable_registration" severity="secondary" @click="showLoginDialog = false; showRegisterDialog = true;" />
      <Button type="button" label="注册" v-else disabled severity="secondary" @click="showLoginDialog = false; showRegisterDialog = true;" />
      <Button type="button" label="登录" @click="onLogin" />
    </template>
  </Dialog>

  <Dialog
    v-model:visible="showRegisterDialog"
    modal
    header="注册"
    :style="{ width: '25rem' }"
    :closable="false"
  >
    <div style="display: flex; flex-direction: column">
      <Message
        v-if="showRegMessage"
        :severity="RegMsgSeverity"
        icon="pi pi-times-circle"
        style="margin-top: 5px;margin-bottom: 5px"
      >{{ RegMsgContent }}</Message>
      <Message
        v-if="cfg.total_users === 0"
        severity="warn"
        style="margin-top: 5px"
      >当前用户注册后将自动配置为管理员账号</Message>
      <label for="username" style="margin-bottom: 10px; margin-top: 10px">账号名</label>
      <InputText id="username" class="flex-auto" v-model="username" variant="filled" :invalid="!username" />
      <label for="password" style="margin-bottom: 10px; margin-top: 10px">密码</label>
      <InputText id="password" class="flex-auto" v-model="password" variant="filled" type="password" :invalid="!password" />
      <label for="confirmPassword" style="margin-bottom: 10px; margin-top: 10px">确认密码</label>
      <InputText id="confirmPassword" class="flex-auto" v-model="Confirmpassword" variant="filled" type="password" :invalid="!(password === Confirmpassword)" />
    </div>
    <template #footer>
      <Button type="button" label="登录" severity="secondary" @click="showRegisterDialog = false; showLoginDialog = true;" />
      <Button type="button" label="注册" @click="onRegister"/>
    </template>
  </Dialog>
  <RouterView v-if="isLogin" />
</template>

<script setup>
import { ref, onMounted,provide } from "vue";
import { useToast } from "primevue/usetoast";
import { PrimeIcons } from "@primevue/core/api";
import { RouterView } from "vue-router";
import Menubar from "primevue/menubar";
import Badge from "primevue/badge";
import Dialog from "primevue/dialog";
import Toast from "primevue/toast";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Message from "primevue/message";
import Loading from 'vue-loading-overlay'
import axios from "@/utils/axios";
import { clearCookie } from "@/utils/cookie";
import router from "./router";


const items = ref([
  { key: "Home", label: "主页", icon: PrimeIcons.HOME,path: "/" },
  { key: "Config", label: "配置", icon: PrimeIcons.COG,path: "/options" },
]);

const isLogin = ref(false);
const showLoginDialog = ref(false);
const showLoginMessage = ref(false);
const LoginMsgContent = ref("");
const LoginMsgSeverity = ref("error");
const showRegMessage = ref(false);
const RegMsgContent = ref("");
const RegMsgSeverity = ref("error");
const userData = ref({ username: "" });
const username = ref("");
const password = ref("");
const Confirmpassword = ref("");
const showRegisterDialog = ref(false);
const loading = ref(false);
const cfg = ref({});

const toast = useToast();

function showLoginErrorToast(content) {
  toast.add({ severity: "error", summary: "操作异常", detail: content, life: 3000, closable: false });
}

function showLoginSuccessToast(content) {
  toast.add({ severity: "success", summary: "操作成功", detail: content, life: 3000, closable: false });
}

provide("showErrorToast",showLoginErrorToast)
provide("showSuccessToast",showLoginSuccessToast)

async function onLogin() {
  showLoginMessage.value = false;
  showRegMessage.value = false;
  LoginMsgSeverity.value = "error";
  LoginMsgContent.value = "";
  if (!username.value || !password.value) {
    showLoginMessage.value = true;
    LoginMsgSeverity.value = "error";
    LoginMsgContent.value = "账号名和密码不能为空";
    return;
  }
  try {
    const res = await axios.post("/api/user/login", { username: username.value, password: password.value }, { withCredentials: true });
    if (res.status === 200) {
      userData.value = res.data;
      isLogin.value = true;
      showLoginDialog.value = false;
      showLoginSuccessToast("登录成功");
      try {
        const res = await axios.get("/api/user/get_user", { withCredentials: true });
        if (res.status === 200) {
          userData.value = res.data.data;
          isLogin.value = true;
          showLoginDialog.value = false;
        } else {
          isLogin.value = false;
          showLoginDialog.value = true;
          showLoginErrorToast(res.data.detail || "登录状态异常，请重新登录");
        }
      } catch (e) {
        isLogin.value = false;
        showLoginDialog.value = true;
        showLoginErrorToast(e.message || "登录请求异常");
      }
    } else {
      isLogin.value = false;
      showLoginMessage.value = true;
      LoginMsgSeverity.value = "error";
      LoginMsgContent.value = res.data.message || "登录失败，请重新登录";
    }
  } catch (e) {
    isLogin.value = false;
    showLoginMessage.value = true;
    LoginMsgSeverity.value = "error";
    LoginMsgContent.value = e.message || "登录请求异常";
  }
}

function onLogout() {
  userData.value = {};
  isLogin.value = false;
  showLoginDialog.value = true;
  clearCookie("_auth");
  showLoginSuccessToast("登出成功");
}

async function onRegister(){
  if (!username.value || !password.value || !Confirmpassword.value) {
    showRegMessage.value = true;
    RegMsgSeverity.value = "error";
    RegMsgContent.value = "账号名、密码和确认密码不能为空";
    return;
  }
  if (password.value !== Confirmpassword.value) {
    showRegMessage.value = true;
    RegMsgSeverity.value = "error";
    RegMsgContent.value = "两次输入的密码不一致";
    return;
  }
  try {
    const res = await axios.post("/api/user/register", { username: username.value, password: password.value }, { withCredentials: true });
    if (res.status === 200) {
      showLoginMessage.value = true;
      LoginMsgSeverity.value = "success";
      LoginMsgContent.value = "注册成功，请登录";
      showRegisterDialog.value = false;
      showLoginDialog.value = true;
      username.value = "";
      password.value = "";
      Confirmpassword.value = "";
    } else {
      showRegMessage.value = true;
      RegMsgSeverity.value = "error";
      RegMsgContent.value = res.data.message || "注册失败，请稍后重试";
    }
  } catch (e) {
    showRegMessage.value = true;
    RegMsgSeverity.value = "error";
    RegMsgContent.value = e.message || "注册请求异常，请稍后重试";
  }

}

async function getConfig(){
  const res = await axios.get("/api/config")
  if (res.status === 200) {
    cfg.value = res.data.data;
  } else {
    showLoginErrorToast("获取配置失败，请稍后重试");
    return
  }
}

onMounted(async () => {
  getConfig();
  loading.value = true;
  if (!document.cookie.includes("_auth")) {
    loading.value = false;
    showLoginErrorToast("请先登录");
    showLoginDialog.value = true;
    return;
  }
  try {
    const res = await axios.get("/api/user/get_user", { withCredentials: true });
    if (res.status === 200) {
      loading.value = false;
      userData.value = res.data.data;
      isLogin.value = true;
      showLoginDialog.value = false;
    } else {
      loading.value = false;
      isLogin.value = false;
      showLoginDialog.value = true;
      showLoginErrorToast(res.data.detail || "登录状态异常，请重新登录");
    }
  } catch (e) {
    loading.value = false;
    isLogin.value = false;
    showLoginDialog.value = true;
    showLoginErrorToast(e.message || "登录请求异常");
  }
});
</script>
