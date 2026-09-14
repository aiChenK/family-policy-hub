import { ref } from 'vue';
import { AppApi } from '../api/index.js';
import { deepClone, DEFAULT_PHONE_CONFIG } from '../utils/helpers.js';

/**
 * 计算家庭成员的年度在保保费预算（支持单人保单与家庭多人保单分摊模式）
 */
export function calcMemberSummary(members = [], policies = []) {
  const newSummary = {};
  (members || []).forEach(m => {
    let prem = 0;
    (policies || []).filter(p => p && p.status === 'active').forEach(p => {
      if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
        if (p.premiumSplitMode === 'equal') {
          // 均摊模式：该成员在被保人列表中则均摊保费
          if (p.insuredMembers.includes(m)) {
            prem += (Number(p.premium) || 0) / p.insuredMembers.length;
          }
        } else {
          // payer 模式：全额计入主被保人
          if (p.member === m) {
            prem += Number(p.premium) || 0;
          }
        }
      } else {
        // 普通单人保单
        if (p.member === m) {
          prem += Number(p.premium) || 0;
        }
      }
    });
    newSummary[m] = Math.round(prem * 100) / 100;
  });
  return newSummary;
}

export function createInitialData() {
  return {
    updatedAt: '',
    members: [],
    memberSummary: {},
    familyMembers: [],
    policies: [],
    vehicles: [],
    companies: [],
    paymentRecords: {
      updatedAt: '',
      confirmations: {},
      archiveRecords: []
    }
  };
}

// 模块级单例状态：保证组件 HMR 热重载时内存中保单与爱车数据不丢失
const data = ref(createInitialData());
const isApiConnected = ref(false);
const saving = ref(false);
const toast = ref({ show: false, message: '', type: 'success' });
const phoneConfig = ref(deepClone(DEFAULT_PHONE_CONFIG));

let toastTimer = null;
const showToast = (msg, type = 'success') => {
  toast.value = { show: true, message: msg, type };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value.show = false;
  }, 3500);
};

const clearSensitiveData = () => {
  data.value = createInitialData();
  phoneConfig.value = deepClone(DEFAULT_PHONE_CONFIG);
  AppApi.clearLocalCache();
};

export function useAppData() {

  const loadData = async () => {
    try {
      const res = await AppApi.loadData();
      data.value = res.data;
      if (!data.value.companies) {
        data.value.companies = [];
      }
      isApiConnected.value = res.isApiConnected;

      // 智能为旧版数据补齐基础档案
      if (!data.value.familyMembers || data.value.familyMembers.length === 0) {
        data.value.familyMembers = (data.value.members || []).map((m, idx) => ({
          id: 'm_' + Date.now() + '_' + idx,
          name: m,
          relation: idx === 0 ? '本人' : '家庭成员',
          gender: idx === 0 ? '男' : '女',
          birthDate: '',
          phone: '',
          hasSocialSecurity: true,
          socialSecurityCity: '',
          remark: ''
        }));
      }

      // 优先加载保险电话配置
      try {
        const phonesRes = await AppApi.loadInsurancePhones();
        if (phonesRes && phonesRes.phones) {
          phoneConfig.value = phonesRes;
        } else if (res.data && res.data.insurancePhones) {
          phoneConfig.value = res.data.insurancePhones;
        }
      } catch (_) {}
    } catch (e) {
      if (e.message === 'UNAUTHORIZED') {
        clearSensitiveData();
        throw e;
      }
      showToast('读取数据失败', 'error');
    }
  };

  const saveData = async () => {
    saving.value = true;
    try {
      data.value.insurancePhones = phoneConfig.value;
      await AppApi.saveData(data.value);
      showToast('数据已成功保存并原子落盘至本地文件！');
      isApiConnected.value = true;
    } catch (e) {
      if (e.message === 'UNAUTHORIZED') {
        showToast('访问凭据已失效，请重新解锁', 'error');
      } else {
        showToast('已保存至本地缓存 (离线模式)', 'success');
      }
    } finally {
      saving.value = false;
    }
  };

  const handleSavePhones = async (newConfig) => {
    phoneConfig.value = newConfig;
    if (!data.value) data.value = {};
    data.value.insurancePhones = newConfig;
    try {
      await AppApi.saveInsurancePhones(newConfig);
      showToast('保险机构服务与报案电话配置已成功保存！');
    } catch (e) {
      showToast('电话配置保存失败: ' + (e.message || '网络异常'), 'error');
    }
  };

  const handleSaveVehicles = async (updatedVehicles) => {
    data.value.vehicles = updatedVehicles;
    await saveData();
  };

  const handleUpdateCompanies = async (newCompanies) => {
    data.value.companies = newCompanies;
    await saveData();
    showToast('企业档案及营业执照已成功同步保存！');
  };

  const handleUpdateMembers = async ({ familyMembers: newFamilyMembers, members: newMembers }) => {
    data.value.familyMembers = newFamilyMembers;
    data.value.members = newMembers;

    // 重新计算并维护 memberSummary 预算
    data.value.memberSummary = calcMemberSummary(newMembers, data.value.policies || []);

    await saveData();
    showToast('家庭成员档案已成功同步保存！');
  };

  const handleCascadeRename = async ({ oldName, newName }) => {
    let updatedPolicies = 0;
    let updatedVehicles = 0;

    // 同步保单被保人、投保人与家庭多人参保名单
    (data.value.policies || []).forEach(p => {
      let changed = false;
      if (p.member === oldName) {
        p.member = newName;
        changed = true;
      }
      if (p.applicant === oldName) {
        p.applicant = newName;
        changed = true;
      }
      if (Array.isArray(p.insuredMembers) && p.insuredMembers.includes(oldName)) {
        p.insuredMembers = p.insuredMembers.map(m => m === oldName ? newName : m);
        changed = true;
      }
      if (changed) updatedPolicies++;
    });

    // 同步车辆所有人与日常使用人
    (data.value.vehicles || []).forEach(v => {
      let changed = false;
      if (v.owner === oldName) {
        v.owner = newName;
        changed = true;
      }
      if (v.driver === oldName) {
        v.driver = newName;
        changed = true;
      }
      if (changed) updatedVehicles++;
    });

    // 级联重算家庭成员保费预算
    data.value.memberSummary = calcMemberSummary(data.value.members || [], data.value.policies || []);

    await saveData();
    showToast(`已成功将 ${updatedPolicies} 笔保单与 ${updatedVehicles} 辆爱车归属人同步更新为【${newName}】！`);
  };

  return {
    data,
    isApiConnected,
    saving,
    toast,
    phoneConfig,
    showToast,
    clearSensitiveData,
    loadData,
    saveData,
    handleSavePhones,
    handleSaveVehicles,
    handleUpdateCompanies,
    handleUpdateMembers,
    handleCascadeRename
  };
}
