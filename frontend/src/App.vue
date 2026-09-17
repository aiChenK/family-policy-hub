<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <!-- 0. 访问安全保护遮罩层 (全屏拦截未认证访问) -->
    <AuthLock
      v-if="authState?.required && !authState?.authenticated"
      :auth-state="authState"
      @login="handleLogin"
    />

    <!-- 1. 认证通过或免密系统视图主体 -->
    <template v-else-if="isSystemUnlocked">
      <!-- 顶部全局导航栏 -->
      <HeaderNav
        :tabs="tabs"
        :current-tab="currentTab"
        :is-api-connected="isApiConnected"
        :saving="saving"
        :auth-state="authState"
        :member-count="(data.members || []).length"
        :covered-member-count="coveredMembersCount"
        :is-all-covered="isAllCovered"
        :active-policy-count="activePolicies.length"
        :vehicle-count="(data.vehicles || []).length"
        :company-count="(data.companies || []).length"
        @update:current-tab="currentTab = $event"
        @open-phones="showPhoneModal = true"
        @open-members="(tab) => openMemberModal(tab === 'companies' ? 'companies' : 'members')"
        @open-companies="openMemberModal('companies')"
        @open-cleaner="showCleanerModal = true"
        @export-json="handleExportJson"
        @export-ics="handleExportIcs"
        @import-json="handleImportJson"
        @logout="handleLogout"
      />

      <!-- 主视图路由容器 -->
      <main class="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 pb-24 md:pb-8">
        <!-- Tab 1: 保障总览 -->
        <DashboardView
          v-if="currentTab === 'dashboard'"
          :unpaid-count="unpaidCount"
          :unpaid-amount="unpaidAmount"
          :near-due-count="nearDueCount"
          :near-due-amount="nearDueAmount"
          :upcoming-count="upcomingCount"
          :upcoming-amount="upcomingAmount"
          :active-annual-premium="activeAnnualPremium"
          :total-annual-premium="totalAnnualPremium"
          :life-annual-premium="lifeAnnualPremium"
          :vehicle-annual-premium="vehicleAnnualPremium"
          :active-vehicles-count="activeVehiclesCount"
          :vehicles="data.vehicles || []"
          :vehicles-expiring-count="vehiclesExpiringCount"
          :total-paid-amount="totalPaidAmount"
          :paid-records-count="paidRecordsCount"
          :life-total-paid-amount="lifeTotalPaidAmount"
          :vehicle-total-paid-amount="vehicleTotalPaidAmount"
          :life-paid-records-count="lifePaidRecordsCount"
          :vehicle-paid-records-count="vehiclePaidRecordsCount"
          :active-policies="activePolicies"
          :stopped-policies="stoppedPolicies"
          :members="data.members || []"
          :covered-member-count="coveredMembersCount"
          :is-all-covered="isAllCovered"
          :member-summary="data.memberSummary || {}"
          :all-payment-schedule="allPaymentSchedule"
          :all-policies="data.policies || []"
          @navigate-to-payments="navigateToPayments"
          @navigate-to-calendar="currentTab = 'calendar'"
          @navigate-to-pending-payments="navigateToPayments('upcoming')"
          @navigate-to-vehicles="navigateToVehicles"
          @select-member-filter="selectMemberFilter"
          @open-members="openMemberModal('members')"
        />

        <!-- Tab 2: 保单列表管理 -->
        <PoliciesView
          v-else-if="currentTab === 'policies'"
          :policies="data.policies || []"
          :members="data.members || []"
          :active-count="activePolicies.length"
          :stopped-count="stoppedPolicies.length"
          :initial-member-filter="policyFilterMember"
          @open-add-modal="openAddModal"
          @open-edit-modal="openEditModal"
          @view-policy-detail="viewPolicyDetail"
          @view-policy-payments="viewPolicyPayments"
          @open-members="openMemberModal('members')"
        />

        <!-- Tab 3: 车辆资产与车险专区 -->
        <VehiclesView
          v-else-if="currentTab === 'vehicles'"
          :vehicles="data.vehicles || []"
          :members="data.members || []"
          :companies="data.companies || []"
          :phone-config="phoneConfig"
          :initial-filter-status="vehicleInitialFilterStatus"
          @save-vehicles="handleSaveVehicles"
          @open-companies="openMemberModal('companies')"
          @view-company="openMemberModal('companies', $event)"
        />

        <!-- Tab 4: 历年缴费台账与支出流水 -->
        <PaymentsView
          v-else-if="currentTab === 'payments'"
          :all-payment-schedule="allPaymentSchedule"
          :policies="data.policies || []"
          :members="data.members || []"
          :vehicles="data.vehicles || []"
          :paid-records-count="paidRecordsCount"
          :upcoming-count="upcomingCount"
          :unpaid-records-count="unpaidCount"
          :default-filter-status="paymentInitialFilterStatus"
          @toggle-confirm="togglePaymentConfirm"
          @save-record="savePaymentRecordDetail"
          @skip-record="skipPaymentRecord"
        />

        <!-- Tab 5: 缴费日历 -->
        <CalendarView
          v-else-if="currentTab === 'calendar'"
          :calendar-groups="calendarGroups"
          @export-ics="handleExportIcs"
        />

        <!-- Tab 6: 就医应急卡 -->
        <EmergencyView
          v-else-if="currentTab === 'emergency'"
          :members="data.members || []"
          :active-policies="activePolicies"
          :default-member="data.members?.[0] || ''"
          :phone-config="phoneConfig"
          @open-phones="showPhoneModal = true"
        />
      </main>

      <!-- 全局浮动操作提示与 Toast -->
      <ToastAlert :toast="toast" />

      <!-- 保单详情查看模态框 -->
      <PolicyDetailModal
        :policy="activeModalPolicy"
        :phone-config="phoneConfig"
        @close="activeModalPolicy = null"
        @view-payments="viewPolicyPayments"
      />

      <!-- 保单专属缴费流水与排期台账模态框 -->
      <PolicyPaymentsModal
        :policy="activePaymentsPolicy"
        :all-payment-schedule="allPaymentSchedule"
        @close="closePolicyPayments"
        @toggle-confirm="togglePaymentConfirm"
        @save-record="savePaymentRecordDetail"
        @skip-record="skipPaymentRecord"
        @navigate-to-ledger="handleNavigateToLedger"
      />

      <!-- 保单录入与编辑模态框 -->
      <PolicyEditModal
        :show="editForm.show"
        :is-new="editForm.isNew"
        :form-data="editForm.data"
        :members="data.members || []"
        @update:show="editForm.show = $event"
        @save="savePolicyForm"
        @delete="deletePolicy"
      />

      <!-- 孤儿附件智能扫描与清理模态框 -->
      <AttachmentCleanerModal
        :show="showCleanerModal"
        @update:show="showCleanerModal = $event"
        @toast="showToast"
      />

      <!-- 保险机构官方客服专线与报案电话配置模态框 -->
      <InsurancePhoneModal
        :show="showPhoneModal"
        :phone-config="phoneConfig"
        @update:show="showPhoneModal = $event"
        @save="handleSavePhones"
      />

      <!-- 家庭成员与企业主体综合配置模态框 -->
      <MemberManagementModal
        :show="showMemberModal"
        :initial-tab="memberModalTab"
        :initial-focus-company="memberModalFocusCompany"
        :members="data.members || []"
        :family-members="data.familyMembers || []"
        :policies="data.policies || []"
        :vehicles="data.vehicles || []"
        :companies="data.companies || []"
        :member-summary="data.memberSummary || {}"
        @update:show="showMemberModal = $event"
        @update-members="handleUpdateMembers"
        @cascade-rename="handleCascadeRename"
        @update-companies="handleUpdateCompanies"
        @toast="showToast"
      />

      <!-- 移动端专用吸底 TabBar -->
      <MobileTabBar
        :current-tab="currentTab"
        :unpaid-count="unpaidCount"
        :vehicles-expiring-count="vehiclesExpiringCount"
        @update:current-tab="currentTab = $event"
        @open-phones="showPhoneModal = true"
        @open-members="openMemberModal('members')"
        @open-companies="openMemberModal('companies')"
        @export-ics="handleExportIcs"
      />
    </template>

    <!-- 2. 系统就绪加载中兜底骨架（避免未命中分支导致的空白） -->
    <div v-else class="flex-1 flex flex-col items-center justify-center py-32 text-slate-400">
      <div class="w-9 h-9 border-3 border-sky-500/20 border-t-sky-600 rounded-full animate-spin mb-3"></div>
      <p class="text-xs font-medium text-slate-500">正在载入家庭保险资产...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getTodayStr } from './utils/helpers.js';
import { PaymentScheduleEngine, extractVehicleInsuranceRecords } from './utils/payment-schedule.js';

// 组合式函数引入
import { useAppData } from './composables/useAppData.js';
import { useAuth } from './composables/useAuth.js';
import { usePolicyActions } from './composables/usePolicyActions.js';
import { usePaymentActions } from './composables/usePaymentActions.js';

// 组件引入
import HeaderNav from './components/HeaderNav.vue';
import MobileTabBar from './components/MobileTabBar.vue';
import AuthLock from './components/AuthLock.vue';
import ToastAlert from './components/ToastAlert.vue';
import PolicyDetailModal from './components/PolicyDetailModal.vue';
import PolicyEditModal from './components/PolicyEditModal.vue';
import PolicyPaymentsModal from './components/policy/PolicyPaymentsModal.vue';
import AttachmentCleanerModal from './components/AttachmentCleanerModal.vue';
import InsurancePhoneModal from './components/InsurancePhoneModal.vue';
import MemberManagementModal from './components/MemberManagementModal.vue';

// 视图引入
import DashboardView from './views/DashboardView.vue';
import PoliciesView from './views/PoliciesView.vue';
import CalendarView from './views/CalendarView.vue';
import EmergencyView from './views/EmergencyView.vue';
import PaymentsView from './views/PaymentsView.vue';
import VehiclesView from './views/VehiclesView.vue';

// 1. 全局交互与弹窗挂载状态
const currentTab = ref('dashboard');
const showCleanerModal = ref(false);
const showPhoneModal = ref(false);
const showMemberModal = ref(false);
const memberModalTab = ref('members');
const memberModalFocusCompany = ref('');
const policyFilterMember = ref('');
const paymentInitialFilterStatus = ref('paid');
const vehicleInitialFilterStatus = ref('all');

function navigateToVehicles(status = 'all') {
  vehicleInitialFilterStatus.value = status;
  currentTab.value = 'vehicles';
}

// 2. 核心数据持久化与通用操作
const {
  data,
  isApiConnected,
  saving,
  toast,
  phoneConfig,
  showToast,
  clearSensitiveData,
  loadData,
  saveData,
  handleSavePhones,
  handleSaveVehicles,
  handleUpdateCompanies,
  handleUpdateMembers,
  handleCascadeRename
} = useAppData();

// 3. 全局鉴权管理与安全拦截
const {
  authReady,
  authState,
  isSystemUnlocked,
  checkAuth,
  handleLogin,
  handleLogout
} = useAuth({
  onLoginSuccess: loadData,
  onSecurityClear: () => {
    clearSensitiveData();
    activeModalPolicy.value = null;
    activePaymentsPolicy.value = null;
    editForm.value = { show: false, isNew: false, data: {} };
    showCleanerModal.value = false;
    showPhoneModal.value = false;
    showMemberModal.value = false;
    memberModalTab.value = 'members';
    memberModalFocusCompany.value = '';
  },
  showToast
});

// 4. 计算属性层
const activePolicies = computed(() => (data.value.policies || []).filter(p => p.status === 'active'));
const stoppedPolicies = computed(() => (data.value.policies || []).filter(p => p.status === 'stopped'));

const coveredMembersCount = computed(() => {
  const set = new Set();
  (activePolicies.value || []).forEach(p => {
    if (p.member) set.add(p.member);
  });
  return set.size;
});

const isAllCovered = computed(() => {
  const total = data.value.members ? data.value.members.length : 0;
  return total > 0 && coveredMembersCount.value >= total;
});

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

// 纯人身商业险年度在缴保费
const lifeAnnualPremium = computed(() => {
  return activePolicies.value.reduce((sum, p) => sum + (Number(p.premium) || 0), 0);
});

// 纯车辆车险最新年度保费
const vehicleAnnualPremium = computed(() => {
  return (data.value.vehicles || []).reduce((sum, v) => {
    const active = getVehicleActivePolicy(v);
    if (active) {
      return sum + Number(active.totalPremium || 0);
    }
    const comm = Number(v.commercialInsurance?.premium || 0);
    const comp = Number(v.compulsoryInsurance?.premium || 0);
    const tax = Number(v.compulsoryInsurance?.tax || 0);
    return sum + comm + comp + tax;
  }, 0);
});

// 在保/有保单爱车数量
const activeVehiclesCount = computed(() => {
  return (data.value.vehicles || []).filter(v => !!getVehicleActivePolicy(v)).length;
});

// 全家年度保费总支出（双轨汇总）
const totalAnnualPremium = computed(() => {
  return lifeAnnualPremium.value + vehicleAnnualPremium.value;
});

// 兼容老调用
const activeAnnualPremium = computed(() => totalAnnualPremium.value);

const allPaymentSchedule = computed(() => {
  return PaymentScheduleEngine.generateSchedule(data.value.policies, data.value.paymentRecords, new Date(), data.value.vehicles || []);
});

// 1. 扣费异常记录 (用户手动标记扣费失败)
const unpaidRecords = computed(() => allPaymentSchedule.value.filter(s => s.status === 'unpaid'));
const unpaidCount = computed(() => unpaidRecords.value.length);
const unpaidAmount = computed(() => unpaidRecords.value.reduce((sum, s) => sum + s.premium, 0));

// 2. 近30天即将自动代扣保费
const nearDueRecords = computed(() => allPaymentSchedule.value.filter(s => s.isNearUpcoming));
const nearDueCount = computed(() => nearDueRecords.value.length);
const nearDueAmount = computed(() => nearDueRecords.value.reduce((sum, s) => sum + s.premium, 0));

// 3. 已缴流水（包含已到期自动流转与车险实缴）
const paidRecords = computed(() => allPaymentSchedule.value.filter(s => s.status === 'paid'));
const paidRecordsCount = computed(() => paidRecords.value.length);
const totalPaidAmount = computed(() => paidRecords.value.reduce((sum, s) => sum + s.premium, 0));

// 细分人身险与车险实缴
const lifePaidRecords = computed(() => paidRecords.value.filter(s => !s.isVehicle));
const lifeTotalPaidAmount = computed(() => lifePaidRecords.value.reduce((sum, s) => sum + s.premium, 0));
const lifePaidRecordsCount = computed(() => lifePaidRecords.value.length);

const vehiclePaidRecords = computed(() => paidRecords.value.filter(s => s.isVehicle));
const vehicleTotalPaidAmount = computed(() => vehiclePaidRecords.value.reduce((sum, s) => sum + s.premium, 0));
const vehiclePaidRecordsCount = computed(() => vehiclePaidRecords.value.length);

// 4. 未来全部未到期预测
const upcomingRecords = computed(() => allPaymentSchedule.value.filter(s => s.status === 'upcoming'));
const upcomingCount = computed(() => upcomingRecords.value.length);
const upcomingAmount = computed(() => upcomingRecords.value.reduce((sum, s) => sum + s.premium, 0));

// 兼容老字段
const pendingDueCount = unpaidCount;
const pendingDueAmount = unpaidAmount;

const vehiclesExpiringCount = computed(() => {
  const today = new Date(getTodayStr());
  return (data.value.vehicles || []).filter(v => {
    const records = extractVehicleInsuranceRecords(v);
    const end = (records.length > 0 && records[0].endDate) || v.commercialInsurance?.endDate || v.compulsoryInsurance?.endDate;
    if (!end) return false;
    const endDate = new Date(end);
    const diffDays = Math.ceil((endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays <= 30;
  }).length;
});

const calendarGroups = computed(() => {
  return PaymentScheduleEngine.generateCalendarGroups(activePolicies.value, data.value.paymentRecords, new Date(), data.value.vehicles || []);
});

const tabs = computed(() => [
  { id: 'dashboard', name: '保障总览', icon: 'fa-solid fa-chart-pie' },
  { id: 'policies', name: '保单管理', icon: 'fa-solid fa-file-shield' },
  {
    id: 'vehicles',
    name: '爱车与车险',
    icon: 'fa-solid fa-car',
    badge: vehiclesExpiringCount.value > 0
      ? `${vehiclesExpiringCount.value} 辆需续保`
      : (data.value.vehicles && data.value.vehicles.length > 0 ? `${data.value.vehicles.length} 辆` : null),
    badgeClass: vehiclesExpiringCount.value > 0
      ? 'bg-amber-500 text-white font-bold animate-pulse'
      : 'bg-slate-100 text-slate-600'
  },
  {
    id: 'payments',
    name: '缴费台账',
    icon: 'fa-solid fa-receipt',
    badge: unpaidCount.value > 0 ? `${unpaidCount.value} 笔异常` : null,
    badgeClass: 'bg-rose-500 text-white font-bold animate-pulse'
  },
  { id: 'calendar', name: '缴费日历', icon: 'fa-solid fa-calendar-days' },
  { id: 'emergency', name: '就医应急卡', icon: 'fa-solid fa-kit-medical' }
]);

// 5. 保单行为管理
const {
  activeModalPolicy,
  activePaymentsPolicy,
  editForm,
  viewPolicyDetail,
  viewPolicyPayments,
  closePolicyPayments,
  openAddModal,
  openEditModal,
  savePolicyForm,
  deletePolicy
} = usePolicyActions({ data, saveData, showToast });

// 6. 缴费核销与备份导入导出
const {
  togglePaymentConfirm,
  confirmAllDuePayments,
  savePaymentRecordDetail,
  skipPaymentRecord,
  handleExportJson,
  handleImportJson,
  handleExportIcs
} = usePaymentActions({ data, activePolicies, saveData, showToast });

// 页面导航与筛选交互
const selectMemberFilter = (m) => {
  policyFilterMember.value = m;
  currentTab.value = 'policies';
};

const navigateToPayments = (status = 'paid') => {
  currentTab.value = 'payments';
  paymentInitialFilterStatus.value = status;
};

const handleNavigateToLedger = (pol) => {
  navigateToPayments('all');
};

const navigateToPendingPayments = () => {
  navigateToPayments('upcoming');
};

const openMemberModal = (tab = 'members', focusCompany = '') => {
  memberModalTab.value = tab;
  memberModalFocusCompany.value = focusCompany;
  showMemberModal.value = true;
};

// 7. 初始化生命周期
onMounted(async () => {
  try {
    const auth = await checkAuth();
    if (!auth.authRequired || auth.authenticated) {
      await loadData();
    } else {
      clearSensitiveData();
    }
  } catch (e) {
    console.error('Auth verification error:', e);
  } finally {
    authReady.value = true;
  }
});
</script>
