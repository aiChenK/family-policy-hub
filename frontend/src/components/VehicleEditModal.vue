<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 top-0 left-0 right-0 bottom-0 z-50 !m-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
    <div class="bg-white rounded-2xl sm:rounded-3xl max-w-xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[94vh] sm:max-h-[92vh] flex flex-col">
      <!-- 标题栏 -->
      <div class="p-4 sm:p-5 bg-gradient-to-r from-sky-50 to-indigo-50 border-b border-sky-100 flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-2 sm:space-x-2.5">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-sky-600 text-white flex items-center justify-center shadow-md shadow-sky-200 shrink-0">
            <i class="fa-solid fa-car"></i>
          </div>
          <div>
            <h3 class="text-sm sm:text-base font-bold text-slate-900">{{ isNew ? '添加爱车档案' : '编辑车辆基本信息' }}</h3>
            <p class="text-[11px] sm:text-xs text-slate-500 mt-0.5">录入行驶证基本信息与证件凭证（车险保单可在添加后独立录入）</p>
          </div>
        </div>
        <button @click="$emit('update:show', false)" class="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-white/60 transition">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 表单主体 -->
      <div class="p-4 sm:p-6 overflow-y-auto space-y-4 text-xs custom-scrollbar flex-1">
        <!-- 车牌与车牌类型 -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="sm:col-span-2">
            <label class="block text-slate-700 font-semibold mb-1">车牌号码 *</label>
            <div class="relative">
              <input
                v-model.trim="formData.plateNo"
                placeholder="如：浙A13K52 或 浙AD12345"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-bold text-slate-900 uppercase font-mono tracking-wider focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
              <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 font-medium">大写</span>
            </div>
          </div>
          <div>
            <label class="block text-slate-700 font-semibold mb-1">号牌类型</label>
            <select
              v-model="formData.plateType"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-medium focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="blue">传统蓝牌 (燃油车)</option>
              <option value="green">渐变绿牌 (新能源)</option>
              <option value="yellow">大型黄牌 (营运/大型)</option>
            </select>
          </div>
        </div>

        <!-- 车辆性质与归属 (个人私家车 vs 公司公户车) -->
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/80 space-y-3">
          <div>
            <label class="block text-slate-700 font-semibold mb-1.5">车辆归属性质 *</label>
            <div class="grid grid-cols-2 gap-2.5">
              <button
                type="button"
                @click="formData.isCompany = false"
                :class="!formData.isCompany ? 'bg-sky-600 text-white font-bold shadow-sm shadow-sky-200 border-sky-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'"
                class="py-2 px-3 rounded-xl border text-xs flex items-center justify-center space-x-1.5 transition"
              >
                <i class="fa-solid fa-user"></i>
                <span>个人私家车</span>
              </button>
              <button
                type="button"
                @click="formData.isCompany = true"
                :class="formData.isCompany ? 'bg-indigo-600 text-white font-bold shadow-sm shadow-indigo-200 border-indigo-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'"
                class="py-2 px-3 rounded-xl border text-xs flex items-center justify-center space-x-1.5 transition"
              >
                <i class="fa-solid fa-building"></i>
                <span>公司公户车</span>
              </button>
            </div>
          </div>

          <!-- 个人私家车：选择家庭成员 -->
          <div v-if="!formData.isCompany" class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div>
              <label class="block text-slate-700 font-semibold mb-1">车辆所有人 (车主) *</label>
              <select
                v-model="formData.owner"
                class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <option value="">请选择家庭成员</option>
                <option v-for="m in members" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">品牌型号 *</label>
              <input
                v-model.trim="formData.model"
                placeholder="如：特斯拉 Model Y 2023款"
                class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </div>
          </div>

          <!-- 公司公户车：输入公司名称及日常使用人 -->
          <div v-else class="space-y-3 pt-1">
            <!-- 快速选择已登记企业 -->
            <div v-if="companies && companies.length > 0" class="p-2.5 bg-indigo-50/50 rounded-xl border border-indigo-100 flex items-center justify-between">
              <div class="flex items-center space-x-2 text-xs text-indigo-900 font-medium">
                <i class="fa-solid fa-building-circle-check text-indigo-600"></i>
                <span>从已登记企业中快速带出：</span>
              </div>
              <div class="flex items-center space-x-1.5">
                <select
                  @change="handleSelectCompany($event.target.value)"
                  class="bg-white border border-indigo-200 text-indigo-900 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- 选择已登记企业 --</option>
                  <option v-for="c in companies" :key="c.id || c.name" :value="c.name">
                    {{ c.name }} {{ c.taxNo ? `(${c.taxNo.slice(0, 8)}...)` : '' }}
                  </option>
                </select>
                <button
                  type="button"
                  @click="$emit('open-companies')"
                  class="text-[11px] px-2 py-1 bg-white border border-indigo-200 text-indigo-600 hover:text-indigo-800 rounded-lg hover:bg-indigo-50 transition"
                  title="打开企业资质备查箱录入新企业"
                >
                  <i class="fa-solid fa-plus mr-0.5"></i>新企业
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-700 font-semibold mb-1">
                  公司全称 (车辆所有人) *
                </label>
                <div class="relative">
                  <input
                    v-model.trim="formData.companyName"
                    @input="formData.owner = formData.companyName"
                    placeholder="如：杭州极速科技有限公司"
                    class="w-full bg-white border border-indigo-200 rounded-xl p-2.5 font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div>
                <label class="block text-slate-700 font-semibold mb-1">品牌型号 *</label>
                <input
                  v-model.trim="formData.model"
                  placeholder="如：别克 GL8 商务车"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-700 font-semibold mb-1">
                  日常使用人 / 常用驾驶人 (可选)
                </label>
                <select
                  v-model="formData.driver"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">家庭公用 / 未指定成员</option>
                  <option v-for="m in members" :key="m" :value="m">{{ m }} (家庭成员)</option>
                </select>
              </div>
              <div class="flex items-center text-[11px] text-indigo-700 bg-indigo-50/70 rounded-xl p-2.5 border border-indigo-100/80">
                <i class="fa-solid fa-circle-info mr-1.5 shrink-0 text-indigo-500"></i>
                <span>公司公户车辆将单独归类显示，车险保费将计入统一资产台账。</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 车架号 VIN -->
        <div>
          <label class="block text-slate-700 font-semibold mb-1">车辆识别代号 / 车架号 (VIN 码 17位)</label>
          <input
            v-model.trim="formData.vin"
            maxlength="17"
            placeholder="如：LSGZR53L4KH123745"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-mono uppercase tracking-wider text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <!-- 初次登记日期 与 下次年检到期日 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-700 font-semibold mb-1">初次登记日期</label>
            <input
              type="date"
              v-model="formData.registerDate"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-mono text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="block text-slate-700 font-semibold mb-1">下次年检到期日</label>
            <input
              type="date"
              v-model="formData.annualInspectionDate"
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-mono text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
            <p class="text-[10px] text-slate-400 mt-1">系统将根据此日期提前 60 天提醒年检或申领检验合格标志</p>
          </div>
        </div>

        <!-- 行驶证证件原件与车辆照片附件 -->
        <div class="space-y-2 pt-2 border-t border-slate-100">
          <div class="flex items-center justify-between">
            <div>
              <span class="font-bold text-slate-700 flex items-center space-x-1.5">
                <i class="fa-solid fa-id-card text-sky-600"></i>
                <span>行驶证正副本 / 车辆照片附件</span>
              </span>
              <p class="text-[10px] text-slate-400 mt-0.5">上传行驶证扫描件或照片，方便随时调取备查</p>
            </div>
            <label class="cursor-pointer inline-flex items-center space-x-1 px-3 py-1.5 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded-xl text-xs font-semibold border border-sky-200 transition">
              <i class="fa-solid" :class="uploading ? 'fa-spinner fa-spin' : 'fa-arrow-up-from-bracket'"></i>
              <span>{{ uploading ? '上传中...' : '上传行驶证/照片' }}</span>
              <input type="file" accept=".pdf,image/*" class="hidden" @change="handleFileUpload" :disabled="uploading" />
            </label>
          </div>

          <p v-if="uploadError" class="text-rose-600 text-xs">{{ uploadError }}</p>

          <div v-if="formData.attachments && formData.attachments.length > 0" class="space-y-1.5">
            <div
              v-for="(att, idx) in formData.attachments"
              :key="att.id || idx"
              class="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs hover:border-slate-300 transition"
            >
              <!-- 重命名编辑模式 -->
              <div v-if="editingAttIndex === idx" class="flex items-center space-x-1.5 flex-1 mr-2">
                <i class="fa-regular fa-file-pdf text-rose-500 text-base shrink-0" v-if="att.name && att.name.endsWith('.pdf')"></i>
                <i class="fa-regular fa-file-image text-sky-500 text-base shrink-0" v-else></i>
                <input
                  v-model="editingAttName"
                  ref="attNameInputRef"
                  class="flex-1 bg-white border border-sky-400 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-sky-400"
                  @keydown.enter.prevent="saveAttName(att)"
                  @keydown.esc.prevent="cancelEditAttName"
                  placeholder="请输入证件/照片显示名称"
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
                  class="px-2 py-1 bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-lg text-[11px] font-medium transition shrink-0"
                  title="取消"
                >
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>

              <!-- 正常展示模式 -->
              <div v-else class="flex items-center space-x-2 truncate flex-1 mr-2">
                <i class="fa-regular fa-file-pdf text-rose-500 text-base shrink-0" v-if="att.name && att.name.endsWith('.pdf')"></i>
                <i class="fa-regular fa-file-image text-sky-500 text-base shrink-0" v-else></i>
                <div class="truncate">
                  <div
                    class="font-medium text-slate-800 truncate hover:text-sky-600 cursor-pointer transition"
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
                  class="text-slate-400 hover:text-sky-600 p-1 rounded-lg hover:bg-white transition text-[11px]"
                  title="修改显示名称"
                >
                  <i class="fa-regular fa-pen-to-square"></i>
                </button>
                <a :href="getAttachmentUrl(att.url)" target="_blank" class="text-sky-600 hover:text-sky-800 px-2 py-1 bg-white rounded-lg border border-slate-200 text-[11px] font-medium shadow-2xs">
                  <i class="fa-regular fa-eye mr-1"></i>预览
                </a>
                <button type="button" @click="removeAttachment(idx)" class="text-rose-500 hover:text-rose-700 p-1 rounded-lg hover:bg-rose-50 transition" title="删除附件">
                  <i class="fa-regular fa-trash-can"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-3 bg-slate-50/50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
            暂无行驶证附件，可点击右上角按钮上传
          </div>
        </div>

        <!-- 车辆备注 -->
        <div class="pt-2 border-t border-slate-100">
          <label class="block text-slate-700 font-semibold mb-1">车辆备忘与配置说明</label>
          <textarea
            v-model="formData.remark"
            rows="2"
            placeholder="如：选配了全景天幕与冬暖套装、备用车钥匙放在书房抽屉中、每逢1万公里保养..."
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
          ></textarea>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="p-3.5 sm:p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-2 shrink-0">
        <button v-if="!isNew" @click="$emit('delete', formData.id)" class="text-rose-600 hover:text-rose-800 text-xs font-medium py-1.5 px-2 rounded-lg hover:bg-rose-50 transition">
          <i class="fa-regular fa-trash-can mr-1"></i>删除
        </button>
        <div v-else></div>
        <div class="flex items-center space-x-2">
          <button @click="$emit('update:show', false)" class="px-3.5 sm:px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-semibold transition">取消</button>
          <button @click="handleSave" class="px-4 sm:px-5 py-2 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white rounded-xl text-xs font-semibold shadow-sm transition">
            {{ isNew ? '保存车辆档案' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { AppApi, getAttachmentUrl } from '../api/index.js';

const props = defineProps({
  show: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false },
  formData: { type: Object, required: true },
  members: { type: Array, default: () => [] },
  companies: { type: Array, default: () => [] }
});

const emit = defineEmits(['update:show', 'save', 'delete', 'open-companies']);

function handleSelectCompany(compName) {
  if (!compName) return;
  props.formData.companyName = compName;
  props.formData.owner = compName;
}

const uploading = ref(false);
const uploadError = ref('');

function formatSize(bytes) {
  if (!bytes) return '未知大小';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function handleSave() {
  if (!props.formData.plateNo || !props.formData.plateNo.trim()) {
    alert('请填写车牌号码');
    return;
  }
  if (props.formData.isCompany) {
    if (!props.formData.companyName || !props.formData.companyName.trim()) {
      alert('请填写公司全称 (车辆所有人)');
      return;
    }
    props.formData.owner = props.formData.companyName.trim();
  } else {
    if (!props.formData.owner) {
      alert('请选择车辆所有人 (车主)');
      return;
    }
  }
  if (!props.formData.model || !props.formData.model.trim()) {
    alert('请填写品牌型号');
    return;
  }
  emit('save');
}

async function handleFileUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > 30 * 1024 * 1024) {
    alert('附件大小不能超过 30MB');
    return;
  }
  uploading.value = true;
  uploadError.value = '';
  try {
    // 车辆行驶证与照片资料按车牌号归档至对应子文件夹
    const plateFolder = (props.formData.plateNo || '').trim() || 'vehicles';
    const att = await AppApi.uploadAttachment('vehicle', file, plateFolder);
    if (!props.formData.attachments) {
      props.formData.attachments = [];
    }
    props.formData.attachments.push(att);
  } catch (err) {
    console.error('[Upload Vehicle File]', err);
    uploadError.value = '上传失败，请重试';
  } finally {
    uploading.value = false;
    event.target.value = '';
  }
}

async function removeAttachment(index) {
  if (!props.formData.attachments) return;
  const att = props.formData.attachments[index];
  if (att && att.storedName) {
    try {
      await AppApi.deleteAttachment('vehicle', att.storedName);
    } catch (_) {}
  }
  props.formData.attachments.splice(index, 1);
  if (editingAttIndex.value === index) {
    cancelEditAttName();
  }
}

// 附件名称修改交互逻辑
const editingAttIndex = ref(-1);
const editingAttName = ref('');
const attNameInputRef = ref(null);

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

watch(() => props.show, (newVal) => {
  if (newVal) {
    cancelEditAttName();
  }
});
</script>
