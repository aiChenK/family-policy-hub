<template>
  <div v-if="policy" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
    <div class="bg-white rounded-2xl sm:rounded-3xl max-w-xl w-full shadow-2xl overflow-hidden border border-slate-100 animate-in fade-in zoom-in-95 duration-150 max-h-[94vh] sm:max-h-[92vh] flex flex-col">
      <!-- 弹窗头部 -->
      <div class="p-4 sm:p-6 bg-slate-50 border-b border-slate-100 flex justify-between items-start shrink-0">
        <div>
          <div class="flex items-center space-x-2 flex-wrap gap-y-1">
            <span class="text-xs font-bold px-2.5 py-1 rounded-full" :class="getTypeBadgeClass(policy.type)">
              {{ policy.type }}
            </span>
            <span v-if="policy.isFamilyPolicy" class="text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full text-xs font-bold border border-purple-200/80 flex items-center gap-1">
              <i class="fa-solid fa-people-roof text-purple-600"></i>
              <span>家庭多人单</span>
            </span>
            <span v-if="policy.status === 'active'" class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full text-xs font-medium border border-emerald-200/60">
              <i class="fa-solid fa-shield-check mr-1"></i>在保正常
            </span>
            <span v-else class="text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full text-xs font-medium">
              已停保
            </span>
          </div>
          <h3 class="text-base sm:text-lg font-bold text-slate-900 mt-2">{{ policy.name }}</h3>
          <div class="text-xs text-slate-500 mt-1 flex flex-wrap gap-1.5 sm:gap-2 items-center">
            <span>承保公司：<strong>{{ policy.company }}</strong></span>
            <span>·</span>
            <span v-if="policy.isFamilyPolicy">
              参保家属 (共 {{ (policy.insuredMembers || []).length }} 人)：
              <strong class="text-purple-800">{{ (policy.insuredMembers || []).join('、') }}</strong>
            </span>
            <span v-else>被保人：<strong>{{ policy.member }}</strong></span>
            <span v-if="policy.applicant">· 投保人：{{ policy.applicant }}</span>
          </div>
        </div>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 p-1 rounded-lg">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 核心内容 -->
      <div class="p-4 sm:p-6 space-y-4 text-xs overflow-y-auto custom-scrollbar flex-1">
        <!-- 保单号醒目横幅 (带复制) -->
        <div class="p-3 bg-sky-50/60 rounded-xl border border-sky-100 flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-id-card text-sky-600 text-sm"></i>
            <div>
              <span class="text-slate-400 text-[10px] block">保单合同编号 (理赔报案/客服查询)</span>
              <strong class="font-mono text-slate-800 text-xs select-all">{{ policy.policyNo || '未录入保单号' }}</strong>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <a
              v-if="policy.company"
              :href="'tel:' + getCompanyPhone(policy.company, phoneConfig)"
              class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg border border-emerald-200 text-xs font-medium transition flex items-center space-x-1"
              :title="'官方客服/报案电话: ' + getCompanyPhone(policy.company, phoneConfig)"
            >
              <i class="fa-solid fa-phone text-xs"></i>
              <span>报案: {{ getCompanyPhone(policy.company, phoneConfig) }}</span>
            </a>
            <button
              v-if="policy.policyNo"
              @click="copyPolicyNo(policy.policyNo)"
              class="px-2.5 py-1 bg-white hover:bg-sky-50 text-sky-700 rounded-lg border border-sky-200 text-xs font-medium transition flex items-center space-x-1"
            >
              <i :class="copied ? 'fa-solid fa-check text-emerald-600' : 'fa-regular fa-copy'"></i>
              <span>{{ copied ? '已复制' : '复制' }}</span>
            </button>
          </div>
        </div>

        <!-- 关键利益指标网格 -->
        <div class="grid grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
          <div>
            <span class="text-slate-400">保障额度/计划：</span>
            <strong class="text-slate-800 font-bold ml-1">{{ policy.amount || '-' }}</strong>
          </div>
          <div>
            <span class="text-slate-400">保障期限：</span>
            <strong class="text-slate-800 ml-1">{{ policy.coveragePeriod || '终身' }}</strong>
          </div>
          <div>
            <span class="text-slate-400">应缴保费：</span>
            <strong class="text-slate-900 font-bold text-sm ml-1">¥{{ formatMoney(policy.premium) }}</strong>
            <span class="text-[10px] text-slate-400 ml-1">({{ policy.paymentFrequency || '年缴' }})</span>
            <button
              type="button"
              @click="$emit('view-payments', policy)"
              class="ml-2 text-[10px] text-emerald-700 hover:text-emerald-900 bg-emerald-50 hover:bg-emerald-100/80 px-1.5 py-0.5 rounded font-medium transition inline-flex items-center gap-0.5 cursor-pointer border border-emerald-200/60"
              title="查看该保单缴费流水与排期"
            >
              <i class="fa-solid fa-receipt text-[9px] text-emerald-600"></i>
              <span>流水</span>
            </button>
          </div>
          <div>
            <span class="text-slate-400">缴费年限与排期：</span>
            <span class="text-slate-700 font-medium ml-1">共 {{ policy.paymentYears }} 年 (每年 {{ policy.paymentMonthDay }} 缴)</span>
          </div>
          <div v-if="policy.paymentAccount" class="col-span-2">
            <span class="text-slate-400">自动扣费银行/渠道：</span>
            <span class="text-slate-800 font-medium ml-1"><i class="fa-regular fa-credit-card text-sky-600 mr-1"></i>{{ policy.paymentAccount }}</span>
          </div>
          <div v-if="policy.isFamilyPolicy" class="col-span-2 p-2 bg-purple-50/70 rounded-lg border border-purple-100 flex items-center justify-between text-xs">
            <span class="text-purple-900 font-medium">各成员预算分摊：</span>
            <span class="text-purple-700 font-bold">
              {{ policy.premiumSplitMode === 'equal' ? `参保家属平均分摊 (人均约 ¥${(((Number(policy.premium) || 0) / ((policy.insuredMembers || []).length || 1))).toFixed(2)}/年)` : `全部计入主被保人 (${policy.member})` }}
            </span>
          </div>
          <div class="col-span-2 pt-2 border-t border-slate-200/60 flex flex-wrap justify-between gap-2 items-center">
            <div>
              <span class="text-slate-400">保障起止：</span>
              <span class="text-slate-700 font-mono font-medium ml-1">{{ policy.startDate }} ~ {{ policy.endDate }}</span>
            </div>
            <div v-if="policy.beneficiary">
              <span class="text-slate-400">身故受益人：</span>
              <span class="text-slate-700 font-medium ml-1">{{ policy.beneficiary }}</span>
            </div>
          </div>
        </div>

        <!-- 核保特别约定与除外责任 (极其重要) -->
        <div v-if="policy.exclusions" class="p-3 bg-amber-50 rounded-xl border border-amber-200/80 text-amber-900">
          <div class="font-bold flex items-center space-x-1 mb-1">
            <i class="fa-solid fa-triangle-exclamation text-amber-600"></i>
            <span>核保特别约定 / 除外责任提示：</span>
          </div>
          <p class="whitespace-pre-line leading-relaxed text-xs">{{ policy.exclusions }}</p>
        </div>

        <!-- 期间与渠道 -->
        <div v-if="policy.waitingPeriod || policy.gracePeriod || policy.salesChannel" class="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-[11px]">
          <div v-if="policy.waitingPeriod">
            <span class="text-slate-400">等待期：</span>
            <span class="text-slate-700 font-medium">{{ policy.waitingPeriod }}</span>
          </div>
          <div v-if="policy.gracePeriod">
            <span class="text-slate-400">宽限期：</span>
            <span class="text-slate-700 font-medium">{{ policy.gracePeriod }}</span>
          </div>
          <div v-if="policy.salesChannel" class="col-span-2">
            <span class="text-slate-400">投保渠道/服务人：</span>
            <span class="text-slate-700 font-medium">{{ policy.salesChannel }}</span>
          </div>
        </div>

        <!-- 电子保单与附件凭证 -->
        <div v-if="policy.attachments && policy.attachments.length > 0" class="space-y-1.5">
          <div class="font-bold text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-sky-600"></i>
            <span>电子保单原件与合同附件 ({{ policy.attachments.length }})：</span>
          </div>
          <div class="grid grid-cols-1 gap-2">
            <div
              v-for="att in policy.attachments"
              :key="att.id || att.storedName"
              class="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200/70"
            >
              <div class="flex items-center space-x-2 truncate">
                <i class="fa-regular fa-file-pdf text-rose-500 text-lg" v-if="att.name && att.name.endsWith('.pdf')"></i>
                <i class="fa-regular fa-file-image text-sky-500 text-lg" v-else></i>
                <div class="truncate">
                  <span class="font-medium text-slate-800 block truncate" :title="att.name">{{ att.name }}</span>
                  <span class="text-[10px] text-slate-400">{{ formatSize(att.size) }} · {{ att.uploadedAt || '已归档' }}</span>
                </div>
              </div>
              <a
                :href="getAttachmentUrl(att.url)"
                target="_blank"
                class="px-2.5 py-1 bg-white hover:bg-sky-50 text-sky-700 rounded-lg border border-slate-200 text-xs font-semibold shrink-0 ml-2 transition"
              >
                <i class="fa-regular fa-eye mr-1"></i>在线查看
              </a>

            </div>
          </div>
        </div>

        <div v-if="policy.premiumDetail" class="space-y-1">
          <div class="font-bold text-slate-700">保费分项拆解：</div>
          <p class="bg-slate-50 p-3 rounded-xl text-slate-600 whitespace-pre-line">{{ policy.premiumDetail }}</p>
        </div>

        <div v-if="policy.description" class="space-y-1">
          <div class="font-bold text-slate-700">保障责任及赔付标准：</div>
          <p class="bg-slate-50 p-3 rounded-xl text-slate-600 whitespace-pre-line leading-relaxed">{{ policy.description }}</p>
        </div>

        <div v-if="policy.extra" class="space-y-1">
          <div class="font-bold text-slate-700">附加险清单与特别约定：</div>
          <p class="bg-slate-50 p-3 rounded-xl text-slate-600 whitespace-pre-line">{{ policy.extra }}</p>
        </div>
      </div>

      <!-- 弹窗底部操作 -->
      <div class="p-3.5 sm:p-4 bg-slate-50 border-t border-slate-100 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-2 shrink-0">
        <button
          type="button"
          @click="$emit('view-payments', policy)"
          class="px-3.5 py-2 bg-emerald-50 hover:bg-emerald-100 active:bg-emerald-200 text-emerald-700 border border-emerald-200 rounded-xl font-medium text-xs transition flex items-center justify-center space-x-1.5 cursor-pointer shadow-2xs"
        >
          <i class="fa-solid fa-receipt text-emerald-600"></i>
          <span>查看该保单缴费流水与排期</span>
        </button>
        <button @click="$emit('close')" class="px-4 py-2 bg-slate-200 hover:bg-slate-300 active:bg-slate-400 text-slate-700 rounded-xl font-semibold text-xs transition cursor-pointer">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { formatMoney, getTypeBadgeClass, getCompanyPhone } from '../utils/helpers.js';
import { getAttachmentUrl } from '../api/index.js';

defineProps({
  policy: {
    type: Object,
    default: null
  },
  phoneConfig: {
    type: Object,
    default: () => ({})
  }
});

defineEmits(['close', 'view-payments']);

const copied = ref(false);

function copyPolicyNo(no) {
  if (!no) return;
  navigator.clipboard.writeText(no).then(() => {
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  }).catch(() => {});
}

function formatSize(bytes) {
  if (!bytes) return '未知大小';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
</script>

