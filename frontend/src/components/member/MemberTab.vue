<template>
  <div class="space-y-4">
    <!-- 1. 成员编辑/录入表单子组件 -->
    <MemberEditForm
      v-if="isEditingMember"
      :form="editingMemberForm"
      :is-new="editingMemberIsNew"
      @save="saveMemberForm"
      @cancel="cancelMemberEdit"
    />

    <!-- 2. 成员卡片列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
      <div
        v-for="(member, idx) in memberList"
        :key="member.id || member.name"
        class="p-4 rounded-2xl border transition bg-white hover:shadow-md flex flex-col justify-between"
        :class="selectedCardName === member.name ? 'border-sky-400 ring-2 ring-sky-100' : 'border-slate-200/80'"
      >
        <div>
          <!-- 顶部信息：姓名、关系徽章、性别、操作按钮 -->
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-2.5">
              <div
                class="w-10 h-10 rounded-2xl flex items-center justify-center text-white font-bold text-sm shadow-sm"
                :class="getAvatarBgClass(member)"
              >
                {{ member.name ? member.name.slice(0, 1) : '人' }}
              </div>
              <div>
                <div class="flex items-center space-x-2">
                  <h4 class="text-sm font-bold text-slate-900">{{ member.name }}</h4>
                  <span
                    class="px-2 py-0.5 rounded-md text-[10px] font-semibold border"
                    :class="getRelationBadgeClass(member.relation)"
                  >
                    {{ member.relation || '家庭成员' }}
                  </span>
                  <span
                    v-if="member.gender"
                    class="text-[11px]"
                    :class="member.gender === '女' ? 'text-rose-500' : 'text-sky-500'"
                    :title="member.gender"
                  >
                    <i class="fa-solid" :class="member.gender === '女' ? 'fa-venus' : 'fa-mars'"></i>
                  </span>
                </div>
                <div class="text-[11px] text-slate-400 mt-0.5 flex items-center space-x-2">
                  <span v-if="member.birthDate">
                    {{ calculateAge(member.birthDate) }} 岁 ({{ member.birthDate }})
                  </span>
                  <span v-else>生日未录入</span>
                  <span>·</span>
                  <span v-if="member.hasSocialSecurity" class="text-emerald-600 font-medium">
                    <i class="fa-solid fa-check-circle text-[10px] mr-0.5"></i>已参保
                  </span>
                  <span v-else class="text-slate-400">无社保</span>
                </div>
              </div>
            </div>

            <!-- 右侧排序与编辑操作 -->
            <div class="flex items-center space-x-1">
              <!-- 上移 -->
              <button
                @click="moveMember(idx, -1)"
                :disabled="idx === 0"
                title="上移此成员"
                class="p-1.5 text-slate-400 hover:text-slate-700 disabled:opacity-20 rounded-lg hover:bg-slate-100 transition"
              >
                <i class="fa-solid fa-arrow-up text-xs"></i>
              </button>
              <!-- 下移 -->
              <button
                @click="moveMember(idx, 1)"
                :disabled="idx === memberList.length - 1"
                title="下移此成员"
                class="p-1.5 text-slate-400 hover:text-slate-700 disabled:opacity-20 rounded-lg hover:bg-slate-100 transition"
              >
                <i class="fa-solid fa-arrow-down text-xs"></i>
              </button>
              <!-- 编辑 -->
              <button
                @click="startEditMember(member)"
                title="编辑成员档案"
                class="p-1.5 text-sky-600 hover:text-sky-800 rounded-lg hover:bg-sky-50 transition"
              >
                <i class="fa-regular fa-pen-to-square text-xs"></i>
              </button>
              <!-- 删除 -->
              <button
                @click="confirmDeleteMember(member)"
                title="删除成员"
                class="p-1.5 text-rose-500 hover:text-rose-700 rounded-lg hover:bg-rose-50 transition"
              >
                <i class="fa-regular fa-trash-can text-xs"></i>
              </button>
            </div>
          </div>

          <!-- 名下关联资产指标卡片 -->
          <div class="grid grid-cols-3 gap-2 mt-3.5 pt-3 border-t border-slate-100 text-center">
            <div class="bg-slate-50/80 rounded-xl p-2 border border-slate-100">
              <div class="text-[10px] text-slate-400">在保人身险</div>
              <div class="text-xs font-bold text-slate-800 mt-0.5">
                {{ countActivePolicies(member.name) }} 份
              </div>
            </div>
            <div class="bg-slate-50/80 rounded-xl p-2 border border-slate-100">
              <div class="text-[10px] text-slate-400">名下车辆</div>
              <div class="text-xs font-bold text-slate-800 mt-0.5">
                {{ countVehicles(member.name) }} 辆
              </div>
            </div>
            <div class="bg-slate-50/80 rounded-xl p-2 border border-slate-100">
              <div class="text-[10px] text-slate-400">年度商业保费</div>
              <div class="text-xs font-bold text-sky-700 mt-0.5">
                ¥{{ formatMoney(getMemberAnnualPremium(member.name)) }}
              </div>
            </div>
          </div>

          <!-- 辅助档案信息条目 -->
          <div v-if="member.phone || member.remark || member.socialSecurityCity" class="mt-2.5 text-[11px] text-slate-500 space-y-1">
            <div v-if="member.phone" class="flex items-center space-x-1.5">
              <i class="fa-solid fa-phone text-slate-400 text-[10px]"></i>
              <span>{{ member.phone }}</span>
            </div>
            <div v-if="member.socialSecurityCity" class="flex items-center space-x-1.5">
              <i class="fa-solid fa-city text-slate-400 text-[10px]"></i>
              <span>医保地：{{ member.socialSecurityCity }}</span>
            </div>
            <div v-if="member.remark" class="text-slate-400 text-[10px] truncate" :title="member.remark">
              <i class="fa-regular fa-comment-dots text-slate-300 mr-1"></i>{{ member.remark }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 暂无成员提示 -->
    <div v-if="memberList.length === 0" class="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
      <div class="w-12 h-12 rounded-full bg-sky-100 text-sky-600 flex items-center justify-center mx-auto mb-2">
        <i class="fa-solid fa-users text-lg"></i>
      </div>
      <p class="text-sm font-bold text-slate-700">暂无家庭成员档案</p>
      <p class="text-xs text-slate-400 mt-1">点击上方“添加新成员”录入您的第一位家庭保障成员</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { formatMoney, deepClone } from '../../utils/helpers.js';
import MemberEditForm from './MemberEditForm.vue';

const props = defineProps({
  members: { type: Array, default: () => [] },
  familyMembers: { type: Array, default: () => [] },
  policies: { type: Array, default: () => [] },
  vehicles: { type: Array, default: () => [] },
  memberSummary: { type: Object, default: () => ({}) }
});

const emit = defineEmits([
  'update-members',
  'cascade-rename',
  'toast'
]);

const memberList = ref([]);
const isEditingMember = ref(false);
const editingMemberIsNew = ref(false);
const editingMemberForm = ref({});
const selectedCardName = ref('');

// 监听并同步初始数据
watch(
  () => [props.members, props.familyMembers],
  () => {
    initMemberList();
  },
  { immediate: true, deep: true }
);

function initMemberList() {
  const existingProfiles = (props.familyMembers && props.familyMembers.length > 0)
    ? deepClone(props.familyMembers)
    : [];

  const profileMap = new Map();
  existingProfiles.forEach(p => {
    if (p.name) profileMap.set(p.name, p);
  });

  const merged = [];
  (props.members || []).forEach((name, idx) => {
    if (profileMap.has(name)) {
      merged.push(profileMap.get(name));
      profileMap.delete(name);
    } else {
      merged.push({
        id: 'm_' + Date.now() + '_' + idx,
        name: name,
        relation: idx === 0 ? '本人' : '家庭成员',
        gender: idx === 0 ? '男' : '女',
        birthDate: '',
        phone: '',
        hasSocialSecurity: true,
        socialSecurityCity: '',
        remark: ''
      });
    }
  });

  profileMap.forEach(p => {
    merged.push(p);
  });

  memberList.value = merged;
}

function calculateAge(birthDate) {
  if (!birthDate) return 0;
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age >= 0 ? age : 0;
}

function countActivePolicies(name) {
  if (!name) return 0;
  return (props.policies || []).filter(p => {
    if (p.status !== 'active') return false;
    if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
      return p.insuredMembers.includes(name);
    }
    return p.member === name;
  }).length;
}

function countVehicles(name) {
  if (!name) return 0;
  return (props.vehicles || []).filter(v => v.owner === name || v.driver === name).length;
}

function getMemberAnnualPremium(name) {
  if (!name) return 0;
  if (props.memberSummary && props.memberSummary[name] !== undefined) {
    return props.memberSummary[name];
  }
  return (props.policies || []).filter(p => p && p.status === 'active').reduce((sum, p) => {
    if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
      if (p.premiumSplitMode === 'equal') {
        if (p.insuredMembers.includes(name)) {
          return sum + ((Number(p.premium) || 0) / p.insuredMembers.length);
        }
        return sum;
      }
      return p.member === name ? sum + (Number(p.premium) || 0) : sum;
    }
    return p.member === name ? sum + (Number(p.premium) || 0) : sum;
  }, 0);
}

function getAvatarBgClass(member) {
  const rel = member.relation || '';
  if (rel.includes('本人')) return 'bg-gradient-to-tr from-sky-500 to-blue-600';
  if (rel.includes('配偶') || rel.includes('妻') || rel.includes('夫')) return 'bg-gradient-to-tr from-purple-500 to-pink-500';
  if (rel.includes('儿') || rel.includes('女') || rel.includes('子')) return 'bg-gradient-to-tr from-emerald-500 to-teal-600';
  if (rel.includes('父') || rel.includes('母') || rel.includes('长辈')) return 'bg-gradient-to-tr from-amber-500 to-orange-600';
  return 'bg-gradient-to-tr from-slate-500 to-slate-700';
}

function getRelationBadgeClass(rel) {
  if (!rel) return 'bg-slate-100 text-slate-600 border-slate-200';
  if (rel.includes('本人')) return 'bg-sky-50 text-sky-700 border-sky-200';
  if (rel.includes('配偶') || rel.includes('妻') || rel.includes('夫')) return 'bg-purple-50 text-purple-700 border-purple-200';
  if (rel.includes('儿') || rel.includes('女') || rel.includes('子')) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (rel.includes('父') || rel.includes('母') || rel.includes('长辈')) return 'bg-amber-50 text-amber-700 border-amber-200';
  return 'bg-slate-50 text-slate-600 border-slate-200';
}

function openAddMemberForm() {
  editingMemberIsNew.value = true;
  editingMemberForm.value = {
    id: 'm_' + Date.now(),
    name: '',
    relation: memberList.value.length === 0 ? '本人' : '家庭成员',
    gender: '男',
    birthDate: '',
    phone: '',
    hasSocialSecurity: true,
    socialSecurityCity: '',
    remark: ''
  };
  isEditingMember.value = true;
}

function startEditMember(member) {
  editingMemberIsNew.value = false;
  editingMemberForm.value = deepClone(member);
  isEditingMember.value = true;
}

function cancelMemberEdit() {
  isEditingMember.value = false;
  editingMemberForm.value = {};
}

function saveMemberForm() {
  const f = editingMemberForm.value;
  if (!f.name || !f.name.trim()) {
    alert('请填写成员姓名 / 称呼');
    return;
  }
  const targetName = f.name.trim();

  if (editingMemberIsNew.value) {
    if (memberList.value.some(m => m.name === targetName)) {
      alert(`家庭成员【${targetName}】已存在，请使用不同姓名或加上称谓后缀区分`);
      return;
    }
    f.name = targetName;
    memberList.value.push(deepClone(f));
    notifyMemberUpdate();
    isEditingMember.value = false;
  } else {
    const idx = memberList.value.findIndex(m => m.id === f.id);
    if (idx !== -1) {
      const oldName = memberList.value[idx].name;
      if (oldName !== targetName && memberList.value.some((m, i) => i !== idx && m.name === targetName)) {
        alert(`已存在名为【${targetName}】的成员，请核对`);
        return;
      }

      if (oldName !== targetName) {
        const polCount = (props.policies || []).filter(p =>
          p.member === oldName ||
          p.applicant === oldName ||
          (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.includes(oldName))
        ).length;
        const vehCount = (props.vehicles || []).filter(v => v.owner === oldName || v.driver === oldName).length;

        if (polCount > 0 || vehCount > 0) {
          const confirmCascade = confirm(
            `检测到成员姓名从【${oldName}】变更为【${targetName}】。\n\n系统共有 ${polCount} 笔关联保单和 ${vehCount} 辆关联车辆归属于原姓名。\n\n是否同步将这些保单与车辆上的姓名更新为【${targetName}】？`
          );
          if (confirmCascade) {
            emit('cascade-rename', { oldName, newName: targetName });
          }
        }
      }

      f.name = targetName;
      memberList.value[idx] = deepClone(f);
      notifyMemberUpdate();
      isEditingMember.value = false;
    }
  }
}

function moveMember(idx, offset) {
  const targetIdx = idx + offset;
  if (targetIdx < 0 || targetIdx >= memberList.value.length) return;
  const temp = memberList.value[idx];
  memberList.value[idx] = memberList.value[targetIdx];
  memberList.value[targetIdx] = temp;
  notifyMemberUpdate();
}

function confirmDeleteMember(member) {
  const name = member.name;
  const activePolCount = (props.policies || []).filter(p =>
    p.member === name ||
    (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.includes(name))
  ).length;
  const vehCount = (props.vehicles || []).filter(v => v.owner === name).length;

  if (activePolCount > 0 || vehCount > 0) {
    alert(
      `无法直接删除成员【${name}】！\n\n该成员名下仍有 ${activePolCount} 笔商业保单与 ${vehCount} 辆车辆。\n为保障数据完整性，请先在保单管理或爱车专区中将名下保单/车辆转移给其他成员或删除，再执行成员移除。`
    );
    return;
  }

  if (confirm(`确认删除家庭成员【${name}】吗？删除后该成员将从所有筛选列表中移除。`)) {
    memberList.value = memberList.value.filter(m => m.name !== name && m.id !== member.id);
    notifyMemberUpdate();
  }
}

function notifyMemberUpdate() {
  const names = memberList.value.map(m => m.name).filter(Boolean);
  emit('update-members', {
    familyMembers: deepClone(memberList.value),
    members: names
  });
}

// 暴露给外层 Modal 调用的方法与状态
defineExpose({
  openAddMemberForm,
  isEditingMember,
  notifyMemberUpdate,
  memberCount: () => memberList.value.length
});
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.2s ease-out forwards;
}
</style>
