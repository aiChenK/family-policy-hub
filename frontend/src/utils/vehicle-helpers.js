/**
 * 家庭保险管理系统 - 车辆与车险业务辅助模块
 */
import { getTodayStr } from './helpers.js';
import { extractVehicleInsuranceRecords } from './payment-schedule.js';
import { AppApi } from '../api/index.js';

/**
 * 获取车辆所有保单记录（按年份逆序）
 */
export function getVehicleRecords(veh) {
  return extractVehicleInsuranceRecords(veh);
}

/**
 * 获取车辆最新一期保单记录
 */
export function getLatestPolicy(veh) {
  const records = getVehicleRecords(veh);
  return records.length > 0 ? records[0] : null;
}

/**
 * 获取车辆当前有效保单（在保期内）
 */
export function getActivePolicy(veh) {
  const records = getVehicleRecords(veh);
  if (records.length === 0) return null;
  const today = getTodayStr();

  const unexpired = records.filter(r => {
    if (r.endDate) return r.endDate >= today;
    return Number(r.year) >= new Date().getFullYear();
  });

  if (unexpired.length === 0) return null;
  const running = unexpired.find(r => r.startDate && r.startDate <= today && r.endDate >= today);
  return running || unexpired[0];
}

/**
 * 计算距离到期剩余天数
 */
export function getDaysUntilExpire(veh) {
  const active = getActivePolicy(veh);
  const target = active || getLatestPolicy(veh);
  if (!target || !target.endDate) return null;
  const today = new Date(getTodayStr());
  const endDate = new Date(target.endDate);
  const diffTime = endDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * 物理清理附件文件
 */
export async function cleanAttachmentList(attachments) {
  if (!attachments || !Array.isArray(attachments)) return;
  for (const att of attachments) {
    const fname = att.storedName || (att.url ? att.url.split('/').pop() : '');
    if (fname) {
      try {
        await AppApi.deleteAttachment(att.category || 'vehicle', fname);
      } catch (err) {
        console.warn('物理删除车辆附件失败:', err);
      }
    }
  }
}

/**
 * 推算并构建默认的新车险表单数据
 */
export function buildDefaultPolicyForm(targetId, targetVeh, prevRec) {
  let defYear = new Date().getFullYear();
  let defStart = getTodayStr();
  let defEnd = '';

  if (prevRec && prevRec.endDate) {
    const pEnd = new Date(prevRec.endDate);
    const pNextStart = new Date(pEnd);
    pNextStart.setDate(pNextStart.getDate() + 1);
    defStart = pNextStart.toISOString().slice(0, 10);

    const pNextEnd = new Date(pNextStart);
    pNextEnd.setFullYear(pNextEnd.getFullYear() + 1);
    pNextEnd.setDate(pNextEnd.getDate() - 1);
    defEnd = pNextEnd.toISOString().slice(0, 10);
    defYear = parseInt(defStart.slice(0, 4), 10) || (prevRec.year + 1);
  } else {
    const cur = new Date();
    const end = new Date(cur);
    end.setFullYear(end.getFullYear() + 1);
    end.setDate(end.getDate() - 1);
    defEnd = end.toISOString().slice(0, 10);
  }

  return {
    id: `rec_${targetId}_${defYear}_${Date.now()}`,
    vehicleId: targetId,
    year: defYear,
    company: prevRec?.company || '',
    totalPremium: prevRec?.totalPremium || null,
    commercialPolicyNo: '',
    commercialPremium: prevRec?.commercialPremium || null,
    thirdPartyAmount: prevRec?.thirdPartyAmount || '300万',
    hasDamage: prevRec ? prevRec.hasDamage : true,
    hasMedicalExcluded: prevRec ? prevRec.hasMedicalExcluded : true,
    driverAmount: prevRec?.driverAmount || '10万/座',
    extra: prevRec?.extra || '',
    startDate: defStart,
    endDate: defEnd,
    compulsoryPolicyNo: '',
    compulsoryPremium: prevRec?.compulsoryPremium || null,
    tax: prevRec?.tax !== undefined ? prevRec.tax : (targetVeh?.plateType === 'green' ? 0 : null),
    accidentPolicyNo: '',
    accidentPremium: prevRec?.accidentPremium || null,
    cashback: prevRec?.cashback || null,
    attachments: [],
    remark: ''
  };
}

/**
 * 格式化并校验保单记录以准备保存落盘
 */
export function formatPolicyRecord(form, targetVeh) {
  const cPrem = form.commercialPremium !== '' && form.commercialPremium !== null && form.commercialPremium !== undefined
    ? Number(form.commercialPremium) : 0;
  const compPrem = form.compulsoryPremium !== '' && form.compulsoryPremium !== null && form.compulsoryPremium !== undefined
    ? Number(form.compulsoryPremium) : 0;
  const tax = form.tax !== '' && form.tax !== null && form.tax !== undefined
    ? Number(form.tax) : 0;
  const accidentPrem = form.accidentPremium !== '' && form.accidentPremium !== null && form.accidentPremium !== undefined
    ? Number(form.accidentPremium) : 0;
  const cashbackVal = form.cashback !== '' && form.cashback !== null && form.cashback !== undefined && !isNaN(Number(form.cashback))
    ? Number(form.cashback) : 0;

  let finalTotal = 0;
  if (form.totalPremium !== '' && form.totalPremium !== null && form.totalPremium !== undefined && !isNaN(Number(form.totalPremium))) {
    finalTotal = Number(form.totalPremium);
  } else {
    finalTotal = cPrem + compPrem + tax + accidentPrem;
  }

  return {
    ...form,
    id: form.id || `rec_${targetVeh.id}_${form.year}_${Date.now()}`,
    vehicleId: targetVeh.id,
    year: Number(form.year),
    totalPremium: finalTotal,
    commercialPremium: cPrem,
    compulsoryPremium: compPrem,
    tax: tax,
    accidentPremium: accidentPrem,
    cashback: cashbackVal,
    commercialPolicyNo: (form.commercialPolicyNo || '').trim(),
    compulsoryPolicyNo: (form.compulsoryPolicyNo || '').trim(),
    accidentPolicyNo: (form.accidentPolicyNo || '').trim(),
    dueDate: form.startDate || `${form.year}-01-01`
  };
}

/**
 * 构建默认的新车登记表单数据
 */
export function buildDefaultVehicleForm(members = []) {
  return {
    id: 'v_' + Date.now(),
    plateNo: '',
    plateType: 'blue',
    isCompany: false,
    companyName: '',
    driver: '',
    model: '',
    owner: members[0] || '',
    vin: '',
    registerDate: '',
    annualInspectionDate: '',
    remark: '',
    attachments: []
  };
}

/**
 * 统计 60 天内待年检的车辆数
 */
export function countInspectionSoon(vehicles = []) {
  const today = new Date(getTodayStr());
  return vehicles.filter(v => {
    if (!v.annualInspectionDate) return false;
    const inspectDate = new Date(v.annualInspectionDate);
    const diffDays = Math.ceil((inspectDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 60;
  }).length;
}

/**
 * 车辆列表多维度综合过滤
 */
export function filterVehicles(vehicles = [], { query = '', owner = '', status = 'all' } = {}) {
  const q = (query || '').trim().toLowerCase();
  return vehicles.filter(v => {
    if (owner) {
      if (owner === '__company__') {
        if (!v.isCompany && !v.companyName) return false;
      } else {
        const isMatch = v.owner === owner || v.companyName === owner;
        if (!isMatch) return false;
      }
    }

    const days = getDaysUntilExpire(v);
    const hasActive = !!getActivePolicy(v);
    if (status === 'active' && !hasActive) return false;
    if (status === 'expiring' && (days === null || days < 0 || days > 30)) return false;
    if (status === 'no_policy' && hasActive) return false;

    if (q) {
      const matchPlate = (v.plateNo || '').toLowerCase().includes(q);
      const matchModel = (v.model || '').toLowerCase().includes(q);
      const matchOwner = (v.owner || '').toLowerCase().includes(q);
      const matchComp = (v.companyName || '').toLowerCase().includes(q);
      const matchDriver = (v.driver || '').toLowerCase().includes(q);
      const active = getActivePolicy(v);
      const latest = getLatestPolicy(v);
      const matchCompany = ((active?.company || latest?.company) || '').toLowerCase().includes(q);
      if (!matchPlate && !matchModel && !matchOwner && !matchComp && !matchDriver && !matchCompany) return false;
    }
    return true;
  });
}

