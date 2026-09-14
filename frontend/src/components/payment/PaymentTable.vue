<template>
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
    <div class="overflow-x-auto custom-scrollbar">
      <table class="min-w-[1180px] w-full divide-y divide-slate-200 text-xs text-left border-separate border-spacing-0">
        <thead class="bg-slate-50 font-semibold text-slate-600">
          <tr>
            <!-- 固定头部首列：应缴年份 / 扣款日 -->
            <th class="sticky left-0 z-20 bg-slate-50 py-3.5 px-4 whitespace-nowrap min-w-[140px] shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80">
              应缴年份 / 扣款日
            </th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[130px]">被保人 / 车辆</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[95px]">险种</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[200px]">产品名称</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[110px]">承保机构</th>
            <th class="py-3.5 px-4 whitespace-nowrap min-w-[120px]">期数排期</th>
            <th class="py-3.5 px-4 text-right whitespace-nowrap min-w-[110px]">保费金额</th>
            <th class="py-3.5 px-4 text-center whitespace-nowrap min-w-[160px]">扣缴状态</th>
            <!-- 固定尾部列：操作列 -->
            <th class="sticky right-0 z-20 bg-slate-50 py-3.5 px-4 text-right whitespace-nowrap min-w-[140px] shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="item in payments"
            :key="item.key"
            class="group transition-colors"
            :class="[item.status === 'due' ? 'bg-amber-50/40 hover:bg-amber-50/70' : 'hover:bg-slate-50/80']"
          >
            <!-- 固定头部首列：应缴年份与具体日期 -->
            <td
              class="sticky left-0 z-10 py-3 px-4 whitespace-nowrap shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80 border-b border-slate-100 transition-colors"
              :class="item.status === 'due' ? 'bg-amber-50/90 group-hover:bg-amber-100/90' : 'bg-white group-hover:bg-slate-50/90'"
            >
              <div class="flex items-center space-x-1.5 font-mono">
                <span class="font-bold text-sm" :class="item.year === currentYear ? 'text-sky-600' : 'text-slate-900'">
                  {{ item.year }}
                </span>
                <span class="text-slate-300">·</span>
                <span class="text-slate-700 font-medium text-xs">{{ item.dueDate }}</span>
              </div>
            </td>

            <!-- 成员姓名与车牌 -->
            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-700">
              <div class="flex items-center space-x-1.5">
                <span class="font-semibold text-slate-900">{{ item.member }}</span>
                <span
                  v-if="item.isVehicle"
                  class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold shrink-0 whitespace-nowrap"
                  :class="item.plateType === 'green' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'"
                  :title="'车牌：' + item.plateNo"
                >
                  {{ item.plateNo }}
                </span>
              </div>
            </td>

            <!-- 险种 -->
            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100">
              <span :class="getTypeBadgeClass(item.type)" class="px-2 py-0.5 rounded-full font-medium inline-flex items-center space-x-1 text-[11px]">
                <i v-if="item.isVehicle" class="fa-solid fa-car text-[10px] mr-1"></i>
                <span>{{ item.type }}</span>
              </span>
            </td>

            <!-- 产品名称 -->
            <td class="py-3 px-4 min-w-[200px] whitespace-nowrap border-b border-slate-100">
              <div class="font-medium text-slate-800 flex items-center space-x-1">
                <i v-if="item.isVehicle" class="fa-solid fa-shield-cat text-sky-500 mr-1 text-[11px] shrink-0"></i>
                <span class="truncate max-w-[260px]" :title="item.name">{{ item.name }}</span>
              </div>
              <div v-if="item.isArchive" class="text-[10px] text-slate-400 mt-0.5">历史已停售归档</div>
              <div v-else-if="item.isVehicle && item.amount" class="text-[10px] text-slate-400 font-mono mt-0.5">{{ item.amount }}</div>
            </td>

            <!-- 承保机构 -->
            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100 text-slate-600">
              {{ item.company || '-' }}
            </td>

            <!-- 期数排期 -->
            <td class="py-3 px-4 whitespace-nowrap border-b border-slate-100">
              <span v-if="item.isVehicle" class="text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md font-mono text-[11px] font-medium inline-flex items-center space-x-1 border border-sky-100">
                <i class="fa-solid fa-rotate-right text-[9px]"></i>
                <span>车险年度续保</span>
              </span>
              <span v-else-if="item.isShortTerm" class="text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md font-mono text-[11px] border border-slate-200/60">
                1年期续保
              </span>
              <span v-else class="text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md font-mono text-[11px] font-medium border border-sky-100">
                第 {{ item.periodIndex }} / {{ item.totalPeriods }} 期
              </span>
            </td>

            <!-- 应缴/实缴保费 -->
            <td class="py-3 px-4 text-right whitespace-nowrap border-b border-slate-100 font-mono font-extrabold text-slate-900 text-sm">
              ¥{{ formatMoney(item.premium) }}
            </td>

            <!-- 状态徽章 -->
            <td class="py-3 px-4 text-center whitespace-nowrap border-b border-slate-100">
              <span
                v-if="item.status === 'paid'"
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 shadow-2xs"
              >
                <i class="fa-solid fa-circle-check mr-1 text-emerald-500 text-[10px]"></i>
                <span>{{ item.isVehicle ? '已支付' : '已自动代扣' }}</span>
                <span v-if="item.paidDate" class="ml-1 font-mono text-[10px] text-emerald-600 font-normal">({{ item.paidDate }})</span>
              </span>

              <span
                v-else-if="item.status === 'unpaid'"
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-900 border border-rose-300 shadow-sm animate-pulse"
              >
                <i class="fa-solid fa-triangle-exclamation mr-1 text-rose-600 text-[11px]"></i>
                <span>扣款异常 / 未缴</span>
              </span>

              <span
                v-else-if="item.isNearUpcoming"
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 shadow-2xs"
              >
                <i class="fa-solid fa-clock text-sky-500 mr-1 text-[10px]"></i>
                <span>即将代扣 ({{ item.diffDays }}天后)</span>
              </span>

              <span v-else class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200/60 shadow-2xs">
                <i class="fa-regular fa-clock mr-1 text-slate-400 text-[10px]"></i>
                <span>未到扣费日</span>
              </span>
            </td>

            <!-- 固定尾部列：操作按钮 -->
            <td
              class="sticky right-0 z-10 py-3 px-4 text-right whitespace-nowrap shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80 border-b border-slate-100 transition-colors"
              :class="item.status === 'due' ? 'bg-amber-50/90 group-hover:bg-amber-100/90' : 'bg-white group-hover:bg-slate-50/90'"
            >
              <div class="inline-flex items-center space-x-1.5">
                <!-- 编辑当期实缴金额与详细信息 -->
                <button
                  @click="$emit('edit-record', item)"
                  class="p-1 text-slate-400 hover:text-sky-600 hover:bg-sky-50 rounded transition cursor-pointer"
                  title="编辑当期实缴金额、日期与备注"
                >
                  <i class="fa-solid fa-pen text-[11px]"></i>
                </button>

                <!-- 恢复已缴 / 标记扣款失败 / 提前转实缴 -->
                <button
                  v-if="item.status === 'unpaid'"
                  @click="$emit('toggle-confirm', item, true)"
                  class="px-2 py-0.8 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white rounded-md text-[11px] font-semibold shadow-2xs transition inline-flex items-center space-x-1 cursor-pointer"
                >
                  <i class="fa-solid fa-check text-[9px]"></i>
                  <span>恢复已缴</span>
                </button>
                <button
                  v-else-if="item.status === 'upcoming'"
                  @click="$emit('edit-record', item)"
                  class="px-2 py-0.8 bg-sky-50 hover:bg-sky-100 active:bg-sky-200 text-sky-700 border border-sky-200 rounded-md text-[11px] font-semibold transition inline-flex items-center space-x-1 cursor-pointer"
                  title="提前确认并输入实缴保费"
                >
                  <i class="fa-solid fa-check-double text-[9px]"></i>
                  <span>转实缴</span>
                </button>
                <button
                  v-else-if="item.status === 'paid'"
                  @click="$emit('toggle-confirm', item, false)"
                  title="若因银行卡余额不足等原因未扣款，可标记为扣费异常"
                  class="text-slate-400 hover:text-rose-600 text-[11px] hover:underline transition cursor-pointer"
                >
                  标记异常
                </button>

                <!-- 单期断缴删除按钮 (从台账彻底剔除) -->
                <button
                  @click="$emit('skip-record', item)"
                  class="p-1 text-slate-300 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                  title="中途断缴/未参保：从台账中彻底剔除此期"
                >
                  <i class="fa-regular fa-trash-can text-[11px]"></i>
                </button>
              </div>
            </td>
          </tr>

          <!-- 空状态展示 -->
          <tr v-if="payments.length === 0">
            <td colspan="9" class="py-12 text-center text-slate-400 border-b border-slate-100">
              <i class="fa-solid fa-receipt text-3xl mb-2 text-slate-300"></i>
              <p class="text-sm">暂无符合筛选条件的{{ filterStatus === 'upcoming' ? '预测' : '缴费' }}记录</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 底部汇总统计 -->
    <div class="px-6 py-3.5 bg-slate-50 border-t border-slate-200/80 flex flex-wrap items-center justify-between text-xs text-slate-600">
      <div>
        <span>当前筛选：<strong>{{ payments.length }}</strong> 笔记录</span>
        <span class="mx-2 text-slate-300">|</span>
        <span v-if="filterStatus === 'upcoming'">
          未到期预测：<strong class="text-sky-700 font-bold">{{ payments.length }}</strong> 笔 (按年份正序推算)
        </span>
        <span v-else>
          已缴流水：<strong class="text-emerald-700 font-bold">{{ payments.filter(p => p.status === 'paid').length }}</strong> 笔
          <span v-if="payments.some(p => p.status === 'unpaid')" class="ml-2 text-rose-600 font-bold">
            (含 {{ payments.filter(p => p.status === 'unpaid').length }} 笔异常)
          </span>
        </span>
      </div>
      <div class="text-right font-mono font-bold text-slate-900 text-sm">
        合计金额：¥{{ formatMoney(totalAmount) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatMoney, getTypeBadgeClass } from '../../utils/helpers.js';

const currentYear = new Date().getFullYear();

defineProps({
  payments: { type: Array, default: () => [] },
  filterStatus: { type: String, default: 'paid' },
  totalAmount: { type: Number, default: 0 }
});

defineEmits(['edit-record', 'toggle-confirm', 'skip-record']);
</script>
