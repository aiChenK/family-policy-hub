<template>
  <section class="space-y-6">
    <div class="bg-rose-500 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-kit-medical text-2xl"></i>
          <h3 class="text-lg font-bold">就医与意外理赔应急向导</h3>
        </div>
        <p class="text-rose-100 text-xs mt-1">
          当家人生病就医或发生意外时，快速检索对应成员可报销的医疗险/意外险保单，查看免赔额、报销范围及客服报案电话。
        </p>
      </div>
      <!-- 右侧：管理电话配置与选择成员切换 -->
      <div class="flex items-center space-x-2 flex-wrap gap-y-2">
        <button
          type="button"
          @click="$emit('open-phones')"
          class="px-3 py-1.5 rounded-xl bg-rose-600/90 hover:bg-rose-700 text-white text-xs font-medium transition border border-rose-400/50 flex items-center space-x-1.5 shadow-sm"
          title="管理各保司报案电话与匹配规则"
        >
          <i class="fa-solid fa-phone-volume"></i>
          <span>管理电话配置</span>
        </button>

        <div class="flex items-center space-x-1 bg-rose-600 p-1 rounded-xl">
          <button
            v-for="m in members"
            :key="m"
            @click="selectedMember = m"
            :class="selectedMember === m ? 'bg-white text-rose-700 shadow-sm font-bold' : 'text-white hover:bg-rose-500'"
            class="px-3 py-1.5 rounded-lg text-xs transition"
          >
            {{ m }}
          </button>
        </div>
      </div>
    </div>

    <!-- 成员可报销保单卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="pol in emergencyPolicies"
        :key="pol.id"
        class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 space-y-3.5"
      >
        <div class="flex justify-between items-start gap-2">
          <div>
            <div class="flex items-center space-x-2">
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold" :class="getTypeBadgeClass(pol.type)">
                {{ pol.type }}
              </span>
              <span v-if="pol.applicant && pol.applicant !== pol.member" class="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                投保人: {{ pol.applicant }}
              </span>
            </div>
            <h4 class="text-base font-bold text-slate-900 mt-1.5">{{ pol.name }}</h4>
            <div class="text-xs text-slate-500 mt-0.5">
              承保机构：<strong>{{ pol.company }}</strong> · 保额：<strong class="text-slate-800">{{ pol.amount }}</strong>
            </div>
          </div>
          <a
            v-if="getCompanyPhone(pol.company, phoneConfig)"
            :href="'tel:' + getCompanyPhone(pol.company, phoneConfig)"
            class="px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-bold text-xs flex items-center space-x-1.5 transition border border-emerald-200 shrink-0"
          >
            <i class="fa-solid fa-phone"></i>
            <span>报案: {{ getCompanyPhone(pol.company, phoneConfig) }}</span>
          </a>
          <span
            v-else
            class="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-400 text-[11px] shrink-0"
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
    if (p.member !== selectedMember.value) return false;
    const t = p.type || '';
    return t.includes('医疗') || t.includes('意外') || t.includes('重疾');
  });
});
</script>

