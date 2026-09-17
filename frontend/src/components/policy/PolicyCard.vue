<template>
  <div
    class="bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-sky-300 transition-all duration-200 p-4 sm:p-5 flex flex-col justify-between group relative overflow-hidden"
    :class="{ 'opacity-70 bg-slate-50/70 border-slate-200': pol.status === 'stopped' }"
  >
    <!-- 左侧状态指示竖条 -->
    <div
      class="absolute left-0 top-0 bottom-0 w-1"
      :class="pol.status === 'active' ? 'bg-sky-500' : 'bg-slate-300'"
    ></div>

    <div>
      <!-- 顶栏：被保人姓名、险种Badge、公司、投保人关系、停保标识 -->
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap min-w-0">
          <div v-if="pol.isFamilyPolicy" class="inline-flex items-center gap-1 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg bg-purple-50 text-purple-800 font-bold text-xs whitespace-nowrap border border-purple-200/90 shrink-0 shadow-2xs" :title="'参保家属：' + (pol.insuredMembers || []).join('、')">
            <i class="fa-solid fa-people-roof text-[11px] text-purple-600"></i>
            <span>{{ (pol.insuredMembers && pol.insuredMembers.length > 0) ? (pol.insuredMembers.length <= 2 ? pol.insuredMembers.join('、') : `${pol.insuredMembers.slice(0, 2).join('、')}等${pol.insuredMembers.length}人`) : pol.member }}</span>
          </div>
          <div v-else class="inline-flex items-center gap-1 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg bg-sky-50 text-sky-800 font-bold text-xs whitespace-nowrap border border-sky-100/90 shrink-0 shadow-2xs">
            <i class="fa-solid fa-user-shield text-[11px] text-sky-600"></i>
            <span>{{ pol.member }}</span>
          </div>
          <span class="text-xs font-semibold px-2 sm:px-2.5 py-0.5 rounded-full whitespace-nowrap shadow-2xs shrink-0" :class="getTypeBadgeClass(pol.type)">
            {{ pol.type }}
          </span>
          <span class="text-xs text-slate-500 font-medium truncate shrink min-w-0" :title="pol.company">
            {{ pol.company }}
          </span>
        </div>

        <div class="flex items-center gap-1.5 shrink-0">
          <span v-if="pol.status === 'stopped'" class="text-[11px] bg-slate-200/80 text-slate-600 px-2 py-0.5 rounded-full font-medium border border-slate-300/60">
            已停保
          </span>
          <span v-if="pol.applicant && (pol.applicant !== pol.member || pol.isFamilyPolicy)" class="text-[11px] bg-amber-50/90 text-amber-800 px-1.5 sm:px-2 py-0.5 rounded-md border border-amber-200/60 inline-flex items-center gap-1" title="投保人家属">
            <i class="fa-solid fa-hand-holding-heart text-[10px] text-amber-500"></i>
            <span>投保: {{ pol.applicant }}</span>
          </span>
        </div>
      </div>

      <!-- 产品名称与保额/受益人指标 -->
      <div class="mt-3 sm:mt-3.5">
        <h4 class="text-sm sm:text-base font-bold text-slate-900 group-hover:text-sky-700 transition leading-snug line-clamp-1" :title="pol.name">
          {{ pol.name }}
        </h4>
        <div class="mt-1.5 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-slate-500">
          <div class="flex items-center gap-1">
            <span class="text-slate-400">保额计划:</span>
            <span class="font-bold text-slate-900 bg-slate-100/80 px-1.5 py-0.5 rounded text-[12px]">{{ pol.amount || '-' }}</span>
          </div>
          <span class="text-slate-300">·</span>
          <div class="flex items-center gap-1">
            <span class="text-slate-400">保障期:</span>
            <span class="text-slate-700 font-medium">{{ pol.coveragePeriod || '终身' }}</span>
          </div>
          <template v-if="pol.beneficiary">
            <span class="text-slate-300">·</span>
            <div class="flex items-center gap-1" title="身故受益人">
              <span class="text-slate-400">受益人:</span>
              <span class="text-slate-700 font-medium">{{ pol.beneficiary }}</span>
            </div>
          </template>
        </div>
      </div>

      <!-- 保单合同号行 -->
      <div v-if="pol.policyNo" class="mt-2.5 px-2.5 py-1 bg-slate-50/90 rounded-lg border border-slate-100/90 flex items-center justify-between text-[11px]">
        <div class="flex items-center gap-1.5 truncate text-slate-500 font-mono">
          <i class="fa-solid fa-file-contract text-slate-400 text-[10px]"></i>
          <span class="truncate select-all">单号: {{ pol.policyNo }}</span>
        </div>
        <button
          type="button"
          @click.stop="copyText(pol.policyNo, pol.id)"
          class="text-sky-600 hover:text-sky-800 ml-2 text-[10px] font-medium inline-flex items-center gap-1 py-1 px-2 rounded-md hover:bg-sky-50 transition shrink-0 cursor-pointer"
          :title="copiedId === pol.id ? '已复制' : '复制保单号'"
        >
          <i :class="copiedId === pol.id ? 'fa-solid fa-check text-emerald-600' : 'fa-regular fa-copy'"></i>
          <span :class="copiedId === pol.id ? 'text-emerald-600 font-bold' : ''">{{ copiedId === pol.id ? '已复制' : '复制' }}</span>
        </button>
      </div>

      <!-- 缴费与保障日期精细拆分展示 -->
      <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] bg-slate-50/80 p-2.5 rounded-xl border border-slate-100">
        <div>
          <div class="text-slate-400 flex items-center gap-1">
            <i class="fa-regular fa-calendar-check text-[10px] text-slate-400"></i>
            <span>保障起止</span>
          </div>
          <div class="font-mono text-slate-700 truncate mt-0.5 font-medium" :title="pol.startDate + ' ~ ' + pol.endDate">
            {{ pol.startDate }} ~ {{ pol.endDate }}
          </div>
        </div>
        <div>
          <div class="text-slate-400 flex items-center gap-1">
            <i class="fa-regular fa-clock text-[10px] text-slate-400"></i>
            <span>缴费年限与排期</span>
          </div>
          <div class="text-slate-700 font-medium truncate mt-0.5">
            共 {{ pol.paymentYears }} 年 <span v-if="pol.paymentMonthDay" class="text-slate-500 font-normal">({{ pol.paymentMonthDay }} 缴)</span>
          </div>
        </div>
      </div>

      <!-- 保费金额与扣费卡 (支持组合险保费拆解展开) -->
      <div class="mt-3 p-3 rounded-xl bg-gradient-to-r from-sky-50/60 to-blue-50/40 border border-sky-100/70">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-[11px] text-slate-400 flex items-center gap-1.5">
              <span>应缴保费 ({{ pol.paymentFrequency || '年缴' }})</span>
              <button
                v-if="pol.premiumDetail"
                type="button"
                @click.stop="togglePremiumDetail"
                class="text-[10px] text-sky-600 hover:text-sky-800 bg-sky-100/80 hover:bg-sky-200 px-1.5 py-0.5 rounded font-medium transition inline-flex items-center gap-0.5 cursor-pointer"
                :title="isPremiumExpanded ? '收起保费拆解' : '查看组合保费拆解'"
              >
                <i class="fa-solid fa-list-ol text-[9px]"></i>
                <span>{{ isPremiumExpanded ? '收起明细' : '明细' }}</span>
              </button>
            </div>
            <div class="text-base font-extrabold text-slate-900 tracking-tight mt-0.5">
              ¥{{ formatMoney(pol.premium) }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-[11px] text-slate-500 flex items-center justify-end gap-1" v-if="pol.paymentAccount" :title="pol.paymentAccount">
              <i class="fa-regular fa-credit-card text-[10px] text-slate-400"></i>
              <span class="truncate max-w-[130px] inline-block">{{ pol.paymentAccount }}</span>
            </div>
            <div class="text-[11px] text-slate-400" v-else>扣款渠道未录入</div>
            <div class="text-xs font-semibold mt-0.5" :class="pol.status === 'active' ? 'text-sky-700' : 'text-slate-400'">
              {{ pol.paymentYears > 1 ? `交 ${pol.paymentYears} 年` : '一年期消费险' }}
            </div>
          </div>
        </div>

        <!-- 组合保费分项拆解 -->
        <div
          v-if="pol.premiumDetail && isPremiumExpanded"
          class="mt-2.5 pt-2 border-t border-sky-200/50 text-[11px] text-slate-600 whitespace-pre-line bg-white/80 p-2 rounded-lg leading-relaxed shadow-2xs animate-in fade-in duration-150"
        >
          <div class="font-semibold text-sky-800 mb-1 flex items-center gap-1 text-[10px]">
            <i class="fa-solid fa-calculator text-[10px]"></i>
            <span>分项保费明细：</span>
          </div>
          {{ pol.premiumDetail }}
        </div>
      </div>

      <!-- 核保除外特别约定 -->
      <div v-if="pol.exclusions" class="mt-2.5 text-[11px] bg-amber-50/90 text-amber-900 p-2 rounded-lg border border-amber-200/70 leading-relaxed">
        <div class="flex items-start gap-1.5">
          <i class="fa-solid fa-triangle-exclamation text-amber-600 mt-0.5 text-[11px] shrink-0"></i>
          <div class="flex-1">
            <span class="font-semibold text-amber-800">特别约定/除外：</span>
            <span>{{ pol.exclusions }}</span>
          </div>
        </div>
      </div>

      <!-- 核心保障摘要 -->
      <div v-if="pol.description" class="mt-2.5 bg-slate-50/70 p-2.5 rounded-lg border border-slate-100 text-xs text-slate-600">
        <div
          :class="isDescExpanded ? 'whitespace-pre-line leading-relaxed' : 'line-clamp-2 leading-relaxed'"
          class="transition-all"
        >
          {{ pol.description }}
        </div>
        <button
          v-if="(pol.description.length > 50 || pol.description.includes('\n'))"
          type="button"
          @click.stop="isDescExpanded = !isDescExpanded"
          class="text-[11px] text-sky-600 hover:text-sky-800 font-medium mt-1 inline-flex items-center gap-1 cursor-pointer"
        >
          <span>{{ isDescExpanded ? '收起保障责任' : '展开查看全部保障' }}</span>
          <i :class="isDescExpanded ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down'" class="text-[9px]"></i>
        </button>
      </div>
    </div>

    <!-- 底部操作与电子保单原件快捷入口 -->
    <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
      <div class="flex items-center gap-2 text-slate-400">
        <span class="font-mono text-[11px]">#{{ pol.id }}</span>

        <!-- 电子保单合同附件直达预览 -->
        <template v-if="pol.attachments && pol.attachments.length > 0">
          <a
            v-if="pol.attachments.length === 1"
            :href="getAttachmentUrl(pol.attachments[0].url)"
            target="_blank"
            @click.stop
            class="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-white border border-slate-200 text-sky-700 hover:bg-sky-50 font-medium shadow-2xs transition"
            :title="'在线打开合同原件: ' + pol.attachments[0].name"
          >
            <i class="fa-regular fa-file-pdf text-rose-500"></i>
            <span>合同原件</span>
          </a>
          <div v-else class="relative group/att">
            <button
              type="button"
              class="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-white border border-slate-200 text-sky-700 hover:bg-sky-50 font-medium shadow-2xs transition cursor-pointer"
            >
              <i class="fa-solid fa-paperclip text-sky-600"></i>
              <span>{{ pol.attachments.length }} 份原件</span>
            </button>
            <div class="absolute bottom-full left-0 mb-1 hidden group-hover/att:block z-30 bg-white border border-slate-200 rounded-xl shadow-lg p-1.5 min-w-[200px] text-xs">
              <a
                v-for="att in pol.attachments"
                :key="att.id || att.storedName"
                :href="getAttachmentUrl(att.url)"
                target="_blank"
                class="flex items-center gap-2 p-1.5 hover:bg-slate-50 rounded-lg text-slate-700 hover:text-sky-700 truncate"
                :title="att.name"
              >
                <i class="fa-regular fa-file-pdf text-rose-500 shrink-0" v-if="att.name && att.name.endsWith('.pdf')"></i>
                <i class="fa-regular fa-file-image text-sky-500 shrink-0" v-else></i>
                <span class="truncate">{{ att.name }}</span>
              </a>
            </div>
          </div>
        </template>
      </div>

      <div class="flex items-center space-x-2.5">
        <button
          type="button"
          @click="$emit('view-policy-payments', pol)"
          class="text-emerald-700 hover:text-emerald-900 bg-emerald-50 hover:bg-emerald-100/80 border border-emerald-200/80 px-2 py-1 rounded-lg font-medium inline-flex items-center gap-1 cursor-pointer transition shadow-2xs text-[11px]"
          title="查看该保单各期缴费流水与排期明细"
        >
          <i class="fa-solid fa-receipt text-emerald-600 text-[10px]"></i>
          <span>缴费流水</span>
        </button>
        <button @click="$emit('open-edit-modal', pol)" class="text-sky-600 hover:text-sky-800 font-medium cursor-pointer">编辑</button>
        <button @click="$emit('view-policy-detail', pol)" class="text-slate-600 hover:text-slate-900 font-medium inline-flex items-center gap-0.5 cursor-pointer">
          <span>详情</span>
          <i class="fa-solid fa-angle-right text-[10px]"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { formatMoney, getTypeBadgeClass } from '../../utils/helpers.js';
import { getAttachmentUrl } from '../../api/index.js';

defineProps({
  pol: {
    type: Object,
    required: true
  }
});

defineEmits(['open-edit-modal', 'view-policy-detail', 'view-policy-payments']);

const isDescExpanded = ref(false);
const isPremiumExpanded = ref(false);
const copiedId = ref(null);

function togglePremiumDetail() {
  isPremiumExpanded.value = !isPremiumExpanded.value;
}

function copyText(text, id) {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id;
    setTimeout(() => {
      copiedId.value = null;
    }, 2000);
  }).catch(() => {});
}
</script>
