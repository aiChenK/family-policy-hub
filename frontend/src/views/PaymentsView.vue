<template>
  <section class="space-y-6">
    <!-- 顶部操作与筛选总览栏 -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
      <div class="flex flex-wrap gap-4 items-center justify-between">
        <div>
          <div class="flex items-center space-x-2.5">
            <h3 class="text-base font-bold text-slate-900">家庭保险缴费台账与支出明细</h3>
            <span class="text-xs bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full font-medium">自动流转 · 支出台账</span>
          </div>
          <p class="text-xs text-slate-500 mt-1">车险保单录入即自动计入实缴；长期与连续商业险到期自动按期代扣流转，无需逐笔手动打卡核验。</p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="openAddRecordModal"
            class="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center space-x-1.5 cursor-pointer"
            title="支持提前登记新一年续保（如2027年）或补录历史实际扣款流水"
          >
            <i class="fa-solid fa-plus text-[11px]"></i>
            <span>登记新一期续保 / 补录</span>
          </button>
        </div>
      </div>

      <!-- 状态筛选胶囊与多维过滤器 -->
      <div class="pt-2 border-t border-slate-100 flex flex-wrap gap-3 items-center justify-between">
        <!-- 状态快速筛选胶囊：仅保留已缴流水与未到期预测 -->
        <div class="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-xl text-xs font-medium">
          <button
            @click="paymentFilterStatus = 'paid'"
            :class="paymentFilterStatus === 'paid' ? 'bg-emerald-600 text-white shadow-sm font-semibold' : 'text-emerald-700 hover:bg-emerald-100/50'"
            class="px-3.5 py-1.5 rounded-lg transition cursor-pointer flex items-center space-x-1.5"
          >
            <i class="fa-solid fa-receipt text-[11px]"></i>
            <span>已缴流水</span>
            <span class="px-1.5 py-0.2 text-[10px] rounded-full font-bold" :class="paymentFilterStatus === 'paid' ? 'bg-white/20 text-white' : 'bg-emerald-200/60 text-emerald-800'">{{ paidRecordsCount }}</span>
          </button>
          <button
            @click="paymentFilterStatus = 'upcoming'"
            :class="paymentFilterStatus === 'upcoming' ? 'bg-slate-700 text-white shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'"
            class="px-3.5 py-1.5 rounded-lg transition cursor-pointer flex items-center space-x-1.5"
          >
            <i class="fa-regular fa-calendar-check text-[11px]"></i>
            <span>未到期预测</span>
            <span class="px-1.5 py-0.2 text-[10px] rounded-full font-bold" :class="paymentFilterStatus === 'upcoming' ? 'bg-white/20 text-white' : 'bg-slate-200 text-slate-700'">{{ upcomingCount }}</span>
          </button>
          <button
            v-if="unpaidRecordsCount > 0"
            @click="paymentFilterStatus = 'unpaid'"
            :class="paymentFilterStatus === 'unpaid' ? 'bg-rose-600 text-white shadow-sm font-bold animate-pulse' : 'text-rose-700 hover:bg-rose-100/50'"
            class="px-3 py-1.5 rounded-lg transition flex items-center space-x-1 cursor-pointer"
          >
            <span>扣款异常</span>
            <span class="px-1.5 py-0.2 bg-white text-rose-700 text-[10px] rounded-full font-extrabold">{{ unpaidRecordsCount }}</span>
          </button>
        </div>

        <!-- 年份与险种下拉筛选 -->
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <div class="relative">
            <input
              v-model="paymentSearchQuery"
              placeholder="搜索产品/险种/车牌..."
              class="bg-slate-50 border border-slate-200 rounded-lg pl-7 pr-3 py-1.5 text-xs text-slate-700 w-36 focus:w-48 transition-all"
            />
            <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-[10px]"></i>
          </div>

          <select v-model="paymentFilterYear" class="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 font-medium text-slate-700">
            <option value="">全部年份</option>
            <option v-for="y in paymentAvailableYears" :key="y" :value="y">{{ y }} 年</option>
          </select>

          <select v-model="paymentFilterType" class="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 font-medium text-slate-700">
            <option value="">全部险种</option>
            <option value="重疾">重疾险/寿险</option>
            <option value="医疗">医疗消费险</option>
            <option value="意外">意外险</option>
            <option value="车险">车险 / 财产险</option>
            <option value="社保">社保/农保</option>
          </select>
        </div>
      </div>

      <!-- 缴费对象独立快捷筛选行 (人/车单选) -->
      <div class="pt-3 border-t border-slate-100 flex flex-wrap items-center gap-2 text-xs">
        <div class="flex items-center space-x-1.5 text-slate-500 font-medium shrink-0 mr-1">
          <i class="fa-solid fa-users-viewfinder text-sky-600 text-xs"></i>
          <span>缴费对象:</span>
        </div>

        <!-- 全部对象胶囊 -->
        <button
          @click="clearTargetFilter"
          :class="!selectedTarget ? 'bg-sky-600 text-white font-semibold shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-800'"
          class="px-2.5 py-1 rounded-lg transition-all flex items-center space-x-1 cursor-pointer"
        >
          <span>全部对象</span>
          <span class="text-[10px] opacity-80">({{ totalCurrentRecordsCount }})</span>
        </button>

        <!-- 分组1: 家庭成员 (人，单选) -->
        <div class="flex flex-wrap items-center gap-1.5">
          <button
            v-for="m in displayMembers"
            :key="'m_' + m"
            @click="selectTarget('member', m)"
            :class="isTargetSelected('member', m) ? 'bg-sky-600 text-white font-semibold shadow-xs' : 'bg-slate-100/90 text-slate-700 hover:bg-slate-200/90'"
            class="px-2.5 py-1 rounded-lg transition-all flex items-center space-x-1.5 cursor-pointer border border-transparent"
          >
            <i class="fa-solid fa-user text-[10px]" :class="isTargetSelected('member', m) ? 'text-white' : 'text-sky-600'"></i>
            <span>{{ m }}</span>
            <span class="text-[10px] opacity-75">({{ countScheduleByTarget('member', m) }})</span>
          </button>
        </div>

        <!-- 纵向分隔线 -->
        <div v-if="displayVehicles.length > 0" class="h-4 w-px bg-slate-200 mx-1 hidden sm:block"></div>

        <!-- 分组2: 车辆资产 (车，仅展示车牌，单选) -->
        <div class="flex flex-wrap items-center gap-1.5">
          <button
            v-for="v in displayVehicles"
            :key="'v_' + v.plateNo"
            @click="selectTarget('vehicle', v.plateNo)"
            :class="isTargetSelected('vehicle', v.plateNo) ? 'bg-sky-600 text-white font-semibold shadow-xs' : 'bg-slate-100/90 text-slate-700 hover:bg-slate-200/90'"
            class="px-2.5 py-1 rounded-lg transition-all flex items-center space-x-1.5 cursor-pointer border border-transparent"
            :title="v.model ? `${v.plateNo} (${v.model})` : v.plateNo"
          >
            <i class="fa-solid fa-car text-[10px]" :class="isTargetSelected('vehicle', v.plateNo) ? 'text-white' : (v.plateType === 'green' ? 'text-emerald-600' : 'text-blue-600')"></i>
            <span class="font-mono font-medium">{{ v.plateNo }}</span>
            <span class="text-[10px] opacity-75">({{ countScheduleByTarget('vehicle', v.plateNo) }})</span>
          </button>
        </div>

        <!-- 当前选中提示与快速清除 -->
        <div v-if="selectedTarget" class="flex items-center space-x-1.5 ml-auto text-[11px] text-slate-400">
          <span>当前筛选: <strong class="text-sky-600 font-semibold">{{ selectedTarget.value }}</strong></span>
          <button
            @click="clearTargetFilter"
            class="text-slate-400 hover:text-rose-600 transition cursor-pointer p-0.5"
            title="清空筛选恢复全部"
          >
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 缴费记录数据列表 -->
    <PaymentTable
      :payments="filteredPayments"
      :filter-status="paymentFilterStatus"
      :total-amount="filteredPaymentsTotalAmount"
      @edit-record="openEditRecordModal"
      @toggle-confirm="(item, status) => $emit('toggle-confirm', item, status)"
      @skip-record="confirmSkipRecord"
    />

    <!-- 单期缴费详情编辑 / 新一期续保登记弹窗 -->
    <PaymentRecordModal
      :is-open="isRecordModalOpen"
      :record="selectedRecordForEdit"
      :policies="policies"
      @close="isRecordModalOpen = false"
      @save="handleSaveRecord"
      @skip="handleSkipRecord"
    />
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { formatMoney, getTypeBadgeClass } from '../utils/helpers.js';
import { PaymentScheduleEngine } from '../utils/payment-schedule.js';
import PaymentRecordModal from '../components/PaymentRecordModal.vue';
import PaymentTable from '../components/payment/PaymentTable.vue';

const props = defineProps({
  allPaymentSchedule: { type: Array, default: () => [] },
  policies: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  vehicles: { type: Array, default: () => [] },
  paidRecordsCount: { type: Number, default: 0 },
  upcomingCount: { type: Number, default: 0 },
  unpaidRecordsCount: { type: Number, default: 0 },
  defaultFilterStatus: { type: String, default: 'paid' }
});

const emit = defineEmits(['toggle-confirm', 'save-record', 'skip-record']);

const paymentFilterStatus = ref(props.defaultFilterStatus === 'all' ? 'paid' : props.defaultFilterStatus);
const paymentFilterYear = ref('');
const paymentFilterType = ref('');
const paymentSearchQuery = ref('');

// 缴费对象单选状态管理 (对象格式为 { type: 'member'|'vehicle', value: 'xxx' }，null 代表全部)
const selectedTarget = ref(null);

const isTargetSelected = (type, val) => {
  return selectedTarget.value?.type === type && selectedTarget.value?.value === val;
};

const selectTarget = (type, val) => {
  if (selectedTarget.value?.type === type && selectedTarget.value?.value === val) {
    selectedTarget.value = null; // 再次点击取消选中恢复全部
  } else {
    selectedTarget.value = { type, value: val };
  }
};

const clearTargetFilter = () => {
  selectedTarget.value = null;
};

// 动态提取家庭成员对象 (结合 props.members 与实际台账去重，绝不硬编码)
const displayMembers = computed(() => {
  const set = new Set(props.members || []);
  (props.allPaymentSchedule || []).forEach(p => {
    if (!p.isVehicle && p.member) set.add(p.member);
  });
  return Array.from(set);
});

// 动态提取爱车对象 (结合 props.vehicles 与实际台账去重，仅展示车牌号，绝不硬编码)
const displayVehicles = computed(() => {
  const map = new Map();
  (props.vehicles || []).forEach(v => {
    if (v.plateNo) {
      map.set(v.plateNo, {
        plateNo: v.plateNo,
        plateType: v.plateType || 'blue',
        model: v.model || ''
      });
    }
  });
  (props.allPaymentSchedule || []).forEach(p => {
    if (p.isVehicle && p.plateNo && !map.has(p.plateNo)) {
      map.set(p.plateNo, {
        plateNo: p.plateNo,
        plateType: p.plateType || 'blue',
        model: p.name || ''
      });
    }
  });
  return Array.from(map.values());
});

// 动态统计当前流转状态下的各对象记录笔数
function countScheduleByTarget(type, val) {
  const status = paymentFilterStatus.value;
  return (props.allPaymentSchedule || []).filter(item => {
    if (status === 'paid' && item.status !== 'paid') return false;
    if (status === 'upcoming' && item.status !== 'upcoming') return false;
    if ((status === 'unpaid' || status === 'due') && item.status !== 'unpaid') return false;
    if (type === 'member') {
      return !item.isVehicle && item.member === val;
    }
    if (type === 'vehicle') {
      return item.isVehicle && item.plateNo === val;
    }
    return false;
  }).length;
}

// 当前流转状态下的总记录笔数
const totalCurrentRecordsCount = computed(() => {
  const status = paymentFilterStatus.value;
  return (props.allPaymentSchedule || []).filter(item => {
    if (status === 'paid' && item.status !== 'paid') return false;
    if (status === 'upcoming' && item.status !== 'upcoming') return false;
    if ((status === 'unpaid' || status === 'due') && item.status !== 'unpaid') return false;
    return true;
  }).length;
});

// 弹窗状态管理
const isRecordModalOpen = ref(false);
const selectedRecordForEdit = ref(null);

const openAddRecordModal = () => {
  selectedRecordForEdit.value = null;
  isRecordModalOpen.value = true;
};

const openEditRecordModal = (item) => {
  selectedRecordForEdit.value = item;
  isRecordModalOpen.value = true;
};

const handleSaveRecord = (formData) => {
  emit('save-record', formData);
};

const handleSkipRecord = (item) => {
  emit('skip-record', item);
};

const confirmSkipRecord = (item) => {
  if (!item) return;
  if (confirm(`确认将《${item.name}》(${item.year}年) 标记为断缴并从台账中彻底剔除吗？\n\n剔除后该年份将不再计入家庭保费支出统计，亦不会产生扣款异常提示。`)) {
    emit('skip-record', item);
  }
};

// 年份列表：在预测模式下按正序排列（2026, 2027, 2028...），在已缴模式下按倒序排列（2026, 2025...）
const paymentAvailableYears = computed(() => {
  const s = new Set();
  const baseList = (props.allPaymentSchedule || []).filter(p => {
    if (paymentFilterStatus.value === 'upcoming') return p.status === 'upcoming';
    if (paymentFilterStatus.value === 'paid') return p.status === 'paid';
    if (paymentFilterStatus.value === 'unpaid') return p.status === 'unpaid';
    return true;
  });
  baseList.forEach(p => s.add(p.year));
  const list = Array.from(s);
  if (paymentFilterStatus.value === 'upcoming') {
    return list.sort((a, b) => a - b);
  }
  return list.sort((a, b) => b - a);
});

const filteredPayments = computed(() => {
  return PaymentScheduleEngine.filterSchedule(props.allPaymentSchedule, {
    status: paymentFilterStatus.value,
    year: paymentFilterYear.value,
    type: paymentFilterType.value,
    search: paymentSearchQuery.value,
    selectedTargets: selectedTarget.value ? [selectedTarget.value] : []
  });
});

const filteredPaymentsTotalAmount = computed(() => {
  return filteredPayments.value.reduce((acc, curr) => acc + (Number(curr.premium) || 0), 0);
});
</script>
