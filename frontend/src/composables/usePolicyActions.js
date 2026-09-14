import { ref } from 'vue';
import { getTodayStr, deepClone } from '../utils/helpers.js';
import { AppApi } from '../api/index.js';

export function usePolicyActions({ data, saveData, showToast }) {
  const activeModalPolicy = ref(null);
  const activePaymentsPolicy = ref(null);
  const editForm = ref({
    show: false,
    isNew: false,
    data: {}
  });

  const viewPolicyDetail = (pol) => {
    activeModalPolicy.value = pol;
  };

  const viewPolicyPayments = (pol) => {
    activePaymentsPolicy.value = pol;
  };

  const closePolicyPayments = () => {
    activePaymentsPolicy.value = null;
  };

  const openAddModal = () => {
    const todayStr = getTodayStr();
    editForm.value = {
      show: true,
      isNew: true,
      data: {
        id: Date.now(),
        policyNo: '',
        member: data.value.members?.[0] || '成员',
        applicant: data.value.members?.[0] || '成员',
        beneficiary: '法定受益人',
        paymentFrequency: '年缴',
        paymentAccount: '',
        exclusions: '',
        waitingPeriod: '',
        gracePeriod: '60天',
        salesChannel: '',
        attachments: [],
        type: '重疾险+寿险',
        name: '',
        company: '',
        amount: '',
        startDate: todayStr,
        endDate: '终身',
        coveragePeriod: '终身',
        paymentYears: 20,
        paymentMonthDay: todayStr.slice(5),
        premium: 0,
        premiumDetail: '',
        description: '',
        extra: '',
        status: 'active',
        stopYear: null
      }
    };
  };

  const openEditModal = (pol) => {
    const copy = deepClone(pol);
    if (!copy.startDate && copy.coverageDates) {
      copy.startDate = copy.coverageDates.split('~')[0].trim();
      copy.endDate = copy.coverageDates.split('~')[1]?.trim() || '终身';
    }
    if (!copy.paymentYears) {
      copy.paymentYears = 20;
    }
    if (!copy.coveragePeriod) {
      copy.coveragePeriod = copy.endDate === '终身' ? '终身' : `${copy.paymentYears}年`;
    }
    if (!copy.paymentMonthDay) {
      copy.paymentMonthDay = copy.startDate ? copy.startDate.slice(5) : '01-01';
    }
    if (!copy.applicant) {
      copy.applicant = copy.member;
    }
    if (!copy.beneficiary) {
      copy.beneficiary = '法定受益人';
    }
    if (!copy.paymentFrequency) {
      copy.paymentFrequency = '年缴';
    }
    if (!copy.attachments) {
      copy.attachments = [];
    }
    editForm.value = {
      show: true,
      isNew: false,
      data: copy
    };
  };

  const savePolicyForm = () => {
    const p = editForm.value.data;
    if (!p.name) {
      alert('请输入产品名称');
      return;
    }
    if (!p.startDate) {
      p.startDate = getTodayStr();
    }
    if (!p.endDate) {
      p.endDate = '终身';
    }
    if (!p.paymentMonthDay) {
      p.paymentMonthDay = p.startDate.slice(5);
    }
    p.paymentYears = Number(p.paymentYears) || 1;
    p.period = p.paymentYears > 1 ? `${p.coveragePeriod || '终身'}/${p.paymentYears}年` : `${p.coveragePeriod || '1年'}/1年`;
    p.coverageDates = `${p.startDate}~${p.endDate}`;

    if (editForm.value.isNew) {
      data.value.policies.push(p);
    } else {
      const idx = data.value.policies.findIndex(x => x.id === p.id);
      if (idx !== -1) {
        data.value.policies[idx] = p;
      }
    }
    editForm.value.show = false;
    saveData();
  };

  const deletePolicy = async (id) => {
    const targetPolicy = (data.value.policies || []).find(p => p.id === id);
    if (!targetPolicy) return;

    if (confirm(`确认删除保单【${targetPolicy.name || '未命名'}】吗？关联附件也将同步清理。`)) {
      if (targetPolicy.attachments && targetPolicy.attachments.length > 0) {
        for (const att of targetPolicy.attachments) {
          const fname = att.storedName || (att.url ? att.url.split('/').pop() : '');
          if (fname) {
            try {
              await AppApi.deleteAttachment(att.category || 'personal', fname);
            } catch (err) {
              console.warn('物理删除保单附件异常:', err);
            }
          }
        }
      }

      data.value.policies = data.value.policies.filter(p => p.id !== id);
      editForm.value.show = false;
      await saveData();
      showToast('保单及关联附件已成功删除！');
    }
  };

  return {
    activeModalPolicy,
    activePaymentsPolicy,
    editForm,
    viewPolicyDetail,
    viewPolicyPayments,
    closePolicyPayments,
    openAddModal,
    openEditModal,
    savePolicyForm,
    deletePolicy
  };
}
