<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 top-0 left-0 right-0 bottom-0 z-[70] !m-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4"
    >
      <div
        class="bg-white rounded-2xl sm:rounded-3xl max-w-xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[92vh] flex flex-col transition-all animate-in"
      >
        <!-- 弹窗顶部栏 -->
        <div class="px-5 py-4 bg-gradient-to-r from-violet-600 via-indigo-600 to-sky-600 text-white flex justify-between items-center shrink-0">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-2xl bg-white/20 backdrop-blur-md text-white flex items-center justify-center shadow-inner shrink-0">
              <i class="fa-solid fa-wand-magic-sparkles text-lg"></i>
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <h3 class="text-base font-bold tracking-tight">AI 识单引擎配置</h3>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border"
                  :class="form.enabled ? 'bg-emerald-400/20 text-emerald-200 border-emerald-300/30' : 'bg-slate-400/20 text-slate-200 border-slate-300/30'"
                >
                  {{ form.enabled ? '已启用' : '已关闭' }}
                </span>
              </div>
              <p class="text-xs text-white/80 mt-0.5">
                手动配置兼容 OpenAI 协议的接口端点、密钥与模型名称
              </p>
            </div>
          </div>
          <button
            type="button"
            @click="closeModal"
            class="text-white/70 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition cursor-pointer"
            title="关闭窗口"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <!-- 弹窗表单主体 (纯手动填写) -->
        <div class="p-6 overflow-y-auto space-y-5 text-xs custom-scrollbar flex-1">
          <!-- 功能总开关 -->
          <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/80 flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-800 text-xs flex items-center space-x-1.5">
                <i class="fa-solid fa-power-off text-indigo-600"></i>
                <span>启用 AI 智能识别保单功能</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5">关闭后录入保单时将隐藏 AI 解析提示与快速提取通道</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="form.enabled" class="sr-only peer" />
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          <!-- Base URL 端点 -->
          <div class="space-y-1.5">
            <label class="block font-bold text-slate-700 text-xs">
              API 端点 (Base URL) <span class="text-rose-500">*</span>
            </label>
            <input
              type="text"
              v-model="form.baseUrl"
              placeholder="如：https://dashscope.aliyuncs.com/compatible-mode/v1 或 https://api.deepseek.com/v1"
              class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p class="text-[10px] text-slate-400">兼容标准 OpenAI 协议端点，系统将向 /{version}/chat/completions 发起请求</p>
          </div>

          <!-- API Key 密钥 -->
          <div class="space-y-1.5">
            <label class="block font-bold text-slate-700 text-xs flex justify-between items-center">
              <span>API Key (接口密钥) <span class="text-rose-500">*</span></span>
              <span v-if="initialHasApiKey" class="text-[10px] text-emerald-600 font-normal">
                <i class="fa-solid fa-shield-check mr-0.5"></i>已存储密钥 (未修改时将继续沿用)
              </span>
            </label>
            <div class="relative">
              <input
                :type="showApiKey ? 'text' : 'password'"
                v-model="form.apiKey"
                placeholder="请输入 sk-..."
                class="w-full bg-white border border-slate-200 rounded-xl pl-3 pr-10 py-2.5 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="button"
                @click="showApiKey = !showApiKey"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                title="切换显示/隐藏密钥"
              >
                <i class="fa-regular" :class="showApiKey ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
            <p class="text-[10px] text-slate-400">密钥保存在服务端本地 data/ 目录下，不会泄漏给第三方或上传公开网络</p>
          </div>

          <!-- 模型名称 (Model) -->
          <div class="space-y-1.5">
            <label class="block font-bold text-slate-700 text-xs">
              模型名称 (Model) <span class="text-rose-500">*</span>
            </label>
            <input
              type="text"
              v-model="form.model"
              placeholder="如：qwen-plus / deepseek-chat / glm-4-flash / gpt-4o-mini"
              class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p class="text-[10px] text-slate-400">请填写服务商提供的有效模型代号，支持文本或多模态视觉模型</p>
          </div>

          <!-- 连通性测试结果面板 -->
          <div
            v-if="testResult"
            class="p-3 rounded-xl border text-xs flex items-start space-x-2.5 transition animate-in"
            :class="testResult.success ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'"
          >
            <i class="fa-solid text-sm mt-0.5 shrink-0" :class="testResult.success ? 'fa-circle-check text-emerald-600' : 'fa-circle-xmark text-rose-600'"></i>
            <div class="flex-1 break-words">
              <div class="font-bold">{{ testResult.success ? '测试通过' : '测试失败' }}</div>
              <div class="text-[11px] mt-0.5">{{ testResult.message }}</div>
            </div>
          </div>
        </div>

        <!-- 弹窗底部操作按钮 -->
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center gap-3 shrink-0">
          <button
            type="button"
            @click="runTestConnection"
            :disabled="testing"
            class="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 active:bg-slate-100 transition shadow-2xs cursor-pointer disabled:opacity-60"
          >
            <i class="fa-solid" :class="testing ? 'fa-spinner fa-spin text-indigo-600' : 'fa-network-wired text-indigo-600'"></i>
            <span>{{ testing ? '测试中...' : '测试连通性' }}</span>
          </button>

          <div class="flex items-center space-x-2">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200/70 transition cursor-pointer"
            >
              取消
            </button>
            <button
              type="button"
              @click="handleSave"
              :disabled="saving"
              class="inline-flex items-center space-x-1.5 px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 transition shadow-md shadow-indigo-200 cursor-pointer disabled:opacity-60"
            >
              <i class="fa-solid" :class="saving ? 'fa-spinner fa-spin' : 'fa-check'"></i>
              <span>{{ saving ? '保存中...' : '保存配置' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { AppApi } from '../api/index.js';

const props = defineProps({
  show: { type: Boolean, default: false }
});

const emit = defineEmits(['update:show', 'saved']);

const form = reactive({
  enabled: false,
  baseUrl: '',
  apiKey: '',
  model: '',
  timeout: 60
});

const initialHasApiKey = ref(false);
const showApiKey = ref(false);
const saving = ref(false);
const testing = ref(false);
const testResult = ref(null);

async function loadSettings() {
  try {
    const res = await AppApi.getAiSettings();
    form.enabled = !!res.enabled;
    form.baseUrl = res.baseUrl || '';
    form.apiKey = res.apiKey || '';
    form.model = res.model || '';
    form.timeout = res.timeout || 60;
    initialHasApiKey.value = !!res.hasApiKey;
    testResult.value = null;
  } catch (err) {
    console.error('[AI Settings] 获取配置失败:', err);
  }
}

watch(
  () => props.show,
  (val) => {
    if (val) {
      loadSettings();
      showApiKey.value = false;
      testResult.value = null;
    }
  },
  { immediate: true }
);

async function runTestConnection() {
  if (!form.baseUrl.trim()) {
    testResult.value = { success: false, message: '请先填写 API 端点 (Base URL)' };
    return;
  }
  if (!form.apiKey.trim() && !initialHasApiKey.value) {
    testResult.value = { success: false, message: '请先填写 API Key' };
    return;
  }
  if (!form.model.trim()) {
    testResult.value = { success: false, message: '请先填写模型名称 (Model)' };
    return;
  }

  testing.value = true;
  testResult.value = null;
  try {
    const res = await AppApi.testAiSettings({
      baseUrl: form.baseUrl,
      apiKey: form.apiKey,
      model: form.model,
      timeout: 20
    });
    testResult.value = res;
  } catch (err) {
    testResult.value = {
      success: false,
      message: err.message || '测试连接网络异常'
    };
  } finally {
    testing.value = false;
  }
}

async function handleSave() {
  if (form.enabled) {
    if (!form.baseUrl.trim()) {
      alert('请填写 API 端点 (Base URL)');
      return;
    }
    if (!form.apiKey.trim() && !initialHasApiKey.value) {
      alert('启用 AI 解析时必须提供有效的 API Key');
      return;
    }
    if (!form.model.trim()) {
      alert('请填写模型名称 (Model)');
      return;
    }
  }

  saving.value = true;
  try {
    const saved = await AppApi.saveAiSettings(form);
    emit('saved', saved);
    emit('update:show', false);
  } catch (err) {
    alert(`保存失败: ${err.message}`);
  } finally {
    saving.value = false;
  }
}

function closeModal() {
  emit('update:show', false);
}
</script>
