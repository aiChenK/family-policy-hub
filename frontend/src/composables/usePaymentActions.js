import { getTodayStr } from '../utils/helpers.js';
import { AppApi } from '../api/index.js';
import { exportToJson, importFromJson, exportToICS } from '../utils/export.js';

export function usePaymentActions({ data, activePolicies, saveData, showToast }) {
  const togglePaymentConfirm = async (item, targetPaidStatus) => {
    // 若未传入 targetPaidStatus，则取当前 isPaid 的反向状态
    const newPaid = targetPaidStatus !== undefined ? targetPaidStatus : !item.isPaid;
    const todayStr = getTodayStr();

    if (!data.value.paymentRecords) {
      data.value.paymentRecords = { updatedAt: '', confirmations: {}, archiveRecords: [] };
    }
    if (!data.value.paymentRecords.confirmations) {
      data.value.paymentRecords.confirmations = {};
    }

    const conf = {
      policyId: item.policyId || 0,
      year: item.year,
      paid: newPaid,
      paidDate: newPaid ? (item.paidDate || item.dueDate || todayStr) : '',
      paidAmount: item.premium,
      note: newPaid ? (item.isVehicle ? '录入已支付' : (item.isArchive ? '历史归档已确认' : '系统自动代扣/已确认')) : '手动标记扣款失败/未缴',
      confirmedAt: new Date().toLocaleString()
    };
    data.value.paymentRecords.confirmations[item.key] = conf;

    try {
      await AppApi.confirmPaymentRecord(item.key, conf);
      showToast(newPaid ? `已确认：${item.member} - ${item.name} (${item.year}年) 状态正常已扣款` : `已将 ${item.name} (${item.year}年) 标记为扣款异常/未缴`, newPaid ? 'success' : 'info');
    } catch (e) {
      await saveData();
    }
  };

  const confirmAllDuePayments = async (dueList) => {
    if (!dueList || dueList.length === 0) {
      showToast('当前筛选条件下无待核实保费', 'info');
      return;
    }
    if (!confirm(`确认将当前筛选的 ${dueList.length} 笔到期保费全部标记为“已缴费”吗？`)) {
      return;
    }
    const todayStr = getTodayStr();
    if (!data.value.paymentRecords) {
      data.value.paymentRecords = { updatedAt: '', confirmations: {}, archiveRecords: [] };
    }
    if (!data.value.paymentRecords.confirmations) {
      data.value.paymentRecords.confirmations = {};
    }

    dueList.forEach(item => {
      data.value.paymentRecords.confirmations[item.key] = {
        policyId: item.policyId,
        year: item.year,
        paid: true,
        paidDate: item.dueDate <= todayStr ? item.dueDate : todayStr,
        paidAmount: item.premium,
        note: '批量确认已缴',
        confirmedAt: new Date().toLocaleString()
      };
    });

    await saveData();
    showToast(`成功批量确认 ${dueList.length} 笔保费！`);
  };

  const handleExportJson = () => {
    try {
      exportToJson(data.value);
      showToast('JSON 数据备份导出成功！');
    } catch (e) {
      showToast('导出 JSON 失败: ' + e.message, 'error');
    }
  };

  const handleImportJson = async (file) => {
    try {
      const imported = await importFromJson(file);
      if (confirm(`已成功解析备份文件，包含 ${(imported.policies || []).length} 笔保单。确认覆盖当前数据吗？`)) {
        data.value = imported;
        await saveData();
        showToast('数据恢复成功并已落盘！');
      }
    } catch (e) {
      showToast(e.message, 'error');
    }
  };

  const handleExportIcs = () => {
    try {
      exportToICS(activePolicies.value);
      showToast('日历订阅文件 (.ics) 导出成功，双击即可加入系统日历！');
    } catch (e) {
      showToast('导出日历失败: ' + e.message, 'error');
    }
  };

  /**
   * 保存或更新缴费记录详细信息（支持单期金额调整、日期修改、新一年续费登记）
   */
  const savePaymentRecordDetail = async (payload) => {
    const { key, policyId, year, paid, paidAmount, paidDate, note } = payload;
    if (!key) return;

    if (!data.value.paymentRecords) {
      data.value.paymentRecords = { updatedAt: '', confirmations: {}, archiveRecords: [] };
    }
    if (!data.value.paymentRecords.confirmations) {
      data.value.paymentRecords.confirmations = {};
    }

    const conf = {
      policyId: policyId || 0,
      year: Number(year),
      paid: paid !== false,
      paidDate: paidDate || '',
      paidAmount: Number(paidAmount) || 0,
      note: note || '',
      skipped: false,
      deleted: false,
      confirmedAt: new Date().toLocaleString()
    };
    data.value.paymentRecords.confirmations[key] = conf;

    // 若对应的是历史归档记录，同步更新 archiveRecords 原生条目
    if (data.value.paymentRecords.archiveRecords) {
      const targetArch = data.value.paymentRecords.archiveRecords.find(a => a.id === key);
      if (targetArch) {
        targetArch.premium = conf.paidAmount;
        if (conf.paidDate) targetArch.paymentDate = conf.paidDate;
        targetArch.paid = conf.paid;
        targetArch.note = conf.note;
      }
    }

    try {
      await AppApi.confirmPaymentRecord(key, conf);
      showToast(`缴费记录已更新保存（${year}年，¥${conf.paidAmount}）`, 'success');
    } catch (e) {
      await saveData();
    }
  };

  /**
   * 将某一期记录标记为断缴/排除（从台账流水中剔除）
   */
  const skipPaymentRecord = async (item) => {
    if (!item || !item.key) return;

    if (!data.value.paymentRecords) {
      data.value.paymentRecords = { updatedAt: '', confirmations: {}, archiveRecords: [] };
    }
    if (!data.value.paymentRecords.confirmations) {
      data.value.paymentRecords.confirmations = {};
    }

    const conf = {
      policyId: item.policyId || 0,
      year: item.year,
      paid: false,
      skipped: true,
      deleted: true,
      note: item.isArchive ? '历史归档记录已从台账剔除' : '中途断缴/未参保 (已从台账剔除)',
      confirmedAt: new Date().toLocaleString()
    };
    data.value.paymentRecords.confirmations[item.key] = conf;

    try {
      await AppApi.confirmPaymentRecord(item.key, conf);
      showToast(`已将 ${item.name} (${item.year}年) 标记为断缴并从台账剔除`, 'info');
    } catch (e) {
      await saveData();
    }
  };

  return {
    togglePaymentConfirm,
    confirmAllDuePayments,
    savePaymentRecordDetail,
    skipPaymentRecord,
    handleExportJson,
    handleImportJson,
    handleExportIcs
  };
}
