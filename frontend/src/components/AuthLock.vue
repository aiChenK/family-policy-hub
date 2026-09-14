<template>
  <div class="min-h-screen w-full flex flex-col items-center justify-center relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-sky-950 p-4 sm:p-6 select-none">
    <!-- 氛围微光背景装饰 -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute inset-0 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px] opacity-10 pointer-events-none"></div>

    <!-- 门禁安全主体卡片 -->
    <div
      class="relative z-10 w-full max-w-md bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-700/60 shadow-2xl shadow-sky-950/50 p-8 sm:p-10 text-center transition-all duration-300"
      :class="{ 'animate-shake': hasShake }"
    >
      <!-- 顶部轻奢光晕流光条 -->
      <div class="absolute top-0 left-8 right-8 h-[2px] bg-gradient-to-r from-transparent via-sky-400 to-transparent opacity-80"></div>

      <!-- 核心安全盾牌徽标 -->
      <div class="relative w-20 h-20 mx-auto mb-6 flex items-center justify-center">
        <div class="absolute inset-0 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 opacity-30 blur-lg animate-pulse"></div>
        <div class="relative w-20 h-20 rounded-2xl bg-gradient-to-tr from-sky-500 via-sky-600 to-indigo-600 flex items-center justify-center text-white text-3xl shadow-xl shadow-sky-500/20 border border-sky-300/30">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
      </div>

      <!-- 系统标题与保护提示 -->
      <h1 class="text-2xl font-black text-white tracking-tight mb-2 flex items-center justify-center gap-2">
        <span>家庭保险资产管理</span>
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/20 text-sky-300 border border-sky-400/30">
          <i class="fa-solid fa-lock text-[9px] mr-1"></i>已加锁
        </span>
      </h1>
      <p class="text-xs text-slate-400 leading-relaxed mb-8 max-w-xs mx-auto">
        系统存储有家庭成员私密保单、医疗保障与车辆保险信息，请输入访问密码以解锁查阅。
      </p>

      <!-- 密码输入与解锁表单 -->
      <form @submit.prevent="submitForm" class="space-y-5 text-left">
        <div>
          <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>访问密码</span>
            <span v-if="authState.error" class="text-[11px] text-rose-400 lowercase font-normal flex items-center gap-1">
              <i class="fa-solid fa-circle-exclamation text-[10px]"></i>
              {{ authState.error }}
            </span>
          </label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-sky-400 transition-colors">
              <i class="fa-solid fa-key text-xs"></i>
            </div>
            <input
              ref="inputRef"
              :type="authState.showPassword ? 'text' : 'password'"
              v-model="authState.password"
              placeholder="请输入访问密码并按回车"
              autocomplete="current-password"
              autofocus
              class="w-full pl-10 pr-11 py-3.5 text-sm bg-slate-950/60 text-white placeholder-slate-500 rounded-xl border transition-all duration-200 focus:outline-none"
              :class="[
                authState.error
                  ? 'border-rose-500/80 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                  : 'border-slate-700/80 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 hover:border-slate-600'
              ]"
            />
            <button
              type="button"
              @click="authState.showPassword = !authState.showPassword"
              class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 transition-colors text-sm"
              title="切换密码明暗显示"
              tabindex="-1"
            >
              <i :class="authState.showPassword ? 'fa-eye-slash' : 'fa-eye'" class="fa-solid text-xs"></i>
            </button>
          </div>
        </div>

        <!-- 解锁提交按钮 -->
        <button
          type="submit"
          :disabled="authState.loading || !authState.password"
          class="w-full py-3.5 px-5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 active:from-sky-600 active:to-indigo-700 text-white font-semibold text-sm rounded-xl transition-all duration-200 shadow-lg shadow-sky-500/25 flex items-center justify-center space-x-2 disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-sky-500/35"
        >
          <i v-if="authState.loading" class="fa-solid fa-spinner fa-spin text-sm"></i>
          <span>{{ authState.loading ? '正在验证凭证...' : '立即验证并解锁' }}</span>
          <i v-if="!authState.loading" class="fa-solid fa-arrow-right text-xs"></i>
        </button>
      </form>

      <!-- 底部安全背书与提示 -->
      <div class="mt-8 pt-6 border-t border-slate-800/80 flex items-center justify-center text-[11px] text-slate-500 gap-2">
        <i class="fa-solid fa-lock text-slate-600"></i>
        <span>服务端 HMAC 防篡改签名鉴权 · 数据安全隔离</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  authState: { type: Object, required: true }
});

const emit = defineEmits(['login']);

const inputRef = ref(null);
const hasShake = ref(false);

const submitForm = () => {
  if (props.authState.loading || !props.authState.password) return;
  emit('login');
};

// 监听错误发生时触发抖动动效
watch(
  () => props.authState.error,
  (newVal) => {
    if (newVal) {
      hasShake.value = true;
      setTimeout(() => {
        hasShake.value = false;
      }, 600);
      nextTick(() => {
        if (inputRef.value) {
          inputRef.value.focus();
          inputRef.value.select();
        }
      });
    }
  }
);
</script>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
</style>
