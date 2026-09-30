<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 top-0 left-0 right-0 bottom-0 z-[60] !m-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
      <div class="bg-white rounded-2xl sm:rounded-3xl max-w-3xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[94vh] sm:max-h-[92vh] flex flex-col transition-all">
        <!-- 弹窗标题栏 -->
        <div class="px-4 sm:px-6 py-3.5 sm:py-4 bg-gradient-to-r from-sky-50 via-indigo-50/60 to-purple-50/40 border-b border-sky-100 flex justify-between items-center shrink-0">
          <div class="flex items-center space-x-2.5 sm:space-x-3">
            <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white flex items-center justify-center shadow-md shadow-sky-200 shrink-0">
              <i class="fa-solid fa-file-contract text-sm sm:text-base"></i>
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <h3 class="text-sm sm:text-base font-bold text-slate-900">
                  {{ titleText }}
                </h3>
                <span v-if="selectedVehicle" class="px-2 py-0.5 rounded-full text-[11px] font-mono font-bold shrink-0 whitespace-nowrap" :class="selectedVehicle.plateType === 'green' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'">
                  {{ selectedVehicle.plateNo }}
                </span>
              </div>
              <p class="text-[11px] sm:text-xs text-slate-500 mt-0.5">
                {{ subtitleText }}
              </p>
            </div>
          </div>
          <button
            type="button"
            @click="$emit('update:show', false)"
            class="text-slate-400 hover:text-slate-600 p-1.5 rounded-xl hover:bg-white/80 transition cursor-pointer"
            title="关闭弹窗"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <!-- 表单内容主体 -->
        <div class="p-6 overflow-y-auto space-y-5 text-xs custom-scrollbar flex-1">
          <!-- 0. AI 智能识单卡片 (未配置时温和引导，已配置时支持拖拽/多选一键提取并预审) -->
          <div
            class="rounded-2xl border transition overflow-hidden shadow-2xs"
            :class="aiSettings?.isConfigured ? 'bg-gradient-to-br from-indigo-50/70 via-sky-50/50 to-purple-50/40 border-indigo-200/80' : 'bg-slate-50 border-slate-200/80'"
          >
            <!-- A. 未配置 AI 引擎时的优雅提示条 -->
            <div v-if="!aiSettings?.isConfigured" class="p-3.5 flex items-center justify-between gap-3 text-xs">
              <div class="flex items-center space-x-2.5 text-slate-600">
                <div class="w-7 h-7 rounded-xl bg-violet-100 text-violet-600 flex items-center justify-center shrink-0">
                  <i class="fa-solid fa-wand-magic-sparkles text-xs"></i>
                </div>
                <div>
                  <span class="font-bold text-slate-800">支持 AI 智能识单自动填表：</span>
                  <span class="text-slate-500">上传商业险/交强险 PDF 或照片，秒级提取保费明细与保单号</span>
                </div>
              </div>
              <button
                type="button"
                @click="$emit('open-ai-settings')"
                class="inline-flex items-center space-x-1 px-3 py-1.5 bg-violet-600 hover:bg-violet-700 active:bg-violet-800 text-white rounded-xl text-xs font-semibold shadow-xs shrink-0 transition cursor-pointer"
              >
                <i class="fa-solid fa-sliders text-[11px]"></i>
                <span>配置 AI 识单引擎</span>
              </button>
            </div>

            <!-- B. 已配置 AI 引擎时的上传交互卡片 -->
            <div v-else class="p-4 space-y-3">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <span class="w-6 h-6 rounded-lg bg-indigo-600 text-white flex items-center justify-center text-xs shadow-xs">
                    <i class="fa-solid fa-wand-magic-sparkles"></i>
                  </span>
                  <span class="font-bold text-indigo-950 text-xs">AI 智能提取保单 (交强险 / 商业险 PDF 或照片)</span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-indigo-100/80 text-indigo-700 border border-indigo-200/60">
                    {{ aiSettings?.model || '大模型引擎' }}
                  </span>
                  <button
                    type="button"
                    @click="$emit('open-ai-settings')"
                    class="text-slate-400 hover:text-indigo-600 text-[11px] p-1 transition cursor-pointer"
                    title="修改 AI 识单引擎配置"
                  >
                    <i class="fa-solid fa-gear"></i>
                  </button>
                </div>
              </div>

              <!-- 上传托盘区域 (支持点击与拖拽，支持同时选商业险与交强险) -->
              <div
                v-if="!aiParsing && !aiParsedResult"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleAiDrop"
                @click="triggerAiFileInput"
                class="p-4 rounded-xl border-2 border-dashed transition cursor-pointer flex flex-col items-center justify-center text-center group"
                :class="isDragging ? 'border-indigo-500 bg-indigo-50/80 scale-[0.99]' : 'border-indigo-200/80 bg-white/70 hover:bg-white hover:border-indigo-400'"
              >
                <input
                  type="file"
                  ref="aiFileInputRef"
                  multiple
                  accept=".pdf,image/*"
                  class="hidden"
                  @change="handleAiFileSelect"
                />
                <div class="w-10 h-10 rounded-2xl bg-indigo-50 group-hover:bg-indigo-100 text-indigo-600 flex items-center justify-center mb-2 transition shadow-inner">
                  <i class="fa-solid fa-cloud-arrow-up text-lg group-hover:scale-110 transition-transform"></i>
                </div>
                <div class="text-xs font-bold text-slate-800">
                  点击选择或拖入车险保单 <span class="text-indigo-600 font-extrabold">(支持同时选多个 PDF/图片)</span>
                </div>
                <p class="text-[11px] text-slate-400 mt-1 max-w-md">
                  支持安盛、平安、人保、太保等全保司单据，AI 将自动归并商业险保费、交强险、车船税、单号及保障责任，并同步存为本期附件
                </p>
              </div>

              <!-- 解析中动效 -->
              <div v-else-if="aiParsing" class="py-6 px-4 bg-white/80 rounded-xl border border-indigo-200 text-center space-y-3">
                <div class="relative w-12 h-12 mx-auto flex items-center justify-center">
                  <div class="w-12 h-12 rounded-full border-3 border-indigo-200 border-t-indigo-600 animate-spin"></div>
                  <i class="fa-solid fa-brain text-indigo-600 text-sm absolute"></i>
                </div>
                <div>
                  <div class="font-bold text-indigo-950 text-xs">大模型正在深度解析保单合同...</div>
                  <p class="text-[11px] text-slate-400 mt-0.5">正在提取保司、起止日期、保费明细、单号与责任条款，请稍候</p>
                </div>
              </div>

              <!-- 识别错误提示条 -->
              <div v-if="aiParseError" class="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-start justify-between gap-2">
                <div class="flex items-start space-x-2">
                  <i class="fa-solid fa-circle-exclamation mt-0.5 text-rose-500"></i>
                  <span>{{ aiParseError }}</span>
                </div>
                <button type="button" @click="aiParseError = ''" class="text-rose-400 hover:text-rose-600">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>

              <!-- 识别结果确认面板 (对比与采纳) -->
              <div v-if="aiParsedResult" class="bg-white rounded-xl border border-indigo-200 p-3.5 space-y-3 shadow-xs animate-in">
                <div class="flex items-center justify-between pb-2 border-b border-slate-100">
                  <span class="font-bold text-emerald-700 flex items-center space-x-1.5 text-xs">
                    <i class="fa-solid fa-circle-check text-emerald-500"></i>
                    <span>保单信息识别成功！请核对以下提取明细：</span>
                  </span>
                  <span class="text-[10px] text-slate-400">已自动归档 {{ aiParsedResult.fileCount || 1 }} 份电子原件</span>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  <div class="p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <span class="text-slate-400 block text-[10px]">承保公司</span>
                    <strong class="text-slate-800">{{ aiParsedResult.policyData?.company || '未识别' }}</strong>
                  </div>
                  <div class="p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <span class="text-slate-400 block text-[10px]">归档年度 / 起止日期</span>
                    <strong class="text-slate-800 font-mono">{{ aiParsedResult.policyData?.year }}年</strong>
                    <span class="text-[10px] text-slate-400 block truncate">{{ aiParsedResult.policyData?.startDate }} 起</span>
                  </div>
                  <div class="p-2 rounded-lg bg-indigo-50/60 border border-indigo-100">
                    <span class="text-indigo-600 block text-[10px] font-semibold">识别总保费</span>
                    <strong class="text-indigo-950 font-bold font-mono text-xs">¥{{ formatMoney(aiParsedResult.policyData?.totalPremium) }}</strong>
                  </div>
                  <div class="p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <span class="text-slate-400 block text-[10px]">费用分项提取</span>
                    <span class="text-slate-700 font-mono text-[10px] block">商: ¥{{ aiParsedResult.policyData?.commercialPremium || 0 }} | 交: ¥{{ aiParsedResult.policyData?.compulsoryPremium || 0 }}</span>
                    <span class="text-slate-500 font-mono text-[10px] block">税: ¥{{ aiParsedResult.policyData?.tax || 0 }}</span>
                  </div>
                </div>

                <!-- 责任与单号概览条 -->
                <div class="p-2 rounded-lg bg-slate-50 text-[11px] text-slate-600 flex flex-wrap gap-x-3 gap-y-1">
                  <span v-if="aiParsedResult.policyData?.plateNo" class="font-medium">
                    车牌: <strong class="text-slate-900 font-mono">{{ aiParsedResult.policyData?.plateNo }}</strong>
                  </span>
                  <span v-if="aiParsedResult.policyData?.commercialPolicyNo">
                    商业单号: <strong class="text-slate-800 font-mono text-[10px]">{{ aiParsedResult.policyData?.commercialPolicyNo }}</strong>
                  </span>
                  <span v-if="aiParsedResult.policyData?.compulsoryPolicyNo">
                    交强单号: <strong class="text-slate-800 font-mono text-[10px]">{{ aiParsedResult.policyData?.compulsoryPolicyNo }}</strong>
                  </span>
                  <span v-if="aiParsedResult.policyData?.thirdPartyAmount" class="text-sky-700 font-semibold">
                    三者: {{ aiParsedResult.policyData?.thirdPartyAmount }}
                  </span>
                  <span v-if="aiParsedResult.policyData?.hasDamage" class="text-emerald-700 font-semibold">
                    已含车损
                  </span>
                  <span v-if="aiParsedResult.policyData?.extra" class="text-purple-700 truncate max-w-full">
                    特约: {{ aiParsedResult.policyData?.extra }}
                  </span>
                </div>

                <!-- 采纳与重试操作 -->
                <div class="flex items-center justify-end space-x-2 pt-1">
                  <button
                    type="button"
                    @click="dismissAiResult"
                    class="px-3 py-1.5 rounded-lg text-slate-500 hover:bg-slate-100 text-xs transition cursor-pointer"
                  >
                    放弃此识别
                  </button>
                  <button
                    type="button"
                    @click="applyAiResult"
                    class="inline-flex items-center space-x-1.5 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold shadow-sm transition cursor-pointer"
                  >
                    <i class="fa-solid fa-check"></i>
                    <span>一键采纳填入表单</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 1. 基础信息卡片 (爱车、归档年度、保司、保险期间) -->
          <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 space-y-3.5">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-800 flex items-center space-x-1.5 text-xs">
                <i class="fa-solid fa-car text-sky-600"></i>
                <span>1. 爱车与保险期间基础信息</span>
              </span>
              <span v-if="selectedVehicle" class="text-[11px] text-slate-500 font-medium">
                {{ (selectedVehicle.isCompany || selectedVehicle.companyName) ? '公户单位：' : '车主：' }}
                <span class="text-slate-800 font-semibold">{{ selectedVehicle.companyName || selectedVehicle.owner }}</span> · {{ selectedVehicle.model }}
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-12 gap-3">
              <!-- 关联爱车 -->
              <div class="sm:col-span-5">
                <label class="block text-slate-700 font-semibold mb-1">
                  关联爱车 <span class="text-rose-500">*</span>
                </label>
                <select
                  v-model="form.vehicleId"
                  @change="handleVehicleChange"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-bold text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                  :disabled="lockVehicle"
                >
                  <option value="" disabled>请选择关联爱车</option>
                  <option v-for="v in vehicles" :key="v.id" :value="v.id">
                    {{ v.plateNo }} ({{ (v.isCompany || v.companyName) ? (v.companyName || '公司车') : v.owner }} · {{ v.model }})
                  </option>
                </select>
              </div>

              <!-- 归档年度 -->
              <div class="sm:col-span-3">
                <label class="block text-slate-700 font-semibold mb-1">
                  归档年度 <span class="text-rose-500">*</span>
                </label>
                <div class="relative">
                  <input
                    type="number"
                    v-model.number="form.year"
                    @input="handleYearChange"
                    @change="handleYearChange"
                    placeholder="如：2026"
                    class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-bold font-mono text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-[10px] pointer-events-none">年</span>
                </div>
              </div>

              <!-- 承保保司 -->
              <div class="sm:col-span-4">
                <div class="flex justify-between items-center mb-1">
                  <label class="text-slate-700 font-semibold">承保保险公司</label>
                  <div class="flex gap-1">
                    <button
                      type="button"
                      v-for="c in ['平安', '人保', '太保']"
                      :key="c"
                      @click="form.company = c + '产险'"
                      class="px-1 py-0.2 rounded text-[9px] bg-slate-200/70 hover:bg-sky-100 hover:text-sky-800 text-slate-600 transition"
                    >
                      {{ c }}
                    </button>
                  </div>
                </div>
                <input
                  v-model="form.company"
                  placeholder="如：平安产险 / 人保财险"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-medium text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
            </div>

            <!-- 保险期间 (起期与止期联动) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div>
                <label class="block text-slate-700 font-semibold mb-1">
                  保险起期 (生效日) <span class="text-rose-500">*</span>
                </label>
                <input
                  type="date"
                  v-model="form.startDate"
                  @change="handleStartDateChange"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
              <div>
                <label class="block text-slate-700 font-semibold mb-1">
                  保险止期 (到期日) <span class="text-rose-500">*</span>
                </label>
                <input
                  type="date"
                  v-model="form.endDate"
                  class="w-full bg-white border border-slate-200 rounded-xl p-2.5 font-mono text-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
            </div>
          </div>

          <!-- 2. 费用构成与返点结算卡片 -->
          <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 space-y-3.5">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-800 flex items-center space-x-1.5 text-xs">
                <i class="fa-solid fa-coins text-amber-500"></i>
                <span>2. 保费构成与返现结算</span>
              </span>
              <div class="flex items-center space-x-2">
                <button
                  v-if="hasAnyPremiumValue"
                  type="button"
                  @click="clearPremiumFields"
                  class="text-[10px] text-slate-400 hover:text-rose-600 transition flex items-center space-x-1 cursor-pointer"
                  title="清空预填保费，全新手工录入"
                >
                  <i class="fa-regular fa-trash-can"></i>
                  <span>清空金额</span>
                </button>
                <span class="text-[10px] text-slate-400">支持只填总价，或分项自动汇总</span>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
              <!-- 最终归档总保费 (核心关键指标) -->
              <div class="sm:col-span-6 bg-white p-3.5 rounded-xl border-2 border-indigo-200 shadow-xs">
                <div class="flex justify-between items-center mb-1">
                  <label class="text-indigo-950 font-black text-xs flex items-center space-x-1">
                    <span>实际归档总保费</span>
                    <span class="text-rose-500">*</span>
                  </label>
                  <button
                    v-if="breakdownTotal > 0"
                    type="button"
                    @click="applyBreakdownTotal"
                    class="text-[10px] text-sky-600 hover:text-sky-800 font-medium cursor-pointer"
                  >
                    采用分项合计 (¥{{ formatMoney(breakdownTotal) }})
                  </button>
                </div>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 font-bold text-indigo-400 text-sm">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.totalPremium"
                    @input="handleTotalInput"
                    placeholder="输入总额或填写右侧明细"
                    class="w-full bg-indigo-50/30 border border-indigo-200 rounded-lg pl-7 pr-3 py-2 font-black font-mono text-indigo-950 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                  />
                </div>
              </div>

              <!-- 专员返现/抵扣红包 -->
              <div class="sm:col-span-6 bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
                <div class="flex justify-between items-center mb-1">
                  <label class="text-slate-700 font-bold text-xs flex items-center space-x-1">
                    <i class="fa-solid fa-gift text-emerald-600"></i>
                    <span>续保专员返现 / 补贴 (选填)</span>
                  </label>
                  <span v-if="form.cashback" class="text-[10px] text-emerald-700 font-semibold font-mono">
                    实付支出: ¥{{ formatMoney(netPremiumDisplay) }}
                  </span>
                </div>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 font-bold text-emerald-500 text-xs">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.cashback"
                    placeholder="输入返现金额，自动计算实付"
                    class="w-full bg-emerald-50/30 border border-emerald-200 rounded-lg pl-7 pr-3 py-2 font-bold font-mono text-emerald-950 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
                  />
                </div>
              </div>
            </div>

            <!-- 四项明细分项 -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
              <!-- 商业险 -->
              <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                <div class="text-slate-600 font-semibold text-[11px] mb-1">商业险保费</div>
                <div class="relative">
                  <span class="absolute left-2.5 top-1/2 -translate-y-1/2 font-bold text-slate-400 text-xs">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.commercialPremium"
                    @input="handleBreakdownChange"
                    placeholder="如：2600"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-6 pr-2 py-1.5 font-bold font-mono text-slate-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  />
                </div>
              </div>

              <!-- 交强险 -->
              <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                <div class="text-slate-600 font-semibold text-[11px] mb-1">交强险保费</div>
                <div class="relative">
                  <span class="absolute left-2.5 top-1/2 -translate-y-1/2 font-bold text-slate-400 text-xs">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.compulsoryPremium"
                    @input="handleBreakdownChange"
                    placeholder="如：665 / 950"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-6 pr-2 py-1.5 font-bold font-mono text-slate-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  />
                </div>
              </div>

              <!-- 车船税 -->
              <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-slate-600 font-semibold text-[11px]">车船税</span>
                  <span v-if="selectedVehicle?.plateType === 'green'" class="text-[9px] text-emerald-600 font-medium">新能源免税</span>
                </div>
                <div class="relative">
                  <span class="absolute left-2.5 top-1/2 -translate-y-1/2 font-bold text-slate-400 text-xs">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.tax"
                    @input="handleBreakdownChange"
                    placeholder="如：360 (电车0)"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-6 pr-2 py-1.5 font-bold font-mono text-slate-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  />
                </div>
              </div>

              <!-- 驾乘险 / 意外险保费 -->
              <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                <div class="flex justify-between items-center mb-1">
                  <label class="text-purple-900 font-bold text-[11px] flex items-center space-x-1">
                    <i class="fa-solid fa-person-shelter text-purple-600"></i>
                    <span>附带驾乘险</span>
                  </label>
                  <span class="text-[9px] text-purple-600 font-medium">选填</span>
                </div>
                <div class="relative">
                  <span class="absolute left-2.5 top-1/2 -translate-y-1/2 font-bold text-slate-400 text-xs">¥</span>
                  <input
                    type="number"
                    step="0.01"
                    v-model.number="form.accidentPremium"
                    @input="handleBreakdownChange"
                    placeholder="如：200"
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-6 pr-2 py-1.5 font-bold font-mono text-purple-950 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 3. 保障责任方案子组件 -->
          <VehiclePolicyPlanSection :form="form" />

          <!-- 4. 单号与电子保单凭证子组件 -->
          <VehiclePolicyAttachmentSection
            ref="attachmentSectionRef"
            :form="form"
            :selected-vehicle="selectedVehicle"
          />

          <!-- 5. 续保备注与专员返点 -->
          <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 space-y-2">
            <label class="block font-bold text-slate-800 text-xs">
              5. 本期续保备注 / 专员信息与返点礼包
            </label>
            <input
              v-model="form.remark"
              placeholder="如：返现500元加油卡已到账、专员王经理 13900000000、赠送2次全合成保养与洗车券"
              class="w-full bg-white border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
        </div>

        <!-- 弹窗底部操作与汇总栏 -->
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-200/70 flex flex-col sm:flex-row justify-between items-center gap-3 shrink-0">
          <div class="text-xs text-slate-600 flex items-center flex-wrap gap-1.5">
            <span>实际归档总保费：</span>
            <strong class="text-indigo-950 font-black text-base font-mono">
              ¥{{ formatMoney(currentTotalDisplay) }}
            </strong>
            <span class="text-[11px] text-slate-400 ml-1">
              ({{ summaryCompositionText }})
            </span>
            <span
              v-if="form.cashback && Number(form.cashback) > 0"
              class="inline-flex items-center space-x-1 px-2 py-0.5 bg-emerald-100/90 text-emerald-800 rounded-full text-[10px] font-bold ml-1.5"
            >
              <i class="fa-solid fa-gift text-emerald-600"></i>
              <span>返现 ¥{{ formatMoney(form.cashback) }} (实付支出 ¥{{ formatMoney(netPremiumDisplay) }})</span>
            </span>
          </div>

          <div class="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
            <button
              type="button"
              @click="$emit('update:show', false)"
              class="px-4 py-2 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-semibold transition cursor-pointer"
            >
              取消
            </button>
            <button
              type="button"
              @click="handleSave"
              class="px-6 py-2 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-200 transition cursor-pointer"
            >
              {{ isNew ? '确认录入并归档' : '保存保单修改' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { formatMoney } from '../utils/helpers.js';
import { AppApi } from '../api/index.js';
import VehiclePolicyPlanSection from './vehicle/VehiclePolicyPlanSection.vue';
import VehiclePolicyAttachmentSection from './vehicle/VehiclePolicyAttachmentSection.vue';

const props = defineProps({
  show: { type: Boolean, default: false },
  isNew: { type: Boolean, default: true },
  form: { type: Object, required: true },
  vehicles: { type: Array, default: () => [] },
  lockVehicle: { type: Boolean, default: false },
  aiSettings: { type: Object, default: () => ({}) }
});

const emit = defineEmits(['update:show', 'save', 'open-ai-settings']);
const attachmentSectionRef = ref(null);

const isUserEditedTotal = ref(false);

const selectedVehicle = computed(() => {
  return (props.vehicles || []).find(v => v.id === props.form.vehicleId) || null;
});

const titleText = computed(() => {
  if (!props.isNew) {
    return `编辑 ${props.form.year || ''} 年度车险保单`;
  }
  return '录入车险保单';
});

const subtitleText = computed(() => {
  if (props.isNew) {
    return '支持直接填写总保费，可选录入驾乘险及分项明细，自动计入家庭台账';
  }
  return '更新此期车险保单合同、保费明细与电子凭据附件';
});

const breakdownTotal = computed(() => {
  const c = Number(props.form.commercialPremium) || 0;
  const comp = Number(props.form.compulsoryPremium) || 0;
  const tax = Number(props.form.tax) || 0;
  const acc = Number(props.form.accidentPremium) || 0;
  return Math.round((c + comp + tax + acc) * 100) / 100;
});

const currentTotalDisplay = computed(() => {
  if (props.form.totalPremium !== '' && props.form.totalPremium !== null && props.form.totalPremium !== undefined && !isNaN(Number(props.form.totalPremium))) {
    return Number(props.form.totalPremium);
  }
  return breakdownTotal.value;
});

const summaryCompositionText = computed(() => {
  const parts = [];
  if (props.form.commercialPremium) parts.push(`商 ¥${formatMoney(props.form.commercialPremium)}`);
  if (props.form.compulsoryPremium) parts.push(`交 ¥${formatMoney(props.form.compulsoryPremium)}`);
  if (props.form.tax) parts.push(`税 ¥${formatMoney(props.form.tax)}`);
  if (props.form.accidentPremium) parts.push(`驾乘 ¥${formatMoney(props.form.accidentPremium)}`);

  if (parts.length > 0) {
    return parts.join(' + ');
  }
  return '仅总价';
});

const netPremiumDisplay = computed(() => {
  const total = currentTotalDisplay.value;
  const cb = Number(props.form.cashback) || 0;
  return Math.max(0, Math.round((total - cb) * 100) / 100);
});

function handleTotalInput() {
  isUserEditedTotal.value = true;
}

function handleBreakdownChange() {
  if (!isUserEditedTotal.value || !props.form.totalPremium) {
    props.form.totalPremium = breakdownTotal.value > 0 ? breakdownTotal.value : null;
  }
}

function applyBreakdownTotal() {
  props.form.totalPremium = breakdownTotal.value;
  isUserEditedTotal.value = false;
}

const hasAnyPremiumValue = computed(() => {
  return (
    (props.form.totalPremium !== null && props.form.totalPremium !== '' && props.form.totalPremium !== undefined) ||
    (props.form.commercialPremium !== null && props.form.commercialPremium !== '' && props.form.commercialPremium !== undefined) ||
    (props.form.compulsoryPremium !== null && props.form.compulsoryPremium !== '' && props.form.compulsoryPremium !== undefined) ||
    (props.form.accidentPremium !== null && props.form.accidentPremium !== '' && props.form.accidentPremium !== undefined) ||
    (props.form.cashback !== null && props.form.cashback !== '' && props.form.cashback !== undefined) ||
    (props.form.tax !== null && props.form.tax !== '' && props.form.tax !== undefined && selectedVehicle.value?.plateType !== 'green')
  );
});

function clearPremiumFields() {
  props.form.totalPremium = null;
  props.form.commercialPremium = null;
  props.form.compulsoryPremium = null;
  props.form.accidentPremium = null;
  props.form.cashback = null;
  if (selectedVehicle.value?.plateType !== 'green') {
    props.form.tax = null;
  }
  isUserEditedTotal.value = false;
}

function handleYearChange() {
  const y = Number(props.form.year);
  if (!y || isNaN(y) || y < 1900 || y > 2100) return;
  const yStr = String(Math.floor(y));
  if (yStr.length !== 4) return;

  // 联动保险起期年份与归档年度保持一致
  let newStart = '';
  if (props.form.startDate && typeof props.form.startDate === 'string' && props.form.startDate.includes('-')) {
    const parts = props.form.startDate.split('-');
    if (parts.length === 3) {
      let mm = parts[1];
      let dd = parts[2];
      // 闰年2月29日安全保护
      if (mm === '02' && dd === '29') {
        const isLeapYear = (y % 4 === 0 && y % 100 !== 0) || (y % 400 === 0);
        if (!isLeapYear) dd = '28';
      }
      newStart = `${yStr}-${mm}-${dd}`;
    }
  }

  if (!newStart) {
    const today = new Date();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    newStart = `${yStr}-${mm}-${dd}`;
  }

  props.form.startDate = newStart;
  handleStartDateChange();
}

function handleVehicleChange() {
  if (selectedVehicle.value?.plateType === 'green') {
    props.form.tax = 0;
  }
}

function handleStartDateChange() {
  if (!props.form.startDate) return;
  try {
    const s = new Date(props.form.startDate);
    if (!isNaN(s.getTime())) {
      s.setFullYear(s.getFullYear() + 1);
      s.setDate(s.getDate() - 1);
      props.form.endDate = s.toISOString().slice(0, 10);
    }
  } catch (_) {}
}

function handleSave() {
  if (!props.form.vehicleId) {
    alert('请选择要关联的爱车');
    return;
  }
  if (!props.form.year) {
    alert('请填写投保归档年度');
    return;
  }
  props.form.company = (props.form.company || '').trim();

  if ((props.form.totalPremium === '' || props.form.totalPremium === null || props.form.totalPremium === undefined) && breakdownTotal.value > 0) {
    props.form.totalPremium = breakdownTotal.value;
  }

  emit('save');
}

// ==================== AI 识单处理逻辑 ====================
const aiFileInputRef = ref(null);
const isDragging = ref(false);
const aiParsing = ref(false);
const aiParseError = ref('');
const aiParsedResult = ref(null);

function triggerAiFileInput() {
  if (aiParsing.value) return;
  aiFileInputRef.value?.click();
}

function handleAiDrop(e) {
  isDragging.value = false;
  if (aiParsing.value) return;
  const files = Array.from(e.dataTransfer?.files || []);
  if (files.length > 0) {
    parseFiles(files);
  }
}

function handleAiFileSelect(e) {
  const files = Array.from(e.target?.files || []);
  if (files.length > 0) {
    parseFiles(files);
  }
  if (e.target) e.target.value = '';
}

async function parseFiles(files) {
  for (const f of files) {
    if (f.size > 30 * 1024 * 1024) {
      alert(`文件 [${f.name}] 大小不能超过 30MB`);
      return;
    }
  }

  aiParsing.value = true;
  aiParseError.value = '';
  aiParsedResult.value = null;

  try {
    const plateHint = selectedVehicle.value?.plateNo || props.form.plateNo || '';
    const res = await AppApi.parseVehiclePolicy(files, plateHint);
    aiParsedResult.value = {
      policyData: res.policyData || {},
      attachments: res.attachments || [],
      fileCount: files.length
    };
  } catch (err) {
    console.error('[AI Parse Policy Error]', err);
    aiParseError.value = err.message || 'AI 保单识别失败，请检查服务配置或重试';
  } finally {
    aiParsing.value = false;
  }
}

function applyAiResult() {
  if (!aiParsedResult.value?.policyData) return;
  const pd = aiParsedResult.value.policyData;

  // 1. 匹配或自动选中爱车
  if (!props.lockVehicle && pd.plateNo) {
    const matched = (props.vehicles || []).find(v => v.plateNo === pd.plateNo || (v.vin && pd.vin && v.vin.includes(pd.vin)));
    if (matched) {
      props.form.vehicleId = matched.id;
    }
  }

  // 2. 基础信息
  if (pd.company) props.form.company = pd.company;
  if (pd.year) props.form.year = pd.year;
  if (pd.startDate) props.form.startDate = pd.startDate;
  if (pd.endDate) {
    props.form.endDate = pd.endDate;
  } else if (pd.startDate) {
    handleStartDateChange();
  }

  // 3. 保费构成
  if (pd.commercialPremium !== undefined) props.form.commercialPremium = pd.commercialPremium;
  if (pd.compulsoryPremium !== undefined) props.form.compulsoryPremium = pd.compulsoryPremium;
  if (pd.tax !== undefined) props.form.tax = pd.tax;
  if (pd.accidentPremium !== undefined) props.form.accidentPremium = pd.accidentPremium;
  if (pd.totalPremium !== undefined && pd.totalPremium > 0) {
    props.form.totalPremium = pd.totalPremium;
    isUserEditedTotal.value = true;
  } else if (breakdownTotal.value > 0) {
    props.form.totalPremium = breakdownTotal.value;
  }

  // 4. 保单号
  if (pd.commercialPolicyNo) props.form.commercialPolicyNo = pd.commercialPolicyNo;
  if (pd.compulsoryPolicyNo) props.form.compulsoryPolicyNo = pd.compulsoryPolicyNo;
  if (pd.accidentPolicyNo) props.form.accidentPolicyNo = pd.accidentPolicyNo;

  // 5. 责任方案
  if (pd.hasDamage !== undefined) props.form.hasDamage = pd.hasDamage;
  if (pd.hasMedicalExcluded !== undefined) props.form.hasMedicalExcluded = pd.hasMedicalExcluded;
  if (pd.thirdPartyAmount) props.form.thirdPartyAmount = pd.thirdPartyAmount;
  if (pd.driverAmount) props.form.driverAmount = pd.driverAmount;
  if (pd.extra) props.form.extra = pd.extra;

  // 6. 附件合并挂载
  if (aiParsedResult.value.attachments && aiParsedResult.value.attachments.length > 0) {
    if (!props.form.attachments) props.form.attachments = [];
    aiParsedResult.value.attachments.forEach(att => {
      if (!props.form.attachments.some(existing => existing.storedName === att.storedName)) {
        props.form.attachments.push(att);
      }
    });
  }

  aiParsedResult.value = null;
  aiParseError.value = '';
}

function dismissAiResult() {
  aiParsedResult.value = null;
  aiParseError.value = '';
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    isUserEditedTotal.value = false;
    attachmentSectionRef.value?.cancelEditAttName();
    aiParsing.value = false;
    aiParseError.value = '';
    aiParsedResult.value = null;
  }
});
</script>
