<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 top-0 left-0 right-0 bottom-0 z-50 !m-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 text-center space-y-4 animate-in fade-in zoom-in duration-200">
        <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center text-xl shadow-sm">
          <i class="fa-solid fa-circle-check"></i>
        </div>
        <div>
          <h4 class="text-base font-bold text-slate-900">车辆档案添加成功！</h4>
          <p class="text-xs text-slate-500 mt-1">
            已成功登记车牌【<span class="font-mono font-bold text-slate-800">{{ vehicle?.plateNo }}</span>】。是否立即为此车录入第一期车险保单？
          </p>
        </div>
        <div class="flex items-center space-x-2 pt-2">
          <button
            type="button"
            @click="$emit('cancel')"
            class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-semibold transition cursor-pointer"
          >
            稍后录入
          </button>
          <button
            type="button"
            @click="$emit('proceed')"
            class="flex-1 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            立即录入保单
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  vehicle: { type: Object, default: null }
});

defineEmits(['cancel', 'proceed']);
</script>
