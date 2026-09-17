<template>
  <section class="space-y-6">
    <!-- 顶部到期高急预警横幅与统计指标卡片 -->
    <VehicleStatsBanner
      :vehicle-total-count="vehicles.length"
      :vehicles-with-insurance-count="vehiclesWithInsuranceCount"
      :vehicles-without-insurance-count="vehiclesWithoutInsuranceCount"
      :total-vehicle-premium="totalVehiclePremium"
      :expiring-soon-count="expiringSoonCount"
      :inspection-soon-count="inspectionSoonCount"
      @filter-expiring="filterStatus = 'expiring'"
    />

    <!-- 筛选栏与解耦的两步操作按钮 -->
    <div class="bg-white p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
      <!-- 第一行：搜索框与主行动按钮组 -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div class="relative flex-1 min-w-0">
          <input
            v-model="searchQuery"
            placeholder="搜索车牌/车型/车主/保司..."
            class="text-xs bg-slate-50 border border-slate-200 rounded-xl pl-7 pr-3 py-2 w-full font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
          <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-[10px]"></i>
        </div>

        <!-- 移动端并排的两步核心操作按钮 -->
        <div class="grid grid-cols-2 sm:flex items-center gap-2 shrink-0">
          <!-- 步骤一：录入车辆信息 -->
          <button
            @click="openAddVehicleModal"
            class="inline-flex items-center justify-center space-x-1.5 px-3 py-2 text-xs font-semibold rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 transition border border-slate-200/80 shadow-2xs cursor-pointer"
            title="第一步：录入车辆行驶证与车架号档案"
          >
            <i class="fa-solid fa-car text-sky-600"></i>
            <span>添加爱车</span>
          </button>

          <!-- 步骤二：录入车险保单 -->
          <button
            @click="openAddPolicyModal('')"
            :disabled="vehicles.length === 0"
            class="inline-flex items-center justify-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl text-white bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            title="第二步：选择车辆录入当期或历年车险保单"
          >
            <i class="fa-solid fa-shield-halved"></i>
            <span>录入车险保单</span>
          </button>
        </div>
      </div>

      <!-- 第二行：车主筛选、到期状态胶囊与视图切换 -->
      <div class="flex flex-wrap gap-2 items-center justify-between pt-1 border-t border-slate-100 sm:border-0 sm:pt-0">
        <div class="flex items-center gap-2 flex-1 min-w-0 overflow-x-auto no-scrollbar py-0.5">
          <!-- 车主与归属筛选 -->
          <select
            v-model="filterOwner"
            class="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500 shrink-0"
          >
            <option value="">全部车辆 ({{ vehicles.length }})</option>
            <optgroup label="个人私家车">
              <option v-for="m in members" :key="m" :value="m">{{ m }} 的车辆</option>
            </optgroup>
            <optgroup label="企业/公司车辆" v-if="hasCompanyVehicles">
              <option value="__company__">所有公司公户车 ({{ companyVehicleCount }})</option>
              <option v-for="c in companyNames" :key="c" :value="c">{{ c }}</option>
            </optgroup>
          </select>

          <!-- 到期与保单状态筛选 -->
          <div class="inline-flex bg-slate-100 p-0.5 rounded-xl text-xs font-medium shrink-0">
            <button
              @click="filterStatus = 'all'"
              :class="filterStatus === 'all' ? 'bg-white shadow-sm text-slate-900 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2.5 sm:px-3 py-1.5 rounded-lg transition cursor-pointer"
            >
              全部
            </button>
            <button
              @click="filterStatus = 'active'"
              :class="filterStatus === 'active' ? 'bg-white shadow-sm text-emerald-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2.5 sm:px-3 py-1.5 rounded-lg transition cursor-pointer"
            >
              在保
            </button>
            <button
              @click="filterStatus = 'expiring'"
              :class="filterStatus === 'expiring' ? 'bg-white shadow-sm text-amber-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2 sm:px-3 py-1.5 rounded-lg transition flex items-center space-x-1 cursor-pointer"
            >
              <span>待续保</span>
              <span v-if="expiringSoonCount > 0" class="px-1.5 py-0.2 bg-amber-500 text-white text-[10px] rounded-full font-bold">{{ expiringSoonCount }}</span>
            </button>
            <button
              @click="filterStatus = 'no_policy'"
              :class="filterStatus === 'no_policy' ? 'bg-white shadow-sm text-slate-800 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2 sm:px-3 py-1.5 rounded-lg transition flex items-center space-x-1 cursor-pointer"
            >
              <span>待录</span>
              <span v-if="vehiclesWithoutInsuranceCount > 0" class="px-1.5 py-0.2 bg-slate-400 text-white text-[10px] rounded-full">{{ vehiclesWithoutInsuranceCount }}</span>
            </button>
          </div>
        </div>

        <!-- 视图切换 -->
        <div class="inline-flex bg-slate-100 p-0.5 rounded-xl text-xs font-medium shrink-0">
          <button
            @click="viewMode = 'grid'"
            :class="viewMode === 'grid' ? 'bg-white shadow-sm text-sky-700 font-bold' : 'text-slate-500'"
            class="px-2.5 py-1 rounded-lg cursor-pointer"
            title="卡片视图"
          >
            <i class="fa-solid fa-table-cells-large"></i>
          </button>
          <button
            @click="viewMode = 'table'"
            :class="viewMode === 'table' ? 'bg-white shadow-sm text-sky-700 font-bold' : 'text-slate-500'"
            class="px-2.5 py-1 rounded-lg cursor-pointer"
            title="表格视图"
          >
            <i class="fa-solid fa-list"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 卡片视图 -->
    <div v-if="viewMode === 'grid' && filteredVehicles.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <VehicleCard
        v-for="veh in filteredVehicles"
        :key="veh.id"
        :veh="veh"
        :phone-config="phoneConfig"
        @open-history="openHistoryModal"
        @renew="openRenewModal"
        @add-policy="openAddPolicyModal"
        @edit-vehicle="openEditVehicleModal"
        @delete-vehicle="confirmDeleteVehicle"
        @edit-policy="openEditPolicyModal"
        @delete-policy="confirmDeleteRecord"
        @view-company="$emit('view-company', $event)"
      />
    </div>

    <!-- 表格视图 -->
    <VehicleTable
      v-else-if="viewMode === 'table' && filteredVehicles.length > 0"
      :filtered-vehicles="filteredVehicles"
      @view-company="$emit('view-company', $event)"
      @renew="openRenewModal"
      @add-policy="openAddPolicyModal"
      @open-history="openHistoryModal"
      @edit-vehicle="openEditVehicleModal"
      @delete-vehicle="confirmDeleteVehicle"
    />

    <!-- 空状态提示 -->
    <div v-else class="bg-white rounded-3xl border border-slate-200 p-12 text-center text-slate-400">
      <i class="fa-solid fa-car text-5xl mb-3 text-slate-300"></i>
      <h4 class="text-base font-bold text-slate-700 mb-1">暂无车辆与车险记录</h4>
      <p class="text-xs text-slate-400 mb-5">先录入爱车基本档案（车牌、车型、行驶证），随后录入或补录历年车险保单。</p>
      <button
        @click="openAddVehicleModal"
        class="inline-flex items-center space-x-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
      >
        <i class="fa-solid fa-plus"></i>
        <span>添加第一辆车</span>
      </button>
    </div>

    <!-- 1. 车辆纯基本信息录入/编辑模态框 (解耦第一步) -->
    <VehicleEditModal
      :show="editModal.show"
      :is-new="editModal.isNew"
      :form-data="editModal.data"
      :members="members"
      :companies="companies"
      @update:show="editModal.show = $event"
      @open-companies="$emit('open-companies')"
      @save="handleSaveVehicle"
      @delete="confirmDeleteVehicle"
    />

    <!-- 2. 独立车险保单录入/续保/编辑模态框 (解耦第二步) -->
    <VehiclePolicyModal
      :show="policyModal.show"
      :is-new="policyModal.isNew"
      :form="policyModal.form"
      :vehicles="vehicles"
      :lock-vehicle="policyModal.lockVehicle"
      @update:show="policyModal.show = $event"
      @save="handleSavePolicy"
    />

    <!-- 3. 历年车险投保档案与凭证管理独立弹窗 -->
    <VehicleHistoryModal
      :show="historyModal.show"
      :veh="historyModalVehicle"
      :phone-config="phoneConfig"
      @update:show="historyModal.show = $event"
      @add-policy="openAddPolicyModal"
      @edit-policy="openEditPolicyModal"
      @delete-policy="confirmDeleteRecord"
    />

    <!-- 4. 新车添加成功后的平滑引导提示框 -->
    <VehicleGuidePrompt
      :show="promptGuide.show"
      :vehicle="promptGuide.vehicle"
      @cancel="promptGuide.show = false"
      @proceed="handleProceedToPolicy"
    />
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { getTodayStr, deepClone } from '../utils/helpers.js';
import {
  getVehicleRecords,
  getLatestPolicy,
  getActivePolicy,
  getDaysUntilExpire,
  cleanAttachmentList,
  buildDefaultPolicyForm,
  formatPolicyRecord,
  buildDefaultVehicleForm,
  countInspectionSoon,
  filterVehicles
} from '../utils/vehicle-helpers.js';
import VehicleStatsBanner from '../components/vehicle/VehicleStatsBanner.vue';
import VehicleCard from '../components/vehicle/VehicleCard.vue';
import VehicleTable from '../components/vehicle/VehicleTable.vue';
import VehicleEditModal from '../components/VehicleEditModal.vue';
import VehiclePolicyModal from '../components/VehiclePolicyModal.vue';
import VehicleHistoryModal from '../components/vehicle/VehicleHistoryModal.vue';
import VehicleGuidePrompt from '../components/vehicle/VehicleGuidePrompt.vue';

const props = defineProps({
  vehicles: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  companies: { type: Array, default: () => [] },
  phoneConfig: { type: Object, default: () => ({}) },
  initialFilterStatus: { type: String, default: 'all' }
});

const emit = defineEmits(['save-vehicles', 'open-companies', 'view-company']);

const searchQuery = ref('');
const filterOwner = ref('');
const filterStatus = ref(props.initialFilterStatus || 'all');
const viewMode = ref('grid');

watch(
  () => props.initialFilterStatus,
  (val) => {
    if (val) filterStatus.value = val;
  }
);

// 历年保单弹窗状态
const historyModal = ref({ show: false, vehicleId: '' });
const historyModalVehicle = computed(() => {
  return (props.vehicles || []).find(v => v.id === historyModal.value.vehicleId) || null;
});

function openHistoryModal(veh) {
  historyModal.value = { show: true, vehicleId: veh.id };
}

// 模态框状态
const editModal = ref({ show: false, isNew: false, data: {} });
const policyModal = ref({ show: false, isNew: true, lockVehicle: false, form: {} });
const promptGuide = ref({ show: false, vehicle: null });

// 统计计算：仅统计当前有效在保保单的年保费
const totalVehiclePremium = computed(() => {
  return (props.vehicles || []).reduce((sum, v) => {
    const active = getActivePolicy(v);
    return sum + (active ? Number(active.totalPremium || 0) : 0);
  }, 0);
});

const vehiclesWithInsuranceCount = computed(() => {
  return (props.vehicles || []).filter(v => !!getActivePolicy(v)).length;
});

const vehiclesWithoutInsuranceCount = computed(() => {
  return (props.vehicles || []).filter(v => !getActivePolicy(v)).length;
});

const expiringSoonCount = computed(() => {
  return (props.vehicles || []).filter(v => {
    const days = getDaysUntilExpire(v);
    return days !== null && days >= 0 && days <= 30;
  }).length;
});

const companyVehicles = computed(() => {
  return (props.vehicles || []).filter(v => v.isCompany || v.companyName);
});

const hasCompanyVehicles = computed(() => companyVehicles.value.length > 0);
const companyVehicleCount = computed(() => companyVehicles.value.length);

const companyNames = computed(() => {
  const set = new Set();
  companyVehicles.value.forEach(v => {
    const name = (v.companyName || v.owner || '').trim();
    if (name) set.add(name);
  });
  return Array.from(set);
});

const inspectionSoonCount = computed(() => countInspectionSoon(props.vehicles));

const filteredVehicles = computed(() => {
  return filterVehicles(props.vehicles, {
    query: searchQuery.value,
    owner: filterOwner.value,
    status: filterStatus.value
  });
});

// 车辆操作
function openAddVehicleModal() {
  editModal.value = {
    show: true,
    isNew: true,
    data: buildDefaultVehicleForm(props.members)
  };
}

function openEditVehicleModal(veh) {
  const copy = deepClone(veh);
  if (copy.isCompany === undefined) {
    copy.isCompany = !!copy.companyName;
  }
  editModal.value = { show: true, isNew: false, data: copy };
  if (!editModal.value.data.attachments) {
    editModal.value.data.attachments = [];
  }
}

function handleSaveVehicle() {
  const list = [...props.vehicles];
  const isNew = editModal.value.isNew;
  const target = editModal.value.data;

  if (isNew) {
    target.insuranceRecords = target.insuranceRecords || [];
    target.attachments = target.attachments || [];
    list.push(target);
  } else {
    const idx = list.findIndex(v => v.id === target.id);
    if (idx >= 0) {
      target.insuranceRecords = list[idx].insuranceRecords || [];
      list[idx] = { ...list[idx], ...target };
    }
  }

  emit('save-vehicles', list);
  editModal.value.show = false;

  if (isNew) {
    promptGuide.value = { show: true, vehicle: target };
  }
}

function handleProceedToPolicy() {
  const veh = promptGuide.value.vehicle;
  promptGuide.value.show = false;
  if (veh) {
    openAddPolicyModal(veh.id);
  }
}

async function confirmDeleteVehicle(id) {
  const targetVeh = props.vehicles.find(v => v.id === id);
  if (!targetVeh) return;
  if (confirm(`确定要删除车辆【${targetVeh.plateNo}】的信息及所有关联车险档案吗？关联附件也将同步清理。`)) {
    const records = getVehicleRecords(targetVeh);
    for (const rec of records) {
      await cleanAttachmentList(rec.attachments);
    }
    await cleanAttachmentList(targetVeh.attachments);

    const list = props.vehicles.filter(v => v.id !== id);
    emit('save-vehicles', list);
    editModal.value.show = false;
  }
}

// 保单操作
function openAddPolicyModal(vehicleId = '') {
  const targetId = vehicleId || (props.vehicles[0]?.id || '');
  const targetVeh = props.vehicles.find(v => v.id === targetId);
  const records = targetVeh ? getVehicleRecords(targetVeh) : [];
  const prevRec = records.length > 0 ? records[0] : null;

  policyModal.value = {
    show: true,
    isNew: true,
    lockVehicle: !!vehicleId,
    form: buildDefaultPolicyForm(targetId, targetVeh, prevRec)
  };
}

function openRenewModal(veh) {
  openAddPolicyModal(veh.id);
}

function openEditPolicyModal(veh, rec) {
  const cPrem = Number(rec.commercialPremium) || 0;
  const compPrem = Number(rec.compulsoryPremium) || 0;
  const tax = Number(rec.tax) || 0;
  const accidentPrem = Number(rec.accidentPremium) || 0;
  const defaultTotal = rec.totalPremium !== undefined && rec.totalPremium !== null
    ? Number(rec.totalPremium)
    : (cPrem + compPrem + tax + accidentPrem);

  policyModal.value = {
    show: true,
    isNew: false,
    lockVehicle: true,
    form: {
      ...deepClone(rec),
      vehicleId: veh.id,
      totalPremium: defaultTotal,
      commercialPremium: rec.commercialPremium ?? null,
      compulsoryPremium: rec.compulsoryPremium ?? null,
      tax: rec.tax ?? null,
      accidentPremium: rec.accidentPremium ?? null,
      accidentPolicyNo: rec.accidentPolicyNo || '',
      cashback: rec.cashback ?? null
    }
  };
}

function handleSavePolicy() {
  const { form, isNew } = policyModal.value;
  const list = [...props.vehicles];
  const targetVeh = list.find(v => v.id === form.vehicleId);
  if (!targetVeh) return;

  let records = getVehicleRecords(targetVeh);
  const formattedRec = formatPolicyRecord(form, targetVeh);

  if (isNew) {
    records.unshift(formattedRec);
  } else {
    const rIdx = records.findIndex(r => r.id === form.id);
    if (rIdx >= 0) {
      records[rIdx] = formattedRec;
    } else {
      records.unshift(formattedRec);
    }
  }

  records.sort((a, b) => (b.year || 0) - (a.year || 0));
  targetVeh.insuranceRecords = records;

  emit('save-vehicles', list);
  policyModal.value.show = false;
}

async function confirmDeleteRecord(veh, recId) {
  const records = getVehicleRecords(veh);
  const targetRec = records.find(r => r.id === recId);
  if (!targetRec) return;
  if (!confirm(`确定要删除 ${targetRec.year} 年度的车险保单记录吗？关联附件也将同步清理。`)) return;

  if (targetRec.attachments) {
    await cleanAttachmentList(targetRec.attachments);
  }

  const list = [...props.vehicles];
  const targetVeh = list.find(v => v.id === veh.id);
  if (targetVeh) {
    targetVeh.insuranceRecords = records.filter(r => r.id !== recId);
    emit('save-vehicles', list);
  }
}
</script>
