<template>
  <section class="space-y-6">
    <!-- 筛选栏与操作 -->
    <div class="bg-white p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
      <!-- 第一行：搜索框与核心添加保单按钮 (手机端整齐占满) -->
      <div class="flex items-center gap-2">
        <div class="relative flex-1 min-w-0">
          <input
            v-model="searchQuery"
            placeholder="搜索保单号/产品/公司/投保人..."
            class="text-xs bg-slate-50 border border-slate-200 rounded-xl pl-7 pr-3 py-2 w-full font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
          <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-[10px]"></i>
        </div>

        <!-- 新增保单按钮 (核心主操作) -->
        <button
          @click="$emit('open-add-modal')"
          class="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl text-white bg-sky-600 hover:bg-sky-700 active:bg-sky-800 transition shadow-sm shrink-0 cursor-pointer"
        >
          <i class="fa-solid fa-plus text-[11px]"></i>
          <span>添加保单</span>
        </button>
      </div>

      <!-- 第二行：险种、扣费状态、视图切换与管理成员 -->
      <div class="flex flex-wrap gap-2 items-center justify-between">
        <div class="flex items-center gap-2 flex-1 min-w-0 overflow-x-auto no-scrollbar py-0.5">
          <!-- 险种筛选 -->
          <select
            v-model="filterType"
            class="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500 shrink-0"
          >
            <option value="">全部险种</option>
            <option value="家庭多人">👥 家庭多人单</option>
            <option value="重疾险">重疾险 / 寿险</option>
            <option value="意外险">意外险</option>
            <option value="医疗消费险">医疗消费险</option>
          </select>

          <!-- 状态筛选 -->
          <div class="inline-flex bg-slate-100 p-0.5 rounded-xl text-xs font-medium shrink-0">
            <button
              @click="filterStatus = 'all'"
              :class="filterStatus === 'all' ? 'bg-white shadow-sm text-slate-900 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2.5 sm:px-3 py-1.5 rounded-lg transition"
            >
              全部
            </button>
            <button
              @click="filterStatus = 'active'"
              :class="filterStatus === 'active' ? 'bg-white shadow-sm text-emerald-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2.5 sm:px-3 py-1.5 rounded-lg transition"
            >
              正常 ({{ activeCount }})
            </button>
            <button
              @click="filterStatus = 'stopped'"
              :class="filterStatus === 'stopped' ? 'bg-white shadow-sm text-slate-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
              class="px-2.5 sm:px-3 py-1.5 rounded-lg transition"
            >
              已停缴 ({{ stoppedCount }})
            </button>
          </div>
        </div>

        <div class="flex items-center space-x-2 shrink-0">
          <!-- 视图切换 -->
          <div class="inline-flex bg-slate-100 p-0.5 rounded-xl text-xs font-medium">
            <button
              @click="viewMode = 'grid'"
              :class="viewMode === 'grid' ? 'bg-white shadow-sm text-sky-700 font-bold' : 'text-slate-500'"
              class="px-2.5 py-1 rounded-lg"
              title="网格卡片视图"
            >
              <i class="fa-solid fa-table-cells-large"></i>
            </button>
            <button
              @click="viewMode = 'table'"
              :class="viewMode === 'table' ? 'bg-white shadow-sm text-sky-700 font-bold' : 'text-slate-500'"
              class="px-2.5 py-1 rounded-lg"
              title="数据表格视图"
            >
              <i class="fa-solid fa-list"></i>
            </button>
          </div>

          <!-- 管理成员按钮 -->
          <button
            @click="$emit('open-members')"
            class="inline-flex items-center space-x-1 px-2.5 py-1.5 text-xs font-medium rounded-xl text-slate-700 bg-slate-100 hover:bg-sky-50 hover:text-sky-700 transition shadow-2xs"
            title="管理家庭成员档案"
          >
            <i class="fa-solid fa-users text-sky-600"></i>
            <span class="hidden sm:inline">管理成员</span>
          </button>
        </div>
      </div>

      <!-- 第三行：独立的缴费对象快捷筛选行 (单行平滑横向滚动) -->
      <div class="pt-2.5 border-t border-slate-100 flex items-center gap-1.5 text-xs overflow-x-auto no-scrollbar whitespace-nowrap py-0.5">
        <div class="flex items-center space-x-1 text-slate-500 font-medium shrink-0 mr-1">
          <i class="fa-solid fa-users text-sky-600 text-xs"></i>
          <span>对象:</span>
        </div>

        <!-- 全部成员胶囊 -->
        <button
          @click="clearMemberFilter"
          :class="!selectedMember ? 'bg-sky-600 text-white font-semibold shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-800'"
          class="px-2.5 py-1 rounded-lg transition-all flex items-center space-x-1 cursor-pointer shrink-0"
        >
          <span>全部成员</span>
          <span class="text-[10px] opacity-80">({{ policies.length }})</span>
        </button>

        <!-- 各成员胶囊 (单选点击，再次点击取消) -->
        <button
          v-for="m in displayMembers"
          :key="m"
          @click="selectMember(m)"
          :class="selectedMember === m ? 'bg-sky-600 text-white font-semibold shadow-xs' : 'bg-slate-100/90 text-slate-700 hover:bg-slate-200/90'"
          class="px-2.5 py-1 rounded-lg transition-all flex items-center space-x-1.5 cursor-pointer border border-transparent shrink-0"
        >
          <i class="fa-solid fa-user text-[10px]" :class="selectedMember === m ? 'text-white' : 'text-sky-600'"></i>
          <span>{{ m }}</span>
          <span class="text-[10px] opacity-75">({{ countPoliciesByMember(m) }})</span>
        </button>

        <!-- 当前选中提示与快速清除 -->
        <div v-if="selectedMember" class="flex items-center space-x-1.5 pl-2 shrink-0 text-[11px] text-slate-400">
          <span>筛选: <strong class="text-sky-600 font-semibold">{{ selectedMember }}</strong></span>
          <button
            @click="clearMemberFilter"
            class="text-slate-400 hover:text-rose-600 transition cursor-pointer p-0.5"
            title="清空筛选恢复全部"
          >
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 卡片视图 -->
    <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <PolicyCard
        v-for="pol in filteredPolicies"
        :key="pol.id"
        :pol="pol"
        @open-edit-modal="$emit('open-edit-modal', $event)"
        @view-policy-detail="$emit('view-policy-detail', $event)"
        @view-policy-payments="$emit('view-policy-payments', $event)"
      />
    </div>

    <!-- 表格视图子组件 -->
    <PolicyTable
      v-else
      :policies="filteredPolicies"
      @open-edit-modal="$emit('open-edit-modal', $event)"
      @view-policy-detail="$emit('view-policy-detail', $event)"
      @view-policy-payments="$emit('view-policy-payments', $event)"
    />
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import PolicyCard from '../components/policy/PolicyCard.vue';
import PolicyTable from '../components/policy/PolicyTable.vue';

const props = defineProps({
  policies: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  activeCount: { type: Number, default: 0 },
  stoppedCount: { type: Number, default: 0 },
  initialMemberFilter: { type: String, default: '' }
});

defineEmits(['open-add-modal', 'open-edit-modal', 'view-policy-detail', 'view-policy-payments', 'open-members']);

const searchQuery = ref('');

const displayMembers = computed(() => {
  const set = new Set(props.members || []);
  (props.policies || []).forEach(p => {
    if (p.isFamilyPolicy && Array.isArray(p.insuredMembers)) {
      p.insuredMembers.forEach(m => m && set.add(m));
    } else if (p.member) {
      set.add(p.member);
    }
  });
  return Array.from(set);
});

const selectedMember = ref(props.initialMemberFilter || '');

watch(() => props.initialMemberFilter, (newVal) => {
  selectedMember.value = newVal || '';
});

const selectMember = (name) => {
  if (selectedMember.value === name) {
    selectedMember.value = '';
  } else {
    selectedMember.value = name;
  }
};

const clearMemberFilter = () => {
  selectedMember.value = '';
};

const filterType = ref('');
const filterStatus = ref('active');
const viewMode = ref('grid');

function countPoliciesByMember(name) {
  return (props.policies || []).filter(p => {
    if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
      return p.insuredMembers.includes(name);
    }
    return p.member === name;
  }).length;
}

const filteredPolicies = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  return (props.policies || []).filter(p => {
    if (selectedMember.value) {
      const isInsured = (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0)
        ? p.insuredMembers.includes(selectedMember.value)
        : p.member === selectedMember.value;
      if (!isInsured) return false;
    }
    if (filterType.value) {
      if (filterType.value === '家庭多人') {
        if (!p.isFamilyPolicy) return false;
      } else if (!p.type || !p.type.includes(filterType.value)) {
        return false;
      }
    }
    if (filterStatus.value === 'active' && p.status !== 'active') return false;
    if (filterStatus.value === 'stopped' && p.status !== 'stopped') return false;

    if (query) {
      const matchName = (p.name || '').toLowerCase().includes(query);
      const matchCompany = (p.company || '').toLowerCase().includes(query);
      const matchPolicyNo = (p.policyNo || '').toLowerCase().includes(query);
      const matchMember = (p.member || '').toLowerCase().includes(query);
      const matchApplicant = (p.applicant || '').toLowerCase().includes(query);
      const matchAccount = (p.paymentAccount || '').toLowerCase().includes(query);
      const matchInsuredMembers = p.isFamilyPolicy && Array.isArray(p.insuredMembers)
        ? p.insuredMembers.some(m => (m || '').toLowerCase().includes(query))
        : false;
      if (!matchName && !matchCompany && !matchPolicyNo && !matchMember && !matchApplicant && !matchAccount && !matchInsuredMembers) {
        return false;
      }
    }
    return true;
  });
});
</script>

