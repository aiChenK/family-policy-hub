<template>
  <div class="bg-slate-50 p-5 rounded-2xl border border-sky-100 shadow-inner space-y-4 animate-fadeIn">
    <div class="flex justify-between items-center pb-3 border-b border-slate-200">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-sky-600"></span>
        <h4 class="text-sm font-bold text-slate-900">
          {{ isNew ? '录入新成员档案' : `编辑成员资料：${form.name}` }}
        </h4>
      </div>
      <button @click="$emit('cancel')" class="text-xs text-slate-400 hover:text-slate-600 cursor-pointer">
        取消编辑
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
      <!-- 姓名 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">姓名 / 称谓 *</label>
        <input
          v-model.trim="form.name"
          placeholder="如：陈凯、小宝"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>

      <!-- 与户主关系 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">与户主关系 *</label>
        <select
          v-model="form.relation"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <option value="本人">本人 (户主)</option>
          <option value="配偶">配偶 (妻子/丈夫)</option>
          <option value="儿子">儿子</option>
          <option value="女儿">女儿</option>
          <option value="父亲">父亲</option>
          <option value="母亲">母亲</option>
          <option value="公公">公公</option>
          <option value="婆婆">婆婆</option>
          <option value="岳父">岳父</option>
          <option value="岳母">岳母</option>
          <option value="其他长辈">其他长辈</option>
          <option value="其他">其他</option>
        </select>
      </div>

      <!-- 性别 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">生理性别</label>
        <div class="flex space-x-2 mt-0.5">
          <button
            type="button"
            @click="form.gender = '男'"
            :class="form.gender === '男' ? 'bg-sky-600 text-white font-bold border-sky-600' : 'bg-white text-slate-600 border-slate-200'"
            class="flex-1 py-2 rounded-xl border text-xs flex items-center justify-center space-x-1 transition cursor-pointer"
          >
            <i class="fa-solid fa-mars"></i>
            <span>男</span>
          </button>
          <button
            type="button"
            @click="form.gender = '女'"
            :class="form.gender === '女' ? 'bg-rose-500 text-white font-bold border-rose-500' : 'bg-white text-slate-600 border-slate-200'"
            class="flex-1 py-2 rounded-xl border text-xs flex items-center justify-center space-x-1 transition cursor-pointer"
          >
            <i class="fa-solid fa-venus"></i>
            <span>女</span>
          </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
      <!-- 出生日期 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">出生日期</label>
        <input
          type="date"
          v-model="form.birthDate"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <p class="text-[10px] text-slate-400 mt-1" v-if="form.birthDate">
          当前年龄约：{{ calculateAge(form.birthDate) }} 岁
        </p>
      </div>

      <!-- 联系电话 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">联系电话</label>
        <input
          v-model.trim="form.phone"
          placeholder="如：13800000000"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>

      <!-- 社保状态 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">基本医保/社保状态</label>
        <select
          v-model="form.hasSocialSecurity"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <option :value="true">已参保 (城镇职工/居民/新农合)</option>
          <option :value="false">无社保 / 待参保</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
      <div>
        <label class="block text-slate-700 font-semibold mb-1">社保参保地 / 医保归属地</label>
        <input
          v-model.trim="form.socialSecurityCity"
          placeholder="如：浙江杭州、绍兴柯桥"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
      <div>
        <label class="block text-slate-700 font-semibold mb-1">健康提醒与就医备忘</label>
        <input
          v-model.trim="form.remark"
          placeholder="如：青霉素过敏、医保卡留存处、定期复查提醒..."
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
    </div>

    <!-- 保存表单操作 -->
    <div class="flex justify-end space-x-2 pt-2 border-t border-slate-200">
      <button
        type="button"
        @click="$emit('cancel')"
        class="px-4 py-2 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 rounded-xl text-xs font-medium transition cursor-pointer"
      >
        取消
      </button>
      <button
        type="button"
        @click="$emit('save')"
        class="px-5 py-2 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
      >
        {{ isNew ? '确认添加成员' : '保存修改' }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  isNew: { type: Boolean, default: false }
});

defineEmits(['save', 'cancel']);

function calculateAge(birthDateStr) {
  if (!birthDateStr) return '';
  const birth = new Date(birthDateStr);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) {
    age--;
  }
  return age >= 0 ? age : 0;
}
</script>
