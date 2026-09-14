<template>
  <!-- 4. 单号与电子保单凭证卡片 -->
  <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 space-y-3.5">
    <div class="flex items-center justify-between">
      <span class="font-bold text-slate-800 flex items-center space-x-1.5 text-xs">
        <i class="fa-solid fa-paperclip text-sky-600"></i>
        <span>4. 保单号与电子保单凭据附件</span>
      </span>
      <label class="cursor-pointer inline-flex items-center space-x-1 px-3 py-1.5 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded-xl text-xs font-semibold border border-sky-200 transition shadow-2xs">
        <i class="fa-solid" :class="uploading ? 'fa-spinner fa-spin' : 'fa-arrow-up-from-bracket'"></i>
        <span>{{ uploading ? '上传中...' : '上传保单凭证' }}</span>
        <input type="file" accept=".pdf,image/*" class="hidden" @change="handleFileUpload" :disabled="uploading" />
      </label>
    </div>

    <!-- 3 项保单号 (商业险单号、交强险单号、驾乘险单号) -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
      <div>
        <label class="block text-slate-500 text-[10px] mb-1">商业险保单号</label>
        <input
          v-model="form.commercialPolicyNo"
          placeholder="商业单号(选填)"
          class="w-full bg-white border border-slate-200 rounded-xl p-2 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
      <div>
        <label class="block text-slate-500 text-[10px] mb-1">交强险保单号</label>
        <input
          v-model="form.compulsoryPolicyNo"
          placeholder="交强单号(选填)"
          class="w-full bg-white border border-slate-200 rounded-xl p-2 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
      <div>
        <label class="block text-slate-500 text-[10px] mb-1">驾乘险保单号</label>
        <input
          v-model="form.accidentPolicyNo"
          placeholder="驾乘单号(选填)"
          class="w-full bg-white border border-slate-200 rounded-xl p-2 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
    </div>

    <!-- 附件列表展示 -->
    <div v-if="form.attachments && form.attachments.length > 0" class="space-y-1.5 pt-1">
      <div
        v-for="(att, aIdx) in form.attachments"
        :key="aIdx"
        class="flex items-center justify-between p-2.5 bg-white rounded-xl border border-slate-200 text-xs shadow-2xs group hover:border-slate-300 transition"
      >
        <!-- 处于重命名编辑状态 -->
        <div v-if="editingAttIndex === aIdx" class="flex items-center space-x-1.5 flex-1 mr-2">
          <i class="fa-regular text-base shrink-0" :class="att.name?.endsWith('.pdf') ? 'fa-file-pdf text-rose-500' : 'fa-file-image text-sky-500'"></i>
          <input
            v-model="editingAttName"
            ref="attNameInputRef"
            class="flex-1 bg-slate-50 border border-sky-400 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-sky-400"
            @keydown.enter.prevent="saveAttName(att)"
            @keydown.esc.prevent="cancelEditAttName"
            placeholder="请输入附件显示名称"
          />
          <button
            type="button"
            @click="saveAttName(att)"
            class="px-2 py-1 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg text-[11px] font-bold transition shrink-0 shadow-xs"
            title="确认修改"
          >
            <i class="fa-solid fa-check"></i>
          </button>
          <button
            type="button"
            @click="cancelEditAttName"
            class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-[11px] font-medium transition shrink-0"
            title="取消"
          >
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <!-- 正常展示状态 -->
        <div v-else class="flex items-center space-x-2 truncate flex-1 mr-2">
          <i class="fa-regular text-base shrink-0" :class="att.name?.endsWith('.pdf') ? 'fa-file-pdf text-rose-500' : 'fa-file-image text-sky-500'"></i>
          <span
            class="truncate font-medium text-slate-800 hover:text-sky-600 cursor-pointer transition"
            :title="`${att.name} (点击修改名称)`"
            @click="startEditAttName(aIdx, att.name)"
          >
            {{ att.name }}
          </span>
          <!-- 附件类型轻量标签推测 -->
          <span v-if="att.name?.includes('驾乘')" class="px-1.5 py-0.2 rounded text-[10px] bg-purple-100 text-purple-700 font-semibold shrink-0">驾乘险</span>
          <span v-else-if="att.name?.includes('交强')" class="px-1.5 py-0.2 rounded text-[10px] bg-emerald-100 text-emerald-700 font-semibold shrink-0">交强险</span>
          <span v-else-if="att.name?.includes('商业')" class="px-1.5 py-0.2 rounded text-[10px] bg-sky-100 text-sky-700 font-semibold shrink-0">商业险</span>
        </div>

        <div class="flex items-center space-x-1.5 ml-2 shrink-0" v-if="editingAttIndex !== aIdx">
          <button
            type="button"
            @click="startEditAttName(aIdx, att.name)"
            class="text-slate-400 hover:text-sky-600 p-1 rounded-lg hover:bg-sky-50 transition text-[11px]"
            title="修改显示名称"
          >
            <i class="fa-regular fa-pen-to-square"></i>
          </button>
          <a :href="getAttachmentUrl(att.url)" target="_blank" class="text-sky-600 hover:text-sky-800 px-2 py-1 bg-slate-50 rounded-lg border border-slate-200 text-[11px] font-medium transition">
            <i class="fa-regular fa-eye mr-1"></i>预览
          </a>
          <button type="button" @click="removeAttachment(aIdx)" class="text-rose-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 transition" title="删除此附件">
            <i class="fa-regular fa-trash-can"></i>
          </button>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-2.5 bg-white rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
      暂无本期保单附件，可点击右上角上传 PDF / 图片保单或发票凭据
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { AppApi, getAttachmentUrl } from '../../api/index.js';

const props = defineProps({
  form: { type: Object, required: true },
  selectedVehicle: { type: Object, default: null }
});

const uploading = ref(false);
const editingAttIndex = ref(-1);
const editingAttName = ref('');
const attNameInputRef = ref(null);

async function handleFileUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > 30 * 1024 * 1024) {
    alert('附件大小不能超过 30MB');
    return;
  }
  uploading.value = true;
  try {
    let yearFolder = '';
    if (props.form.startDate) {
      const match = String(props.form.startDate).match(/\d{4}/);
      if (match) yearFolder = match[0];
    }
    if (!yearFolder && props.form.year) {
      yearFolder = String(props.form.year).trim();
    }
    const plateFolder = (props.selectedVehicle?.plateNo || '').trim() || 'vehicles';
    const subfolder = `${plateFolder}/${yearFolder}`;

    const att = await AppApi.uploadAttachment('vehicle', file, subfolder);
    if (!props.form.attachments) {
      props.form.attachments = [];
    }
    props.form.attachments.push(att);
  } catch (err) {
    console.error('[Upload Vehicle Policy File]', err);
    alert('上传保单凭证失败，请重试');
  } finally {
    uploading.value = false;
    event.target.value = '';
  }
}

async function removeAttachment(index) {
  if (!props.form.attachments) return;
  const att = props.form.attachments[index];
  if (att && att.storedName) {
    try {
      await AppApi.deleteAttachment('vehicle', att.storedName);
    } catch (_) {}
  }
  props.form.attachments.splice(index, 1);
  if (editingAttIndex.value === index) {
    cancelEditAttName();
  }
}

function startEditAttName(index, currentName) {
  editingAttIndex.value = index;
  editingAttName.value = currentName || '';
  nextTick(() => {
    if (attNameInputRef.value) {
      const el = Array.isArray(attNameInputRef.value) ? attNameInputRef.value[0] : attNameInputRef.value;
      el?.focus();
      el?.select();
    }
  });
}

function saveAttName(att) {
  if (editingAttIndex.value === -1 || !att) return;
  let trimmed = (editingAttName.value || '').trim();
  if (trimmed) {
    const originalExt = att.name && att.name.includes('.') ? att.name.slice(att.name.lastIndexOf('.')) : '';
    if (originalExt && !trimmed.includes('.')) {
      trimmed += originalExt;
    }
    att.name = trimmed;
  }
  cancelEditAttName();
}

function cancelEditAttName() {
  editingAttIndex.value = -1;
  editingAttName.value = '';
}

defineExpose({
  cancelEditAttName
});
</script>
