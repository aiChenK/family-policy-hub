<template>
  <div class="bg-slate-50 p-5 rounded-2xl border border-indigo-100 shadow-inner space-y-4 animate-fadeIn">
    <div class="flex justify-between items-center pb-3 border-b border-slate-200">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
        <h4 class="text-sm font-bold text-slate-900">
          {{ isNew ? '登记新关联企业' : `编辑企业资质：${form.name}` }}
        </h4>
      </div>
      <button @click="$emit('cancel')" class="text-xs text-slate-400 hover:text-slate-600 cursor-pointer">
        取消编辑
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
      <!-- 公司全称 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">公司全称 (车辆公户所有人) *</label>
        <input
          v-model.trim="form.name"
          placeholder="如：杭州极速科技有限公司"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- 统一社会信用代码 -->
      <div>
        <label class="block text-slate-700 font-semibold mb-1">统一社会信用代码 / 税号 *</label>
        <input
          v-model.trim="form.taxNo"
          placeholder="18位统一代码，如：91330108MA28XXXXXX"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono uppercase tracking-wider text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>

    <!-- 开票对公银行与账号 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
      <div>
        <label class="block text-slate-700 font-semibold mb-1">开户银行全称</label>
        <input
          v-model.trim="form.bankName"
          placeholder="如：招商银行杭州分行营业部"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-slate-700 font-semibold mb-1">对公银行账号 (出险理赔接收账户)</label>
        <input
          v-model.trim="form.bankAccount"
          placeholder="如：571900000000000"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>

    <!-- 注册地址电话与联系人 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
      <div class="sm:col-span-2">
        <label class="block text-slate-700 font-semibold mb-1">注册地址与电话 (开票信息)</label>
        <input
          v-model.trim="form.addressPhone"
          placeholder="如：杭州市滨江区科技大道1号 0571-88888888"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-slate-700 font-semibold mb-1">常用联系人 / 财务</label>
        <input
          v-model.trim="form.contactPerson"
          placeholder="如：陈凯 (13800000000)"
          class="w-full bg-white border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>

    <!-- 营业执照扫描件上传 -->
    <div class="space-y-2 pt-2 border-t border-slate-200 text-xs">
      <div class="flex items-center justify-between">
        <div>
          <span class="font-bold text-slate-700 flex items-center space-x-1.5">
            <i class="fa-solid fa-file-contract text-indigo-600"></i>
            <span>营业执照正本/副本照片与扫描件</span>
          </span>
          <p class="text-[10px] text-slate-400 mt-0.5">上传清晰扫描件或照片，办理车险续保与理赔时随时一键调取发给保险专员</p>
        </div>
        <label class="cursor-pointer inline-flex items-center space-x-1 px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-xl text-xs font-semibold border border-indigo-200 transition">
          <i class="fa-solid" :class="uploading ? 'fa-spinner fa-spin' : 'fa-arrow-up-from-bracket'"></i>
          <span>{{ uploading ? '上传中...' : '上传执照照片/PDF' }}</span>
          <input type="file" accept=".pdf,image/*" class="hidden" @change="handleFileUpload" :disabled="uploading" />
        </label>
      </div>

      <p v-if="uploadError" class="text-rose-600 text-xs">{{ uploadError }}</p>

      <div v-if="form.attachments && form.attachments.length > 0" class="space-y-1.5">
        <div
          v-for="(att, idx) in form.attachments"
          :key="att.id || idx"
          class="flex items-center justify-between p-2.5 bg-white rounded-xl border border-slate-200 text-xs hover:border-slate-300 transition"
        >
          <!-- 重命名编辑模式 -->
          <div v-if="editingAttIndex === idx" class="flex items-center space-x-1.5 flex-1 mr-2">
            <i class="fa-regular fa-file-pdf text-rose-500 text-base shrink-0" v-if="att.name && att.name.endsWith('.pdf')"></i>
            <i class="fa-regular fa-file-image text-indigo-500 text-base shrink-0" v-else></i>
            <input
              v-model="editingAttName"
              ref="attNameInputRef"
              class="flex-1 bg-slate-50 border border-indigo-400 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-indigo-400"
              @keydown.enter.prevent="saveAttName(att)"
              @keydown.esc.prevent="cancelEditAttName"
              placeholder="请输入执照证件显示名称"
            />
            <button
              type="button"
              @click="saveAttName(att)"
              class="px-2 py-1 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg text-[11px] font-bold transition shrink-0 shadow-xs cursor-pointer"
              title="确认修改"
            >
              <i class="fa-solid fa-check"></i>
            </button>
            <button
              type="button"
              @click="cancelEditAttName"
              class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-[11px] font-medium transition shrink-0 cursor-pointer"
              title="取消"
            >
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- 正常展示模式 -->
          <div v-else class="flex items-center space-x-2 truncate flex-1 mr-2">
            <i class="fa-regular fa-file-pdf text-rose-500 text-base shrink-0" v-if="att.name && att.name.endsWith('.pdf')"></i>
            <i class="fa-regular fa-file-image text-indigo-500 text-base shrink-0" v-else></i>
            <div class="truncate">
              <div
                class="font-medium text-slate-800 truncate hover:text-indigo-600 cursor-pointer transition"
                :title="`${att.name} (点击修改名称)`"
                @click="startEditAttName(idx, att.name)"
              >
                {{ att.name }}
              </div>
              <div class="text-[10px] text-slate-400">{{ formatSize(att.size) }} · {{ att.uploadedAt || '已保存' }}</div>
            </div>
          </div>

          <div class="flex items-center space-x-1.5 shrink-0 ml-2" v-if="editingAttIndex !== idx">
            <button
              type="button"
              @click="startEditAttName(idx, att.name)"
              class="text-slate-400 hover:text-indigo-600 p-1 rounded-lg hover:bg-indigo-50 transition text-[11px] cursor-pointer"
              title="修改显示名称"
            >
              <i class="fa-regular fa-pen-to-square"></i>
            </button>
            <a :href="getAttachmentUrl(att.url)" target="_blank" class="text-indigo-600 hover:text-indigo-800 px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 rounded-lg text-[11px] font-medium transition cursor-pointer">
              <i class="fa-regular fa-eye mr-1"></i>预览
            </a>
            <button type="button" @click="removeAttachment(idx)" class="text-rose-500 hover:text-rose-700 p-1 rounded-lg hover:bg-rose-50 transition cursor-pointer" title="删除附件">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-3 bg-white rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
        暂未上传营业执照，可点击右上角按钮上传
      </div>
    </div>

    <!-- 备注说明 -->
    <div>
      <label class="block text-slate-700 font-semibold mb-1">备忘与补充说明</label>
      <input
        v-model.trim="form.remark"
        placeholder="如：公司名下挂靠一辆公户车，每年6月办理车险续保"
        class="w-full bg-white border border-slate-200 rounded-xl p-2 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
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
        class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white rounded-xl text-xs font-semibold shadow-sm transition cursor-pointer"
      >
        {{ isNew ? '确认登记企业' : '保存修改' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { AppApi, getAttachmentUrl } from '../../api/index.js';

const props = defineProps({
  form: { type: Object, required: true },
  isNew: { type: Boolean, default: false }
});

defineEmits(['save', 'cancel']);

const uploading = ref(false);
const uploadError = ref('');
const editingAttIndex = ref(-1);
const editingAttName = ref('');
const attNameInputRef = ref(null);

function formatSize(bytes) {
  if (!bytes) return '未知大小';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function handleFileUpload(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  if (file.size > 20 * 1024 * 1024) {
    uploadError.value = '文件体积超出限制 (最大 20MB)';
    return;
  }
  uploading.value = true;
  uploadError.value = '';

  try {
    const safeCompFolder = (props.form.name || '').trim() ? (props.form.name.trim() + '/licenses') : 'licenses';
    const att = await AppApi.uploadAttachment('company', file, safeCompFolder);
    if (!props.form.attachments) props.form.attachments = [];
    props.form.attachments.push(att);
  } catch (err) {
    console.error('[Upload Company File]', err);
    uploadError.value = '上传失败，请重试';
  } finally {
    uploading.value = false;
    e.target.value = '';
  }
}

async function removeAttachment(idx) {
  if (!props.form.attachments) return;
  const att = props.form.attachments[idx];
  if (att && att.storedName) {
    try {
      await AppApi.deleteAttachment('company', att.storedName);
    } catch (_) {}
  }
  props.form.attachments.splice(idx, 1);
  if (editingAttIndex.value === idx) cancelEditAttName();
}

function startEditAttName(idx, curName) {
  editingAttIndex.value = idx;
  editingAttName.value = curName || '';
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
    const ext = att.name && att.name.includes('.') ? att.name.slice(att.name.lastIndexOf('.')) : '';
    if (ext && !trimmed.includes('.')) trimmed += ext;
    att.name = trimmed;
  }
  cancelEditAttName();
}

function cancelEditAttName() {
  editingAttIndex.value = -1;
  editingAttName.value = '';
}
</script>
