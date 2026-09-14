<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
    <div
      class="bg-white rounded-3xl max-w-lg w-full shadow-2xl overflow-hidden border border-slate-100 animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[90vh]"
    >
      <!-- 弹窗头部 -->
      <div class="p-5 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center text-sm"
            :class="isAddMode ? 'bg-emerald-100 text-emerald-700' : 'bg-sky-100 text-sky-700'"
          >
            <i :class="isAddMode ? 'fa-solid fa-plus' : 'fa-solid fa-pen-to-square'"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-900">
              {{ isAddMode ? '登记新一期续保 / 补录缴费' : '修改台账记录' }}
            </h3>
            <p class="text-[11px] text-slate-500">
              {{ isAddMode ? '支持提前录入下一年保费，或补录历史实际扣款流水' : `${formData.memberName || ''} · ${formData.policyName || ''} (${formData.year}年)` }}
            </p>
          </div>
        </div>
        <button
          @click="closeModal"
          class="text-slate-400 hover:text-slate-600 p-1 rounded-lg transition cursor-pointer"
        >
          <i class="fa-solid fa-xmark text-base"></i>
        </button>
      </div>

      <!-- 核心表单区域 -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4 overflow-y-auto custom-scrollbar flex-1 text-xs">
        <!-- 登记模式：选择关联保单与年份 -->
        <template v-if="isAddMode">
          <div>
            <label class="block font-medium text-slate-700 mb-1.5">
              关联保单 <span class="text-rose-500">*</span>
            </label>
            <select
              v-model="selectedPolicyId"
              @change="handlePolicySelect"
              required
              class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:bg-white focus:border-sky-500 transition"
            >
              <option value="" disabled>请选择要续费/补录的保单...</option>
              <option
                v-for="p in activePoliciesList"
                :key="p.id"
                :value="p.id"
              >
                {{ p.member }} - {{ p.name }} ({{ p.company || '未知机构' }} · 参考 ¥{{ p.premium }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-medium text-slate-700 mb-1.5">
                续费/缴费年份 <span class="text-rose-500">*</span>
              </label>
              <input
                v-model.number="formData.year"
                type="number"
                min="2010"
                max="2040"
                required
                placeholder="如 2027"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 font-mono focus:bg-white focus:border-sky-500 transition"
              />
            </div>
            <div>
              <label class="block font-medium text-slate-700 mb-1.5">
                扣费状态 <span class="text-rose-500">*</span>
              </label>
              <select
                v-model="formData.paid"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold focus:bg-white focus:border-sky-500 transition"
                :class="formData.paid ? 'text-emerald-700 bg-emerald-50/50 border-emerald-200' : 'text-slate-700'"
              >
                <option :value="true">已完成缴费 (实缴流水)</option>
                <option :value="false">扣款失败 / 异常</option>
              </select>
            </div>
          </div>
        </template>

        <!-- 编辑模式：保单提示小卡片 -->
        <template v-else>
          <div class="p-3 bg-slate-50 rounded-xl border border-slate-200/60 flex items-center justify-between text-slate-600">
            <div>
              <div class="font-bold text-slate-800 text-xs flex items-center space-x-1.5">
                <span>{{ formData.policyName }}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-mono">{{ formData.year }} 年度</span>
              </div>
              <div class="text-[11px] text-slate-500 mt-0.5">
                <span>被保人：{{ formData.memberName }}</span>
              </div>
            </div>
            <div class="text-right">
              <span
                class="text-[11px] px-2 py-0.8 rounded-lg font-semibold"
                :class="formData.paid ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
              >
                {{ formData.paid ? '正常已缴' : '扣款异常' }}
              </span>
            </div>
          </div>
        </template>

        <!-- 保费金额输入 -->
        <div class="space-y-1">
          <label class="block font-medium text-slate-700">
            当期实缴保费金额 (元) <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 font-mono font-bold text-slate-400 text-sm">¥</span>
            <input
              v-model.number="formData.paidAmount"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="请输入实际缴纳的金额"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl pl-7 pr-3 py-2.5 text-sm font-extrabold font-mono text-slate-900 focus:bg-white focus:border-sky-500 transition shadow-2xs"
            />
          </div>
          <p class="text-[10px] text-slate-400">
            适用于越惠保、医疗险等每年费率浮动的险种，台账实际支出将以此金额为准。
          </p>
        </div>

        <!-- 实缴扣款日期 -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-medium text-slate-700 mb-1.5">
              实际扣款 / 缴费日期
            </label>
            <input
              v-model="formData.paidDate"
              type="date"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 font-mono focus:bg-white focus:border-sky-500 transition"
            />
          </div>
          <div>
            <label class="block font-medium text-slate-700 mb-1.5">
              当期扣费状态
            </label>
            <select
              v-model="formData.paid"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold focus:bg-white focus:border-sky-500 transition"
              :class="formData.paid ? 'text-emerald-700 bg-emerald-50/50 border-emerald-200' : 'text-rose-700 bg-rose-50/50 border-rose-200'"
            >
              <option :value="true">已完成扣缴 (正常实缴)</option>
              <option :value="false">扣款失败 / 扣费异常</option>
            </select>
          </div>
        </div>

        <!-- 备注信息 -->
        <div>
          <label class="block font-medium text-slate-700 mb-1.5">
            记账备注与核销说明
          </label>
          <input
            v-model="formData.note"
            type="text"
            placeholder="如：2027年度提前续保 / 医保个账代扣 / 微信自费"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:bg-white focus:border-sky-500 transition"
          />
        </div>

        <!-- 断缴删除操作专区 (仅编辑模式展示) -->
        <div v-if="!isAddMode" class="pt-2 border-t border-slate-100">
          <div class="p-3 bg-rose-50/60 rounded-xl border border-rose-100 flex items-center justify-between">
            <div>
              <span class="text-xs font-bold text-rose-800 block">中途断缴 / 未参保处理</span>
              <span class="text-[10px] text-rose-600 block">若该年度中途停保未参保，可从台账中彻底剔除，不计入家庭保费支出。</span>
            </div>
            <button
              type="button"
              @click="handleSkipRecord"
              class="px-2.5 py-1.5 bg-white hover:bg-rose-100/80 active:bg-rose-200 text-rose-700 border border-rose-200 rounded-lg text-xs font-semibold transition shrink-0 cursor-pointer shadow-2xs"
            >
              <i class="fa-solid fa-trash-can mr-1 text-[11px]"></i>
              <span>断缴剔除</span>
            </button>
          </div>
        </div>

        <!-- 底部提交按钮 -->
        <div class="pt-4 flex items-center justify-end space-x-2 border-t border-slate-100">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition cursor-pointer"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white rounded-xl font-semibold shadow-sm transition flex items-center space-x-1.5 cursor-pointer"
          >
            <i class="fa-solid fa-check text-xs"></i>
            <span>{{ isAddMode ? '保存并记入台账' : '保存修改' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  record: { type: Object, default: null }, // 传入待编辑的台账项（null 则为新增模式）
  policies: { type: Array, default: () => [] }
});

const emit = defineEmits(['close', 'save', 'skip']);

const isAddMode = computed(() => !props.record);
const selectedPolicyId = ref('');

// 过滤出在保中的商业险供登记选择
const activePoliciesList = computed(() => {
  return (props.policies || []).filter(p => p.status !== 'stopped');
});

const formData = reactive({
  key: '',
  policyId: '',
  year: new Date().getFullYear(),
  policyName: '',
  memberName: '',
  standardPremium: 0,
  paidAmount: 0,
  paidDate: '',
  paid: true,
  note: ''
});

watch(
  () => props.record,
  (newVal) => {
    if (newVal) {
      formData.key = newVal.key;
      formData.policyId = newVal.policyId;
      formData.year = newVal.year;
      formData.policyName = newVal.name;
      formData.memberName = newVal.member;
      formData.standardPremium = newVal.standardPremium !== undefined ? newVal.standardPremium : newVal.premium;
      formData.paidAmount = newVal.paidAmount !== undefined ? newVal.paidAmount : newVal.premium;
      formData.paidDate = newVal.paidDate || newVal.dueDate || '';
      formData.paid = newVal.status === 'paid' || newVal.isPaid === true;
      formData.note = newVal.note || '';
    } else {
      // 新增模式重置
      selectedPolicyId.value = '';
      const nextYear = new Date().getFullYear() + 1;
      formData.key = '';
      formData.policyId = '';
      formData.year = nextYear;
      formData.policyName = '';
      formData.memberName = '';
      formData.standardPremium = 0;
      formData.paidAmount = 0;
      formData.paidDate = `${nextYear}-01-01`;
      formData.paid = true;
      formData.note = '';
    }
  },
  { immediate: true }
);

const handlePolicySelect = () => {
  const p = activePoliciesList.value.find(item => item.id === selectedPolicyId.value);
  if (p) {
    formData.policyId = p.id;
    formData.policyName = p.name;
    formData.memberName = p.member;
    formData.standardPremium = Number(p.premium) || 0;
    formData.paidAmount = Number(p.premium) || 0;
    const mDay = p.paymentMonthDay || (p.startDate ? p.startDate.slice(5) : '01-01');
    formData.paidDate = `${formData.year}-${mDay}`;
  }
};

const closeModal = () => {
  emit('close');
};

const handleSubmit = () => {
  if (isAddMode.value) {
    if (!formData.policyId) {
      alert('请选择关联保单');
      return;
    }
    if (!formData.year) {
      alert('请输入有效年份');
      return;
    }
    formData.key = `p_${formData.policyId}_${formData.year}`;
  }

  emit('save', {
    key: formData.key,
    policyId: formData.policyId,
    year: formData.year,
    paid: formData.paid,
    paidAmount: Number(formData.paidAmount) || 0,
    paidDate: formData.paidDate,
    note: formData.note
  });
  closeModal();
};

const handleSkipRecord = () => {
  if (!confirm(`确认将《${formData.policyName}》(${formData.year}年) 标记为断缴并从台账中剔除吗？\n\n剔除后该年份将不再计入家庭支出统计，亦不会预警扣费异常。`)) {
    return;
  }
  emit('skip', props.record);
  closeModal();
};
</script>
