<template>
  <div class="space-y-6">
    <!-- 顶部到期高急预警横幅 (若有车辆30天内需续保或已脱保) -->
    <div
      v-if="expiringSoonCount > 0"
      class="p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/80 shadow-sm flex flex-wrap items-center justify-between gap-3"
    >
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-lg shadow-md shadow-amber-200 animate-bounce">
          <i class="fa-solid fa-car-burst"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h4 class="text-sm font-bold text-amber-950">
              您有 {{ expiringSoonCount }} 辆车的车险即将到期或已脱保，请注意续保比价！
            </h4>
            <span class="text-xs bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded-full font-semibold">续保提醒</span>
          </div>
          <p class="text-xs text-amber-700 mt-0.5">
            车辆脱保将失去事故赔偿保障且无法合法上路，通常提前 30 天可联系各大保险公司锁定续保返点与保费折扣。
          </p>
        </div>
      </div>
      <button
        @click="$emit('filter-expiring')"
        class="px-4 py-2 bg-amber-600 hover:bg-amber-700 active:bg-amber-800 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center space-x-1.5 cursor-pointer"
      >
        <span>查看待续保车辆</span>
        <i class="fa-solid fa-arrow-right text-[10px]"></i>
      </button>
    </div>

    <!-- 统计指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden">
        <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">爱车总数</div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-2xl font-bold text-slate-900">{{ vehicleTotalCount }}</span>
          <span class="text-xs text-slate-400">辆家庭资产</span>
        </div>
        <div class="mt-3 flex items-center text-xs text-slate-500">
          <i class="fa-solid fa-car-rear mr-1 text-sky-500"></i>
          <span>{{ vehiclesWithInsuranceCount }} 辆在保 · {{ vehiclesWithoutInsuranceCount }} 辆待录保单</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-sky-50 text-6xl pointer-events-none">
          <i class="fa-solid fa-car-side"></i>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden">
        <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">年度车险总支出</div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-2xl font-bold text-slate-900">¥{{ formatMoney(totalVehiclePremium) }}</span>
          <span class="text-xs text-slate-400">/ 最新年度</span>
        </div>
        <div class="mt-3 flex items-center text-xs text-emerald-600">
          <i class="fa-solid fa-receipt mr-1"></i>
          <span>按每车当前最新一期保单汇总统揽</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-emerald-50 text-6xl pointer-events-none">
          <i class="fa-solid fa-coins"></i>
        </div>
      </div>

      <div
        @click="$emit('filter-expiring')"
        class="bg-white p-5 rounded-2xl border transition cursor-pointer relative overflow-hidden group hover:shadow-md"
        :class="expiringSoonCount > 0 ? 'border-amber-300 bg-amber-50/20 hover:border-amber-400' : 'border-slate-200/80'"
      >
        <div class="text-xs font-semibold uppercase tracking-wider flex items-center justify-between" :class="expiringSoonCount > 0 ? 'text-amber-700' : 'text-slate-500'">
          <span>30天内到期 / 脱保</span>
          <span v-if="expiringSoonCount > 0" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
        </div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-2xl font-extrabold" :class="expiringSoonCount > 0 ? 'text-amber-600' : 'text-slate-700'">{{ expiringSoonCount }}</span>
          <span class="text-xs text-slate-400">辆需续保</span>
        </div>
        <div class="mt-3 flex items-center text-xs text-sky-600 font-medium">
          <span>点击快速筛选查看 &gt;</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-amber-50 text-6xl pointer-events-none">
          <i class="fa-solid fa-bell"></i>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden">
        <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">年检提醒</div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-2xl font-bold text-slate-900">{{ inspectionSoonCount }}</span>
          <span class="text-xs text-slate-400">辆近期需年检</span>
        </div>
        <div class="mt-3 flex items-center text-xs text-slate-500">
          <i class="fa-solid fa-calendar-check mr-1 text-sky-500"></i>
          <span>按初登与年检日期推算周期</span>
        </div>
        <div class="absolute right-3 -bottom-2 text-indigo-50 text-6xl pointer-events-none">
          <i class="fa-solid fa-wrench"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../../utils/helpers.js';

defineProps({
  vehicleTotalCount: { type: Number, default: 0 },
  vehiclesWithInsuranceCount: { type: Number, default: 0 },
  vehiclesWithoutInsuranceCount: { type: Number, default: 0 },
  totalVehiclePremium: { type: Number, default: 0 },
  expiringSoonCount: { type: Number, default: 0 },
  inspectionSoonCount: { type: Number, default: 0 }
});

defineEmits(['filter-expiring']);
</script>
