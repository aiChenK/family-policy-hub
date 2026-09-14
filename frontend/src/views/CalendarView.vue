<template>
  <section class="space-y-6">
    <div class="bg-gradient-to-r from-sky-600 to-indigo-700 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <h3 class="text-lg font-bold">家庭年度保费扣缴日历</h3>
        <p class="text-sky-100 text-xs mt-1">按每年固定扣款月份排列，清晰掌握每个月的资金支出节点，避免因银行卡余额不足脱保。</p>
      </div>
      <button
        @click="$emit('export-ics')"
        class="px-4 py-2 bg-white text-sky-800 hover:bg-sky-50 rounded-xl text-xs font-bold transition shadow-sm flex items-center space-x-2 shrink-0"
      >
        <i class="fa-solid fa-calendar-plus text-sky-600"></i>
        <span>导出并同步至手机日历 (.ics)</span>
      </button>
    </div>

    <!-- 按月份分组扣费时间轴 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="group in calendarGroups"
        :key="group.month"
        class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col"
      >
        <div class="p-4 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
          <div class="flex items-center space-x-2">
            <span class="w-8 h-8 rounded-lg bg-sky-600 text-white font-bold text-xs flex items-center justify-center shadow-sm">
              {{ group.month }}月
            </span>
            <span class="font-bold text-slate-800 text-sm">扣款月份</span>
          </div>
          <span class="text-xs font-bold text-slate-900 bg-white px-2.5 py-1 rounded-lg border border-slate-200/80">
            当月合计: ¥{{ formatMoney(group.total) }}
          </span>
        </div>

        <div class="p-4 space-y-3 flex-1">
          <div
            v-for="item in group.items"
            :key="item.id"
            class="p-3 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:border-sky-200 hover:shadow-sm transition"
          >
            <div class="flex justify-between items-start">
              <div class="flex items-center flex-wrap gap-1">
                <span class="text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-100 mr-1">
                  {{ item.paymentDay }}日
                </span>
                <span class="font-bold text-slate-900 text-xs">{{ item.member }}</span>
                <!-- 缴费状态标签 -->
                <span
                  v-if="item.isUnpaid"
                  class="text-[10px] text-rose-800 bg-rose-100 px-1.5 py-0.5 rounded font-bold inline-flex items-center"
                >
                  <i class="fa-solid fa-triangle-exclamation mr-0.5 text-[9px]"></i>扣款异常
                </span>
                <span
                  v-else-if="item.currentYearPaid"
                  class="text-[10px] text-emerald-700 bg-emerald-100/80 px-1.5 py-0.5 rounded font-medium inline-flex items-center"
                >
                  <i class="fa-solid fa-check mr-0.5 text-[9px]"></i>{{ item.isVehicle ? '已缴' : '已代扣' }}
                </span>
                <span v-else class="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">待扣款</span>
              </div>
              <span class="font-extrabold text-slate-900 text-xs">¥{{ formatMoney(item.premium) }}</span>
            </div>
            <div class="mt-1 text-xs text-slate-700 font-medium">{{ item.name }}</div>
            <div class="mt-0.5 text-[11px] text-slate-400 flex justify-between">
              <span>{{ item.company }} · {{ item.type }}</span>
              <span>{{ item.coveragePeriod || '终身' }} / {{ item.paymentYears }}年</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { formatMoney } from '../utils/helpers.js';

defineProps({
  calendarGroups: { type: Array, default: () => [] }
});

defineEmits(['export-ics']);
</script>
