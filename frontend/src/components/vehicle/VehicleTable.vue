<template>
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
    <div class="overflow-x-auto custom-scrollbar">
      <table class="min-w-[1260px] w-full divide-y divide-slate-200 text-xs text-left border-separate border-spacing-0">
        <thead class="bg-slate-50 font-semibold text-slate-600">
          <tr>
            <!-- 固定头部首列：车牌号 -->
            <th class="sticky left-0 z-20 bg-slate-50 py-3 px-4 whitespace-nowrap min-w-[110px] shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80">
              车牌号
            </th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[140px]">车型</th>
            <!-- 所有人列加宽，尽量不换行 -->
            <th class="py-3 px-4 whitespace-nowrap min-w-[240px]">所有人</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[90px]">最新保司</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[80px]">三者保额</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[105px]">商业险保费</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[110px]">交强+车船税</th>
            <!-- 新增：总保费列（方案C：双行直观并列 应付 与 实付/返现） -->
            <th class="py-3 px-4 whitespace-nowrap min-w-[140px]">总保费</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[110px]">商业险到期日</th>
            <th class="py-3 px-4 whitespace-nowrap min-w-[140px]">保险状态</th>
            <!-- 固定尾部列：操作列 -->
            <th class="sticky right-0 z-20 bg-slate-50 py-3 px-4 text-right whitespace-nowrap min-w-[120px] shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="veh in filteredVehicles"
            :key="veh.id"
            class="group hover:bg-slate-50/80 transition-colors"
          >
            <!-- 固定头部首列：车牌号（稍微放大、加粗等宽、跟随整行hover底色） -->
            <td class="sticky left-0 z-10 bg-white group-hover:bg-slate-50/90 transition-colors py-3 px-4 whitespace-nowrap shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80">
              <span class="font-mono font-bold text-sm text-slate-900 tracking-wide select-all">
                {{ veh.plateNo }}
              </span>
            </td>

            <!-- 车型 -->
            <td class="py-3 px-4 font-medium text-slate-800 whitespace-nowrap">
              {{ veh.model }}
            </td>

            <!-- 所有人：加宽不折行 -->
            <td class="py-3 px-4 min-w-[240px] whitespace-nowrap text-slate-700">
              <div class="flex items-center space-x-1.5 flex-nowrap">
                <span
                  v-if="veh.isCompany || veh.companyName"
                  class="px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-700 text-[10px] font-bold shrink-0"
                >
                  公户
                </span>
                <span class="font-medium text-slate-800" :title="veh.companyName || veh.owner">
                  {{ veh.companyName || veh.owner }}
                </span>
                <!-- 行驶证快速查看链接 (如有) -->
                <a
                  v-if="veh.attachments && veh.attachments.length > 0"
                  :href="getAttachmentUrl(veh.attachments[0].url)"
                  target="_blank"
                  class="text-[10px] text-sky-700 hover:text-sky-800 bg-sky-50 hover:bg-sky-100 px-1.5 py-0.5 rounded-md border border-sky-200 inline-flex items-center space-x-0.5 shrink-0 transition cursor-pointer"
                  :title="'查看行驶证原件：' + veh.attachments[0].name"
                >
                  <i class="fa-solid fa-id-card text-[9px] text-sky-600"></i>
                  <span>行驶证</span>
                  <i class="fa-solid fa-arrow-up-right-from-square text-[8px] text-sky-500"></i>
                </a>
              </div>
              <div v-if="veh.isCompany || veh.companyName" class="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5 whitespace-nowrap">
                <span v-if="veh.driver">使用人: {{ veh.driver }}</span>
                <button
                  type="button"
                  @click.stop="$emit('view-company', veh.companyName || veh.owner)"
                  class="text-[10px] text-indigo-600 hover:text-indigo-800 underline flex items-center space-x-0.5 cursor-pointer"
                  title="查看营业执照与开票代码"
                >
                  <i class="fa-regular fa-file-lines text-[9px]"></i>
                  <span>执照/开票</span>
                </button>
              </div>
            </td>

            <!-- 最新保司 -->
            <td class="py-3 px-4 whitespace-nowrap text-slate-600">
              {{ getActivePolicy(veh) ? (getActivePolicy(veh).company || '-') : (getVehicleRecords(veh).length > 0 ? '已脱保' : '未录保单') }}
            </td>

            <!-- 三者保额 -->
            <td class="py-3 px-4 whitespace-nowrap text-slate-700">
              {{ getActivePolicy(veh)?.thirdPartyAmount || '-' }}
            </td>

            <!-- 商业险保费 -->
            <td class="py-3 px-4 whitespace-nowrap font-bold text-slate-900">
              <template v-if="getActivePolicy(veh)">
                <span v-if="getActivePolicy(veh).commercialPremium">
                  ¥{{ formatMoney(getActivePolicy(veh).commercialPremium) }}
                </span>
                <span v-else-if="getActivePolicy(veh).totalPremium" class="text-indigo-700">
                  总¥{{ formatMoney(getActivePolicy(veh).totalPremium) }}
                </span>
                <span v-else>-</span>
              </template>
              <template v-else-if="getVehicleRecords(veh).length > 0">
                <span class="text-rose-500 text-[11px] font-normal">已脱保</span>
              </template>
              <template v-else>-</template>
            </td>

            <!-- 交强+车船税：驾乘险换行展示 -->
            <td class="py-3 px-4 whitespace-nowrap font-medium text-slate-700">
              <template v-if="getActivePolicy(veh)">
                <div
                  v-if="(Number(getActivePolicy(veh).compulsoryPremium) || 0) + (Number(getActivePolicy(veh).tax) || 0) > 0"
                  class="flex flex-col items-start leading-tight"
                >
                  <span class="text-slate-800">
                    ¥{{ formatMoney((Number(getActivePolicy(veh).compulsoryPremium) || 0) + (Number(getActivePolicy(veh).tax) || 0)) }}
                  </span>
                  <span
                    v-if="getActivePolicy(veh).accidentPremium"
                    class="text-[10px] text-purple-600 font-medium mt-0.5"
                  >
                    驾乘 ¥{{ formatMoney(getActivePolicy(veh).accidentPremium) }}
                  </span>
                </div>
                <div
                  v-else-if="getActivePolicy(veh).accidentPremium"
                  class="flex flex-col items-start leading-tight"
                >
                  <span class="text-slate-400">-</span>
                  <span class="text-[10px] text-purple-600 font-medium mt-0.5">
                    驾乘 ¥{{ formatMoney(getActivePolicy(veh).accidentPremium) }}
                  </span>
                </div>
                <span v-else class="text-slate-400">-</span>
              </template>
              <template v-else-if="getVehicleRecords(veh).length > 0">
                <span class="text-rose-500 text-[11px] font-normal">已脱保</span>
              </template>
              <template v-else><span class="text-slate-400">-</span></template>
            </td>

            <!-- 总保费列（方案C：双行直观并列 应付 与 实付/返现） -->
            <td class="py-3 px-4 whitespace-nowrap">
              <template v-if="getActivePolicy(veh)">
                <div v-if="getTotalPremium(veh) !== null" class="flex flex-col items-start leading-tight">
                  <!-- 有返现时：第一行应付，第二行实付与返现 -->
                  <template v-if="getCashback(veh) > 0">
                    <span class="text-[11px] text-slate-500 font-mono">
                      应付 ¥{{ formatMoney(getTotalPremium(veh)) }}
                    </span>
                    <span class="text-xs font-bold text-emerald-700 font-mono mt-0.5">
                      实付 ¥{{ formatMoney(Math.max(0, getTotalPremium(veh) - getCashback(veh))) }}
                      <span class="text-[10px] font-medium text-emerald-600 ml-0.5">(返¥{{ formatMoney(getCashback(veh)) }})</span>
                    </span>
                  </template>
                  <!-- 无返现时：直接醒目展示总保费 -->
                  <template v-else>
                    <span class="font-bold text-sm text-slate-900 font-mono">
                      ¥{{ formatMoney(getTotalPremium(veh)) }}
                    </span>
                  </template>
                </div>
                <span v-else class="text-slate-400">-</span>
              </template>
              <template v-else-if="getVehicleRecords(veh).length > 0">
                <span class="text-rose-500 text-[11px] font-normal">已脱保</span>
              </template>
              <template v-else>
                <span class="text-slate-400">-</span>
              </template>
            </td>

            <!-- 商业险到期日 -->
            <td class="py-3 px-4 whitespace-nowrap font-mono text-slate-600">
              <span v-if="getActivePolicy(veh)">{{ getActivePolicy(veh).endDate }}</span>
              <span v-else-if="getLatestPolicy(veh)?.endDate" class="text-rose-500 font-medium">已于 {{ getLatestPolicy(veh).endDate }} 到期</span>
              <span v-else>-</span>
            </td>

            <!-- 保险状态：精致徽标、圆点指示灯、防折行 -->
            <td class="py-3 px-4 whitespace-nowrap">
              <div
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border shadow-2xs"
                :class="getInsuranceStatusInfo(veh).badgeClass"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="getInsuranceStatusInfo(veh).dotClass"></span>
                <span>{{ getInsuranceStatusInfo(veh).label }}</span>
                <span
                  v-if="getInsuranceStatusInfo(veh).subText"
                  class="text-[11px] opacity-80 font-mono tracking-tight"
                >
                  ({{ getInsuranceStatusInfo(veh).subText }})
                </span>
              </div>
            </td>

            <!-- 固定尾部列：操作列（两行紧凑布局、跟随整行hover底色） -->
            <td class="sticky right-0 z-10 bg-white group-hover:bg-slate-50/90 transition-colors py-2.5 px-4 text-right whitespace-nowrap shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80">
              <div class="inline-flex flex-col items-end justify-center gap-1.5">
                <!-- 第一行：核心保单业务操作 -->
                <div class="flex items-center gap-2">
                  <button
                    v-if="getVehicleRecords(veh).length > 0"
                    @click="$emit('renew', veh)"
                    class="text-sky-600 hover:text-sky-800 font-semibold inline-flex items-center gap-1 cursor-pointer transition text-xs"
                    title="录入新一期续保单"
                  >
                    <i class="fa-solid fa-arrows-rotate text-[10px]"></i>
                    <span>续保</span>
                  </button>
                  <button
                    v-else
                    @click="$emit('add-policy', veh.id)"
                    class="text-sky-600 hover:text-sky-800 font-semibold inline-flex items-center gap-1 cursor-pointer transition text-xs"
                    title="录入首期车险保单"
                  >
                    <i class="fa-solid fa-plus text-[10px]"></i>
                    <span>录保单</span>
                  </button>
                  <span class="text-slate-200 text-xs">|</span>
                  <button
                    type="button"
                    @click="$emit('open-history', veh)"
                    class="text-slate-600 hover:text-slate-900 font-medium cursor-pointer transition text-xs"
                    title="打开历年车险投保档案与凭证弹窗"
                  >
                    历年({{ getVehicleRecords(veh).length }})
                  </button>
                </div>
                <!-- 第二行：车辆基础信息与管理操作 -->
                <div class="flex items-center gap-2 text-[11px]">
                  <button
                    @click="$emit('edit-vehicle', veh)"
                    class="text-slate-400 hover:text-slate-700 cursor-pointer transition"
                    title="修改车辆与所有人档案"
                  >
                    编辑车辆
                  </button>
                  <span class="text-slate-200">|</span>
                  <button
                    @click="$emit('delete-vehicle', veh.id)"
                    class="text-rose-400 hover:text-rose-600 cursor-pointer transition"
                    title="删除该车辆档案"
                  >
                    删除
                  </button>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { formatMoney, getTodayStr } from '../../utils/helpers.js';
import { extractVehicleInsuranceRecords } from '../../utils/payment-schedule.js';
import { getAttachmentUrl } from '../../api/index.js';

defineProps({
  filteredVehicles: { type: Array, default: () => [] }
});

defineEmits([
  'view-company',
  'renew',
  'add-policy',
  'open-history',
  'edit-vehicle',
  'delete-vehicle'
]);

function getVehicleRecords(veh) {
  return extractVehicleInsuranceRecords(veh);
}

function getLatestPolicy(veh) {
  const records = getVehicleRecords(veh);
  return records.length > 0 ? records[0] : null;
}

function getActivePolicy(veh) {
  const records = getVehicleRecords(veh);
  if (records.length === 0) return null;
  const today = getTodayStr();

  const unexpired = records.filter(r => {
    if (r.endDate) return r.endDate >= today;
    return Number(r.year) >= new Date().getFullYear();
  });

  if (unexpired.length === 0) return null;
  const running = unexpired.find(r => r.startDate && r.startDate <= today && r.endDate >= today);
  return running || unexpired[0];
}

function getDaysUntilExpire(veh) {
  const active = getActivePolicy(veh);
  const target = active || getLatestPolicy(veh);
  if (!target || !target.endDate) return null;
  const today = new Date(getTodayStr());
  const endDate = new Date(target.endDate);
  const diffTime = endDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function getTotalPremium(veh) {
  const p = getActivePolicy(veh);
  if (!p) return null;
  if (p.totalPremium !== null && p.totalPremium !== undefined && p.totalPremium !== '' && !isNaN(Number(p.totalPremium))) {
    return Number(p.totalPremium);
  }
  const c = Number(p.commercialPremium) || 0;
  const comp = Number(p.compulsoryPremium) || 0;
  const t = Number(p.tax) || 0;
  const acc = Number(p.accidentPremium) || 0;
  const total = c + comp + t + acc;
  return total > 0 ? total : null;
}

function getCashback(veh) {
  const p = getActivePolicy(veh);
  if (!p || !p.cashback) return 0;
  const cb = Number(p.cashback);
  return isNaN(cb) ? 0 : cb;
}

function getInsuranceStatusInfo(veh) {
  const days = getDaysUntilExpire(veh);
  if (days === null) {
    return {
      label: '待录保单',
      subText: '',
      dotClass: 'bg-slate-400',
      badgeClass: 'bg-slate-50 text-slate-600 border-slate-200/80',
    };
  }
  if (days < 0) {
    return {
      label: '已脱保',
      subText: `脱保${Math.abs(days)}天`,
      dotClass: 'bg-rose-500',
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200/80',
    };
  }
  if (days === 0) {
    return {
      label: '今日到期',
      subText: '请续保',
      dotClass: 'bg-amber-500 animate-pulse',
      badgeClass: 'bg-amber-50 text-amber-800 border-amber-200/80',
    };
  }
  if (days <= 30) {
    return {
      label: '即将到期',
      subText: `剩${days}天`,
      dotClass: 'bg-amber-500 animate-pulse',
      badgeClass: 'bg-amber-50 text-amber-800 border-amber-200/80',
    };
  }
  return {
    label: '在保中',
    subText: `剩${days}天`,
    dotClass: 'bg-emerald-500',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
  };
}
</script>
