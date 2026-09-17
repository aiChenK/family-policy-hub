<template>
  <div>
    <!-- 1. 扣费异常警示横幅 (仅当存在用户手动标记扣费异常/未缴时展示，最高优先级) -->
    <div
      v-if="unpaidCount > 0"
      class="p-3.5 sm:p-4 rounded-2xl bg-gradient-to-r from-rose-50 to-amber-50 border border-rose-200/80 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
    >
      <div class="flex items-start sm:items-center space-x-3 min-w-0">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-rose-500 text-white flex items-center justify-center text-base sm:text-lg shadow-md shadow-rose-200 animate-pulse shrink-0 mt-0.5 sm:mt-0">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div class="min-w-0">
          <div class="flex items-center space-x-2 flex-wrap gap-y-1">
            <h4 class="text-xs sm:text-sm font-bold text-rose-950">
              注意：发现 {{ unpaidCount }} 笔保单保费扣款异常 / 待跟进
            </h4>
            <span class="text-[10px] sm:text-xs bg-rose-200/80 text-rose-900 px-2 py-0.5 rounded-full font-semibold">扣费异常</span>
          </div>
          <p class="text-xs text-rose-700 mt-1 leading-relaxed">
            涉及金额总计：<strong class="text-rose-900 font-extrabold text-sm">¥{{ formatMoney(unpaidAmount) }}</strong>，请核实扣款卡余额或保单扣费状态，避免断缴脱保。
          </p>
        </div>
      </div>
      <button
        @click="$emit('navigate-to-payments', 'unpaid')"
        class="w-full sm:w-auto px-4 py-2.5 sm:py-2 bg-rose-600 hover:bg-rose-700 active:bg-rose-800 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center justify-center space-x-1.5 cursor-pointer shrink-0"
      >
        <span>前往查看异常保费</span>
        <i class="fa-solid fa-arrow-right text-[10px]"></i>
      </button>
    </div>

    <!-- 2. 爱车车险临期/脱保警示横幅 (30天内到期或已脱保时高急提示) -->
    <div
      v-else-if="vehiclesExpiringCount > 0"
      class="p-3.5 sm:p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/80 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
    >
      <div class="flex items-start sm:items-center space-x-3 min-w-0">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-base sm:text-lg shadow-md shadow-amber-200 animate-bounce shrink-0 mt-0.5 sm:mt-0">
          <i class="fa-solid fa-car-burst"></i>
        </div>
        <div class="min-w-0">
          <div class="flex items-center space-x-2 flex-wrap gap-y-1">
            <h4 class="text-xs sm:text-sm font-bold text-amber-950">
              车险到期提醒：发现 {{ vehiclesExpiringCount }} 辆爱车车险即将到期或已脱保，请注意续保！
            </h4>
            <span class="text-[10px] sm:text-xs bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded-full font-semibold">续保预警</span>
          </div>
          <p class="text-xs text-amber-700 mt-1 leading-relaxed">
            机动车辆脱保将失去事故理赔保障且无法合法上路，通常提前 30 天可联系保险公司锁定续保优惠与商业返现。
          </p>
        </div>
      </div>
      <button
        @click="$emit('navigate-to-vehicles', 'expiring')"
        class="w-full sm:w-auto px-4 py-2.5 sm:py-2 bg-amber-600 hover:bg-amber-700 active:bg-amber-800 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center justify-center space-x-1.5 cursor-pointer shrink-0"
      >
        <span>前往爱车专区查看</span>
        <i class="fa-solid fa-arrow-right text-[10px]"></i>
      </button>
    </div>

    <!-- 3. 近期自动代扣提醒横幅 (未来30天内有保费即将代扣时温馨提示) -->
    <div
      v-else-if="nearDueCount > 0"
      class="p-3.5 sm:p-4 rounded-2xl bg-gradient-to-r from-sky-50 to-indigo-50 border border-sky-200/80 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
    >
      <div class="flex items-start sm:items-center space-x-3 min-w-0">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-sky-500 text-white flex items-center justify-center text-base sm:text-lg shadow-md shadow-sky-200 shrink-0 mt-0.5 sm:mt-0">
          <i class="fa-solid fa-credit-card"></i>
        </div>
        <div class="min-w-0">
          <div class="flex items-center space-x-2 flex-wrap gap-y-1">
            <h4 class="text-xs sm:text-sm font-bold text-sky-950">
              近期扣缴提醒：未来 30 天内有 {{ nearDueCount }} 笔保单将自动代扣
            </h4>
            <span class="text-[10px] sm:text-xs bg-sky-200/70 text-sky-800 px-2 py-0.5 rounded-full font-semibold">银行自动扣缴</span>
          </div>
          <p class="text-xs text-sky-700 mt-1 leading-relaxed">
            预计代扣金额总计：<strong class="text-sky-950 font-extrabold text-sm font-mono">¥{{ formatMoney(nearDueAmount) }}</strong>，到达扣款日后系统将自动流转为已缴，请确保代扣银行卡余额充足。
          </p>
        </div>
      </div>
      <button
        @click="$emit('navigate-to-calendar')"
        class="w-full sm:w-auto px-4 py-2.5 sm:py-2 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center justify-center space-x-1.5 cursor-pointer shrink-0"
      >
        <span>查看扣费日历</span>
        <i class="fa-solid fa-calendar-days text-[10px]"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../../utils/helpers.js';

defineProps({
  unpaidCount: { type: Number, default: 0 },
  unpaidAmount: { type: Number, default: 0 },
  vehiclesExpiringCount: { type: Number, default: 0 },
  nearDueCount: { type: Number, default: 0 },
  nearDueAmount: { type: Number, default: 0 }
});

defineEmits(['navigate-to-payments', 'navigate-to-vehicles', 'navigate-to-calendar']);
</script>
