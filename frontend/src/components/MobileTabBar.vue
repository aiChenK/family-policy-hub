<template>
  <div class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200/90 shadow-[0_-4px_16px_rgba(0,0,0,0.06)] md:hidden pb-safe mobile-tab-bar select-none">
    <!-- 主底栏网格 -->
    <div class="grid grid-cols-5 h-14 items-center px-1">
      <!-- 1. 概览 -->
      <button
        type="button"
        @click="selectTab('dashboard')"
        class="flex flex-col items-center justify-center h-full relative transition-all active:scale-95"
        :class="currentTab === 'dashboard' ? 'text-sky-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
      >
        <div class="relative">
          <i class="fa-solid fa-shield-halved text-lg"></i>
          <span
            v-if="unpaidCount > 0 || vehiclesExpiringCount > 0"
            class="absolute -top-1 -right-1.5 w-2 h-2 rounded-full bg-rose-500 animate-pulse"
          ></span>
        </div>
        <span class="text-[10px] mt-0.5 tracking-tight">概览</span>
      </button>

      <!-- 2. 保单 -->
      <button
        type="button"
        @click="selectTab('policies')"
        class="flex flex-col items-center justify-center h-full relative transition-all active:scale-95"
        :class="currentTab === 'policies' ? 'text-sky-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
      >
        <div class="relative">
          <i class="fa-solid fa-file-shield text-lg"></i>
        </div>
        <span class="text-[10px] mt-0.5 tracking-tight">保单</span>
      </button>

      <!-- 3. 爱车 -->
      <button
        type="button"
        @click="selectTab('vehicles')"
        class="flex flex-col items-center justify-center h-full relative transition-all active:scale-95"
        :class="currentTab === 'vehicles' ? 'text-sky-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
      >
        <div class="relative">
          <i class="fa-solid fa-car-rear text-lg"></i>
          <span
            v-if="vehiclesExpiringCount > 0"
            class="absolute -top-1 -right-1.5 w-2 h-2 rounded-full bg-amber-500"
          ></span>
        </div>
        <span class="text-[10px] mt-0.5 tracking-tight">爱车</span>
      </button>

      <!-- 4. 台账 -->
      <button
        type="button"
        @click="selectTab('payments')"
        class="flex flex-col items-center justify-center h-full relative transition-all active:scale-95"
        :class="currentTab === 'payments' ? 'text-sky-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
      >
        <div class="relative">
          <i class="fa-solid fa-receipt text-lg"></i>
          <span
            v-if="unpaidCount > 0"
            class="absolute -top-1 -right-1.5 w-2 h-2 rounded-full bg-rose-500"
          ></span>
        </div>
        <span class="text-[10px] mt-0.5 tracking-tight">台账</span>
      </button>

      <!-- 5. 应急 / 更多 -->
      <button
        type="button"
        @click="toggleMoreSheet"
        class="flex flex-col items-center justify-center h-full relative transition-all active:scale-95"
        :class="isEmergencyOrCalendarActive ? 'text-rose-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
      >
        <div class="relative">
          <i :class="currentTab === 'emergency' ? 'fa-solid fa-kit-medical text-lg text-rose-600' : (currentTab === 'calendar' ? 'fa-solid fa-calendar-days text-lg text-sky-600' : 'fa-solid fa-grip text-lg')"></i>
        </div>
        <span class="text-[10px] mt-0.5 tracking-tight">
          {{ currentTab === 'emergency' ? '应急卡' : (currentTab === 'calendar' ? '日历' : '更多') }}
        </span>
      </button>
    </div>

    <!-- 更多功能底部快捷抽屉浮层 -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="showMoreSheet"
        class="fixed inset-x-0 bottom-14 z-50 bg-white/95 backdrop-blur-md rounded-t-3xl border-t border-slate-200/90 shadow-2xl p-4 space-y-3"
      >
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <span class="text-xs font-bold text-slate-800">快捷服务与系统工具</span>
          <button
            @click="showMoreSheet = false"
            class="text-slate-400 hover:text-slate-600 p-1 rounded-full text-xs"
          >
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <div class="grid grid-cols-3 gap-2.5 text-xs">
          <!-- 就医应急卡 -->
          <button
            @click="selectTab('emergency')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border transition text-center"
            :class="currentTab === 'emergency' ? 'bg-rose-50 border-rose-200 text-rose-700 font-bold' : 'bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700'"
          >
            <div class="w-9 h-9 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-kit-medical"></i>
            </div>
            <span class="text-xs font-semibold">就医应急卡</span>
            <span class="text-[10px] text-slate-400 mt-0.5">理赔与报案电话</span>
          </button>

          <!-- 缴费日历 -->
          <button
            @click="selectTab('calendar')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border transition text-center"
            :class="currentTab === 'calendar' ? 'bg-sky-50 border-sky-200 text-sky-700 font-bold' : 'bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700'"
          >
            <div class="w-9 h-9 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-calendar-days"></i>
            </div>
            <span class="text-xs font-semibold">缴费日历</span>
            <span class="text-[10px] text-slate-400 mt-0.5">按月排期统揽</span>
          </button>

          <!-- 保司电话配置 -->
          <button
            @click="triggerAction('open-phones')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700 transition text-center"
          >
            <div class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-phone-volume"></i>
            </div>
            <span class="text-xs font-semibold">保司热线</span>
            <span class="text-[10px] text-slate-400 mt-0.5">报案电话管理</span>
          </button>

          <!-- 家庭成员档案 -->
          <button
            @click="triggerAction('open-members')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700 transition text-center"
          >
            <div class="w-9 h-9 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-users"></i>
            </div>
            <span class="text-xs font-semibold">成员档案</span>
            <span class="text-[10px] text-slate-400 mt-0.5">管理家庭资料</span>
          </button>

          <!-- 企业主体资质 -->
          <button
            @click="triggerAction('open-companies')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700 transition text-center"
          >
            <div class="w-9 h-9 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-building"></i>
            </div>
            <span class="text-xs font-semibold">企业资质</span>
            <span class="text-[10px] text-slate-400 mt-0.5">公户车税号备查</span>
          </button>

          <!-- 导出日历订阅 -->
          <button
            @click="triggerAction('export-ics')"
            class="flex flex-col items-center justify-center p-3 rounded-2xl border bg-slate-50 hover:bg-slate-100 border-slate-200/60 text-slate-700 transition text-center"
          >
            <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center text-base mb-1.5 shadow-2xs">
              <i class="fa-solid fa-calendar-check"></i>
            </div>
            <span class="text-xs font-semibold">导出日历</span>
            <span class="text-[10px] text-slate-400 mt-0.5">同步到手机系统</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 遮罩背景点击关闭抽屉 -->
    <div
      v-if="showMoreSheet"
      @click="showMoreSheet = false"
      class="fixed inset-0 bg-slate-900/20 backdrop-blur-2xs z-45 md:hidden"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  currentTab: { type: String, required: true },
  unpaidCount: { type: Number, default: 0 },
  vehiclesExpiringCount: { type: Number, default: 0 }
});

const emit = defineEmits([
  'update:currentTab',
  'open-phones',
  'open-members',
  'open-companies',
  'export-ics'
]);

const showMoreSheet = ref(false);

const isEmergencyOrCalendarActive = computed(() => {
  return props.currentTab === 'emergency' || props.currentTab === 'calendar';
});

function selectTab(tabId) {
  emit('update:currentTab', tabId);
  showMoreSheet.value = false;
}

function toggleMoreSheet() {
  showMoreSheet.value = !showMoreSheet.value;
}

function triggerAction(actionName) {
  emit(actionName);
  showMoreSheet.value = false;
}
</script>
