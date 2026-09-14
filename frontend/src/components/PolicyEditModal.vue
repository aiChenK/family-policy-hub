<template>
  <div v-if="show" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-2xl w-full shadow-2xl overflow-hidden border border-slate-100 max-h-[92vh] flex flex-col">
      <!-- 弹窗标题栏 -->
      <div class="p-5 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
        <div>
          <h3 class="text-base font-bold text-slate-900">{{ isNew ? '添加新保单' : '编辑保单信息' }}</h3>
          <p class="text-xs text-slate-400 mt-0.5">录入基础保障、合同信息与电子保单凭证，系统将自动推算缴费排期</p>
        </div>
        <button @click="$emit('update:show', false)" class="text-slate-400 hover:text-slate-600">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- 表单主体 -->
      <div class="p-6 overflow-y-auto space-y-5 text-xs custom-scrollbar flex-1">
        <!-- 1. 合同标识与当事人信息 -->
        <div class="space-y-3">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <i class="fa-solid fa-file-contract text-sky-600"></i>
            <span>1. 合同基本信息与当事人</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="md:col-span-2">
              <label class="block text-slate-600 font-medium mb-1">产品名称 *</label>
              <input v-model="formData.name" placeholder="如：国寿福终身寿险（至尊版）" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-medium" />
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">承保保险公司 *</label>
              <input v-model="formData.company" placeholder="如：人寿、人保、平安、大都会" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-600 font-medium mb-1">保单合同号 (用于查单/理赔)</label>
              <input v-model="formData.policyNo" placeholder="如：P20230325000188" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-mono" />
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">险种分类 *</label>
              <input v-model="formData.type" placeholder="如：重疾险+寿险、意外险、医疗消费险" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5" />
            </div>
          </div>

          <!-- 承保形式切换 (单人专属单 vs 家庭多人单) -->
          <div class="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2.5">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <i class="fa-solid fa-users text-sky-600 text-sm"></i>
                <div>
                  <span class="font-bold text-slate-800 text-xs">承保形式</span>
                  <span class="text-[11px] text-slate-400 ml-1.5">家庭意外险、全家共享医疗险等请选家庭多人单</span>
                </div>
              </div>
              <div class="inline-flex bg-slate-200/80 p-0.5 rounded-lg text-xs font-medium">
                <button
                  type="button"
                  @click="toggleFamilyPolicy(false)"
                  :class="!formData.isFamilyPolicy ? 'bg-white shadow-xs text-sky-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
                  class="px-2.5 py-1 rounded-md transition"
                >
                  个人专属单
                </button>
                <button
                  type="button"
                  @click="toggleFamilyPolicy(true)"
                  :class="formData.isFamilyPolicy ? 'bg-white shadow-xs text-purple-700 font-bold' : 'text-slate-500 hover:text-slate-800'"
                  class="px-2.5 py-1 rounded-md transition flex items-center space-x-1"
                >
                  <i class="fa-solid fa-people-roof text-xs"></i>
                  <span>家庭多人单</span>
                </button>
              </div>
            </div>

            <!-- 个人专属单：单选被保人 -->
            <div v-if="!formData.isFamilyPolicy">
              <label class="block text-slate-600 font-medium mb-1">被保人家属 *</label>
              <select v-model="formData.member" class="w-full bg-white border border-slate-200 rounded-lg p-2.5">
                <option v-for="m in members" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- 家庭多人单：复选参保家属标签与分摊规则 -->
            <div v-else class="p-3 bg-purple-50/60 rounded-xl border border-purple-200/80 space-y-2.5">
              <div class="flex items-center justify-between">
                <label class="font-bold text-purple-900 flex items-center space-x-1.5">
                  <i class="fa-solid fa-user-check text-purple-600"></i>
                  <span>勾选参保家属 (支持多选) *</span>
                </label>
                <div class="flex space-x-2 text-[10px]">
                  <button type="button" @click="selectAllMembers" class="text-purple-600 hover:text-purple-800 font-medium underline">全选</button>
                  <button type="button" @click="clearAllMembers" class="text-slate-400 hover:text-slate-600">清空</button>
                </div>
              </div>

              <!-- 成员多选标签列表 -->
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  v-for="m in members"
                  :key="m"
                  @click="toggleMemberSelection(m)"
                  :class="(formData.insuredMembers || []).includes(m) ? 'bg-purple-600 text-white font-bold shadow-xs' : 'bg-white text-slate-600 border border-slate-200 hover:border-purple-300'"
                  class="px-2.5 py-1.5 rounded-lg text-xs transition flex items-center space-x-1.5"
                >
                  <i class="fa-solid" :class="(formData.insuredMembers || []).includes(m) ? 'fa-check text-[10px]' : 'fa-plus text-[10px] text-slate-400'"></i>
                  <span>{{ m }}</span>
                </button>
              </div>
              <p v-if="!formData.insuredMembers || formData.insuredMembers.length === 0" class="text-rose-500 text-[11px] font-medium">
                请至少勾选一位家庭参保成员
              </p>

              <!-- 主被保人与保费分摊模式 -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-2 border-t border-purple-100">
                <div>
                  <label class="block text-slate-700 font-medium mb-1">主被保人 (第一被保人)</label>
                  <select v-model="formData.member" class="w-full bg-white border border-purple-200 rounded-lg p-2 text-xs">
                    <option v-for="m in (formData.insuredMembers && formData.insuredMembers.length > 0 ? formData.insuredMembers : members)" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-slate-700 font-medium mb-1">各成员保费预算分摊规则</label>
                  <select v-model="formData.premiumSplitMode" class="w-full bg-white border border-purple-200 rounded-lg p-2 text-xs">
                    <option value="payer">全部计入主被保人/投保人</option>
                    <option value="equal">由参保家属平均分摊 (按人头分摊)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-50/60 p-3 rounded-xl border border-slate-100">
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-slate-600 font-medium">投保人 (涉及保单豁免)</label>
                <button type="button" @click="formData.applicant = formData.member" class="text-[10px] text-sky-600 hover:text-sky-800">同被保人</button>
              </div>
              <div class="flex space-x-1.5">
                <select v-model="formData.applicant" class="w-full bg-white border border-slate-200 rounded-lg p-2">
                  <option value="">请选择或输入投保人</option>
                  <option v-for="m in members" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">身故受益人</label>
              <input v-model="formData.beneficiary" placeholder="默认：法定受益人 或 指定成员" class="w-full bg-white border border-slate-200 rounded-lg p-2" />
            </div>
          </div>
        </div>

        <!-- 2. 保障额度与缴费排期 -->
        <div class="space-y-3 pt-2 border-t border-slate-100">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <i class="fa-solid fa-calculator text-sky-600"></i>
            <span>2. 保额与缴费排期</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label class="block text-slate-600 font-medium mb-1">保额/计划 *</label>
              <input v-model="formData.amount" placeholder="如：50万 / 300万 / 计划一" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-medium" />
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">应缴保费 (元) *</label>
              <input type="number" step="0.01" v-model.number="formData.premium" placeholder="如：6942.43" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-bold text-slate-900" />
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">缴费方式</label>
              <select v-model="formData.paymentFrequency" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-medium">
                <option value="年缴">年缴 (每年一次)</option>
                <option value="月缴">月缴 (按月扣费)</option>
                <option value="趸交">趸交 (一次性缴清)</option>
                <option value="季缴">季缴</option>
              </select>
            </div>
          </div>

          <!-- 日期行 1: 保障起始与保障截止 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 bg-sky-50/40 rounded-xl border border-sky-100/70">
            <div>
              <label class="block text-slate-700 font-semibold mb-1 flex items-center space-x-1">
                <i class="fa-regular fa-calendar-plus text-sky-600"></i>
                <span>保障起始日期</span>
              </label>
              <input type="date" v-model="formData.startDate" @change="onStartDateChange" class="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono text-xs" />
              <p class="text-[10px] text-slate-400 mt-1">选择后将自动提取扣费月日</p>
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1 flex items-center space-x-1">
                <i class="fa-regular fa-calendar-check text-sky-600"></i>
                <span>保障截止 / 期限</span>
              </label>
              <div class="flex space-x-2">
                <input v-model="formData.endDate" placeholder="终身 或 YYYY-MM-DD" class="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono text-xs" />
                <button type="button" @click="formData.endDate = '终身'; formData.coveragePeriod = '终身'" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-[11px] whitespace-nowrap text-slate-600">终身</button>
              </div>
              <p class="text-[10px] text-slate-400 mt-1">填写“终身”或具体的到期日期</p>
            </div>
          </div>

          <!-- 日期行 2: 缴费年数与每年缴费日 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80">
            <div>
              <label class="block text-slate-700 font-semibold mb-1 flex items-center space-x-1">
                <i class="fa-solid fa-hourglass-half text-sky-600"></i>
                <span>缴费年数 (年)</span>
              </label>
              <div class="flex items-center space-x-1">
                <input type="number" min="1" max="50" v-model.number="formData.paymentYears" class="w-16 bg-white border border-slate-200 rounded-lg p-2 font-mono text-xs text-center" />
                <div class="flex space-x-1 text-[10px]">
                  <button type="button" @click="formData.paymentYears = 20" class="px-1.5 py-1 rounded bg-white border border-slate-200 hover:border-sky-400 text-slate-600">20年</button>
                  <button type="button" @click="formData.paymentYears = 10" class="px-1.5 py-1 rounded bg-white border border-slate-200 hover:border-sky-400 text-slate-600">10年</button>
                  <button type="button" @click="formData.paymentYears = 1" class="px-1.5 py-1 rounded bg-white border border-slate-200 hover:border-sky-400 text-slate-600">1年</button>
                </div>
              </div>
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1 flex items-center space-x-1">
                <i class="fa-regular fa-bell text-sky-600"></i>
                <span>每年缴费月日 (MM-DD)</span>
              </label>
              <input v-model="formData.paymentMonthDay" placeholder="如：03-29" class="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono text-xs text-center" />
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1 flex items-center space-x-1">
                <i class="fa-regular fa-credit-card text-sky-600"></i>
                <span>自动扣费卡/渠道</span>
              </label>
              <input v-model="formData.paymentAccount" placeholder="如：招行 6828、支付宝" class="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs" />
            </div>
          </div>
        </div>

        <!-- 3. 核保特别约定与责任说明 -->
        <div class="space-y-3 pt-2 border-t border-slate-100">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <i class="fa-solid fa-shield-halved text-amber-600"></i>
            <span>3. 核保结论、特别约定与责任</span>
          </div>

          <!-- 除外责任高亮 -->
          <div class="p-3 bg-amber-50/60 rounded-xl border border-amber-200/60">
            <label class="block text-amber-900 font-semibold mb-1 flex items-center space-x-1">
              <i class="fa-solid fa-triangle-exclamation text-amber-600"></i>
              <span>核保特别约定 / 除外责任 (就医理赔关键备忘)</span>
            </label>
            <input v-model="formData.exclusions" placeholder="如：甲状腺结节除外、加费20%、标准体承保等（理赔醒目提醒）" class="w-full bg-white border border-amber-200 rounded-lg p-2 text-xs text-amber-900 placeholder-amber-400/80 font-medium" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-600 font-medium mb-1">等待期与宽限期</label>
              <div class="grid grid-cols-2 gap-2">
                <input v-model="formData.waitingPeriod" placeholder="等待期(如90天)" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs" />
                <input v-model="formData.gracePeriod" placeholder="宽限期(如60天)" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs" />
              </div>
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">投保渠道 / 代理人联系方式</label>
              <input v-model="formData.salesChannel" placeholder="如：蚂蚁保 / 经纪人张经理 13800000000" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs" />
            </div>
          </div>

          <!-- 责任说明 -->
          <div>
            <label class="block text-slate-600 font-medium mb-1">保障责任 / 免赔额及赔付说明</label>
            <textarea v-model="formData.description" rows="2" placeholder="如：重疾100种60万\n一般医疗0免赔\n意外身故50万" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5"></textarea>
          </div>

          <!-- 附加险与拆解 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-600 font-medium mb-1">保费分项拆解 (选填)</label>
              <textarea v-model="formData.premiumDetail" rows="2" placeholder="如：主险4860元\n附加医疗1860元" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5"></textarea>
            </div>
            <div>
              <label class="block text-slate-600 font-medium mb-1">附加险清单 / 备注说明</label>
              <textarea v-model="formData.extra" rows="2" placeholder="如：附加特药医疗、投保人重疾豁免" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5"></textarea>
            </div>
          </div>
        </div>

        <!-- 4. 电子保单与合同附件 -->
        <div class="space-y-3 pt-2 border-t border-slate-100">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <div class="flex items-center space-x-1.5">
              <i class="fa-solid fa-paperclip text-sky-600"></i>
              <span>4. 电子保单原件与凭证附件</span>
            </div>
            <label class="cursor-pointer inline-flex items-center space-x-1 px-2.5 py-1 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded-lg text-xs font-semibold border border-sky-200 transition">
              <i class="fa-solid" :class="uploading ? 'fa-spinner fa-spin' : 'fa-arrow-up-from-bracket'"></i>
              <span>{{ uploading ? '上传中...' : '上传 PDF/图片' }}</span>
              <input type="file" accept=".pdf,image/*" class="hidden" @change="handleFileUpload" :disabled="uploading" />
            </label>
          </div>

          <p v-if="uploadError" class="text-rose-600 text-xs">{{ uploadError }}</p>

          <!-- 附件列表展示 -->
          <div v-if="formData.attachments && formData.attachments.length > 0" class="space-y-2">
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
                  placeholder="请输入保单附件显示名称"
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
                <a :href="getAttachmentUrl(att.url)" target="_blank" class="text-sky-600 hover:text-sky-800 px-2 py-1 bg-white rounded border border-slate-200 text-[11px] font-medium" title="在线预览/下载">
                  <i class="fa-regular fa-eye mr-1"></i>预览
                </a>
                <button type="button" @click="removeAttachment(idx)" class="text-rose-500 hover:text-rose-700 p-1 rounded-lg hover:bg-rose-50 transition" title="移除附件">
                  <i class="fa-regular fa-trash-can"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 bg-slate-50/50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
            暂无电子保单附件，可上传 PDF 保单或手机拍照件
          </div>
        </div>

        <!-- 5. 保单在缴/停缴状态 -->
        <div class="pt-2 border-t border-slate-100">
          <label class="block text-slate-600 font-medium mb-1">保单状态</label>
          <div class="flex items-center space-x-5 pt-1">
            <label class="inline-flex items-center"><input type="radio" value="active" v-model="formData.status" class="text-sky-600" /><span class="ml-2 font-medium">正常在保扣费中</span></label>
            <label class="inline-flex items-center"><input type="radio" value="stopped" v-model="formData.status" class="text-rose-600" /><span class="ml-2 text-slate-500">已停保/已退保</span></label>
            
            <div v-if="formData.status === 'stopped'" class="inline-flex items-center space-x-1 ml-4 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-100">
              <span class="text-[11px] text-rose-700">停缴年份:</span>
              <input type="number" v-model.number="formData.stopYear" placeholder="如 2023" class="w-16 bg-white border border-rose-200 rounded px-1.5 py-0.5 text-xs text-center" />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="p-4 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
        <button v-if="!isNew" @click="$emit('delete', formData.id)" class="text-rose-600 hover:text-rose-800 text-xs font-medium">
          <i class="fa-regular fa-trash-can mr-1"></i>删除此保单
        </button>
        <div v-else></div>
        <div class="space-x-2">
          <button @click="$emit('update:show', false)" class="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-medium">取消</button>
          <button @click="$emit('save')" class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-medium">确认保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { AppApi, getAttachmentUrl } from '../api/index.js';

const props = defineProps({

  show: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false },
  formData: { type: Object, required: true },
  members: { type: Array, default: () => [] }
});

const emit = defineEmits(['update:show', 'save', 'delete']);

const uploading = ref(false);
const uploadError = ref('');

function toggleFamilyPolicy(isFamily) {
  props.formData.isFamilyPolicy = isFamily;
  if (isFamily) {
    if (!Array.isArray(props.formData.insuredMembers)) {
      props.formData.insuredMembers = [];
    }
    if (props.formData.member && !props.formData.insuredMembers.includes(props.formData.member)) {
      props.formData.insuredMembers.push(props.formData.member);
    }
    if (props.formData.insuredMembers.length === 0 && props.members && props.members.length > 0) {
      props.formData.insuredMembers = [props.members[0]];
    }
    if (!props.formData.premiumSplitMode) {
      props.formData.premiumSplitMode = 'payer';
    }
  } else {
    // 切换为个人单
    if (!props.formData.member && props.formData.insuredMembers?.length > 0) {
      props.formData.member = props.formData.insuredMembers[0];
    }
  }
}

function toggleMemberSelection(m) {
  if (!Array.isArray(props.formData.insuredMembers)) {
    props.formData.insuredMembers = [];
  }
  const idx = props.formData.insuredMembers.indexOf(m);
  if (idx > -1) {
    props.formData.insuredMembers.splice(idx, 1);
    if (props.formData.member === m) {
      props.formData.member = props.formData.insuredMembers[0] || '';
    }
  } else {
    props.formData.insuredMembers.push(m);
    if (!props.formData.member) {
      props.formData.member = m;
    }
  }
}

function selectAllMembers() {
  props.formData.insuredMembers = [...(props.members || [])];
  if (!props.formData.member && props.formData.insuredMembers.length > 0) {
    props.formData.member = props.formData.insuredMembers[0];
  }
}

function clearAllMembers() {
  props.formData.insuredMembers = [];
  props.formData.member = '';
}

function onStartDateChange() {
  if (props.formData.startDate && props.formData.startDate.length >= 10) {
    props.formData.paymentMonthDay = props.formData.startDate.slice(5);
  }
}

function formatSize(bytes) {
  if (!bytes) return '未知大小';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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
    // 人员保单按照被保人的名字创建文件夹
    const memberName = (props.formData.member || '').trim() || '其他';
    const att = await AppApi.uploadAttachment('personal', file, memberName);
    if (!props.formData.attachments) {
      props.formData.attachments = [];
    }
    props.formData.attachments.push(att);
  } catch (err) {
    console.error('[Upload]', err);
    uploadError.value = '上传失败，请检查网络或附件格式';
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
      await AppApi.deleteAttachment('personal', att.storedName);
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

