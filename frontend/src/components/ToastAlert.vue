<template>
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="transform -translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="toast.show"
      :class="toast.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'"
      class="mb-6 p-4 rounded-xl border flex items-center justify-between shadow-sm"
    >
      <div class="flex items-center space-x-3">
        <i
          :class="toast.type === 'success' ? 'fa-circle-check text-emerald-500' : 'fa-circle-exclamation text-rose-500'"
          class="fa-solid text-lg"
        ></i>
        <span class="text-sm font-medium">{{ toast.message }}</span>
      </div>
      <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-sm">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  toast: {
    type: Object,
    required: true
  }
});

defineEmits(['close']);
</script>
