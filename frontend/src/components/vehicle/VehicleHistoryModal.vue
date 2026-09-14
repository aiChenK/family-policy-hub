<template>
  <Teleport to="body">
    <div v-if="show && veh" class="fixed inset-0 top-0 left-0 right-0 bottom-0 z-50 !m-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-3xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[90vh] flex flex-col transition-all">
      <!-- 弹窗标题栏 -->
      <div class="px-6 py-4 bg-gradient-to-r from-sky-50 via-indigo-50/60 to-purple-50/40 border-b border-sky-100 flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-3">
          <!-- 拟真车牌样式 (防折行、防压缩) -->
          <div
            v-if="veh.plateType === 'green'"
            class="px-2.5 py-1.5 rounded-md bg-gradient-to-b from-white via-emerald-100 to-emerald-300 border-2 border-emerald-600 text-slate-950 font-extrabold font-mono text-xs tracking-wider shadow-sm inline-flex items-center space-x-1 shrink-0 whitespace-nowrap select-none leading-none"
            title="新能源汽车号牌"
          >
            <i class="fa-solid fa-bolt text-emerald-700 text-[10px] shrink-0"></i>
            <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
          </div>
          <div
            v-else-if="veh.plateType === 'yellow'"
            class="px-2.5 py-1.5 rounded-md bg-amber-300 border-2 border-amber-600 text-slate-900 font-extrabold font-mono text-xs tracking-wider shadow-sm shrink-0 whitespace-nowrap select-none leading-none inline-flex items-center justify-center"
          >
            <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
          </div>
          <div
            v-else
            class="px-2.5 py-1.5 rounded-md bg-blue-600 border-2 border-blue-400 text-white font-extrabold font-mono text-xs tracking-wider shadow-sm shadow-blue-200 shrink-0 whitespace-nowrap select-none leading-none inline-flex items-center justify-center"
          >
            <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
          </div>

          <div>
            <div class="flex items-center space-x-2">
              <h3 class="text-base font-bold text-slate-900">历年车险投保档案与凭证</h3>
              <span
                v-if="veh.isCompany || veh.companyName"
                class="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-bold text-[10px] inline-flex items-center space-x-1 border border-indigo-200/80"
              >
                <i class="fa-solid fa-building text-[9px]"></i>
                <span>公户车</span>
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">
              {{ veh.model }} · {{ (veh.isCompany || veh.companyName) ? (veh.companyName || veh.owner) : `车主: ${veh.owner}` }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="$emit('update:show', false)"
          class="text-slate-400 hover:text-slate-600 p-1.5 rounded-xl hover:bg-white/80 transition cursor-pointer"
          title="关闭弹窗"
        >
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 概览指标与操作条 -->
      <div class="px-6 py-3 bg-slate-50/80 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 shrink-0 text-xs">
        <div class="flex items-center space-x-4 text-slate-600">
          <div>
            <span>投保期数：</span>
            <strong class="font-bold font-mono text-slate-900 text-sm">{{ records.length }}</strong>
            <span class="text-slate-400 ml-0.5">期</span>
          </div>
          <div class="h-3 w-px bg-slate-200"></div>
          <div>
            <span>累计保费总额：</span>
            <strong class="font-bold font-mono text-indigo-700 text-sm">¥{{ formatMoney(totalHistoricalPremium) }}</strong>
          </div>
          <div v-if="yearSpan" class="hidden sm:flex items-center space-x-1 text-slate-500">
            <div class="h-3 w-px bg-slate-200 mr-3"></div>
            <span>跨越区间：</span>
            <span class="font-mono font-medium text-slate-700">{{ yearSpan }}</span>
          </div>
        </div>

        <!-- 补录往期保单按钮 -->
        <button
          type="button"
          @click="$emit('add-policy', veh.id)"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
        >
          <i class="fa-solid fa-plus text-[10px]"></i>
          <span>补录/录入保单</span>
        </button>
      </div>

      <!-- 历年记录明细列表 -->
      <div class="p-6 overflow-y-auto space-y-4 text-xs custom-scrollbar flex-1">
        <!-- 空状态 -->
        <div v-if="records.length === 0" class="text-center py-12 bg-slate-50/60 rounded-2xl border border-dashed border-slate-200 text-slate-400 space-y-3">
          <div class="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center text-xl">
            <i class="fa-solid fa-clock-rotate-left"></i>
          </div>
          <div class="font-medium text-slate-600 text-sm">暂无历年车险投保记录</div>
          <p class="text-xs text-slate-400 max-w-sm mx-auto">
            您可以随时为【{{ veh.plateNo }}】录入当期或往期投保保单，系统将建立终身投保与凭证台账。
          </p>
          <button
            type="button"
            @click="$emit('add-policy', veh.id)"
            class="inline-flex items-center space-x-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <i class="fa-solid fa-plus"></i>
            <span>录入首期保单</span>
          </button>
        </div>

        <!-- 历年保单卡片列表 -->
        <div
          v-for="(rec, idx) in records"
          :key="rec.id"
          class="p-4 rounded-2xl border transition shadow-2xs space-y-3"
          :class="isPolicyActive(rec) ? 'bg-sky-50/20 border-sky-200' : 'bg-white border-slate-200/80 hover:border-slate-300'"
        >
          <!-- 单期头部：年度、状态、保司、保费与操作按钮 -->
          <div class="flex items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-slate-100">
            <div class="flex items-center space-x-2.5">
              <span class="font-extrabold font-mono text-base text-slate-900">{{ rec.year }} 年度</span>
              
              <!-- 状态标签 -->
              <span
                v-if="isPolicyActive(rec)"
                class="px-2 py-0.5 bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-full text-[11px] font-bold inline-flex items-center space-x-1"
              >
                <i class="fa-solid fa-circle-check text-[10px]"></i>
                <span>当前有效 / 在保中</span>
              </span>
              <span
                v-else-if="isPolicyFuture(rec)"
                class="px-2 py-0.5 bg-sky-100 text-sky-800 border border-sky-200 rounded-full text-[11px] font-bold inline-flex items-center space-x-1"
              >
                <i class="fa-solid fa-clock text-[10px]"></i>
                <span>待生效 (已承保)</span>
              </span>
              <span
                v-else
                class="px-2 py-0.5 bg-slate-100 text-slate-500 border border-slate-200 rounded-full text-[11px] font-medium"
              >
                已到期
              </span>

              <span v-if="idx === 0" class="px-1.5 py-0.2 bg-indigo-50 text-indigo-700 rounded text-[10px] font-bold">
                最新档案
              </span>

              <span class="text-slate-600 font-semibold ml-1">
                {{ rec.company || '未填承保公司' }}
              </span>
            </div>

            <!-- 右侧保费总额与管理按钮 -->
            <div class="flex items-center space-x-3">
              <div class="text-right">
                <span class="text-[11px] text-slate-400 mr-1">保费合计:</span>
                <span class="font-extrabold font-mono text-base text-slate-900">
                  ¥{{ formatMoney(rec.totalPremium) }}
                </span>
                <div v-if="rec.cashback && Number(rec.cashback) > 0" class="text-[10px] text-emerald-700 font-semibold flex items-center justify-end space-x-1 mt-0.5">
                  <span class="bg-emerald-50 px-1 rounded border border-emerald-200">返现 ¥{{ formatMoney(rec.cashback) }}</span>
                  <span>实付 ¥{{ formatMoney(Math.max(0, (Number(rec.totalPremium) || 0) - Number(rec.cashback))) }}</span>
                </div>
              </div>
              <div class="flex items-center space-x-1 pl-2 border-l border-slate-200">
                <button
                  type="button"
                  @click="$emit('edit-policy', veh, rec)"
                  class="inline-flex items-center space-x-1 px-2.5 py-1 text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded-lg transition font-medium cursor-pointer"
                  title="编辑此期保单"
                >
                  <i class="fa-regular fa-pen-to-square text-[11px]"></i>
                  <span>编辑</span>
                </button>
                <button
                  type="button"
                  @click="$emit('delete-policy', veh, rec.id)"
                  class="inline-flex items-center space-x-1 px-2.5 py-1 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition font-medium cursor-pointer"
                  title="删除此期档案与凭证"
                >
                  <i class="fa-regular fa-trash-can text-[11px]"></i>
                  <span>删除</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 详细拆分内容网格 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[11px]">
            <!-- 商业险保障 -->
            <div class="p-2.5 bg-slate-50/70 rounded-xl space-y-1.5 border border-slate-100">
              <div class="flex justify-between items-center text-slate-700 font-bold">
                <span class="flex items-center space-x-1">
                  <i class="fa-solid fa-shield-halved text-sky-600 text-[10px]"></i>
                  <span>商业险</span>
                </span>
                <span class="font-mono text-slate-900">¥{{ formatMoney(rec.commercialPremium || 0) }}</span>
              </div>
              <div class="text-slate-500 space-y-0.5 pt-0.5">
                <div class="flex justify-between">
                  <span>三者保额：</span>
                  <span class="font-medium text-slate-800">{{ rec.thirdPartyAmount || '未投保' }}</span>
                </div>
                <div class="flex flex-wrap gap-1 pt-0.5">
                  <span v-if="rec.hasDamage" class="text-[10px] bg-emerald-100 text-emerald-800 px-1 py-0.2 rounded">
                    含车损
                  </span>
                  <span v-if="rec.hasMedicalExcluded" class="text-[10px] bg-indigo-100 text-indigo-800 px-1 py-0.2 rounded">
                    含医保外
                  </span>
                  <span v-if="rec.driverAmount" class="text-[10px] bg-slate-200/80 text-slate-700 px-1 py-0.2 rounded">
                    人员: {{ rec.driverAmount }}
                  </span>
                </div>
                <div v-if="rec.extra" class="text-[10px] text-indigo-600 truncate pt-0.5" :title="rec.extra">
                  特约: {{ rec.extra }}
                </div>
                <div v-if="rec.commercialPolicyNo" class="flex justify-between items-center font-mono text-[10px] text-slate-400 pt-0.5">
                  <span class="truncate max-w-[150px]">单号: {{ rec.commercialPolicyNo }}</span>
                  <button type="button" @click="copyText(rec.commercialPolicyNo)" class="text-sky-600 hover:text-sky-800 ml-1">
                    <i class="fa-regular fa-copy"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- 交强险与车船税 -->
            <div class="p-2.5 bg-slate-50/70 rounded-xl space-y-1.5 border border-slate-100">
              <div class="flex justify-between items-center text-slate-700 font-bold">
                <span class="flex items-center space-x-1">
                  <i class="fa-solid fa-file-invoice-dollar text-emerald-600 text-[10px]"></i>
                  <span>交强险 + 车船税</span>
                </span>
                <span class="font-mono text-slate-900">¥{{ formatMoney((Number(rec.compulsoryPremium) || 0) + (Number(rec.tax) || 0)) }}</span>
              </div>
              <div class="text-slate-500 space-y-0.5 pt-0.5">
                <div class="flex justify-between">
                  <span>交强保费：</span>
                  <span class="font-mono text-slate-800">¥{{ formatMoney(rec.compulsoryPremium || 0) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>车船税：</span>
                  <span class="font-mono text-slate-800">¥{{ formatMoney(rec.tax || 0) }}</span>
                </div>
                <div v-if="rec.compulsoryPolicyNo" class="flex justify-between items-center font-mono text-[10px] text-slate-400 pt-0.5">
                  <span class="truncate max-w-[150px]">单号: {{ rec.compulsoryPolicyNo }}</span>
                  <button type="button" @click="copyText(rec.compulsoryPolicyNo)" class="text-sky-600 hover:text-sky-800 ml-1">
                    <i class="fa-regular fa-copy"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- 驾乘险与起止期限 -->
            <div class="p-2.5 bg-slate-50/70 rounded-xl space-y-1.5 border border-slate-100">
              <div class="flex justify-between items-center text-slate-700 font-bold">
                <span class="flex items-center space-x-1">
                  <i class="fa-solid fa-user-shield text-purple-600 text-[10px]"></i>
                  <span>驾乘险 / 保障期</span>
                </span>
                <span class="font-mono text-purple-700 font-bold">
                  {{ rec.accidentPremium ? `¥${formatMoney(rec.accidentPremium)}` : '未单独投保' }}
                </span>
              </div>
              <div class="text-slate-500 space-y-0.5 pt-0.5">
                <div class="flex justify-between">
                  <span>起止日期：</span>
                  <span class="font-mono text-slate-700">{{ rec.startDate || '-' }} ~ {{ rec.endDate || '-' }}</span>
                </div>
                <div v-if="rec.accidentPolicyNo" class="flex justify-between items-center font-mono text-[10px] text-slate-400 pt-0.5">
                  <span class="truncate max-w-[150px]">驾乘单号: {{ rec.accidentPolicyNo }}</span>
                  <button type="button" @click="copyText(rec.accidentPolicyNo)" class="text-sky-600 hover:text-sky-800 ml-1">
                    <i class="fa-regular fa-copy"></i>
                  </button>
                </div>
                <div v-if="rec.company && getAutoCompanyPhone(rec.company)" class="pt-0.5">
                  <span class="text-slate-400">报案电话: </span>
                  <span class="font-mono font-medium text-emerald-700">{{ getAutoCompanyPhone(rec.company) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 附件与凭证展示 -->
          <div v-if="rec.attachments && rec.attachments.length > 0" class="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-2">
            <span class="text-[11px] text-slate-400 flex items-center space-x-1">
              <i class="fa-solid fa-paperclip text-slate-400 text-[10px]"></i>
              <span>保单凭证 ({{ rec.attachments.length }})：</span>
            </span>
            <a
              v-for="(att, aIdx) in rec.attachments"
              :key="aIdx"
              :href="getAttachmentUrl(att.url)"
              target="_blank"
              class="inline-flex items-center space-x-1 px-2.5 py-1 bg-slate-50 hover:bg-sky-50 text-slate-700 hover:text-sky-700 border border-slate-200 rounded-lg text-[11px] transition shadow-2xs"
            >
              <i class="fa-regular" :class="att.name?.endsWith('.pdf') ? 'fa-file-pdf text-rose-500' : 'fa-file-image text-sky-500'"></i>
              <span class="truncate max-w-[160px]">{{ att.name }}</span>
              <i class="fa-solid fa-arrow-up-right-from-square text-[9px] text-slate-400"></i>
            </a>
          </div>

          <!-- 备忘说明 (如有) -->
          <div v-if="rec.remark" class="text-[11px] text-slate-500 italic bg-amber-50/50 p-2 rounded-lg border border-amber-100/60">
            <i class="fa-regular fa-comment-dots mr-1 text-amber-500"></i>
            <span>{{ rec.remark }}</span>
          </div>
        </div>
      </div>

      <!-- 弹窗底部操作栏 -->
      <div class="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
        <div class="text-xs text-slate-400">
          共 {{ records.length }} 期投保凭证已归档
        </div>
        <button
          type="button"
          @click="$emit('update:show', false)"
          class="px-5 py-2 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 font-semibold rounded-xl text-xs transition shadow-2xs cursor-pointer"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</Teleport>
</template>

<script setup>
import { computed } from 'vue';
import { formatMoney, getTodayStr, getCompanyPhone } from '../../utils/helpers.js';
import { extractVehicleInsuranceRecords } from '../../utils/payment-schedule.js';
import { getAttachmentUrl } from '../../api/index.js';

const props = defineProps({
  show: { type: Boolean, default: false },
  veh: { type: Object, default: null },
  phoneConfig: { type: Object, default: () => ({}) }
});

defineEmits([
  'update:show',
  'add-policy',
  'edit-policy',
  'delete-policy'
]);

const records = computed(() => {
  if (!props.veh) return [];
  const list = extractVehicleInsuranceRecords(props.veh);
  return [...list].sort((a, b) => (Number(b.year) || 0) - (Number(a.year) || 0));
});

const totalHistoricalPremium = computed(() => {
  return records.value.reduce((sum, r) => sum + (Number(r.totalPremium) || 0), 0);
});

const yearSpan = computed(() => {
  if (records.value.length === 0) return '';
  const years = records.value.map(r => Number(r.year)).filter(Boolean);
  if (years.length === 0) return '';
  const min = Math.min(...years);
  const max = Math.max(...years);
  return min === max ? `${min} 年度` : `${min} ~ ${max} 年度`;
});

function isPolicyActive(rec) {
  if (!rec) return false;
  const today = getTodayStr();
  if (rec.endDate) {
    return rec.endDate >= today && (!rec.startDate || rec.startDate <= today);
  }
  return Number(rec.year) === new Date().getFullYear();
}

function isPolicyFuture(rec) {
  if (!rec) return false;
  const today = getTodayStr();
  return rec.startDate && rec.startDate > today;
}

function getAutoCompanyPhone(company) {
  return getCompanyPhone(company, props.phoneConfig);
}

function copyText(text) {
  if (!text) return;
  navigator.clipboard.writeText(text);
}
</script>
