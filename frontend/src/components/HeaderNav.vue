<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <!-- 1. 系统 Logo 与综合保障信息概览 -->
        <div class="flex items-center space-x-2.5 sm:space-x-3 min-w-0">
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-100 shrink-0">
            <i class="fa-solid fa-shield-halved text-base sm:text-lg"></i>
          </div>
          <div class="min-w-0">
            <div class="flex items-center space-x-1.5 sm:space-x-2">
              <h1 class="text-base sm:text-lg font-bold text-slate-900 tracking-tight truncate">家庭保险管理系统</h1>
              <span class="hidden sm:inline-flex text-xs bg-sky-100 text-sky-700 px-2 py-0.5 rounded-full font-medium">家庭资产保障</span>
            </div>
            <!-- 精准修正的家庭保障覆盖信息 (桌面端完整版) -->
            <p class="text-xs text-slate-500 mt-0.5 hidden sm:flex items-center flex-wrap gap-x-1.5">
              <span class="font-medium text-slate-700">
                {{ isAllCovered ? `全员 ${memberCount} 位成员在保` : `覆盖 ${coveredMemberCount}/${memberCount} 位成员` }}
              </span>
              <span class="text-slate-300">·</span>
              <span>{{ activePolicyCount }} 笔商业保单</span>
              <template v-if="vehicleCount > 0">
                <span class="text-slate-300">·</span>
                <span class="text-sky-700 font-medium">{{ vehicleCount }} 辆爱车在保</span>
              </template>
            </p>
            <!-- 精准修正的家庭保障覆盖信息 (移动端精炼单行版) -->
            <p class="text-[11px] text-slate-500 mt-0.5 flex sm:hidden items-center gap-x-1 truncate">
              <span class="font-medium text-slate-700">{{ isAllCovered ? `${memberCount}人全保` : `${coveredMemberCount}/${memberCount}人` }}</span>
              <span class="text-slate-300">·</span>
              <span>{{ activePolicyCount }}笔保单</span>
              <template v-if="vehicleCount > 0">
                <span class="text-slate-300">·</span>
                <span class="text-sky-700 font-medium">{{ vehicleCount }}车</span>
              </template>
            </p>
          </div>
        </div>

        <!-- 2. 右侧精简工具栏：状态胶囊 + 二级收拢菜单 + 锁定 -->
        <div class="flex items-center space-x-1.5 sm:space-x-3 relative shrink-0">
          <!-- 动态状态指示器 (遵循静默原则：服务正常时静默隐藏，仅在落盘中或离线异常时提醒) -->
          <transition name="fade">
            <div
              v-if="saving || !isApiConnected"
              class="flex items-center space-x-1.5 px-2 sm:px-3 py-1 rounded-full text-xs font-medium border shadow-2xs transition-all duration-300 shrink-0"
              :class="saving ? 'bg-amber-50 text-amber-700 border-amber-200/80' : 'bg-rose-50 text-rose-700 border-rose-200/80'"
              :title="saving ? '正在将修改原子同步落盘至本地文件' : '未能连接至后端服务，数据修改仅暂存在浏览器本地缓存中'"
            >
              <i
                :class="saving ? 'fa-solid fa-arrows-rotate animate-spin text-amber-600' : 'fa-solid fa-triangle-exclamation text-rose-500'"
                class="text-[11px]"
              ></i>
              <span class="hidden sm:inline">{{ saving ? '正在同步落盘...' : '离线模式' }}</span>
            </div>
          </transition>

          <!-- 二级收拢菜单触发按钮 -->
          <div class="relative" ref="dropdownRef">
            <button
              @click="toggleDropdown"
              class="inline-flex items-center space-x-1.5 px-2.5 sm:px-3.5 py-1.5 text-xs font-semibold rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 active:bg-slate-300 transition shadow-2xs border border-slate-200/70"
              :class="dropdownOpen ? 'ring-2 ring-sky-500/20 bg-slate-200 text-sky-800' : ''"
              title="管理家庭主体档案、保司配置、数据备份与系统工具"
            >
              <i class="fa-solid fa-sliders text-sky-600"></i>
              <span class="hidden sm:inline">管理与工具</span>
              <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200 hidden sm:inline" :class="dropdownOpen ? 'rotate-180 text-sky-600' : ''"></i>
            </button>

            <!-- 二级下拉菜单抽屉浮层 (带屏幕边缘自适应保护) -->
            <transition name="dropdown">
              <div
                v-if="dropdownOpen"
                class="absolute right-0 mt-2 w-72 max-w-[calc(100vw-1.5rem)] bg-white/95 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/90 py-2 z-50 divide-y divide-slate-100 text-xs animate-in"
              >
                <!-- 分组 1：主体档案与配置 -->
                <div class="py-1">
                  <div class="px-3.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">主体档案与配置</div>
                  <button
                    @click="triggerAction('open-members', 'members')"
                    class="w-full text-left px-3.5 py-2 hover:bg-sky-50/80 text-slate-700 hover:text-sky-800 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-sky-100 text-sky-600 flex items-center justify-center text-xs group-hover:scale-105 transition-transform">
                        <i class="fa-solid fa-users"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">家庭成员档案</div>
                        <div class="text-[10px] text-slate-400">管理 {{ memberCount }} 位成员资料与排序</div>
                      </div>
                    </div>
                    <span class="text-[10px] bg-sky-100/70 text-sky-700 px-1.5 py-0.5 rounded font-bold">{{ memberCount }}人</span>
                  </button>

                  <button
                    @click="triggerAction('open-companies')"
                    class="w-full text-left px-3.5 py-2 hover:bg-indigo-50/80 text-slate-700 hover:text-indigo-800 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs group-hover:scale-105 transition-transform">
                        <i class="fa-solid fa-building"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">关联企业资质</div>
                        <div class="text-[10px] text-slate-400">备查公户车税号与营业执照</div>
                      </div>
                    </div>
                    <span class="text-[10px] bg-indigo-100/70 text-indigo-700 px-1.5 py-0.5 rounded font-bold">{{ companyCount }}家</span>
                  </button>

                  <button
                    @click="triggerAction('open-phones')"
                    class="w-full text-left px-3.5 py-2 hover:bg-emerald-50/80 text-slate-700 hover:text-emerald-800 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs group-hover:scale-105 transition-transform">
                        <i class="fa-solid fa-phone-volume"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">保司电话配置</div>
                        <div class="text-[10px] text-slate-400">报案与客服热线维护</div>
                      </div>
                    </div>
                    <i class="fa-solid fa-angle-right text-slate-300 text-[10px] group-hover:translate-x-0.5 transition-transform"></i>
                  </button>
                </div>

                <!-- 分组 2：数据安全与灾备 -->
                <div class="py-1">
                  <div class="px-3.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">数据安全与灾备</div>
                  <button
                    @click="triggerAction('export-json')"
                    class="w-full text-left px-3.5 py-2 hover:bg-slate-50 text-slate-700 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-file-code"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">导出 JSON 备份</div>
                        <div class="text-[10px] text-slate-400">完整导出保单、车辆与台账</div>
                      </div>
                    </div>
                    <i class="fa-solid fa-download text-slate-400 text-xs"></i>
                  </button>

                  <label class="w-full text-left px-3.5 py-2 hover:bg-slate-50 text-slate-700 transition flex items-center justify-between group cursor-pointer">
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-file-import"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">导入 JSON 恢复</div>
                        <div class="text-[10px] text-slate-400">从本地备份文件还原数据</div>
                      </div>
                    </div>
                    <i class="fa-solid fa-upload text-slate-400 text-xs"></i>
                    <input type="file" accept=".json" class="hidden" @change="handleFileChange" />
                  </label>

                  <button
                    @click="triggerAction('export-ics')"
                    class="w-full text-left px-3.5 py-2 hover:bg-slate-50 text-slate-700 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-sky-100 text-sky-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-calendar-check"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">导出日历订阅 (.ics)</div>
                        <div class="text-[10px] text-slate-400">同步至苹果/谷歌系统日历</div>
                      </div>
                    </div>
                    <i class="fa-solid fa-arrow-up-right-from-square text-slate-400 text-[10px]"></i>
                  </button>
                </div>

                <!-- 分组 3：系统维护 -->
                <div class="py-1">
                  <div class="px-3.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">系统维护</div>
                  <button
                    @click="triggerAction('open-cleaner')"
                    class="w-full text-left px-3.5 py-2 hover:bg-rose-50/80 text-slate-700 hover:text-rose-700 transition flex items-center justify-between group"
                  >
                    <div class="flex items-center space-x-2.5">
                      <div class="w-6 h-6 rounded-lg bg-rose-100 text-rose-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-broom"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-900">附件存储清理</div>
                        <div class="text-[10px] text-slate-400">扫描并清理未引用孤儿文件</div>
                      </div>
                    </div>
                    <i class="fa-solid fa-angle-right text-slate-300 text-[10px] group-hover:translate-x-0.5 transition-transform"></i>
                  </button>
                </div>
                <!-- 分组 4：系统服务状态与运行模式 (常驻备查) -->
                <div class="px-3.5 py-2.5 bg-slate-50/90 rounded-b-2xl border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                  <span class="flex items-center space-x-1.5">
                    <span class="w-1.5 h-1.5 rounded-full" :class="isApiConnected ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                    <span class="font-medium text-slate-600">{{ isApiConnected ? '后端服务运行中' : '离线存储模式' }}</span>
                  </span>
                  <span class="text-[10px] text-slate-400 font-mono">{{ isApiConnected ? 'API 就绪' : '本地缓存' }}</span>
                </div>
              </div>
            </transition>
          </div>

          <!-- 锁定/退出按钮 (仅当启用密码保护时展示) -->
          <button
            v-if="authState?.required && authState?.authenticated"
            @click="$emit('logout')"
            title="锁定并保护隐私"
            class="inline-flex items-center space-x-1 px-2 sm:px-3 py-1.5 text-xs font-semibold rounded-xl text-slate-600 bg-slate-100 hover:bg-rose-50 hover:text-rose-600 transition shadow-2xs border border-slate-200/70 shrink-0"
          >
            <i class="fa-solid fa-lock text-slate-400 group-hover:text-rose-500"></i>
            <span class="hidden sm:inline">锁定</span>
          </button>
        </div>
      </div>

      <!-- 标签页导航栏 (桌面展示完整Tabs，移动端由底部MobileTabBar专属接管) -->
      <nav class="hidden md:flex space-x-5 sm:space-x-8 -mb-px overflow-x-auto no-scrollbar py-0.5">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="$emit('update:currentTab', tab.id)"
          :class="[
            currentTab === tab.id
              ? 'border-sky-600 text-sky-600 font-semibold'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 font-medium'
          ]"
          class="whitespace-nowrap py-2.5 sm:py-3 px-1 border-b-2 text-xs sm:text-sm flex items-center space-x-1.5 sm:space-x-2 transition"
        >
          <i :class="tab.icon"></i>
          <span>{{ tab.name }}</span>
          <span
            v-if="tab.badge"
            :class="tab.badgeClass || 'bg-slate-100 text-slate-600'"
            class="ml-1 px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs rounded-full font-medium"
          >
            {{ tab.badge }}
          </span>
        </button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  currentTab: { type: String, required: true },
  tabs: { type: Array, required: true },
  isApiConnected: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  authState: { type: Object, default: () => ({ required: false, authenticated: false }) },
  memberCount: { type: Number, default: 0 },
  coveredMemberCount: { type: Number, default: 0 },
  isAllCovered: { type: Boolean, default: false },
  activePolicyCount: { type: Number, default: 0 },
  vehicleCount: { type: Number, default: 0 },
  companyCount: { type: Number, default: 0 }
});

const emit = defineEmits([
  'update:currentTab',
  'export-json',
  'import-json',
  'export-ics',
  'open-cleaner',
  'open-phones',
  'open-members',
  'open-companies',
  'logout'
]);

const dropdownOpen = ref(false);
const dropdownRef = ref(null);

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

function closeDropdown() {
  dropdownOpen.value = false;
}

function triggerAction(action, payload) {
  closeDropdown();
  if (payload !== undefined) {
    emit(action, payload);
  } else {
    emit(action);
  }
}

function handleFileChange(event) {
  const file = event.target.files?.[0];
  if (file) {
    closeDropdown();
    emit('import-json', file);
  }
  event.target.value = '';
}

// 点击外部与按 Esc 键自动收拢下拉菜单
function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown();
  }
}

function handleKeydown(event) {
  if (event.key === 'Escape' && dropdownOpen.value) {
    closeDropdown();
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
