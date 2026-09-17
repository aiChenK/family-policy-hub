<template>
  <div v-if="show" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
    <div class="bg-white rounded-2xl sm:rounded-3xl max-w-4xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[95vh] sm:max-h-[92vh] flex flex-col">
      <!-- 顶部综合标题与操作栏 -->
      <div class="p-3.5 sm:p-5 bg-gradient-to-r from-sky-50 via-indigo-50 to-slate-50 border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2.5 sm:space-x-3">
            <div
              class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl text-white flex items-center justify-center shadow-md shrink-0 transition-all duration-300"
              :class="activeTab === 'members' ? 'bg-gradient-to-tr from-sky-600 to-indigo-600 shadow-sky-200' : 'bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-indigo-200'"
            >
              <i class="fa-solid" :class="activeTab === 'members' ? 'fa-users text-base sm:text-lg' : 'fa-building text-base sm:text-lg'"></i>
            </div>
            <div>
              <h3 class="text-sm sm:text-base font-bold text-slate-900 leading-snug">人员档案与企业主体配置</h3>
              <p class="text-xs text-slate-500 mt-0.5 line-clamp-1 sm:line-clamp-none">
                {{ activeTab === 'members' ? '维护家庭成员身份档案、医保健康关系与排序' : '备查公司公户车年检、买车险与理赔资质' }}
              </p>
            </div>
          </div>
          <button
            @click="handleClose"
            class="sm:hidden text-slate-400 hover:text-slate-600 p-1.5 rounded-xl hover:bg-white/60 transition shrink-0"
            title="关闭窗口"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <!-- 选项切换与操作按钮区 -->
        <div class="flex items-center justify-between sm:justify-end gap-2 pt-1 sm:pt-0 border-t sm:border-t-0 border-slate-200/50">
          <!-- 快捷 Tab 切换胶囊 -->
          <div class="inline-flex p-1 bg-white/90 backdrop-blur rounded-xl border border-slate-200 shadow-2xs">
            <button
              type="button"
              @click="switchTab('members')"
              :class="activeTab === 'members' ? 'bg-sky-600 text-white font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              class="px-2.5 sm:px-3 py-1 rounded-lg text-xs transition flex items-center space-x-1"
            >
              <i class="fa-solid fa-user-group text-[10px] sm:text-[11px]"></i>
              <span>家庭成员 ({{ (familyMembers || members || []).length }})</span>
            </button>
            <button
              type="button"
              @click="switchTab('companies')"
              :class="activeTab === 'companies' ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              class="px-2.5 sm:px-3 py-1 rounded-lg text-xs transition flex items-center space-x-1"
            >
              <i class="fa-solid fa-building text-[10px] sm:text-[11px]"></i>
              <span>企业资质 ({{ (companies || []).length }})</span>
            </button>
          </div>

          <div class="flex items-center space-x-2">
            <!-- A. 成员 Tab 下的添加按钮 -->
            <button
              v-if="activeTab === 'members' && !isEditingMember"
              @click="triggerAddMember"
              class="inline-flex items-center space-x-1 sm:space-x-1.5 px-3 py-1.5 sm:px-3.5 sm:py-2 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white rounded-xl text-xs font-semibold shadow-sm transition"
            >
              <i class="fa-solid fa-user-plus"></i>
              <span>添加成员</span>
            </button>

            <!-- B. 企业 Tab 下的添加按钮 -->
            <button
              v-if="activeTab === 'companies' && !isEditingCompany"
              @click="triggerAddCompany"
              class="inline-flex items-center space-x-1 sm:space-x-1.5 px-3 py-1.5 sm:px-3.5 sm:py-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white rounded-xl text-xs font-semibold shadow-sm transition"
            >
              <i class="fa-solid fa-plus"></i>
              <span>登记企业</span>
            </button>

            <button
              @click="handleClose"
              class="hidden sm:inline-flex text-slate-400 hover:text-slate-600 p-2 rounded-xl hover:bg-white/60 transition"
              title="关闭窗口"
            >
              <i class="fa-solid fa-xmark text-lg"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 内容主体区 -->
      <div class="p-3.5 sm:p-6 overflow-y-auto flex-1 custom-scrollbar space-y-4">
        <!-- 选项卡一：家庭成员管理 -->
        <MemberTab
          v-if="activeTab === 'members'"
          ref="memberTabRef"
          :members="members"
          :family-members="familyMembers"
          :policies="policies"
          :vehicles="vehicles"
          :member-summary="memberSummary"
          @update-members="$emit('update-members', $event)"
          @cascade-rename="$emit('cascade-rename', $event)"
          @toast="$emit('toast', $event)"
        />

        <!-- 选项卡二：关联企业资质与营业执照 -->
        <CompanyTab
          v-else-if="activeTab === 'companies'"
          ref="companyTabRef"
          :companies="companies"
          :vehicles="vehicles"
          :initial-focus-company="initialFocusCompany"
          @update-companies="$emit('update-companies', $event)"
          @toast="$emit('toast', $event)"
        />
      </div>

      <!-- 底部操作与提示栏 -->
      <div class="p-4 bg-slate-50 border-t border-slate-100 flex justify-between items-center shrink-0">
        <div class="text-xs text-slate-500 flex items-center space-x-1.5">
          <i class="fa-solid fa-shield-halved" :class="activeTab === 'members' ? 'text-sky-600' : 'text-indigo-600'"></i>
          <span>{{ activeTab === 'members' ? '家庭人员档案及排序将即时原子落盘并同步至全站大盘' : '企业营业执照与开票资质仅存储于本地安全环境，专供投保理赔备查' }}</span>
        </div>
        <button
          @click="handleClose"
          class="px-5 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold shadow-sm transition"
        >
          完成并关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import MemberTab from './member/MemberTab.vue';
import CompanyTab from './member/CompanyTab.vue';

const props = defineProps({
  show: { type: Boolean, default: false },
  initialTab: { type: String, default: 'members' },
  initialFocusCompany: { type: String, default: '' },
  members: { type: Array, default: () => [] },
  familyMembers: { type: Array, default: () => [] },
  policies: { type: Array, default: () => [] },
  vehicles: { type: Array, default: () => [] },
  memberSummary: { type: Object, default: () => ({}) },
  companies: { type: Array, default: () => [] }
});

const emit = defineEmits([
  'update:show',
  'update-members',
  'cascade-rename',
  'update-companies',
  'toast'
]);

const activeTab = ref('members');
const memberTabRef = ref(null);
const companyTabRef = ref(null);

const isEditingMember = computed(() => memberTabRef.value?.isEditingMember ?? false);
const isEditingCompany = computed(() => companyTabRef.value?.isEditingCompany ?? false);

watch(
  () => [props.show, props.initialTab],
  ([show, initialTab]) => {
    if (show) {
      activeTab.value = (initialTab || props.initialTab) === 'companies' ? 'companies' : 'members';
    }
  },
  { immediate: true }
);

function switchTab(tab) {
  activeTab.value = tab;
}

function triggerAddMember() {
  if (memberTabRef.value) {
    memberTabRef.value.openAddMemberForm();
  }
}

function triggerAddCompany() {
  if (companyTabRef.value) {
    companyTabRef.value.openAddCompanyForm();
  }
}

function handleClose() {
  if (memberTabRef.value) {
    memberTabRef.value.notifyMemberUpdate();
  }
  emit('update:show', false);
}
</script>
