<template>
  <div v-if="policy" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
    <div
      class="bg-white rounded-3xl max-w-2xl w-full shadow-2xl overflow-hidden border border-slate-100 animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[92vh]"
    >
      <!-- 弹窗头部 -->
      <div class="p-5 bg-gradient-to-r from-slate-50 to-emerald-50/40 border-b border-slate-100 flex items-start justify-between">
        <div class="flex items-start space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-emerald-100/80 text-emerald-700 flex items-center justify-center text-lg shrink-0 mt-0.5 shadow-2xs border border-emerald-200/60">
            <i class="fa-solid fa-receipt"></i>
          </div>
          <div>
            <div class="flex items-center space-x-2 flex-wrap gap-y-1">
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full shadow-2xs" :class="getTypeBadgeClass(policy.type)">
                {{ policy.type }}
              </span>
              <span class="text-xs font-bold text-slate-800 bg-white/90 px-2 py-0.5 rounded-md border border-slate-200/80">
                {{ policy.member }}
              </span>
              <span v-if="policy.status === 'stopped'" class="text-[11px] bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full font-medium">
                已停保
              </span>
              <span v-else class="text-[11px] bg-emerald-100/90 text-emerald-800 px-2 py-0.5 rounded-full font-medium border border-emerald-200/60">
                正常在保
              </span>
            </div>
            <h3 class="text-base font-bold text-slate-900 mt-1.5 leading-tight flex items-center gap-2">
              <span>{{ policy.name }}</span>
            </h3>
            <div class="text-[11px] text-slate-500 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
              <span>承保机构：<strong class="text-slate-700">{{ policy.company }}</strong></span>
              <span v-if="policy.policyNo" class="font-mono text-slate-600">单号：{{ policy.policyNo }}</span>
              <span v-if="policy.paymentAccount" class="text-slate-600">
                <i class="fa-regular fa-credit-card text-sky-600 mr-0.5"></i>{{ policy.paymentAccount }}
              </span>
            </div>
          </div>
        </div>

        <button
          @click="$emit('close')"
          class="text-slate-400 hover:text-slate-600 p-1.5 rounded-xl hover:bg-slate-200/50 transition cursor-pointer"
          title="关闭"
        >
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 核心统计概览横幅 -->
      <div class="p-4 bg-slate-50/80 border-b border-slate-100">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
          <!-- 累计已缴 -->
          <div class="bg-white p-2.5 rounded-xl border border-emerald-100/80 shadow-2xs">
            <span class="text-slate-400 text-[11px] block">累计已实缴</span>
            <div class="text-base font-extrabold text-emerald-700 font-mono mt-0.5">
              ¥{{ formatMoney(totalPaidAmount) }}
            </div>
            <span class="text-[10px] text-slate-400 mt-0.5 block">共 {{ paidRecords.length }} 期已扣款</span>
          </div>

          <!-- 待缴/预测 -->
          <div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <span class="text-slate-400 text-[11px] block">未到期待缴</span>
            <div class="text-base font-extrabold text-slate-700 font-mono mt-0.5">
              ¥{{ formatMoney(totalUpcomingAmount) }}
            </div>
            <span class="text-[10px] text-slate-400 mt-0.5 block">剩余 {{ upcomingRecords.length }} 期预测</span>
          </div>

          <!-- 标保期次 -->
          <div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <span class="text-slate-400 text-[11px] block">标准期缴保费</span>
            <div class="text-base font-extrabold text-slate-900 font-mono mt-0.5">
              ¥{{ formatMoney(policy.premium) }}
            </div>
            <span class="text-[10px] text-slate-500 mt-0.5 block">
              {{ policy.paymentYears > 1 ? `交 ${policy.paymentYears} 年` : '一年期消费险' }} · {{ policy.paymentMonthDay || '按期' }}
            </span>
          </div>

          <!-- 异常状态 / 进度 -->
          <div
            class="p-2.5 rounded-xl shadow-2xs border"
            :class="unpaidRecords.length > 0 ? 'bg-rose-50 border-rose-200 text-rose-800' : 'bg-white border-slate-200/80 text-slate-600'"
          >
            <span class="text-[11px] block" :class="unpaidRecords.length > 0 ? 'text-rose-600 font-bold' : 'text-slate-400'">
              {{ unpaidRecords.length > 0 ? '扣费异常警示' : '长期缴费进度' }}
            </span>
            <div v-if="unpaidRecords.length > 0" class="text-base font-extrabold text-rose-700 font-mono mt-0.5">
              {{ unpaidRecords.length }} 笔异常
            </div>
            <div v-else class="text-base font-extrabold text-sky-700 font-mono mt-0.5">
              {{ paymentProgress }}%
            </div>
            <span class="text-[10px] block mt-0.5 truncate" :class="unpaidRecords.length > 0 ? 'text-rose-600 font-medium' : 'text-slate-400'">
              {{ unpaidRecords.length > 0 ? '需核验银行卡余额' : `已完成 ${paidRecords.length}/${totalPlanPeriods} 期` }}
            </span>
          </div>
        </div>

        <!-- 长期险进度条 (期数大于1年时显示) -->
        <div v-if="totalPlanPeriods > 1" class="mt-3 pt-2.5 border-t border-slate-200/60">
          <div class="flex justify-between text-[11px] text-slate-500 mb-1">
            <span>缴费年限进度</span>
            <span class="font-mono text-slate-700 font-medium">已缴纳 {{ paidRecords.length }} 期 / 共 {{ totalPlanPeriods }} 期 ({{ paymentProgress }}%)</span>
          </div>
          <div class="w-full bg-slate-200/80 h-2 rounded-full overflow-hidden">
            <div
              class="bg-gradient-to-r from-emerald-500 to-sky-500 h-full rounded-full transition-all duration-300"
              :style="{ width: `${paymentProgress}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- 筛选与操作操作栏 -->
      <div class="px-5 py-2.5 bg-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
        <!-- 状态筛选胶囊 -->
        <div class="inline-flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
          <button
            @click="filterStatus = 'all'"
            :class="filterStatus === 'all' ? 'bg-white shadow-2xs text-slate-900 font-semibold' : 'text-slate-500 hover:text-slate-800'"
            class="px-2.5 py-1 rounded-md transition cursor-pointer"
          >
            全部 ({{ policyPayments.length }})
          </button>
          <button
            @click="filterStatus = 'paid'"
            :class="filterStatus === 'paid' ? 'bg-white shadow-2xs text-emerald-700 font-semibold' : 'text-slate-500 hover:text-slate-800'"
            class="px-2.5 py-1 rounded-md transition cursor-pointer"
          >
            已缴流水 ({{ paidRecords.length }})
          </button>
          <button
            @click="filterStatus = 'upcoming'"
            :class="filterStatus === 'upcoming' ? 'bg-white shadow-2xs text-slate-700 font-semibold' : 'text-slate-500 hover:text-slate-800'"
            class="px-2.5 py-1 rounded-md transition cursor-pointer"
          >
            未到期预测 ({{ upcomingRecords.length }})
          </button>
          <button
            v-if="unpaidRecords.length > 0"
            @click="filterStatus = 'unpaid'"
            :class="filterStatus === 'unpaid' ? 'bg-rose-600 text-white shadow-2xs font-bold' : 'text-rose-700 hover:bg-rose-50'"
            class="px-2.5 py-1 rounded-md transition cursor-pointer flex items-center space-x-1"
          >
            <span>扣费异常</span>
            <span class="px-1.5 py-0.2 bg-white text-rose-700 text-[10px] rounded-full font-bold">{{ unpaidRecords.length }}</span>
          </button>
        </div>

        <!-- 快捷操作：登记续保/补录流水 & 前往台账 -->
        <div class="flex items-center space-x-2">
          <button
            type="button"
            @click="openAddRecord"
            class="inline-flex items-center space-x-1 px-2.5 py-1 text-xs font-medium rounded-lg text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition cursor-pointer"
            title="为当前保单登记新一期续保或补录扣费"
          >
            <i class="fa-solid fa-plus text-[10px]"></i>
            <span>登记/补录</span>
          </button>
          <button
            type="button"
            @click="navigateToLedger"
            class="inline-flex items-center space-x-1 px-2.5 py-1 text-xs font-medium rounded-lg text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 transition cursor-pointer"
            title="在家庭缴费台账大盘中查看全部流水"
          >
            <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
            <span>前往台账大盘</span>
          </button>
        </div>
      </div>

      <!-- 单期内联修改 / 补录表单抽屉 (展开时显示) -->
      <div v-if="editingRecord" class="bg-amber-50/70 border-b border-amber-200/80 p-4 animate-in slide-in-from-top-2 duration-150">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-1.5 text-xs font-bold text-amber-900">
            <i class="fa-solid fa-pen-to-square text-amber-600"></i>
            <span>{{ isAddingNew ? `登记新期数续费 (${editingRecord.year}年)` : `修改流水：${editingRecord.year} 年度 (第 ${editingRecord.periodIndex} 期)` }}</span>
          </div>
          <button @click="cancelEdit" class="text-amber-700 hover:text-amber-900 text-xs p-0.5 cursor-pointer">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <form @submit.prevent="submitRecordEdit" class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label class="block font-medium text-slate-700 mb-1">扣费年份</label>
            <input
              v-model.number="editingRecord.year"
              type="number"
              min="2000"
              max="2050"
              required
              class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 font-mono focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="block font-medium text-slate-700 mb-1">实缴保费金额 (¥)</label>
            <input
              v-model.number="editingRecord.paidAmount"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 font-mono font-bold focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="block font-medium text-slate-700 mb-1">实际缴费扣款日期</label>
            <input
              v-model="editingRecord.paidDate"
              type="date"
              class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="block font-medium text-slate-700 mb-1">状态</label>
            <select
              v-model="editingRecord.paid"
              class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-sky-500"
              :class="editingRecord.paid ? 'text-emerald-700' : 'text-rose-700'"
            >
              <option :value="true">已完成扣费 (实缴)</option>
              <option :value="false">扣款失败 / 异常</option>
            </select>
          </div>
          <div class="sm:col-span-3">
            <label class="block font-medium text-slate-700 mb-1">流水备注 / 扣款凭据说明</label>
            <input
              v-model="editingRecord.note"
              placeholder="如：建行尾号8888自动代扣、已核对账单..."
              class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div class="flex items-end space-x-2">
            <button
              type="submit"
              class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-1.5 px-3 rounded-lg font-bold text-xs shadow-xs transition cursor-pointer"
            >
              保存流水
            </button>
            <button
              type="button"
              @click="cancelEdit"
              class="bg-white border border-slate-200 text-slate-600 py-1.5 px-3 rounded-lg font-medium text-xs hover:bg-slate-100 transition cursor-pointer"
            >
              取消
            </button>
          </div>
        </form>
      </div>

      <!-- 流水明细列表区域 -->
      <div class="p-5 overflow-y-auto custom-scrollbar flex-1 space-y-3">
        <div v-if="filteredPayments.length === 0" class="py-12 text-center text-slate-400 text-xs">
          <i class="fa-solid fa-file-circle-question text-3xl text-slate-300 mb-2 block"></i>
          <span>当前筛选分类下暂无缴费记录</span>
        </div>

        <div
          v-for="item in filteredPayments"
          :key="item.key"
          class="bg-white rounded-2xl border transition-all duration-150 p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-sky-300 hover:shadow-xs"
          :class="getCardBorderClass(item)"
        >
          <!-- 左侧：期数、应缴日、状态 -->
          <div class="flex items-start space-x-3 min-w-0">
            <div
              class="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
              :class="getStatusIconClass(item)"
            >
              <span v-if="item.periodIndex && policy.paymentYears > 1">#{{ item.periodIndex }}</span>
              <i v-else-if="item.status === 'paid'" class="fa-solid fa-check"></i>
              <i v-else-if="item.status === 'unpaid'" class="fa-solid fa-exclamation"></i>
              <i v-else class="fa-regular fa-clock"></i>
            </div>

            <div class="min-w-0">
              <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                <span class="font-bold text-xs text-slate-900 font-mono">
                  {{ item.year }} 年度
                  <span v-if="item.periodIndex && policy.paymentYears > 1" class="text-slate-400 font-normal">
                    (第 {{ item.periodIndex }} 期)
                  </span>
                </span>
                <!-- 状态 Badge -->
                <span
                  v-if="item.status === 'paid'"
                  class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100/80 text-emerald-800 font-semibold border border-emerald-200/60 inline-flex items-center gap-1"
                >
                  <i class="fa-solid fa-circle-check text-[9px] text-emerald-600"></i>
                  <span>已完成扣款</span>
                </span>
                <span
                  v-else-if="item.status === 'unpaid'"
                  class="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-bold border border-rose-200 inline-flex items-center gap-1 animate-pulse"
                >
                  <i class="fa-solid fa-triangle-exclamation text-[9px]"></i>
                  <span>扣款异常</span>
                </span>
                <span
                  v-else
                  class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium border border-slate-200/60 inline-flex items-center gap-1"
                >
                  <i class="fa-regular fa-calendar-check text-[9px] text-slate-400"></i>
                  <span>未到期预测</span>
                </span>
              </div>

              <!-- 日期与账户 -->
              <div class="text-[11px] text-slate-500 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
                <span title="计划应缴日期">
                  <i class="fa-regular fa-calendar text-slate-400 mr-1 text-[10px]"></i>
                  应缴: <span class="font-mono">{{ item.dueDate }}</span>
                </span>
                <span v-if="item.paidDate && item.status === 'paid'" class="text-emerald-700">
                  <i class="fa-solid fa-receipt text-emerald-500 mr-1 text-[10px]"></i>
                  实缴: <span class="font-mono">{{ item.paidDate }}</span>
                </span>
                <span v-if="item.note" class="text-slate-400 truncate max-w-[200px]" :title="item.note">
                  · {{ item.note }}
                </span>
              </div>
            </div>
          </div>

          <!-- 右侧：金额与操作按钮 -->
          <div class="flex items-center justify-between sm:justify-end gap-3 shrink-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-100">
            <div class="text-right">
              <div class="text-sm font-extrabold font-mono" :class="item.status === 'paid' ? 'text-emerald-700' : (item.status === 'unpaid' ? 'text-rose-700' : 'text-slate-800')">
                ¥{{ formatMoney(item.premium) }}
              </div>
              <div v-if="item.hasCustomAmount" class="text-[10px] text-amber-600 font-medium" :title="'标保参考: ¥' + formatMoney(item.standardPremium)">
                实缴调整
              </div>
            </div>

            <!-- 操作按钮组 -->
            <div class="flex items-center space-x-1.5 text-xs">
              <!-- 快速状态切换 -->
              <button
                type="button"
                v-if="item.status === 'paid'"
                @click="$emit('toggle-confirm', item, false)"
                class="px-2 py-1 rounded-lg text-slate-500 hover:text-rose-700 hover:bg-rose-50 border border-slate-200 transition text-[11px] cursor-pointer"
                title="标记为扣款异常/未扣费"
              >
                标记异常
              </button>
              <button
                type="button"
                v-else
                @click="$emit('toggle-confirm', item, true)"
                class="px-2 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 font-semibold transition text-[11px] cursor-pointer"
                title="一键标记为已自动代扣/已缴费"
              >
                确认已缴
              </button>

              <!-- 编辑单期明细 -->
              <button
                type="button"
                @click="startEdit(item)"
                class="p-1.5 text-slate-500 hover:text-sky-700 hover:bg-sky-50 rounded-lg transition cursor-pointer"
                title="修改该期扣款金额、日期或备注"
              >
                <i class="fa-regular fa-pen-to-square"></i>
              </button>

              <!-- 剔除/断缴 (仅限未缴或异常) -->
              <button
                v-if="item.status !== 'paid'"
                type="button"
                @click="confirmSkip(item)"
                class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition cursor-pointer"
                title="标记断缴并从台账中彻底剔除"
              >
                <i class="fa-regular fa-trash-can"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 弹窗底部操作栏 -->
      <div class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
        <div class="text-slate-400 text-[11px]">
          共计 {{ policyPayments.length }} 期排期记录 · 数据自动流转落盘
        </div>
        <button
          type="button"
          @click="$emit('close')"
          class="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl font-medium text-xs transition cursor-pointer"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { formatMoney, getTypeBadgeClass, getTodayStr } from '../../utils/helpers.js';

const props = defineProps({
  policy: {
    type: Object,
    default: null
  },
  allPaymentSchedule: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'toggle-confirm', 'save-record', 'skip-record', 'navigate-to-ledger']);

const filterStatus = ref('all');
const editingRecord = ref(null);
const isAddingNew = ref(false);

// 提取当前保单的所有缴费排期与历史流水
const policyPayments = computed(() => {
  if (!props.policy) return [];
  const pIdStr = String(props.policy.id);
  return (props.allPaymentSchedule || []).filter(s => {
    return !s.isVehicle && String(s.policyId) === pIdStr;
  });
});

const paidRecords = computed(() => policyPayments.value.filter(s => s.status === 'paid'));
const upcomingRecords = computed(() => policyPayments.value.filter(s => s.status === 'upcoming'));
const unpaidRecords = computed(() => policyPayments.value.filter(s => s.status === 'unpaid'));

const totalPaidAmount = computed(() => paidRecords.value.reduce((sum, s) => sum + (Number(s.premium) || 0), 0));
const totalUpcomingAmount = computed(() => upcomingRecords.value.reduce((sum, s) => sum + (Number(s.premium) || 0), 0));

const totalPlanPeriods = computed(() => {
  if (!props.policy) return 1;
  const pYears = Number(props.policy.paymentYears) || 1;
  return pYears;
});

const paymentProgress = computed(() => {
  const total = totalPlanPeriods.value;
  if (total <= 1) {
    return paidRecords.value.length > 0 ? 100 : 0;
  }
  const ratio = (paidRecords.value.length / total) * 100;
  return Math.min(100, Math.round(ratio));
});

const filteredPayments = computed(() => {
  if (filterStatus.value === 'all') return policyPayments.value;
  return policyPayments.value.filter(s => s.status === filterStatus.value);
});

function getCardBorderClass(item) {
  if (item.status === 'unpaid') return 'border-rose-200 bg-rose-50/20';
  if (item.status === 'paid') return 'border-slate-200/80 bg-white';
  return 'border-slate-200/60 bg-slate-50/40';
}

function getStatusIconClass(item) {
  if (item.status === 'paid') return 'bg-emerald-100 text-emerald-700';
  if (item.status === 'unpaid') return 'bg-rose-100 text-rose-700';
  return 'bg-slate-100 text-slate-500';
}

function startEdit(item) {
  isAddingNew.value = false;
  editingRecord.value = {
    key: item.key,
    policyId: item.policyId,
    year: item.year,
    paid: item.status === 'paid',
    paidAmount: item.premium,
    paidDate: item.paidDate || item.dueDate || getTodayStr(),
    note: item.note || '',
    periodIndex: item.periodIndex
  };
}

function openAddRecord() {
  if (!props.policy) return;
  isAddingNew.value = true;
  // 智能推断下一个需要补录或续保的年份
  const currentYear = new Date().getFullYear();
  const existingYears = policyPayments.value.map(p => p.year);
  const nextYear = existingYears.length > 0 ? Math.max(...existingYears) + 1 : currentYear;

  editingRecord.value = {
    key: `p_${props.policy.id}_${nextYear}`,
    policyId: props.policy.id,
    year: nextYear,
    paid: true,
    paidAmount: Number(props.policy.premium) || 0,
    paidDate: getTodayStr(),
    note: '提前续保登记 / 流水补录',
    periodIndex: existingYears.length + 1
  };
}

function cancelEdit() {
  editingRecord.value = null;
  isAddingNew.value = false;
}

function submitRecordEdit() {
  if (!editingRecord.value) return;
  const targetYear = Number(editingRecord.value.year);
  const originalKey = editingRecord.value.key;
  const standardKey = `p_${editingRecord.value.policyId}_${targetYear}`;

  emit('save-record', {
    key: standardKey,
    oldKey: (!isAddingNew.value && originalKey && originalKey !== standardKey) ? originalKey : undefined,
    policyId: editingRecord.value.policyId,
    year: targetYear,
    paid: editingRecord.value.paid,
    paidAmount: Number(editingRecord.value.paidAmount) || 0,
    paidDate: editingRecord.value.paidDate,
    note: editingRecord.value.note
  });
  editingRecord.value = null;
  isAddingNew.value = false;
}

function confirmSkip(item) {
  if (confirm(`确认将《${item.name}》(${item.year}年) 标记为断缴并从台账中彻底剔除吗？\n\n剔除后该年份将不再计入家庭保费支出统计。`)) {
    emit('skip-record', item);
  }
}

function navigateToLedger() {
  emit('close');
  emit('navigate-to-ledger', props.policy);
}
</script>
