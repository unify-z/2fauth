<template>
  <div class="main-container">
    <div class="button-group">
      <Button
        style="margin-left: 10px; width: 120px; white-space: nowrap"
        icon="pi pi-plus"
        label="添加应用"
        @click="openDrawer"
      />
      <Button
        loading
        disabled
        severity="contrast"
        variant="text"
        style="margin-left: 10px; width: 150px; white-space: nowrap"
        :label="`自动刷新(${refreshTime}s)`"
      />
    </div>
    <Loading
      class="loading"
      :active="loading"
      is-full-page="false"
      color="#4ade80"
      height="25"
      width="55"
      loader="bars"
      v-if="loading"
    />
    <div class="otp-card-container">
      <Card v-for="item in data" :key="item.otp" style="margin-right: 15px">
        <template #title>
          <div class="card-title">
            {{ item.messages[0] }} | {{ item.messages[1] }}
            <Button
              severity="danger"
              icon="pi pi-trash"
              style="margin-left: 10px; height: 30px; width: 40px"
            />
            <Button
              severity="secondary"
              icon="pi pi-pencil"
              style="margin-left: 10px; height: 30px; width: 40px"
            />
          </div>
        </template>
        <template #content>
          {{ item.otp }}
        </template>
      </Card>
    </div>
  </div>

  <Drawer
    v-model:visible="showDrawer"
    header="添加应用"
    position="right"
    style="width: 400px"
  >
    <label>添加方式</label>
    <Select
      v-model="selectedMethod"
      :options="methods"
      optionLabel="name"
      optionValue="value"
      placeholder="选择添加方式"
      optionDisabled="disabled"
      style="width: 100%; margin-top: 10px"
    />

    <div v-if="selectedMethod === 'manual'">
      <div style="margin-top: 15px; display: flex; flex-direction: column">
        <label for="issuer">应用名称</label>
        <InputText
          id="issuer"
          class="input"
          :invalid="!AppNamevalue"
          v-model="AppNamevalue"
          variant="filled"
        />
        <label for="secret" style="margin-top: 10px">密钥</label>
        <InputText
          id="secret"
          class="input"
          :invalid="!Secretvalue"
          v-model="Secretvalue"
          variant="filled"
        />
        <label for="account" style="margin-top: 10px">账号名</label>
        <InputText
          id="account"
          class="input"
          :invalid="!Accountvalue"
          v-model="Accountvalue"
          variant="filled"
        />
      </div>
    </div>
    <template #footer>
      <div style="display: flex; justify-content: flex-end">
        <Button
          label="取消"
          class="p-button-text"
          @click="closeDrawer"
          style="margin-right: 15px; width: 80px"
        />
        <Button
          label="添加"
          class="p-button-primary"
          @click="handleAddAPP"
          style="margin-right: 15px; width: 80px"
        />
      </div>
    </template>
  </Drawer>
</template>

<script setup>
import Button from "primevue/button";
import Select from "primevue/select";
import Card from "primevue/card";
import { Drawer } from "primevue";
import InputText from "primevue/inputtext";
import { ref, inject, onMounted } from "vue";
import Loading from "vue-loading-overlay";
import axiosInstance from "@/utils/axios";

const AppNamevalue = ref("");
const Secretvalue = ref("");
const Accountvalue = ref("");
const loading = ref(true);
const showDrawer = ref(false);
const selectedMethod = ref(null);
const refreshTime = ref(30);
const methods = ref([
  { name: "二维码解析", value: "qrcode", disabled: true },
  { name: "手动输入", value: "manual" },
]);
const data = ref([]);

const showSuccessToast = inject("showSuccessToast");
const showErrorToast = inject("showErrorToast");

function openDrawer() {
  showDrawer.value = true;
}

function closeDrawer() {
  showDrawer.value = false;
}

async function handleAddAPP() {
  try {
    const res = await axiosInstance.post("/api/totp/add", {
      otpauth_url: `otpauth://totp/${AppNamevalue.value}:${Accountvalue.value}?secret=${Secretvalue.value}&issuer=${AppNamevalue.value}`,
    });
    if (res.status === 200) {
      showSuccessToast("应用添加成功");
      closeDrawer();
      return;
    }
    showErrorToast(`应用添加失败: ${res.data.error} || 未知错误`);
    closeDrawer();
  } catch (e) {
    showErrorToast(`应用添加失败: ${e.message}`);
    closeDrawer();
  }
}

async function fetchData() {
  const res = await axiosInstance.post("/api/totp/list", null, {
    withCredentials: true,
  });
  try {
    if (res.status === 200) {
      loading.value = false;
      data.value = res.data.data;
      return;
    }
    loading.value = false;
    showErrorToast(`数据拉取失败: ${res.data.message} || 未知错误`);
  } catch (e) {
    loading.value = true;
    showErrorToast(`数据拉取失败: ${e.message}`);
  }
}

setInterval(() => {
  refreshTime.value = refreshTime.value - 1;
  if (refreshTime.value <= 0) {
    refreshTime.value = 30;
    fetchData();
  }
}, 1000);

onMounted(async () => {
  await fetchData();
});
</script>

<style>
.main-container {
  margin-top: 30px;
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}
.input {
  width: 100%;
  margin-top: 10px;
}
.button-group {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}
.loading {
  width: 100%;
  height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title {
  display: flex;
  flex-wrap: nowrap;
  justify-content: flex-start;
}
.otp-card-container {
  display: flex;
  justify-content: flex-start;
  flex-direction: row;
  margin-left: 10px;
  margin-top: 20px;
}
</style>
