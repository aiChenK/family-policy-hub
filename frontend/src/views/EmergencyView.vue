<template>
  <section class="space-y-4 sm:space-y-6">
    <div class="bg-rose-500 rounded-2xl p-4 sm:p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-3.5">
      <div>
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-kit-medical text-xl sm:text-2xl"></i>
          <h3 class="text-base sm:text-lg font-bold">就医与意外理赔应急向导</h3>
        </div>
        <p class="text-rose-100 text-xs mt-1 leading-relaxed">
          当家人生病就医或发生意外时，快速检索对应成员可报销的医疗险/意外险保单，查看免赔额、报销范围及客服报案电话。
        </p>
      </div>
      <!-- 右侧：管理电话配置与选择成员切换 -->
      <div class="flex items-center gap-2 flex-wrap w-full md:w-auto justify-between md:justify-end">
        <button
          type="button"
          @click="$emit('open-phones')"
          class="px-2.5 sm:px-3 py-1.5 rounded-xl bg-rose-600/90 hover:bg-rose-700 text-white text-xs font-medium transition border border-rose-400/50 flex items-center space-x-1.5 shadow-sm shrink-0 cursor-pointer"
          title="管理各保司报案电话与匹配规则"
        >
          <i class="fa-solid fa-phone-volume"></i>
          <span>管理电话</span>
        </button>

        <!-- 成员快速横滑切换栏 -->
        <div class="flex items-center space-x-1 bg-rose-600 p-1 rounded-xl overflow-x-auto no-scrollbar py-1">
          <button
            v-for="m in members"
            :key="m"
            @click="selectedMember = m"
            :class="selectedMember === m ? 'bg-white text-rose-700 shadow-sm font-bold' : 'text-white hover:bg-rose-500'"
            class="px-2.5 sm:px-3 py-1 rounded-lg text-xs transition shrink-0 cursor-pointer"
          >
            {{ m }}
          </button>
        </div>
      </div>
    </div>

    <!-- 成员可报销保单卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
      <div
        v-for="pol in emergencyPolicies"
        :key="pol.id"
        class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 sm:p-5 space-y-3.5"
      >
        <div class="flex flex-col sm:flex-row justify-between items-start gap-2.5">
          <div class="min-w-0 flex-1">
            <div class="flex items-center space-x-2 flex-wrap gap-y-1">
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold" :class="getTypeBadgeClass(pol.type)">
                {{ pol.type }}
              </span>
              <span v-if="pol.isFamilyPolicy" class="text-[11px] text-purple-700 bg-purple-50 border border-purple-200/80 px-2 py-0.5 rounded font-medium flex items-center gap-1">
                <i class="fa-solid fa-people-roof text-purple-600"></i>
                <span>家庭共享</span>
              </span>
              <span v-if="pol.applicant && (pol.applicant !== pol.member || pol.isFamilyPolicy)" class="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                投保人: {{ pol.applicant }}
              </span>
            </div>
            <h4 class="text-sm sm:text-base font-bold text-slate-900 mt-1.5">{{ pol.name }}</h4>
            <div class="text-xs text-slate-500 mt-0.5">
              承保机构：<strong>{{ pol.company }}</strong> · 保额：<strong class="text-slate-800">{{ pol.amount }}</strong>
              <span v-if="pol.isFamilyPolicy && pol.insuredMembers" class="ml-1 text-purple-700 font-medium">
                (全家参保: {{ pol.insuredMembers.join('、') }})
              </span>
            </div>
          </div>
          <a
            v-if="getCompanyPhone(pol.company, phoneConfig)"
            :href="'tel:' + getCompanyPhone(pol.company, phoneConfig)"
            class="w-full sm:w-auto px-3.5 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition border border-emerald-200 shrink-0"
          >
            <i class="fa-solid fa-phone"></i>
            <span>报案热线: {{ getCompanyPhone(pol.company, phoneConfig) }}</span>
          </a>
          <span
            v-else
            class="w-full sm:w-auto px-2.5 py-1.5 rounded-lg bg-slate-100 text-slate-400 text-[11px] shrink-0 text-center sm:text-left"
            title="未配置该承保公司报案电话，可在上方点击【管理电话配置】补充"
          >
            未配置电话
          </span>
        </div>

        <!-- 保单号快速查验与复制 -->
        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between text-xs">
          <div class="truncate">
            <span class="text-slate-400 text-[10px]">保单编号：</span>
            <span class="font-mono font-bold text-slate-800 select-all">{{ pol.policyNo || '未登记合同号' }}</span>
          </div>
          <button
            v-if="pol.policyNo"
            type="button"
            @click="copyText(pol.policyNo, pol.id)"
            class="px-2 py-0.5 bg-white text-sky-700 hover:bg-sky-50 border border-slate-200 rounded text-[11px] font-medium transition shrink-0 ml-2"
          >
            <i :class="copiedId === pol.id ? 'fa-solid fa-check text-emerald-600' : 'fa-regular fa-copy'"></i>
            <span>{{ copiedId === pol.id ? '已复制' : '复制' }}</span>
          </button>
        </div>

        <!-- 除外特别约定 (就医就诊防踩坑) -->
        <div v-if="pol.exclusions" class="p-2.5 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-xs">
          <div class="font-bold flex items-center space-x-1 mb-0.5">
            <i class="fa-solid fa-triangle-exclamation text-amber-600"></i>
            <span>除外责任提醒（就诊注意）：</span>
          </div>
          <p class="leading-relaxed">{{ pol.exclusions }}</p>
        </div>

        <!-- 保障明细与报销说明 -->
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs text-slate-700 space-y-1">
          <div class="font-semibold text-slate-900 flex items-center">
            <i class="fa-solid fa-circle-info text-sky-600 mr-1.5"></i>
            <span>报销责任与理赔范围：</span>
          </div>
          <p class="whitespace-pre-line leading-relaxed text-slate-600">
            {{ pol.description || '按保险合同基本条款规定履行医疗或身故保障。' }}
          </p>
        </div>

        <div v-if="pol.extra" class="text-xs text-slate-500 bg-amber-50/40 p-2.5 rounded-xl border border-amber-100">
          <div class="font-semibold text-amber-800 mb-0.5">附加险与特别约定：</div>
          <p class="whitespace-pre-line">{{ pol.extra }}</p>
        </div>

        <!-- 理赔必备材料提醒 -->
        <div class="pt-2 text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-100">
          <span>就医提醒：保留发票原件、费用总清单、出院小结</span>
          <span class="text-emerald-600 font-medium"><i class="fa-solid fa-shield-check mr-1"></i>有效保障中</span>
        </div>
      </div>
    </div>

    <div v-if="emergencyPolicies.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400">
      <i class="fa-solid fa-notes-medical text-4xl mb-3 text-slate-300"></i>
      <p class="text-sm">该成员暂无生效中的医疗险或意外险保单记录</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { getTypeBadgeClass, getCompanyPhone } from '../utils/helpers.js';

const props = defineProps({
  members: { type: Array, default: () => [] },
  activePolicies: { type: Array, default: () => [] },
  defaultMember: { type: String, default: '' },
  phoneConfig: { type: Object, default: () => ({}) }
});

const emit = defineEmits(['open-phones']);

const selectedMember = ref(props.defaultMember || props.members[0] || '');
const copiedId = ref(null);

function copyText(text, id) {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id;
    setTimeout(() => {
      copiedId.value = null;
    }, 2000);
  }).catch(() => {});
}

const emergencyPolicies = computed(() => {
  return (props.activePolicies || []).filter(p => {
    const isInsured = (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0)
      ? p.insuredMembers.includes(selectedMember.value)
      : p.member === selectedMember.value;
    if (!isInsured) return false;
    const t = p.type || '';
    return t.includes('医疗') || t.includes('意外') || t.includes('重疾');
  });
});
</script>

