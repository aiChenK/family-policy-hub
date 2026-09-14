<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
    <div class="bg-white rounded-2xl shadow-2xl border border-slate-100 w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <!-- 弹窗顶部标题 -->
      <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-lg border border-amber-200/50 shadow-sm">
            <i class="fa-solid fa-broom"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-800 tracking-tight">附件存储分析与清理</h3>
            <p class="text-xs text-slate-500">检测并清理未关联任何保单的冗余孤儿文件，减轻服务器存储与备份传输负担</p>
          </div>
        </div>
        <button
          type="button"
          @click="$emit('update:show', false)"
          class="text-slate-400 hover:text-slate-600 p-2 rounded-lg hover:bg-slate-100 transition"
        >
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 弹窗内容主体 -->
      <div class="p-6 overflow-y-auto space-y-6 custom-scrollbar flex-1">
        <!-- 统计面板 -->
        <div class="grid grid-cols-3 gap-3">
          <!-- 总附件 -->
          <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
            <div class="text-[11px] font-medium text-slate-500 flex items-center space-x-1.5">
              <i class="fa-regular fa-folder-open text-slate-400"></i>
              <span>附件总存储</span>
            </div>
            <div class="mt-1.5 flex items-baseline space-x-1">
              <span class="text-xl font-bold text-slate-800">{{ stats.totalSizeFormatted || '0 B' }}</span>
              <span class="text-xs text-slate-400 font-normal">({{ stats.totalFiles || 0 }} 个)</span>
            </div>
          </div>

          <!-- 在用附件 -->
          <div class="p-3.5 bg-sky-50/60 rounded-xl border border-sky-100">
            <div class="text-[11px] font-medium text-sky-700 flex items-center space-x-1.5">
              <i class="fa-solid fa-shield-check text-sky-500"></i>
              <span>在保凭证</span>
            </div>
            <div class="mt-1.5 flex items-baseline space-x-1">
              <span class="text-xl font-bold text-sky-800">{{ stats.referencedFiles || 0 }}</span>
              <span class="text-xs text-sky-600/70 font-normal">个文件正常引用</span>
            </div>
          </div>

          <!-- 冗余孤儿附件 -->
          <div
            :class="stats.orphanCount > 0 ? 'bg-amber-50/80 border-amber-200 text-amber-900' : 'bg-emerald-50/60 border-emerald-200/80 text-emerald-900'"
            class="p-3.5 rounded-xl border transition"
          >
            <div class="text-[11px] font-medium flex items-center space-x-1.5" :class="stats.orphanCount > 0 ? 'text-amber-700' : 'text-emerald-700'">
              <i class="fa-solid" :class="stats.orphanCount > 0 ? 'fa-triangle-exclamation text-amber-500' : 'fa-circle-check text-emerald-500'"></i>
              <span>无引用孤儿文件</span>
            </div>
            <div class="mt-1.5 flex items-baseline space-x-1">
              <span class="text-xl font-bold">{{ stats.orphanSizeFormatted || '0 B' }}</span>
              <span class="text-xs opacity-75 font-normal">({{ stats.orphanCount || 0 }} 个待清理)</span>
            </div>
          </div>
        </div>

        <!-- 扫描加载中 -->
        <div v-if="scanning" class="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
          <i class="fa-solid fa-circle-notch fa-spin text-3xl text-sky-500"></i>
          <span class="text-xs">正在深入扫描服务器磁盘附件与引用关系...</span>
        </div>

        <!-- 扫描完毕：无孤儿附件 -->
        <div v-else-if="stats.orphanCount === 0" class="py-10 text-center flex flex-col items-center justify-center space-y-3 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
          <div class="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xl">
            <i class="fa-solid fa-check"></i>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-slate-800">存储状态极佳，无冗余附件</h4>
            <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              当前所有上传的保单合同、发票和照片均在保单列表中有合法归属，没有产生任何废弃孤立文件。
            </p>
          </div>
        </div>

        <!-- 扫描完毕：有孤儿附件待清理 -->
        <div v-else class="space-y-3">
          <div class="flex items-center justify-between text-xs text-slate-600 font-medium">
            <span>待清理孤儿文件列表 ({{ stats.orphanCount }} 项)</span>
            <span class="text-amber-600 text-[11px]">可安全清理，不影响现有任何保单</span>
          </div>

          <div class="border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100 max-h-60 overflow-y-auto custom-scrollbar">
            <div
              v-for="(item, idx) in stats.orphans"
              :key="idx"
              class="px-4 py-2.5 flex items-center justify-between hover:bg-slate-50 text-xs transition"
            >
              <div class="flex items-center space-x-2.5 truncate flex-1 mr-3">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase shrink-0"
                  :class="item.category === 'vehicle' ? 'bg-amber-100 text-amber-700' : 'bg-sky-100 text-sky-700'"
                >
                  {{ item.category === 'vehicle' ? '车辆附件' : '人身保单' }}
                </span>
                <span class="text-slate-700 font-mono truncate" :title="item.storedName">
                  {{ item.storedName }}
                </span>
              </div>
              <div class="flex items-center space-x-3 text-[11px] text-slate-400 shrink-0">
                <span class="font-medium text-slate-600">{{ item.sizeFormatted }}</span>
                <span>{{ item.modifiedAt }}</span>
              </div>
            </div>
          </div>

          <!-- 原理与安全提示 -->
          <div class="p-3 bg-amber-50/60 rounded-xl border border-amber-200/60 text-amber-800 text-xs leading-relaxed flex items-start space-x-2.5">
            <i class="fa-solid fa-circle-info text-amber-600 text-sm mt-0.5"></i>
            <div>
              <strong>小贴士：</strong>
              当您删除保单、车辆档案或单期续保记录时，若未同步清理附件，便会产生孤儿文件。清理这些文件能直接为服务器节省磁盘，并在后续备份时减少不必要的数据传输。
            </div>
          </div>
        </div>
      </div>

      <!-- 弹窗底部操作栏 -->
      <div class="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
        <button
          type="button"
          @click="fetchOrphans"
          :disabled="scanning || cleaning"
          class="inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl transition shadow-sm disabled:opacity-50"
        >
          <i class="fa-solid fa-arrows-rotate" :class="{ 'fa-spin': scanning }"></i>
          <span>重新扫描</span>
        </button>

        <div class="flex items-center space-x-3">
          <button
            type="button"
            @click="$emit('update:show', false)"
            class="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 rounded-xl transition"
          >
            关闭
          </button>
          <button
            v-if="stats.orphanCount > 0"
            type="button"
            @click="handleClean"
            :disabled="scanning || cleaning"
            class="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 active:bg-rose-800 rounded-xl transition shadow-md shadow-rose-200 disabled:opacity-50"
          >
            <i class="fa-solid" :class="cleaning ? 'fa-spinner fa-spin' : 'fa-trash-can'"></i>
            <span>{{ cleaning ? '清理中...' : `一键安全清理 (${stats.orphanSizeFormatted})` }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { AppApi } from '../api/index.js';

const props = defineProps({
  show: { type: Boolean, default: false }
});

const emit = defineEmits(['update:show', 'toast']);

const scanning = ref(false);
const cleaning = ref(false);
const stats = ref({
  totalFiles: 0,
  totalSize: 0,
  totalSizeFormatted: '0 B',
  referencedFiles: 0,
  orphanCount: 0,
  orphanSize: 0,
  orphanSizeFormatted: '0 B',
  orphans: []
});

watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchOrphans();
  }
});

async function fetchOrphans() {
  scanning.value = true;
  try {
    const res = await AppApi.getOrphanAttachments();
    if (res && res.status === 'ok') {
      stats.value = res;
    }
  } catch (err) {
    emit('toast', '扫描孤儿附件失败: ' + err.message, 'error');
  } finally {
    scanning.value = false;
  }
}

async function handleClean() {
  if (!confirm(`确认彻底删除这 ${stats.value.orphanCount} 个无引用孤儿附件吗？此操作将释放 ${stats.value.orphanSizeFormatted} 磁盘空间。`)) {
    return;
  }

  cleaning.value = true;
  try {
    const res = await AppApi.cleanOrphanAttachments();
    if (res && res.status === 'ok') {
      emit('toast', `成功清理 ${res.cleanedCount} 个冗余文件，释放空间 ${res.freedSizeFormatted}！`, 'success');
      // 重新扫描更新状态
      await fetchOrphans();
    }
  } catch (err) {
    emit('toast', '清理孤儿附件失败: ' + err.message, 'error');
  } finally {
    cleaning.value = false;
  }
}
</script>
