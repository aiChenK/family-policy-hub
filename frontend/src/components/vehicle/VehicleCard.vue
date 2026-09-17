<template>
  <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md transition flex flex-col justify-between overflow-hidden">
    <div class="p-4 sm:p-6 space-y-4">
      <!-- 卡片头部：车牌与车辆基本信息 + 右侧在保状态胶囊 -->
      <div class="space-y-2 sm:space-y-0 sm:flex sm:items-start sm:justify-between sm:gap-3">
        <!-- 移动端第 1 行 / 桌面端左侧核心区：车牌与在保状态 -->
        <div class="flex items-center justify-between sm:justify-start sm:space-x-3">
          <!-- 拟真车牌样式 (防折行、防压缩) -->
          <div class="flex items-center space-x-2">
            <div
              v-if="veh.plateType === 'green'"
              class="px-2.5 py-1.5 rounded-md bg-gradient-to-b from-white via-emerald-100 to-emerald-300 border-2 border-emerald-600 text-slate-950 font-extrabold font-mono text-xs sm:text-sm tracking-wider shadow-sm inline-flex items-center space-x-1 shrink-0 whitespace-nowrap select-none leading-none"
              title="新能源汽车号牌"
            >
              <i class="fa-solid fa-bolt text-emerald-700 text-[10px] shrink-0"></i>
              <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
            </div>
            <div
              v-else-if="veh.plateType === 'yellow'"
              class="px-2.5 py-1.5 rounded-md bg-amber-300 border-2 border-amber-600 text-slate-900 font-extrabold font-mono text-xs sm:text-sm tracking-wider shadow-sm shrink-0 whitespace-nowrap select-none leading-none inline-flex items-center justify-center"
            >
              <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
            </div>
            <div
              v-else
              class="px-2.5 py-1.5 rounded-md bg-blue-600 border-2 border-blue-400 text-white font-extrabold font-mono text-xs sm:text-sm tracking-wider shadow-sm shadow-blue-200 shrink-0 whitespace-nowrap select-none leading-none inline-flex items-center justify-center"
            >
              <span class="whitespace-nowrap inline-block">{{ veh.plateNo }}</span>
            </div>

            <!-- 公户车徽标 -->
            <span
              v-if="veh.isCompany || veh.companyName"
              class="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-bold text-[10px] inline-flex items-center space-x-1 border border-indigo-200/80 shadow-2xs shrink-0"
            >
              <i class="fa-solid fa-building text-[9px]"></i>
              <span>公户</span>
            </span>
          </div>

          <!-- 仅在小屏手机端显示的在保状态徽章 (右对齐，与车牌整洁呼应) -->
          <div class="sm:hidden text-right shrink-0">
            <span
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold shadow-2xs"
              :class="getInsuranceStatusClass(veh)"
            >
              <i class="fa-solid mr-1 text-[9px]" :class="getInsuranceStatusIcon(veh)"></i>
              <span>{{ getInsuranceStatusText(veh) }}</span>
            </span>
          </div>
        </div>

        <!-- 车型信息与所有人归属 -->
        <div class="min-w-0 flex-1 sm:mt-0 mt-1.5">
          <!-- 车型大标题：整行舒展，不再被右侧徽章挤压折断 -->
          <h4 class="text-sm sm:text-base font-bold text-slate-900 leading-snug">
            {{ veh.model }}
          </h4>

          <!-- 所有人 / 行驶证 / 到期时间元信息行 -->
          <div class="text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1">
            <template v-if="veh.isCompany || veh.companyName">
              <span>所有人：<strong class="text-slate-700 font-semibold">{{ veh.companyName || veh.owner }}</strong></span>
              <span v-if="veh.driver" class="text-indigo-600 font-medium shrink-0">(使用人: {{ veh.driver }})</span>
              <button
                type="button"
                @click.stop="$emit('view-company', veh.companyName || veh.owner)"
                class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-medium text-[10px] border border-indigo-200/60 shadow-2xs transition cursor-pointer shrink-0"
                title="查看该公司的营业执照照片与开票税号"
              >
                <i class="fa-regular fa-file-lines text-[9px]"></i>
                <span>执照/开票</span>
              </button>
            </template>
            <template v-else>
              <span>所有人：<strong class="text-slate-700 font-semibold">{{ veh.owner }}</strong></span>
            </template>

            <!-- 车辆行驶证快捷查看 -->
            <template v-if="veh.attachments && veh.attachments.length > 0">
              <a
                v-for="(att, idx) in veh.attachments"
                :key="idx"
                :href="getAttachmentUrl(att.url)"
                target="_blank"
                class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 font-medium text-[10px] border border-sky-200/80 shadow-2xs transition cursor-pointer shrink-0"
                :title="'点击查看行驶证原件：' + att.name"
              >
                <i class="fa-solid fa-id-card text-sky-600 text-[9px]"></i>
                <span>行驶证{{ veh.attachments.length > 1 ? `(${idx + 1})` : '' }}</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[8px] text-sky-500"></i>
              </a>
            </template>

            <!-- 手机端到期日期轻量显示 -->
            <span v-if="activePolicy?.endDate" class="sm:hidden text-[11px] text-slate-400 font-mono">
              到期：{{ activePolicy.endDate }}
            </span>
            <span v-else-if="latestPolicy?.endDate" class="sm:hidden text-[11px] text-rose-500 font-mono">
              已于 {{ latestPolicy.endDate }} 到期
            </span>
          </div>
        </div>

        <!-- 仅在平板/桌面端（sm及以上）显示的右侧状态胶囊与到期日 -->
        <div class="hidden sm:block text-right shrink-0">
          <span
            class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold shadow-2xs"
            :class="getInsuranceStatusClass(veh)"
          >
            <i class="fa-solid mr-1 text-[10px]" :class="getInsuranceStatusIcon(veh)"></i>
            <span>{{ getInsuranceStatusText(veh) }}</span>
          </span>
          <div v-if="activePolicy?.endDate" class="text-[11px] text-slate-400 font-mono mt-1">
            到期：{{ activePolicy.endDate }}
          </div>
          <div v-else-if="latestPolicy?.endDate" class="text-[11px] text-rose-400 font-mono mt-1">
            已于 {{ latestPolicy.endDate }} 到期
          </div>
        </div>
      </div>

      <!-- 核心内容区：按状态精细化展示 -->

      <!-- 1. 无任何投保记录：引导录入首期保单 -->
      <div v-if="records.length === 0" class="p-6 bg-slate-50/70 rounded-2xl border border-dashed border-slate-200 text-center space-y-2">
        <div class="w-10 h-10 rounded-full bg-sky-100 text-sky-600 mx-auto flex items-center justify-center text-base">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h5 class="text-xs font-bold text-slate-700">暂未关联车险保单</h5>
        <p class="text-[11px] text-slate-400 max-w-sm mx-auto">
          车辆档案已建立。点击下方按钮录入该车辆的首期商业险或交强险保单，将自动生成到期预警与全家缴费排期。
        </p>
        <div class="pt-1">
          <button
            type="button"
            @click="$emit('add-policy', veh.id)"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <i class="fa-solid fa-plus text-[10px]"></i>
            <span>为该车录入首期保单</span>
          </button>
        </div>
      </div>

      <!-- 2. 有历史保单但当前已全部脱保/过期：展示明确脱保警示，并引导续保与查看历史 -->
      <div v-else-if="!activePolicy" class="p-5 bg-rose-50/50 rounded-2xl border border-rose-200/80 text-center space-y-3">
        <div class="w-10 h-10 rounded-full bg-rose-100 text-rose-600 mx-auto flex items-center justify-center text-base">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div>
          <h5 class="text-xs font-bold text-rose-900">当前暂无有效在保保单</h5>
          <p class="text-[11px] text-rose-600/80 mt-1 max-w-sm mx-auto">
            上一期保单已于 <span class="font-mono font-bold">{{ latestPolicy?.endDate || (latestPolicy?.year + '年') }}</span> 到期脱保。请及时办理续保以确保行车保障。
          </p>
        </div>
        <div class="flex items-center justify-center space-x-2 pt-1">
          <button
            type="button"
            @click="$emit('renew', veh)"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <i class="fa-solid fa-arrows-rotate text-[10px]"></i>
            <span>立即办理续保</span>
          </button>
          <button
            type="button"
            @click="$emit('open-history', veh)"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-xl text-xs font-medium transition cursor-pointer shadow-2xs"
          >
            <i class="fa-solid fa-clock-rotate-left text-slate-500 text-[10px]"></i>
            <span>查看历年档案 ({{ records.length }})</span>
          </button>
        </div>
      </div>

      <!-- 3. 有当前有效保单：现代金融凭证式左右分栏结构（无色块嵌套，唯一主金额） -->
      <template v-else>
        <div class="rounded-2xl border border-slate-200/80 bg-slate-50/40 p-3 sm:p-4 grid grid-cols-1 lg:grid-cols-12 gap-3.5 sm:gap-4 text-xs">
          <!-- 左侧分区：保障责任与机构服务 (占比 7/12) -->
          <div class="lg:col-span-7 space-y-2.5">
            <!-- 承保保司与报案专线 -->
            <div class="flex items-center justify-between flex-wrap gap-2">
              <div class="flex items-center space-x-2">
                <span class="w-6 h-6 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center text-xs shadow-2xs shrink-0">
                  <i class="fa-solid fa-shield-halved"></i>
                </span>
                <span class="font-bold text-slate-800 text-sm">
                  {{ activePolicy.company || '未填承保机构' }}
                </span>
                <span class="text-[11px] text-slate-400 font-mono">
                  ({{ activePolicy.year }}年度保单)
                </span>
              </div>

              <!-- 报案电话快捷呼叫按钮 -->
              <a
                v-if="activePolicy.company && getAutoCompanyPhone(activePolicy.company)"
                :href="'tel:' + getAutoCompanyPhone(activePolicy.company)"
                class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200/80 rounded-lg text-[11px] font-semibold flex items-center space-x-1 transition shadow-2xs cursor-pointer shrink-0"
                title="一键拨打报案电话"
              >
                <i class="fa-solid fa-phone text-[10px]"></i>
                <span>报案: {{ getAutoCompanyPhone(activePolicy.company) }}</span>
              </a>
            </div>

            <!-- 核心保障责任胶囊组 -->
            <div class="flex flex-wrap items-center gap-1.5 pt-0.5">
              <span class="px-2 py-0.5 rounded-lg bg-sky-100/80 text-sky-800 font-semibold text-[11px] border border-sky-200/60">
                三者险: {{ activePolicy.thirdPartyAmount || '未投保' }}
              </span>
              <span v-if="activePolicy.hasDamage" class="px-2 py-0.5 rounded-lg bg-emerald-100/70 text-emerald-800 font-medium text-[11px] border border-emerald-200/60">
                含车损险
              </span>
              <span v-if="activePolicy.hasMedicalExcluded" class="px-2 py-0.5 rounded-lg bg-indigo-100/70 text-indigo-800 font-medium text-[11px] border border-indigo-200/60">
                含医保外用药
              </span>
              <span v-if="activePolicy.driverAmount" class="px-2 py-0.5 rounded-lg bg-slate-200/70 text-slate-700 font-medium text-[11px]">
                人员: {{ activePolicy.driverAmount }}
              </span>
              <span v-if="Number(activePolicy.accidentPremium)" class="px-2 py-0.5 rounded-lg bg-purple-100/70 text-purple-800 font-medium text-[11px] border border-purple-200/60">
                驾乘险 ¥{{ formatMoney(activePolicy.accidentPremium) }}
              </span>
            </div>

            <!-- 特约增值服务与保单单号清单（交强险单号优先，首字垂直对齐） -->
            <div class="space-y-1 text-[11px] text-slate-500 pt-1 border-t border-slate-200/60">
              <div v-if="activePolicy.extra" class="text-indigo-700 font-medium truncate" :title="activePolicy.extra">
                <span>增值特约: {{ activePolicy.extra }}</span>
              </div>

              <!-- 交强险单号（优先展示） -->
              <div v-if="activePolicy.compulsoryPolicyNo" class="flex items-center space-x-1.5 font-mono text-slate-500">
                <span class="truncate max-w-[240px]">交强单号: {{ activePolicy.compulsoryPolicyNo }}</span>
                <button type="button" @click="copyText(activePolicy.compulsoryPolicyNo)" class="text-sky-600 hover:text-sky-800 cursor-pointer" title="复制交强险保单号">
                  <i class="fa-regular fa-copy"></i>
                </button>
              </div>

              <!-- 商业险单号 -->
              <div v-if="activePolicy.commercialPolicyNo" class="flex items-center space-x-1.5 font-mono text-slate-500">
                <span class="truncate max-w-[240px]">商业单号: {{ activePolicy.commercialPolicyNo }}</span>
                <button type="button" @click="copyText(activePolicy.commercialPolicyNo)" class="text-sky-600 hover:text-sky-800 cursor-pointer" title="复制商业险保单号">
                  <i class="fa-regular fa-copy"></i>
                </button>
              </div>

              <!-- 驾乘险单号 (如有) -->
              <div v-if="activePolicy.accidentPolicyNo" class="flex items-center space-x-1.5 font-mono text-slate-400">
                <span class="truncate max-w-[240px]">驾乘单号: {{ activePolicy.accidentPolicyNo }}</span>
                <button type="button" @click="copyText(activePolicy.accidentPolicyNo)" class="text-sky-600 hover:text-sky-800 cursor-pointer" title="复制驾乘险保单号">
                  <i class="fa-regular fa-copy"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧分区：年度费用清单与保险期间 (占比 5/12，全卡片唯一主金额) -->
          <div class="lg:col-span-5 lg:border-l lg:border-slate-200/80 lg:pl-4 flex flex-col justify-between space-y-2 border-t lg:border-t-0 pt-2 lg:pt-0 border-slate-200/60 min-w-0">
            <div>
              <div class="flex items-baseline justify-between gap-2">
                <span class="text-xs font-semibold text-slate-500 shrink-0 whitespace-nowrap">保费总额</span>
                <div class="text-right">
                  <span class="font-bold font-mono text-lg text-slate-900 tracking-tight shrink-0 whitespace-nowrap">
                    ¥{{ formatMoney(activePolicyTotal) }}
                  </span>
                  <div v-if="activePolicy.cashback && Number(activePolicy.cashback) > 0" class="text-[10px] text-emerald-700 font-medium">
                    实付 ¥{{ formatMoney(Math.max(0, activePolicyTotal - Number(activePolicy.cashback))) }}
                  </div>
                </div>
              </div>

              <!-- 分项轻量清单 -->
              <div class="mt-2 space-y-1 text-[11px] text-slate-500">
                <div class="flex justify-between items-center">
                  <span class="shrink-0 whitespace-nowrap">商业险保费：</span>
                  <span class="font-mono font-medium text-slate-700 shrink-0 whitespace-nowrap">¥{{ formatMoney(activePolicy.commercialPremium || 0) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="shrink-0 whitespace-nowrap">交强险保费：</span>
                  <span class="font-mono font-medium text-slate-700 shrink-0 whitespace-nowrap">¥{{ formatMoney(activePolicy.compulsoryPremium || 0) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="shrink-0 whitespace-nowrap">车船税：</span>
                  <span class="font-mono font-medium shrink-0 whitespace-nowrap text-slate-700">
                    ¥{{ formatMoney(activePolicy.tax || 0) }}
                  </span>
                </div>
                <div v-if="activePolicy.accidentPremium" class="flex justify-between items-center">
                  <span class="shrink-0 whitespace-nowrap">驾乘险保费：</span>
                  <span class="font-mono font-medium text-purple-700 shrink-0 whitespace-nowrap">¥{{ formatMoney(activePolicy.accidentPremium) }}</span>
                </div>
                <div v-if="activePolicy.cashback && Number(activePolicy.cashback) > 0" class="flex justify-between items-center text-emerald-700 font-medium pt-0.5 border-t border-dashed border-slate-200/80">
                  <span class="shrink-0 whitespace-nowrap flex items-center space-x-1">
                    <i class="fa-solid fa-gift text-[10px] text-emerald-600"></i>
                    <span>渠道返现：</span>
                  </span>
                  <span class="font-mono font-bold shrink-0 whitespace-nowrap">-¥{{ formatMoney(activePolicy.cashback) }}</span>
                </div>
              </div>
            </div>

            <!-- 保险起止期间 (换行展示) -->
            <div class="pt-1.5 border-t border-slate-200/60 font-mono text-[11px]">
              <div class="text-slate-400 whitespace-nowrap">保险期限:</div>
              <div class="text-slate-700 font-medium whitespace-nowrap mt-0.5">
                {{ activePolicy.startDate || '-' }} ~ {{ activePolicy.endDate || '-' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 凭证附件与备忘快捷栏 (纯粹保单凭证) -->
        <div class="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
          <div class="flex items-center space-x-2 flex-wrap gap-1">
            <!-- 保单凭证附件列表 -->
            <div v-if="activePolicy?.attachments && activePolicy.attachments.length > 0" class="flex items-center space-x-1.5 flex-wrap gap-1">
              <span class="text-slate-400 text-[11px] flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-sky-600 text-[10px]"></i>
                <span>保单凭证:</span>
              </span>
              <a
                v-for="(att, aIdx) in activePolicy.attachments"
                :key="aIdx"
                :href="getAttachmentUrl(att.url)"
                target="_blank"
                class="inline-flex items-center space-x-1 px-2 py-0.5 bg-slate-50 hover:bg-sky-50 text-slate-600 hover:text-sky-700 border border-slate-200 rounded text-[10px] transition shadow-2xs"
                :title="att.name"
              >
                <i class="fa-regular" :class="att.name?.endsWith('.pdf') ? 'fa-file-pdf text-rose-500' : 'fa-file-image text-sky-500'"></i>
                <span class="truncate max-w-[110px]">{{ att.name }}</span>
              </a>
            </div>
            <span v-else class="text-slate-400 text-[11px]">暂未上传电子保单附件</span>
          </div>

          <div class="flex items-center space-x-3 text-[11px]">
            <span v-if="veh.annualInspectionDate" class="font-mono text-slate-400">
              年检到期: <strong class="text-slate-600 font-medium">{{ veh.annualInspectionDate }}</strong>
            </span>
            <button
              type="button"
              @click="$emit('edit-policy', veh, activePolicy)"
              class="text-sky-600 hover:text-sky-800 font-medium flex items-center space-x-1 cursor-pointer"
              title="编辑当期保单数据与附件"
            >
              <i class="fa-regular fa-pen-to-square"></i>
              <span>编辑当期保单</span>
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- 底部操作栏 -->
    <div class="px-4 sm:px-6 py-3 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between text-xs flex-wrap gap-2">
      <div class="font-mono text-slate-400 text-[11px]">
        <span v-if="veh.vin">VIN: {{ veh.vin }}</span>
        <span v-else>初登: {{ veh.registerDate || '未登记' }}</span>
      </div>

      <div class="flex items-center space-x-2">
        <!-- 历年保单弹窗展示及管理入口 -->
        <button
          type="button"
          @click="$emit('open-history', veh)"
          class="px-2.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-xl font-medium transition shadow-2xs flex items-center space-x-1.5 cursor-pointer"
          title="点击弹窗查看与管理历年车险投保档案与凭证"
        >
          <i class="fa-solid fa-clock-rotate-left text-sky-600 text-[11px]"></i>
          <span>历年保单 ({{ records.length }})</span>
        </button>

        <!-- 办理续保 / 录入保单 -->
        <button
          v-if="records.length > 0"
          @click="$emit('renew', veh)"
          class="px-3 py-1.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center space-x-1 cursor-pointer"
        >
          <i class="fa-solid fa-arrows-rotate text-[10px]"></i>
          <span>办理续保</span>
        </button>
        <button
          v-else
          @click="$emit('add-policy', veh.id)"
          class="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center space-x-1 cursor-pointer"
        >
          <i class="fa-solid fa-plus text-[10px]"></i>
          <span>录保单</span>
        </button>

        <!-- 车辆独立编辑 (只改车，不碰保单) -->
        <button
          @click="$emit('edit-vehicle', veh)"
          class="px-2.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-xl font-medium transition shadow-2xs cursor-pointer"
        >
          编辑车辆
        </button>
        <button
          @click="$emit('delete-vehicle', veh.id)"
          class="px-2 py-1.5 text-rose-500 hover:text-rose-700 font-medium transition cursor-pointer"
        >
          删除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { formatMoney, getTodayStr, getCompanyPhone } from '../../utils/helpers.js';
import { extractVehicleInsuranceRecords } from '../../utils/payment-schedule.js';
import { getAttachmentUrl } from '../../api/index.js';

const props = defineProps({
  veh: { type: Object, required: true },
  phoneConfig: { type: Object, default: () => ({}) }
});

defineEmits([
  'open-history',
  'renew',
  'add-policy',
  'edit-vehicle',
  'delete-vehicle',
  'edit-policy',
  'delete-policy',
  'view-company'
]);

const records = computed(() => {
  const list = extractVehicleInsuranceRecords(props.veh);
  return [...list].sort((a, b) => (Number(b.year) || 0) - (Number(a.year) || 0));
});

// 最新一期记录（可能已到期，也可能在保）
const latestPolicy = computed(() => records.value.length > 0 ? records.value[0] : null);

// 当前有效保单：筛选在保中的保单（endDate >= today 或当期有效）
const activePolicy = computed(() => {
  if (records.value.length === 0) return null;
  const today = getTodayStr();

  // 1. 查找 endDate 尚未过期的保单
  const unexpired = records.value.filter(r => {
    if (r.endDate) return r.endDate >= today;
    return Number(r.year) >= new Date().getFullYear();
  });

  if (unexpired.length === 0) return null;

  // 2. 优先找当前正在生效期内的保单（startDate <= today <= endDate）
  const running = unexpired.find(r => r.startDate && r.startDate <= today && r.endDate >= today);
  if (running) return running;

  // 3. 否则取未过期中最新的一期（例如刚提前续保但尚未到生效日起始日）
  return unexpired[0];
});

// 当前有效保单的合计保费（商业险 + 交强险 + 车船税 + 驾乘险）
const activePolicyTotal = computed(() => {
  if (!activePolicy.value) return 0;
  const p = activePolicy.value;
  if (p.totalPremium !== null && p.totalPremium !== undefined && p.totalPremium !== '' && !isNaN(Number(p.totalPremium))) {
    return Number(p.totalPremium);
  }
  const c = Number(p.commercialPremium) || 0;
  const comp = Number(p.compulsoryPremium) || 0;
  const t = Number(p.tax) || 0;
  const acc = Number(p.accidentPremium) || 0;
  return c + comp + t + acc;
});

function getAutoCompanyPhone(company) {
  return getCompanyPhone(company, props.phoneConfig);
}

function copyText(text) {
  if (!text) return;
  navigator.clipboard.writeText(text);
}

function getDaysUntilExpire(veh) {
  // 如果有有效保单，计算有效保单剩余天数；否则计算最近一期脱保天数
  const target = activePolicy.value || latestPolicy.value;
  if (!target || !target.endDate) return null;
  const today = new Date(getTodayStr());
  const endDate = new Date(target.endDate);
  const diffTime = endDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function getInsuranceStatusText(veh) {
  const days = getDaysUntilExpire(veh);
  if (days === null) return '待录保单';
  if (days < 0) return `已脱保 ${Math.abs(days)} 天`;
  if (days === 0) return '今日到期';
  if (days <= 30) return `剩 ${days} 天到期`;
  return `在保中 (剩 ${days} 天)`;
}

function getInsuranceStatusClass(veh) {
  const days = getDaysUntilExpire(veh);
  if (days === null) return 'bg-slate-100 text-slate-600 border border-slate-200';
  if (days < 0) return 'bg-rose-100 text-rose-800 border border-rose-200';
  if (days <= 30) return 'bg-amber-100 text-amber-900 border border-amber-300 animate-pulse';
  return 'bg-emerald-50 text-emerald-700 border border-emerald-200/60';
}

function getInsuranceStatusIcon(veh) {
  const days = getDaysUntilExpire(veh);
  if (days === null) return 'fa-circle-question text-slate-400';
  if (days < 0) return 'fa-triangle-exclamation text-rose-600';
  if (days <= 30) return 'fa-clock-rotate-left text-amber-600';
  return 'fa-shield-check text-emerald-600';
}
</script>
