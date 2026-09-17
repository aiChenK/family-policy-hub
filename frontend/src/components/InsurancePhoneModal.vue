<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
    <div class="bg-white rounded-2xl shadow-2xl border border-slate-100 w-full max-w-3xl overflow-hidden flex flex-col max-h-[95vh] sm:max-h-[90vh]">
      <!-- 弹窗顶部标题 -->
      <div class="px-4 sm:px-6 py-3.5 sm:py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
        <div class="flex items-center space-x-2.5 sm:space-x-3">
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-600 text-white flex items-center justify-center text-base sm:text-lg shadow-md shadow-teal-100 shrink-0">
            <i class="fa-solid fa-phone-volume"></i>
          </div>
          <div>
            <h3 class="text-sm sm:text-base font-bold text-slate-800 tracking-tight">保险客服与报案电话配置</h3>
            <p class="text-xs text-slate-500 line-clamp-1 sm:line-clamp-none">保单承保机构关键字智能匹配客服专线与报案电话</p>
          </div>
        </div>
        <button
          type="button"
          @click="closeModal"
          class="text-slate-400 hover:text-slate-600 p-1.5 sm:p-2 rounded-lg hover:bg-slate-100 transition"
          title="关闭"
        >
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 弹窗内容主体 -->
      <div class="p-3.5 sm:p-6 overflow-y-auto space-y-4 sm:space-y-5 custom-scrollbar flex-1">
        <!-- 概览与全局默认回退电话 -->
        <div class="p-4 bg-slate-50 rounded-xl border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center space-x-2.5">
            <i class="fa-solid fa-circle-question text-sky-600 text-base"></i>
            <div>
              <div class="text-xs font-bold text-slate-800">未匹配保司时的默认电话</div>
              <div class="text-[11px] text-slate-500">当保单公司未命中下方任何关键字规则时，拨打此兜底号码</div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <input
              type="text"
              v-model="editConfig.defaultPhone"
              placeholder="选填，如 95511 (留空不兜底)"
              class="w-48 px-3 py-1.5 text-xs font-mono font-bold bg-white border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
            />
            <a
              v-if="editConfig.defaultPhone"
              :href="'tel:' + editConfig.defaultPhone"
              class="px-2.5 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-medium transition flex items-center space-x-1"
              title="呼叫测试"
            >
              <i class="fa-solid fa-phone text-xs"></i>
              <span>测试</span>
            </a>
          </div>
        </div>

        <!-- 工具栏：搜索过滤、新增、重置预设 -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pt-1">
          <!-- 实时过滤搜索 -->
          <div class="relative flex-1 max-w-sm">
            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索保司名称、匹配关键字或电话..."
              class="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-sky-500"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs"
            >
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- 右侧操作组 -->
          <div class="flex items-center space-x-2">
            <button
              type="button"
              @click="showAddDrawer = !showAddDrawer"
              class="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium rounded-lg text-white bg-sky-600 hover:bg-sky-700 active:bg-sky-800 transition shadow-sm"
            >
              <i class="fa-solid" :class="showAddDrawer ? 'fa-minus' : 'fa-plus'"></i>
              <span>{{ showAddDrawer ? '收起表单' : '添加电话规则' }}</span>
            </button>
            <button
              type="button"
              @click="resetToDefault"
              class="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium rounded-lg text-slate-600 bg-slate-100 hover:bg-slate-200 transition"
              title="重置为出厂预设的 12 家主流保司及官方热线"
            >
              <i class="fa-solid fa-rotate-left text-slate-500"></i>
              <span>恢复预设</span>
            </button>
          </div>
        </div>

        <!-- 新增/编辑规则抽屉卡片 -->
        <div
          v-if="showAddDrawer"
          class="p-4 bg-sky-50/50 rounded-xl border border-sky-200/80 space-y-3 animate-fade-in"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-sky-900 flex items-center space-x-1.5">
              <i class="fa-solid" :class="editingId ? 'fa-pen-to-square' : 'fa-plus-circle'"></i>
              <span>{{ editingId ? '编辑电话规则' : '新增保司电话规则' }}</span>
            </h4>
            <span class="text-[11px] text-slate-500">
              承保机构名称若包含“匹配关键字”，将自动关联此电话
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
            <div>
              <label class="block text-[11px] font-medium text-slate-600 mb-1">
                机构全称 / 简称 <span class="text-rose-500">*</span>
              </label>
              <input
                type="text"
                v-model="formRule.name"
                placeholder="例如：中国平安"
                class="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
            <div>
              <label class="block text-[11px] font-medium text-slate-600 mb-1">
                匹配关键字 <span class="text-rose-500">*</span>
              </label>
              <input
                type="text"
                v-model="formRule.keyword"
                placeholder="例如：平安"
                class="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
            <div>
              <label class="block text-[11px] font-medium text-slate-600 mb-1">
                报案 / 客服专线 <span class="text-rose-500">*</span>
              </label>
              <input
                type="text"
                v-model="formRule.phone"
                placeholder="例如：95511"
                class="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-slate-800 font-mono font-bold focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
            <div class="sm:col-span-3">
              <label class="block text-[11px] font-medium text-slate-600 mb-1">
                服务范围 / 备注说明
              </label>
              <input
                type="text"
                v-model="formRule.notes"
                placeholder="例如：产险、寿险、健康险全国统一报案热线"
                class="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
          </div>

          <div class="flex justify-end items-center space-x-2 pt-1">
            <button
              type="button"
              @click="cancelEditForm"
              class="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800 bg-white border border-slate-200 rounded-lg transition"
            >
              取消
            </button>
            <button
              type="button"
              @click="submitRuleForm"
              class="px-4 py-1.5 text-xs font-medium text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition shadow-sm"
            >
              {{ editingId ? '保存本条' : '确认添加' }}
            </button>
          </div>
        </div>

        <!-- 电话规则列表展示 -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs text-slate-500 pb-1">
            <span>规则列表 (共 {{ filteredPhones.length }} 条{{ searchQuery ? '匹配项' : '' }})</span>
            <span class="text-[11px] text-slate-400">点击号码右侧按钮可直接测试呼叫或复制</span>
          </div>

          <div v-if="filteredPhones.length === 0" class="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
            <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-300"></i>
            <p>{{ searchQuery ? '未检索到相关保险电话规则' : '暂无配置规则，可点击“恢复预设”初始化' }}</p>
          </div>

          <div
            v-for="item in filteredPhones"
            :key="item.id"
            class="p-3 bg-white rounded-xl border border-slate-200/90 hover:border-sky-300 hover:shadow-sm transition flex flex-col sm:flex-row sm:items-center justify-between gap-2.5"
          >
            <!-- 左侧：保司名称与关键字 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2 flex-wrap">
                <span class="font-bold text-slate-800 text-xs">{{ item.name }}</span>
                <span class="px-2 py-0.5 rounded-md bg-sky-50 text-sky-700 border border-sky-100 text-[11px] font-medium">
                  包含关键字: <strong class="font-bold">{{ item.keyword }}</strong>
                </span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1 truncate" :title="item.notes">
                {{ item.notes || '官方客户服务热线' }}
              </p>
            </div>

            <!-- 右侧：电话与快捷按钮 -->
            <div class="flex items-center space-x-2 shrink-0 self-end sm:self-center">
              <a
                :href="'tel:' + item.phone"
                class="px-2.5 py-1 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-mono font-bold flex items-center space-x-1.5 transition"
                title="点击一键呼叫"
              >
                <i class="fa-solid fa-phone text-xs"></i>
                <span>{{ item.phone }}</span>
              </a>

              <button
                type="button"
                @click="copyPhone(item.phone, item.id)"
                class="p-1.5 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-lg border border-slate-200 text-xs transition"
                :title="copiedId === item.id ? '已复制' : '复制电话号码'"
              >
                <i :class="copiedId === item.id ? 'fa-solid fa-check text-emerald-600' : 'fa-regular fa-copy'"></i>
              </button>

              <button
                type="button"
                @click="startEditRule(item)"
                class="p-1.5 bg-slate-50 hover:bg-sky-50 hover:text-sky-600 text-slate-600 rounded-lg border border-slate-200 text-xs transition"
                title="编辑此规则"
              >
                <i class="fa-solid fa-pen text-xs"></i>
              </button>

              <button
                type="button"
                @click="removeRule(item)"
                class="p-1.5 bg-slate-50 hover:bg-rose-50 hover:text-rose-600 text-slate-600 rounded-lg border border-slate-200 text-xs transition"
                title="删除此规则"
              >
                <i class="fa-regular fa-trash-can text-xs"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 弹窗底部操作条 -->
      <div class="px-4 sm:px-6 py-3 sm:py-3.5 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-2">
        <div class="text-[11px] sm:text-xs text-slate-500">
          已配置 <strong class="text-slate-800">{{ (editConfig.phones || []).length }}</strong> 家机构电话
        </div>
        <div class="flex items-center space-x-2">
          <button
            type="button"
            @click="closeModal"
            class="px-3 sm:px-4 py-1.5 text-xs text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg transition"
          >
            取消
          </button>
          <button
            type="button"
            @click="saveAll"
            :disabled="saving"
            class="inline-flex items-center space-x-1 sm:space-x-1.5 px-3.5 sm:px-4 py-1.5 text-xs font-medium rounded-lg text-white bg-sky-600 hover:bg-sky-700 active:bg-sky-800 transition shadow-sm disabled:opacity-50"
          >
            <i class="fa-solid" :class="saving ? 'fa-spinner fa-spin' : 'fa-floppy-disk'"></i>
            <span>{{ saving ? '保存中...' : '保存配置' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { DEFAULT_PHONE_CONFIG, deepClone } from '../utils/helpers.js';

const props = defineProps({
  show: { type: Boolean, default: false },
  phoneConfig: {
    type: Object,
    default: () => deepClone(DEFAULT_PHONE_CONFIG)
  }
});

const emit = defineEmits(['update:show', 'save', 'toast']);

// 本地编辑态副本
const editConfig = ref(deepClone(DEFAULT_PHONE_CONFIG));
const searchQuery = ref('');
const showAddDrawer = ref(false);
const editingId = ref(null);
const saving = ref(false);
const copiedId = ref(null);

const formRule = ref({
  name: '',
  keyword: '',
  phone: '',
  notes: ''
});

// 监听弹窗显示，每次打开重新克隆外部配置
watch(
  () => props.show,
  (val) => {
    if (val) {
      const src = props.phoneConfig && props.phoneConfig.phones ? props.phoneConfig : DEFAULT_PHONE_CONFIG;
      editConfig.value = deepClone(src);
      searchQuery.value = '';
      cancelEditForm();
    }
  },
  { immediate: true }
);

// 搜索过滤列表
const filteredPhones = computed(() => {
  const list = editConfig.value.phones || [];
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(item => {
    return (
      (item.name && item.name.toLowerCase().includes(q)) ||
      (item.keyword && item.keyword.toLowerCase().includes(q)) ||
      (item.phone && item.phone.toLowerCase().includes(q)) ||
      (item.notes && item.notes.toLowerCase().includes(q))
    );
  });
});

function closeModal() {
  cancelEditForm();
  emit('update:show', false);
}

function copyPhone(phone, id) {
  if (!phone) return;
  navigator.clipboard.writeText(phone).then(() => {
    copiedId.value = id;
    setTimeout(() => {
      copiedId.value = null;
    }, 2000);
  }).catch(() => {});
}

function startEditRule(item) {
  editingId.value = item.id;
  formRule.value = {
    name: item.name,
    keyword: item.keyword,
    phone: item.phone,
    notes: item.notes || ''
  };
  showAddDrawer.value = true;
}

function cancelEditForm() {
  showAddDrawer.value = false;
  editingId.value = null;
  formRule.value = {
    name: '',
    keyword: '',
    phone: '',
    notes: ''
  };
}

function submitRuleForm() {
  const name = formRule.value.name.trim();
  const keyword = formRule.value.keyword.trim();
  const phone = formRule.value.phone.trim();
  const notes = formRule.value.notes.trim();

  if (!name) {
    emit('toast', '请输入机构名称', 'error');
    return;
  }
  if (!keyword) {
    emit('toast', '请输入匹配关键字', 'error');
    return;
  }
  if (!phone) {
    emit('toast', '请输入客服或报案电话', 'error');
    return;
  }

  if (!editConfig.value.phones) {
    editConfig.value.phones = [];
  }

  if (editingId.value) {
    const idx = editConfig.value.phones.findIndex(p => p.id === editingId.value);
    if (idx !== -1) {
      editConfig.value.phones[idx] = {
        ...editConfig.value.phones[idx],
        name,
        keyword,
        phone,
        notes
      };
      emit('toast', `已修改 ${name} 电话规则`);
    }
  } else {
    editConfig.value.phones.unshift({
      id: `phone_${Date.now()}`,
      name,
      keyword,
      phone,
      notes
    });
    emit('toast', `已添加 ${name} 电话规则`);
  }

  cancelEditForm();
}

function removeRule(item) {
  if (confirm(`确认删除“${item.name} (${item.phone})”的电话配置规则吗？`)) {
    editConfig.value.phones = editConfig.value.phones.filter(p => p.id !== item.id);
    emit('toast', `已删除 ${item.name} 规则`);
  }
}

function resetToDefault() {
  if (confirm('确认恢复出厂预设吗？当前的自定义修改将被 12 家主流保司的官方标准预设覆盖。')) {
    editConfig.value = deepClone(DEFAULT_PHONE_CONFIG);
    cancelEditForm();
    emit('toast', '已恢复出厂默认预设');
  }
}

async function saveAll() {
  saving.value = true;
  try {
    const payload = deepClone(editConfig.value);
    if (payload.defaultPhone === undefined || payload.defaultPhone === null) {
      payload.defaultPhone = '';
    } else {
      payload.defaultPhone = String(payload.defaultPhone).trim();
    }
    emit('save', payload);
    emit('update:show', false);
  } finally {
    saving.value = false;
  }
}
</script>
