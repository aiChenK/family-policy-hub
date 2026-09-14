<template>
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
    <div class="overflow-x-auto custom-scrollbar">
      <table class="w-full border-separate border-spacing-0 text-xs text-left min-w-[1100px]">
        <thead class="bg-slate-50 font-semibold text-slate-600">
          <tr>
            <th class="sticky left-0 z-20 bg-slate-50 py-3.5 px-4 whitespace-nowrap min-w-[120px] shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-b border-slate-200/80">
              被保人
            </th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[90px] border-b border-slate-200/80">险种</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[180px] border-b border-slate-200/80">产品名称</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[130px] border-b border-slate-200/80">保单号</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[110px] border-b border-slate-200/80">承保机构</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[110px] border-b border-slate-200/80">保额</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[140px] border-b border-slate-200/80">缴费年限 / 排期</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[130px] border-b border-slate-200/80">保费(频次)</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[130px] border-b border-slate-200/80">扣款卡 / 渠道</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[90px] border-b border-slate-200/80">状态</th>
            <th class="sticky right-0 z-20 bg-slate-50 py-3.5 px-4 text-right whitespace-nowrap min-w-[150px] shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-b border-slate-200/80">
              操作
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pol in policies"
            :key="pol.id"
            class="group hover:bg-slate-50/80 transition-colors"
          >
            <!-- 首列吸顶：被保人 -->
            <td
              class="sticky left-0 z-10 py-3 px-4 whitespace-nowrap shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-b border-slate-100 font-bold text-slate-900 bg-white group-hover:bg-slate-50/90 transition-colors"
            >
              <div v-if="pol.isFamilyPolicy" class="space-y-1">
                <div class="flex items-center space-x-1.5">
                  <span class="px-1.5 py-0.5 rounded text-[10px] bg-purple-100 text-purple-700 font-bold border border-purple-200/80">家庭多人</span>
                  <span class="text-xs text-slate-900 font-bold" :title="'参保家属：' + (pol.insuredMembers || []).join('、')">
                    {{ (pol.insuredMembers && pol.insuredMembers.length > 0) ? (pol.insuredMembers.length <= 2 ? pol.insuredMembers.join('、') : `${pol.insuredMembers.slice(0, 2).join('、')}等${pol.insuredMembers.length}人`) : pol.member }}
                  </span>
                </div>
                <div v-if="pol.applicant" class="text-[10px] text-slate-400 font-normal">
                  投保: {{ pol.applicant }}
                </div>
              </div>
              <div v-else>
                <div>{{ pol.member }}</div>
                <div v-if="pol.applicant && pol.applicant !== pol.member" class="text-[10px] text-slate-400 font-normal">
                  投保: {{ pol.applicant }}
                </div>
              </div>
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100">
              <span :class="getTypeBadgeClass(pol.type)" class="px-2 py-0.5 rounded-full font-medium">{{ pol.type }}</span>
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 font-semibold text-slate-800">
              {{ pol.name }}
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 font-mono text-slate-600">
              {{ pol.policyNo || '-' }}
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-600">
              {{ pol.company }}
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-700">
              {{ pol.amount || '-' }}
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-600">
              {{ pol.paymentYears }}年 <span v-if="pol.paymentMonthDay" class="text-slate-400 font-normal">({{ pol.paymentMonthDay }})</span>
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 font-bold text-slate-900">
              ¥{{ formatMoney(pol.premium) }}
              <span class="text-[10px] text-slate-400 font-normal">({{ pol.paymentFrequency || '年缴' }})</span>
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-600">
              {{ pol.paymentAccount || '-' }}
            </td>

            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100">
              <span v-if="pol.status === 'active'" class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-medium">正常在缴</span>
              <span v-else class="text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full font-medium">已停保</span>
            </td>

            <!-- 尾列吸顶：操作 -->
            <td
              class="sticky right-0 z-10 py-3 px-4 text-right whitespace-nowrap shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-b border-slate-100 bg-white group-hover:bg-slate-50/90 transition-colors space-x-2"
            >
              <button
                @click="$emit('view-policy-payments', pol)"
                class="text-emerald-600 hover:text-emerald-800 font-medium cursor-pointer"
                title="查看关联缴费流水与排期"
              >
                流水
              </button>
              <button
                @click="$emit('open-edit-modal', pol)"
                class="text-sky-600 hover:text-sky-800 font-medium cursor-pointer"
              >
                编辑
              </button>
              <button
                @click="$emit('view-policy-detail', pol)"
                class="text-slate-600 hover:text-slate-900 font-medium cursor-pointer"
              >
                明细
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { formatMoney, getTypeBadgeClass } from '../../utils/helpers.js';

defineProps({
  policies: {
    type: Array,
    default: () => []
  }
});

defineEmits(['open-edit-modal', 'view-policy-detail', 'view-policy-payments']);
</script>
