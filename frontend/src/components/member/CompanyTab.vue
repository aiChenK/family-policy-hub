<template>
  <div class="space-y-4">
    <!-- 1. 企业编辑/登记表单子组件 -->
    <CompanyEditForm
      v-if="isEditingCompany"
      :form="editingCompanyForm"
      :is-new="editingCompanyIsNew"
      @save="saveCompanyForm"
      @cancel="cancelCompanyEdit"
    />

    <!-- 2. 企业卡片列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="comp in companyList"
        :key="comp.id || comp.name"
        :id="`comp-card-${comp.id}`"
        class="p-4 rounded-2xl border transition bg-white hover:shadow-md flex flex-col justify-between"
        :class="highlightCompanyName === comp.name ? 'border-indigo-500 ring-2 ring-indigo-100 shadow-md' : 'border-slate-200/80'"
      >
        <div class="space-y-3">
          <!-- 企业标题栏与操作 -->
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-2.5">
              <div class="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-700 font-bold text-base flex items-center justify-center border border-indigo-100 shadow-2xs">
                <i class="fa-solid fa-building"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-slate-900">{{ comp.name }}</h4>
                <div class="flex items-center space-x-2 mt-0.5">
                  <span class="px-2 py-0.2 rounded bg-slate-100 text-slate-600 text-[10px] font-medium">
                    名下公户车：{{ countCompanyVehicles(comp.name) }} 辆
                  </span>
                  <span v-if="comp.attachments && comp.attachments.length > 0" class="px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 text-[10px] font-medium flex items-center space-x-0.5">
                    <i class="fa-solid fa-check text-[9px]"></i>
                    <span>已附执照</span>
                  </span>
                </div>
              </div>
            </div>

            <div class="flex items-center space-x-1">
              <button
                @click="startEditCompany(comp)"
                title="编辑企业资料"
                class="p-1.5 text-indigo-600 hover:text-indigo-800 rounded-lg hover:bg-indigo-50 transition cursor-pointer"
              >
                <i class="fa-regular fa-pen-to-square text-xs"></i>
              </button>
              <button
                @click="confirmDeleteCompany(comp)"
                title="删除此企业"
                class="p-1.5 text-rose-500 hover:text-rose-700 rounded-lg hover:bg-rose-50 transition cursor-pointer"
              >
                <i class="fa-regular fa-trash-can text-xs"></i>
              </button>
            </div>
          </div>

          <!-- 统一社会信用代码一键复制卡片 -->
          <div class="p-2.5 bg-slate-50/90 rounded-xl border border-slate-100 text-xs space-y-1.5">
            <div class="flex items-center justify-between">
              <div class="text-[11px] text-slate-500">统一社会信用代码 / 税号：</div>
              <button
                v-if="comp.taxNo"
                @click="copyText(comp.taxNo, '信用代码')"
                class="text-[10px] px-2 py-0.5 bg-white border border-slate-200 text-indigo-600 hover:text-indigo-800 rounded-md font-medium shadow-2xs hover:bg-indigo-50 transition flex items-center space-x-1 cursor-pointer"
              >
                <i class="fa-regular fa-copy"></i>
                <span>一键复制</span>
              </button>
            </div>
            <div class="font-mono font-bold text-slate-900 tracking-wider text-xs select-all">
              {{ comp.taxNo || '未录入统一信用代码' }}
            </div>
          </div>

          <!-- 开票账户与银行信息 -->
          <div v-if="comp.bankName || comp.bankAccount" class="p-2.5 bg-slate-50/70 rounded-xl border border-slate-100 text-xs space-y-1">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-slate-500">对公银行账户 (出险理赔)：</span>
              <button
                v-if="comp.bankAccount"
                @click="copyText(`${comp.bankName} ${comp.bankAccount}`, '开户行与账号')"
                class="text-[10px] text-indigo-600 hover:underline cursor-pointer"
              >
                复制账户
              </button>
            </div>
            <div class="text-slate-800 font-medium text-[11px]">{{ comp.bankName }}</div>
            <div class="font-mono text-slate-700 select-all text-xs font-semibold">{{ comp.bankAccount }}</div>
          </div>

          <!-- 营业执照预览胶囊 -->
          <div v-if="comp.attachments && comp.attachments.length > 0" class="pt-1">
            <div class="text-[11px] font-semibold text-slate-600 mb-1.5 flex items-center space-x-1">
              <i class="fa-solid fa-image text-indigo-500"></i>
              <span>营业执照凭证原件：</span>
            </div>
            <div class="flex items-center space-x-2 overflow-x-auto py-1">
              <a
                v-for="att in comp.attachments"
                :key="att.id"
                :href="getAttachmentUrl(att.url)"
                target="_blank"
                class="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-50/80 hover:bg-indigo-100 text-indigo-700 rounded-xl text-xs font-medium border border-indigo-200/60 transition shadow-2xs cursor-pointer"
                :title="att.name"
              >
                <i class="fa-regular fa-file-image text-indigo-600" v-if="!att.name.endsWith('.pdf')"></i>
                <i class="fa-regular fa-file-pdf text-rose-500" v-else></i>
                <span class="truncate max-w-[150px]">{{ att.name }}</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px] opacity-70"></i>
              </a>
            </div>
          </div>
          <div v-else class="text-[11px] text-slate-400 py-1">
            <i class="fa-solid fa-circle-exclamation text-amber-500 mr-1"></i>暂未上传营业执照原件照片
          </div>

          <!-- 关联的公户车列表 -->
          <div v-if="getCompanyVehicles(comp.name).length > 0" class="pt-2 border-t border-slate-100 text-[11px]">
            <span class="text-slate-500">关联公户车辆：</span>
            <span
              v-for="v in getCompanyVehicles(comp.name)"
              :key="v.id"
              class="ml-1 inline-flex items-center px-1.5 py-0.2 rounded bg-slate-100 text-slate-800 font-mono font-bold"
            >
              {{ v.plateNo || v.plateNumber }} ({{ v.model }})
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空白占位 -->
    <div v-if="companyList.length === 0 && !isEditingCompany" class="text-center py-12 bg-slate-50 rounded-2xl border border-dashed border-slate-200 text-slate-400">
      <div class="w-12 h-12 mx-auto rounded-2xl bg-indigo-50 text-indigo-400 flex items-center justify-center text-xl mb-3">
        <i class="fa-solid fa-building"></i>
      </div>
      <p class="text-sm font-medium text-slate-600">暂无关联企业与营业执照备查档案</p>
      <p class="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
        如有名下挂靠公司的私车或公户车辆，可登记对公抬头、税号与银行信息，便于续保与报案时随时调取
      </p>
      <button
        @click="openAddCompanyForm"
        class="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition inline-flex items-center space-x-1.5 cursor-pointer"
      >
        <i class="fa-solid fa-plus text-[10px]"></i>
        <span>登记新企业</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { deepClone } from '../../utils/helpers.js';
import { AppApi, getAttachmentUrl } from '../../api/index.js';
import CompanyEditForm from './CompanyEditForm.vue';

const props = defineProps({
  companies: { type: Array, default: () => [] },
  vehicles: { type: Array, default: () => [] },
  initialFocusCompany: { type: String, default: '' }
});

const emit = defineEmits(['update-companies', 'toast']);

const companyList = ref([]);
const isEditingCompany = ref(false);
const editingCompanyIsNew = ref(false);
const editingCompanyForm = ref({});
const highlightCompanyName = ref('');

watch(
  () => [props.companies, props.initialFocusCompany],
  () => {
    initCompanyList();
    if (props.initialFocusCompany) {
      highlightCompanyName.value = props.initialFocusCompany;
      nextTick(() => {
        const target = companyList.value.find(c => c.name === props.initialFocusCompany);
        if (target && target.id) {
          const el = document.getElementById(`comp-card-${target.id}`);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    }
  },
  { immediate: true, deep: true }
);

function initCompanyList() {
  companyList.value = (props.companies && props.companies.length > 0)
    ? deepClone(props.companies)
    : [];
}

function countCompanyVehicles(compName) {
  if (!compName) return 0;
  return (props.vehicles || []).filter(v => v.companyName === compName || (v.isCompany && v.owner === compName)).length;
}

function getCompanyVehicles(compName) {
  if (!compName) return [];
  return (props.vehicles || []).filter(v => v.companyName === compName || (v.isCompany && v.owner === compName));
}

function copyText(text, label = '内容') {
  if (!text) return;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      emit('toast', `已成功复制【${label}】至剪贴板！`);
    }).catch(() => {
      fallbackCopy(text, label);
    });
  } else {
    fallbackCopy(text, label);
  }
}

function fallbackCopy(text, label) {
  const ta = document.createElement('textarea');
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    emit('toast', `已成功复制【${label}】至剪贴板！`);
  } catch (e) {
    alert(`复制失败，请手动长按选中复制：\n${text}`);
  }
  document.body.removeChild(ta);
}

function openAddCompanyForm() {
  editingCompanyIsNew.value = true;
  editingCompanyForm.value = {
    id: 'comp_' + Date.now(),
    name: '',
    taxNo: '',
    bankName: '',
    bankAccount: '',
    addressPhone: '',
    contactPerson: '',
    remark: '',
    attachments: []
  };
  isEditingCompany.value = true;
}

function startEditCompany(comp) {
  editingCompanyIsNew.value = false;
  editingCompanyForm.value = deepClone(comp);
  if (!editingCompanyForm.value.attachments) {
    editingCompanyForm.value.attachments = [];
  }
  isEditingCompany.value = true;
}

function cancelCompanyEdit() {
  isEditingCompany.value = false;
  editingCompanyForm.value = {};
}

function saveCompanyForm() {
  const f = editingCompanyForm.value;
  if (!f.name || !f.name.trim()) {
    alert('请填写公司全称');
    return;
  }
  const targetName = f.name.trim();

  if (editingCompanyIsNew.value) {
    if (companyList.value.some(c => c.name === targetName)) {
      alert(`企业【${targetName}】已在列表中，请勿重复登记`);
      return;
    }
    f.name = targetName;
    companyList.value.push(deepClone(f));
    notifyCompanyUpdate();
    isEditingCompany.value = false;
    emit('toast', `企业【${targetName}】资质已登记成功！`);
  } else {
    const idx = companyList.value.findIndex(c => c.id === f.id);
    if (idx !== -1) {
      f.name = targetName;
      companyList.value[idx] = deepClone(f);
      notifyCompanyUpdate();
      isEditingCompany.value = false;
      emit('toast', `企业【${targetName}】资料已更新！`);
    }
  }
}

async function confirmDeleteCompany(comp) {
  const vehCount = countCompanyVehicles(comp.name);
  if (vehCount > 0) {
    alert(`无法删除企业【${comp.name}】！\n\n当前名下仍有关联的 ${vehCount} 辆公户爱车。请先在爱车专区中转移或删除车辆，再执行企业资料移除。`);
    return;
  }

  if (confirm(`确认删除关联企业【${comp.name}】及其营业执照备查档案吗？`)) {
    if (comp.attachments && comp.attachments.length > 0) {
      for (const att of comp.attachments) {
        if (att.storedName) {
          try {
            await AppApi.deleteAttachment('company', att.storedName);
          } catch (_) {}
        }
      }
    }

    companyList.value = companyList.value.filter(c => c.id !== comp.id && c.name !== comp.name);
    notifyCompanyUpdate();
    emit('toast', `已移除企业【${comp.name}】备查档案`);
  }
}

function notifyCompanyUpdate() {
  emit('update-companies', deepClone(companyList.value));
}

defineExpose({
  openAddCompanyForm,
  isEditingCompany,
  notifyCompanyUpdate,
  companyCount: () => companyList.value.length
});
</script>
