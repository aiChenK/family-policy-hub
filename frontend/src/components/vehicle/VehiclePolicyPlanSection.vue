<template>
  <!-- 3. 保障方案卡片 (商业险保障、三者保额、车损、医保外、驾乘人员保障) -->
  <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 space-y-3.5">
    <div class="flex items-center justify-between">
      <span class="font-bold text-slate-800 flex items-center space-x-1.5 text-xs">
        <i class="fa-solid fa-shield-halved text-sky-600"></i>
        <span>3. 保障责任方案 (商业险与驾乘人员险)</span>
      </span>
      <span class="text-[10px] text-slate-400">按需选填保额与附加险</span>
    </div>

    <!-- 核心责任开关 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
      <label
        class="flex items-center justify-between p-2.5 rounded-xl border cursor-pointer select-none transition"
        :class="form.hasDamage ? 'bg-sky-50/80 border-sky-300 text-sky-900' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100/50'"
      >
        <div class="flex items-center space-x-2.5">
          <input type="checkbox" v-model="form.hasDamage" class="rounded text-sky-600 h-4 w-4" />
          <div>
            <div class="font-bold text-xs">机动车损失险 (车损险)</div>
            <div class="text-[10px] text-slate-400">保障碰撞/倾覆/火灾/暴雨涉水等车辆自身损失</div>
          </div>
        </div>
        <i class="fa-solid fa-car-burst text-sm" :class="form.hasDamage ? 'text-sky-600' : 'text-slate-300'"></i>
      </label>

      <label
        class="flex items-center justify-between p-2.5 rounded-xl border cursor-pointer select-none transition"
        :class="form.hasMedicalExcluded ? 'bg-indigo-50/80 border-indigo-300 text-indigo-900' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100/50'"
      >
        <div class="flex items-center space-x-2.5">
          <input type="checkbox" v-model="form.hasMedicalExcluded" class="rounded text-indigo-600 h-4 w-4" />
          <div>
            <div class="font-bold text-xs">医保外医疗费用责任险</div>
            <div class="text-[10px] text-slate-400">保障三者险或车上人员医保自费药与器械费用</div>
          </div>
        </div>
        <i class="fa-solid fa-kit-medical text-sm" :class="form.hasMedicalExcluded ? 'text-indigo-600' : 'text-slate-300'"></i>
      </label>
    </div>

    <!-- 三者险保额与驾乘险保额 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
      <!-- 第三者责任险保额 -->
      <div>
        <div class="flex justify-between items-center mb-1">
          <label class="text-slate-700 font-semibold text-[11px]">第三者责任险保额</label>
          <div class="flex gap-1">
            <button
              type="button"
              v-for="amt in ['200万', '300万', '500万']"
              :key="amt"
              @click="form.thirdPartyAmount = amt"
              class="px-1.5 py-0.2 rounded text-[10px] bg-slate-200/70 hover:bg-sky-100 hover:text-sky-800 text-slate-700 transition"
            >
              {{ amt }}
            </button>
          </div>
        </div>
        <input
          v-model="form.thirdPartyAmount"
          placeholder="如：300万 / 500万"
          class="w-full bg-white border border-slate-200 rounded-xl p-2 font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>

      <!-- 驾乘险 / 车上人员险保额 -->
      <div>
        <div class="flex justify-between items-center mb-1">
          <label class="text-slate-700 font-semibold text-[11px] flex items-center space-x-1">
            <i class="fa-solid fa-person-shelter text-purple-600"></i>
            <span>驾乘险 / 车上人员保额</span>
          </label>
          <div class="flex gap-1">
            <button
              type="button"
              v-for="damt in ['10万/座', '20万/座', '50万/座']"
              :key="damt"
              @click="form.driverAmount = damt"
              class="px-1.5 py-0.2 rounded text-[10px] bg-purple-100/80 hover:bg-purple-200 text-purple-800 transition"
            >
              {{ damt }}
            </button>
          </div>
        </div>
        <input
          v-model="form.driverAmount"
          placeholder="如：各10万/座、整车5座各50万、跟车不限人"
          class="w-full bg-white border border-slate-200 rounded-xl p-2 font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
    </div>

    <!-- 附加特约险 -->
    <div>
      <label class="block text-slate-700 font-semibold text-[11px] mb-1">附加特约与其它附加险 (选填)</label>
      <input
        v-model="form.extra"
        placeholder="如：划痕险2000元、无法找到第三方特约、道路救援3次"
        class="w-full bg-white border border-slate-200 rounded-xl p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: {
    type: Object,
    required: true
  }
});
</script>
