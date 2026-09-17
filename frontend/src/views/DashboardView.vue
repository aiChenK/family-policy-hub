<template>
  <section class="space-y-6">
    <!-- 顶部状态与警示横幅 -->
    <DashboardAlertBanner
      :unpaid-count="unpaidCount"
      :unpaid-amount="unpaidAmount"
      :vehicles-expiring-count="vehiclesExpiringCount"
      :near-due-count="nearDueCount"
      :near-due-amount="nearDueAmount"
      @navigate-to-payments="$emit('navigate-to-payments', $event)"
      @navigate-to-vehicles="$emit('navigate-to-vehicles', $event)"
      @navigate-to-calendar="$emit('navigate-to-calendar')"
    />

    <!-- 统计指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
      <!-- 全家年度保费总支出 (双轨呈现：人身险 + 车险) -->
      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">全家年度保费总支出</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-sky-50 text-sky-700 border border-sky-100">双轨统筹</span>
          </div>
          <div class="mt-2 flex items-baseline space-x-2">
            <span class="text-xl sm:text-2xl font-bold text-slate-900">¥{{ formatMoney(displayTotalAnnualPremium) }}</span>
            <span class="text-xs text-slate-400">/ 年</span>
          </div>
          <!-- 双轨细分拆解 -->
          <div class="mt-2.5 flex items-center gap-1.5 text-xs flex-wrap">
            <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]" title="人身商业险年保费支出">
              <i class="fa-solid fa-shield-heart text-sky-500 text-[10px]"></i>
              <span>人身险: ¥{{ formatMoney(lifeAnnualPremium) }}</span>
            </span>
            <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]" title="家庭车辆车险年保费支出">
              <i class="fa-solid fa-car-side text-emerald-500 text-[10px]"></i>
              <span>车险: ¥{{ formatMoney(vehicleAnnualPremium) }}</span>
            </span>
          </div>
        </div>
        <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center text-xs text-emerald-600">
          <i class="fa-solid fa-arrows-rotate mr-1"></i>
          <span>含 {{ activePolicies.length }} 笔商业险 + {{ activeVehiclesCount }} 辆在保爱车</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-sky-50/70 sm:text-sky-50 text-5xl sm:text-6xl pointer-events-none -z-0">
          <i class="fa-solid fa-wallet"></i>
        </div>
      </div>

      <!-- 历年累计已缴保费 (双轨呈现：人身险 + 车险) -->
      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">历年累计已缴保费</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">历史实缴</span>
          </div>
          <div class="mt-2 flex items-baseline space-x-2">
            <span class="text-xl sm:text-2xl font-bold text-slate-900">¥{{ formatMoney(totalPaidAmount) }}</span>
          </div>
          <!-- 双轨细分拆解 -->
          <div class="mt-2.5 flex items-center gap-1.5 text-xs flex-wrap">
            <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]" title="历年累计人身商业险实缴">
              <i class="fa-solid fa-shield-heart text-sky-500 text-[10px]"></i>
              <span>人身险: ¥{{ formatMoney(lifeTotalPaidAmount) }}</span>
            </span>
            <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]" title="历年累计车辆车险实缴">
              <i class="fa-solid fa-car-side text-emerald-500 text-[10px]"></i>
              <span>车险: ¥{{ formatMoney(vehicleTotalPaidAmount) }}</span>
            </span>
          </div>
        </div>
        <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center text-xs text-slate-500">
          <i class="fa-solid fa-circle-check text-emerald-500 mr-1"></i>
          <span>汇总人身险 {{ lifePaidRecordsCount }} 笔 + 车险 {{ vehiclePaidRecordsCount }} 笔</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-indigo-50/70 sm:text-indigo-50 text-5xl sm:text-6xl pointer-events-none -z-0">
          <i class="fa-solid fa-vault"></i>
        </div>
      </div>

      <!-- 近期待扣 / 未来待代扣卡片 -->
      <div
        @click="$emit('navigate-to-payments', nearDueCount > 0 ? 'upcoming' : 'all')"
        class="bg-white p-4 sm:p-5 rounded-2xl border transition cursor-pointer relative overflow-hidden group hover:shadow-md border-slate-200/80 hover:border-sky-300"
      >
        <div class="text-xs font-semibold uppercase tracking-wider flex items-center justify-between text-slate-500">
          <span>{{ nearDueCount > 0 ? '近30天自动待扣' : '未来待代扣保费' }}</span>
          <span v-if="nearDueCount > 0" class="w-2 h-2 rounded-full bg-sky-500"></span>
        </div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-xl sm:text-2xl font-extrabold text-sky-700">{{ nearDueCount > 0 ? nearDueCount : upcomingCount }}</span>
          <span class="text-xs font-medium text-slate-500">笔待扣缴</span>
        </div>
        <div class="mt-3 flex items-center justify-between text-xs">
          <span class="text-slate-600 font-semibold font-mono">¥{{ formatMoney(nearDueCount > 0 ? nearDueAmount : upcomingAmount) }}</span>
          <span class="text-sky-600 group-hover:translate-x-0.5 transition font-medium">查看台账 &gt;</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-sky-50/70 sm:text-sky-50 text-5xl sm:text-6xl pointer-events-none -z-0">
          <i class="fa-solid fa-clock-rotate-left"></i>
        </div>
      </div>

      <!-- 有效商业人身险卡片 (专注家庭成员健康防线) -->
      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden">
        <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">有效商业人身险</div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-xl sm:text-2xl font-bold text-sky-600">{{ activePolicies.length }}</span>
          <span class="text-xs text-slate-500">笔在保 / {{ stoppedPolicies.length }} 笔停缴</span>
        </div>
        <div class="mt-3 flex items-center text-xs text-slate-500">
          <i class="fa-solid fa-users mr-1 text-sky-500"></i>
          <span>已覆盖 {{ coveredMemberCount }}/{{ members.length }} 位成员 ({{ isAllCovered ? '全员参保' : `${Math.round((coveredMemberCount / (members.length || 1)) * 100)}%` }})</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-sky-50/70 sm:text-sky-50 text-5xl sm:text-6xl pointer-events-none -z-0">
          <i class="fa-solid fa-shield-heart"></i>
        </div>
      </div>
    </div>

    <!-- 核心图表行 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- 历年保费走势柱状图 -->
      <div class="lg:col-span-2 bg-white p-4 sm:p-6 rounded-2xl border border-slate-200/80 shadow-sm">
        <div class="flex justify-between items-center mb-4">
          <div>
            <h3 class="text-sm sm:text-base font-bold text-slate-900">历年保费支出走势 (2018 - 2026)</h3>
            <p class="text-xs text-slate-500">从早期单人参保到全家成熟保障体系的费用变动</p>
          </div>
          <span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-lg font-medium shrink-0">柱状趋势</span>
        </div>
        <div class="h-56 sm:h-64 relative">
          <canvas ref="trendCanvas"></canvas>
        </div>
      </div>

      <!-- 家庭成员保费占比 -->
      <div class="bg-white p-4 sm:p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
        <div class="mb-4">
          <h3 class="text-sm sm:text-base font-bold text-slate-900">家庭成员年保费占比</h3>
          <p class="text-xs text-slate-500">当前各成员商业保费贡献比例</p>
        </div>
        <div class="h-48 sm:h-52 relative flex-1">
          <canvas ref="memberPieCanvas"></canvas>
        </div>
      </div>
    </div>

    <!-- 1. 家庭成员保费汇总卡片 -->
    <div class="bg-white p-4 sm:p-6 rounded-2xl border border-slate-200/80 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-4">
        <div>
          <h3 class="text-sm sm:text-base font-bold text-slate-900">家庭成员保障档案概览</h3>
          <p class="text-xs text-slate-500 mt-0.5">点击卡片可快速筛选该成员名下的所有保单</p>
        </div>
        <button
          @click="$emit('open-members')"
          class="inline-flex items-center justify-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-700 rounded-xl text-xs font-medium transition cursor-pointer self-start sm:self-auto"
          title="管理家庭成员档案与社保信息"
        >
          <i class="fa-solid fa-user-gear text-sky-600"></i>
          <span>管理成员档案</span>
        </button>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <div
          v-for="(val, name) in memberSummary"
          :key="name"
          @click="$emit('select-member-filter', name)"
          class="p-3 sm:p-4 rounded-xl border border-slate-200 hover:border-sky-300 hover:shadow-md transition cursor-pointer bg-slate-50/50 flex flex-col justify-between"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-900 text-sm">{{ name }}</span>
            <span class="w-2 h-2 rounded-full bg-sky-500"></span>
          </div>
          <div class="mt-2.5 sm:mt-3">
            <div class="text-[11px] sm:text-xs text-slate-500">年度预算</div>
            <div class="text-base sm:text-lg font-extrabold text-sky-700">¥{{ formatMoney(val) }}</div>
          </div>
          <div class="mt-2 pt-2 border-t border-slate-200/60 text-xs text-slate-500 flex justify-between">
            <span>保单数</span>
            <span class="font-medium text-slate-800">{{ countPoliciesByMember(name) }} 张</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 家庭爱车与车险资产概览卡片 -->
    <div class="bg-white p-4 sm:p-6 rounded-2xl border border-slate-200/80 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-4">
        <div>
          <div class="flex items-center space-x-2 flex-wrap gap-y-1">
            <h3 class="text-sm sm:text-base font-bold text-slate-900">家庭爱车保障与资产概览</h3>
            <span v-if="vehicles.length > 0" class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
              共 {{ vehicles.length }} 辆 · {{ activeVehiclesCount }} 辆在保
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">展示机动车辆最新车险保障与到期状态，点击卡片直达爱车专区</p>
        </div>
        <button
          @click="$emit('navigate-to-vehicles')"
          class="inline-flex items-center justify-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-700 rounded-xl text-xs font-medium transition cursor-pointer self-start sm:self-auto"
          title="前往车辆资产与车险专区"
        >
          <i class="fa-solid fa-car-rear text-sky-600"></i>
          <span>管理车辆资产</span>
          <i class="fa-solid fa-angle-right text-[10px] ml-0.5"></i>
        </button>
      </div>

      <!-- 有车辆时卡片网格 -->
      <div v-if="vehicles.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="veh in vehicles"
          :key="veh.id"
          @click="$emit('navigate-to-vehicles')"
          class="p-4 rounded-xl border border-slate-200 hover:border-sky-300 hover:shadow-md transition cursor-pointer bg-slate-50/50 flex flex-col justify-between group"
        >
          <div>
            <!-- 车牌与状态胶囊 -->
            <div class="flex items-center justify-between mb-2">
              <div
                v-if="veh.plateType === 'green'"
                class="px-2 py-0.5 rounded bg-gradient-to-b from-white via-emerald-100 to-emerald-300 border border-emerald-600 text-slate-950 font-extrabold font-mono text-xs tracking-wider shadow-2xs inline-flex items-center space-x-1 shrink-0 whitespace-nowrap select-none"
                title="新能源车牌"
              >
                <i class="fa-solid fa-bolt text-emerald-700 text-[9px]"></i>
                <span>{{ veh.plateNo }}</span>
              </div>
              <div
                v-else-if="veh.plateType === 'yellow'"
                class="px-2 py-0.5 rounded bg-amber-300 border border-amber-600 text-slate-900 font-extrabold font-mono text-xs tracking-wider shadow-2xs shrink-0 whitespace-nowrap select-none"
              >
                <span>{{ veh.plateNo }}</span>
              </div>
              <div
                v-else
                class="px-2 py-0.5 rounded bg-blue-600 border border-blue-400 text-white font-extrabold font-mono text-xs tracking-wider shadow-2xs shrink-0 whitespace-nowrap select-none"
              >
                <span>{{ veh.plateNo }}</span>
              </div>

              <!-- 到期状态胶囊 -->
              <span
                v-if="getVehicleDaysUntilExpire(veh) !== null && getVehicleDaysUntilExpire(veh) < 0"
                class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-100 text-rose-700 border border-rose-200"
              >
                已脱保
              </span>
              <span
                v-else-if="getVehicleDaysUntilExpire(veh) !== null && getVehicleDaysUntilExpire(veh) <= 30"
                class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-100 text-amber-800 border border-amber-200 flex items-center space-x-1"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></span>
                <span>剩 {{ getVehicleDaysUntilExpire(veh) }} 天</span>
              </span>
              <span
                v-else-if="getVehicleActivePolicy(veh)"
                class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-700 border border-emerald-200"
              >
                在保中
              </span>
              <span
                v-else
                class="text-[10px] px-2 py-0.5 rounded-full font-medium bg-slate-200 text-slate-600"
              >
                待录保单
              </span>
            </div>

            <!-- 车型与归属所有人 -->
            <div class="font-bold text-slate-800 text-sm truncate group-hover:text-sky-600 transition" :title="veh.model">
              {{ veh.model || '未填写车型' }}
            </div>
            <div class="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
              <span>所有人:</span>
              <span class="font-medium text-slate-700 truncate max-w-[120px]">{{ veh.companyName || veh.owner || '家庭' }}</span>
              <span v-if="veh.isCompany || veh.companyName" class="text-[9px] px-1 bg-indigo-50 text-indigo-600 rounded">公户</span>
            </div>
          </div>

          <div class="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs">
            <div>
              <div class="text-slate-400 text-[10px]">最新年保费</div>
              <div class="text-sm font-extrabold text-slate-900">
                ¥{{ formatMoney(getVehicleActivePolicy(veh)?.totalPremium || 0) }}
              </div>
            </div>
            <div class="text-right">
              <div class="text-slate-400 text-[10px]">承保公司</div>
              <div class="text-xs font-semibold text-slate-700 truncate max-w-[90px]">
                {{ getVehicleActivePolicy(veh)?.company || '未录入' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 暂无车辆引导 -->
      <div v-else class="p-8 text-center border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
        <i class="fa-solid fa-car text-3xl text-slate-300 mb-2"></i>
        <p class="text-xs text-slate-500 mb-3">暂未录入家庭车辆资产与车险保单，录入后可在此享受脱保预警与保费汇总</p>
        <button
          @click="$emit('navigate-to-vehicles')"
          class="px-3.5 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer inline-flex items-center space-x-1"
        >
          <i class="fa-solid fa-plus text-[10px]"></i>
          <span>登记第一辆车</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { formatMoney, getTodayStr } from '../utils/helpers.js';
import { extractVehicleInsuranceRecords } from '../utils/payment-schedule.js';
import { AppCharts } from '../utils/charts.js';
import DashboardAlertBanner from '../components/dashboard/DashboardAlertBanner.vue';

const props = defineProps({
  unpaidCount: { type: Number, default: 0 },
  unpaidAmount: { type: Number, default: 0 },
  nearDueCount: { type: Number, default: 0 },
  nearDueAmount: { type: Number, default: 0 },
  upcomingCount: { type: Number, default: 0 },
  upcomingAmount: { type: Number, default: 0 },
  pendingDueCount: { type: Number, default: 0 },
  pendingDueAmount: { type: Number, default: 0 },
  activeAnnualPremium: { type: Number, default: 0 },
  totalAnnualPremium: { type: Number, default: 0 },
  lifeAnnualPremium: { type: Number, default: 0 },
  vehicleAnnualPremium: { type: Number, default: 0 },
  activeVehiclesCount: { type: Number, default: 0 },
  vehiclesExpiringCount: { type: Number, default: 0 },
  vehicles: { type: Array, default: () => [] },
  totalPaidAmount: { type: Number, default: 0 },
  paidRecordsCount: { type: Number, default: 0 },
  lifeTotalPaidAmount: { type: Number, default: 0 },
  vehicleTotalPaidAmount: { type: Number, default: 0 },
  lifePaidRecordsCount: { type: Number, default: 0 },
  vehiclePaidRecordsCount: { type: Number, default: 0 },
  activePolicies: { type: Array, default: () => [] },
  stoppedPolicies: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  coveredMemberCount: { type: Number, default: 0 },
  isAllCovered: { type: Boolean, default: false },
  memberSummary: { type: Object, default: () => ({}) },
  allPaymentSchedule: { type: Array, default: () => [] },
  allPolicies: { type: Array, default: () => [] }
});

const emit = defineEmits([
  'navigate-to-payments',
  'navigate-to-calendar',
  'navigate-to-pending-payments',
  'navigate-to-vehicles',
  'select-member-filter',
  'open-members'
]);

const trendCanvas = ref(null);
const memberPieCanvas = ref(null);

const displayTotalAnnualPremium = computed(() => {
  if (props.totalAnnualPremium) return props.totalAnnualPremium;
  if (props.lifeAnnualPremium || props.vehicleAnnualPremium) {
    return (props.lifeAnnualPremium || 0) + (props.vehicleAnnualPremium || 0);
  }
  return props.activeAnnualPremium || 0;
});

function countPoliciesByMember(name) {
  return (props.allPolicies || []).filter(p => {
    if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
      return p.insuredMembers.includes(name);
    }
    return p.member === name;
  }).length;
}

// 辅助函数：获取车辆最新一期或在保保单
function getVehicleActivePolicy(v) {
  if (!v) return null;
  const records = extractVehicleInsuranceRecords(v);
  if (records.length === 0) return null;
  const today = getTodayStr();
  const unexpired = records.filter(r => {
    if (r.endDate) return r.endDate >= today;
    return Number(r.year) >= new Date().getFullYear();
  });
  if (unexpired.length === 0) return records[0];
  const running = unexpired.find(r => r.startDate && r.startDate <= today && r.endDate >= today);
  return running || unexpired[0];
}

// 辅助函数：获取车辆距离到期天数
function getVehicleDaysUntilExpire(v) {
  const active = getVehicleActivePolicy(v);
  const target = active || (extractVehicleInsuranceRecords(v)[0]);
  if (!target || !target.endDate) return null;
  const today = new Date(getTodayStr());
  const endDate = new Date(target.endDate);
  const diffTime = endDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function updateCharts() {
  nextTick(() => {
    if (trendCanvas.value) {
      AppCharts.renderTrendChart(trendCanvas.value, props.allPaymentSchedule);
    }
    if (memberPieCanvas.value) {
      AppCharts.renderMemberPieChart(memberPieCanvas.value, props.activePolicies);
    }
  });
}

onMounted(() => {
  updateCharts();
});

watch(
  () => [props.allPaymentSchedule, props.activePolicies],
  () => {
    updateCharts();
  },
  { deep: true }
);

onBeforeUnmount(() => {
  AppCharts.destroyAll();
});
</script>
